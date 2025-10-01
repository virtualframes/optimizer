"""
Enhanced VM Manager with Repository Cloning and AI Agent Deployment.

This module intentionally avoids tight coupling to the rest of the repo so it can be
dropped in and run via:
    python -m optimizer.vm_integration.enhanced_vm_manager

Features:
- Repository cloning (GitHub/GitLab/any git remote) with token/SSH support
- Branch selection, shallow/sparse clones, include/exclude patterns
- Containerized agent deployment via Docker (build/run/port mapping/env)
- Minimal runtime monitor to satisfy systemd ExecStart long-running behavior
- Lightweight, dependency-tolerant: works if GitPython is missing (falls back to subprocess)

NOTE:
- Standalone VM providers (Hyper-V/VMware/libvirt) are intentionally omitted to keep
  first cut portable. Containerized deployments are production-friendly and simpler.

"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import signal
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional dependencies: we handle absence gracefully
try:
    import docker  # type: ignore
    from docker.errors import DockerException  # type: ignore
except Exception:  # pragma: no cover
    docker = None  # type: ignore
    DockerException = Exception  # type: ignore

try:
    import git  # GitPython
except Exception:  # pragma: no cover
    git = None

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("JULES_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [enhanced_vm_manager] %(message)s",
)


# ------------------------------------------------------------------------------
# Data Models
# ------------------------------------------------------------------------------

class DeploymentType(Enum):
    CONTAINERIZED = "containerized"
    STANDALONE = "standalone"  # reserved; not implemented in this cut


class RepoType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"


@dataclass
class RepoCloneConfig:
    repo_url: str
    branch: str = "main"
    clone_path: Optional[str] = None
    depth: Optional[int] = None  # shallow clone
    recursive: bool = True
    repo_type: RepoType = RepoType.PUBLIC
    auth_token: Optional[str] = None  # HTTPS token (e.g., GH PAT)
    ssh_key_path: Optional[str] = None  # e.g., ~/.ssh/id_rsa
    clone_strategy: str = "full"  # "full" | "shallow" | "sparse"
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class DeploymentConfig:
    deployment_type: DeploymentType = DeploymentType.CONTAINERIZED
    agent_name: str = "agent"
    python_version: str = "3.11"
    requirements_file: str = "requirements.txt"
    startup_cmd: List[str] = field(default_factory=lambda: ["python", "main.py"])
    environment: Dict[str, str] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)  # mem_limit, cpu_count
    expose_port: int = 8080  # container port that app listens on
    healthcheck_path: str = "/health"
    auto_restart: bool = True
    image_tag: Optional[str] = None  # override image tag if desired


@dataclass
class DeploymentResult:
    ok: bool
    details: Dict[str, Any]


# ------------------------------------------------------------------------------
# Utility helpers
# ------------------------------------------------------------------------------

def _inject_token_into_https_url(url: str, token: str) -> str:
    """
    Convert https://host/org/repo.git into https://<token>@host/org/repo.git
    without double-injecting or breaking ssh URLs.
    """
    if url.startswith("git@") or url.startswith("ssh://"):
        return url  # SSH URL, don't inject token
    # If already has credentials, leave it
    if re.match(r"^https?://[^/]+@.+", url):
        return url
    return re.sub(r"^https?://", f"https://{token}@", url)


async def _run_subprocess(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd) if cwd else None,
        env=env or os.environ.copy(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    return proc.returncode, out.decode(errors="ignore"), err.decode(errors="ignore")


# ------------------------------------------------------------------------------
# Manager
# ------------------------------------------------------------------------------

class EnhancedVMManager:
    """
    Enhanced VM Manager focused on:
      - Cloning repos with flexible auth & strategies
      - Building & running Dockerized agents
      - Tracking deployments in-memory

    The class is intentionally self-contained so it can run as a systemd worker.
    """

    def __init__(self) -> None:
        # Paths (can be overridden via env)
        self.clone_base_path = Path(os.getenv("VM_CLONE_BASE_PATH", "/var/lib/jules/repos"))
        self.deploy_base_path = Path(os.getenv("VM_DEPLOYMENT_BASE_PATH", "/var/lib/jules/deployments"))
        self.clone_base_path.mkdir(parents=True, exist_ok=True)
        self.deploy_base_path.mkdir(parents=True, exist_ok=True)

        # Docker client (optional)
        self.docker_client = None
        if docker is not None:
            try:
                self.docker_client = docker.from_env()  # type: ignore
                _ = self.docker_client.ping()
                logger.info("Docker client ready")
            except Exception as e:
                logger.warning(f"Docker not available: {e}. Containerized deploys will fail.")

        # State
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        self._shutdown = asyncio.Event()

    # ------------------------------------------------------------------
    # Repository Cloning
    # ------------------------------------------------------------------

    async def clone_repository(self, cfg: RepoCloneConfig) -> str:
        """
        Clone a repository to local disk (returns local path).
        Prefers GitPython if available; falls back to 'git' subprocess.
        Supports: shallow, recursive, sparse checkout, tokens, ssh key.
        """
        # Determine target path
        if cfg.clone_path:
            dest = Path(cfg.clone_path)
        else:
            repo_name = re.sub(r"\.git$", "", Path(cfg.repo_url).name)
            dest = self.clone_base_path / f"{repo_name}-{int(time.time())}"

        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Prepare env for auth
        env = os.environ.copy()
        repo_url = cfg.repo_url

        # Token-based auth for HTTPS
        if cfg.auth_token and repo_url.startswith("http"):
            repo_url = _inject_token_into_https_url(repo_url, cfg.auth_token)

        # SSH key path
        if cfg.ssh_key_path:
            env["GIT_SSH_COMMAND"] = f"ssh -i {cfg.ssh_key_path} -o StrictHostKeyChecking=no"

        # --- Try GitPython if present ---
        if git is not None:
            try:
                clone_kwargs: Dict[str, Any] = {"branch": cfg.branch, "depth": cfg.depth} if cfg.depth else {"branch": cfg.branch}
                logger.info(f"Cloning (GitPython) {cfg.repo_url} -> {dest} (branch={cfg.branch}, depth={cfg.depth})")
                await asyncio.to_thread(git.Repo.clone_from, repo_url, str(dest), multi_options=["--recursive"] if cfg.recursive else None, **clone_kwargs)  # type: ignore
                # Sparse checkout
                if cfg.clone_strategy == "sparse" and cfg.include_patterns:
                    await self._apply_sparse_checkout(dest, cfg.include_patterns, cfg.exclude_patterns)
                return str(dest)
            except Exception as e:
                logger.warning(f"GitPython clone failed, falling back to subprocess. Error: {e}")

        # --- Fallback: subprocess git clone ---
        cmd = ["git", "clone"]
        if cfg.depth:
            cmd += ["--depth", str(cfg.depth)]
        if cfg.recursive:
            cmd += ["--recursive"]
        if cfg.clone_strategy == "sparse":
            cmd += ["--filter=blob:none"]
        cmd += ["-b", cfg.branch, repo_url, str(dest)]

        logger.info(f"Cloning (subprocess) {cfg.repo_url} -> {dest}")
        rc, out, err = await _run_subprocess(cmd, env=env)
        if rc != 0:
            raise RuntimeError(f"git clone failed: {err.strip() or out.strip()}")

        if cfg.clone_strategy == "sparse" and cfg.include_patterns:
            await self._apply_sparse_checkout(dest, cfg.include_patterns, cfg.exclude_patterns)

        return str(dest)

    async def _apply_sparse_checkout(self, repo_path: Path, includes: List[str], excludes: List[str]) -> None:
        """
        Enable sparse checkout and write include/exclude patterns.
        """
        logger.info(f"Applying sparse checkout to {repo_path}")
        cfg_cmds = [
            ["git", "config", "core.sparseCheckout", "true"],
        ]
        for cmd in cfg_cmds:
            rc, _, err = await _run_subprocess(cmd, cwd=repo_path)
            if rc != 0:
                raise RuntimeError(f"Sparse config failed: {err}")

        sparse_file = repo_path / ".git" / "info" / "sparse-checkout"
        sparse_file.parent.mkdir(parents=True, exist_ok=True)
        with sparse_file.open("w", encoding="utf-8") as f:
            for p in includes:
                f.write(p.strip() + "\n")
            for p in excludes:
                f.write("!" + p.strip() + "\n")

        rc, _, err = await _run_subprocess(["git", "read-tree", "-mu", "HEAD"], cwd=repo_path)
        if rc != 0:
            raise RuntimeError(f"Sparse read-tree failed: {err}")

    # ------------------------------------------------------------------
    # Containerized Deployment
    # ------------------------------------------------------------------

    async def deploy_containerized_agent(
        self,
        repo_path: str,
        cfg: DeploymentConfig,
    ) -> DeploymentResult:
        """
        Build and run a Dockerized agent from repo_path.
        - Generates a Dockerfile if missing (Python slim base)
        - Builds image
        - Runs container with environment and port mapping
        """
        if not self.docker_client:
            return DeploymentResult(False, {"error": "Docker client not available"})

        repo = Path(repo_path)
        if not repo.exists():
            return DeploymentResult(False, {"error": f"repo_path not found: {repo_path}"})

        # Ensure a Dockerfile exists
        dockerfile = repo / "Dockerfile"
        if not dockerfile.exists():
            logger.info("No Dockerfile found, generating a minimal one.")
            dockerfile.write_text(self._generate_python_dockerfile(cfg), encoding="utf-8")

        # Build image
        tag = cfg.image_tag or f"jules-agent-{cfg.agent_name}:latest"
        logger.info(f"Building docker image: {tag}")
        try:
            image, logs = await asyncio.to_thread(self.docker_client.images.build, path=str(repo), tag=tag, rm=True)
            for chunk in logs:
                msg = (chunk.get("stream") or "").strip()
                if msg:
                    logger.debug(f"[build] {msg}")
        except Exception as e:
            logger.error(f"Image build failed: {e}")
            return DeploymentResult(False, {"error": f"build_failed: {e}"})

        # Run container
        container_name = f"jules-agent-{cfg.agent_name}-{int(time.time())}"
        port_key = f"{cfg.expose_port}/tcp"
        run_kwargs: Dict[str, Any] = dict(
            image=tag,
            name=container_name,
            detach=True,
            environment=cfg.environment or {},
            labels={"jules.agent_name": cfg.agent_name},
            ports={port_key: None},  # random host port
        )
        # Resource limits
        if cfg.resource_limits.get("mem_limit"):
            run_kwargs["mem_limit"] = cfg.resource_limits["mem_limit"]
        if cfg.resource_limits.get("cpu_count"):
            run_kwargs["cpu_count"] = cfg.resource_limits["cpu_count"]
        # Restart policy
        if cfg.auto_restart:
            run_kwargs["restart_policy"] = {"Name": "unless-stopped"}

        try:
            container = await asyncio.to_thread(self.docker_client.containers.run, **run_kwargs)  # type: ignore
            await asyncio.to_thread(container.reload)
            ports = container.attrs.get("NetworkSettings", {}).get("Ports", {})
            assigned = ports.get(port_key, [{}])[0].get("HostPort")
            info = {
                "container_id": container.id,
                "container_name": container.name,
                "image": tag,
                "port": assigned,
                "status": container.status,
            }
            self.active_deployments[container.name] = info
            logger.info(f"Container running: {info}")
            return DeploymentResult(True, info)
        except Exception as e:
            logger.error(f"Container run failed: {e}")
            return DeploymentResult(False, {"error": f"run_failed: {e}"})

    def _generate_python_dockerfile(self, cfg: DeploymentConfig) -> str:
        """
        Minimal Python Dockerfile tailored for FastAPI/CLI style agents.
        """
        run_health = (
            f'HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\\n'
            f'    CMD curl -fsS http://localhost:{cfg.expose_port}{cfg.healthcheck_path} || exit 1\n'
        )
        cmd = json.dumps(cfg.startup_cmd)
        return f"""# Generated by EnhancedVMManager
FROM python:{cfg.python_version}-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl ca-certificates git \\
    && rm -rf /var/lib/apt/lists/*

COPY {cfg.requirements_file} /app/{cfg.requirements_file}
RUN pip install --no-cache-dir -r /app/{cfg.requirements_file} || true

COPY . /app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE {cfg.expose_port}

{run_health}
CMD {cmd}
""".strip() + "\n"

    # ------------------------------------------------------------------
    # Public high-level flow
    # ------------------------------------------------------------------

    async def clone_and_deploy(
        self,
        repo_cfg: RepoCloneConfig,
        deploy_cfg: DeploymentConfig,
    ) -> DeploymentResult:
        """
        Convenience method: clone repo then deploy containerized agent.
        """
        local = await self.clone_repository(repo_cfg)
        if deploy_cfg.deployment_type == DeploymentType.CONTAINERIZED:
            return await self.deploy_containerized_agent(local, deploy_cfg)
        return DeploymentResult(False, {"error": "Only containerized deployment supported in this version."})

    # ------------------------------------------------------------------
    # Monitoring / Lifecycle
    # ------------------------------------------------------------------

    async def monitor_loop(self, interval_sec: int = 30) -> None:
        """
        Lightweight monitor loop: logs active deployments and basic health.
        Keeps the process alive for systemd.
        """
        logger.info("EnhancedVMManager monitor loop started.")
        while not self._shutdown.is_set():
            try:
                count = len(self.active_deployments)
                logger.debug(f"Active deployments: {count}")
                # Optionally, check container health if Docker available
                if self.docker_client and count:
                    for name, info in list(self.active_deployments.items()):
                        try:
                            c = await asyncio.to_thread(self.docker_client.containers.get, name)  # type: ignore
                            await asyncio.to_thread(c.reload)
                            self.active_deployments[name]["status"] = c.status
                        except Exception as e:
                            logger.warning(f"Failed to refresh {name}: {e}")
                await asyncio.wait_for(self._shutdown.wait(), timeout=interval_sec)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Monitor loop error: {e}", exc_info=True)

        logger.info("EnhancedVMManager monitor loop terminated.")

    def stop(self) -> None:
        self._shutdown.set()


# ------------------------------------------------------------------------------
# __main__ entry (for systemd ExecStart)
# ------------------------------------------------------------------------------

async def _main() -> None:
    mgr = EnhancedVMManager()

    # Allow a simple "one-shot" env-driven deployment (optional).
    # If you set JULES_AUTODEPLOY_URL (and optional token), the worker will
    # clone+deploy once at boot, then continue monitoring.
    auto_url = os.getenv("JULES_AUTODEPLOY_URL")
    if auto_url:
        logger.info("JULES_AUTODEPLOY_URL detected — performing one-shot clone+deploy.")
        repo_cfg = RepoCloneConfig(
            repo_url=auto_url,
            branch=os.getenv("JULES_AUTODEPLOY_BRANCH", "main"),
            repo_type=RepoType.PRIVATE if os.getenv("JULES_AUTODEPLOY_PRIVATE", "false").lower() == "true" else RepoType.PUBLIC,
            auth_token=os.getenv("JULES_AUTODEPLOY_TOKEN"),
            ssh_key_path=os.getenv("JULES_AUTODEPLOY_SSH_KEY"),
            clone_strategy=os.getenv("JULES_AUTODEPLOY_STRATEGY", "full"),
        )
        deploy_cfg = DeploymentConfig(
            agent_name=os.getenv("JULES_AGENT_NAME", "agent"),
            python_version=os.getenv("JULES_PYTHON_VERSION", "3.11"),
            requirements_file=os.getenv("JULES_REQUIREMENTS_FILE", "requirements.txt"),
            startup_cmd=json.loads(os.getenv("JULES_STARTUP_CMD", '["python","main.py"]')),
            environment={k[len("JULES_ENV_"):]: v for k, v in os.environ.items() if k.startswith("JULES_ENV_")},
            expose_port=int(os.getenv("JULES_EXPOSE_PORT", "8080")),
            image_tag=os.getenv("JULES_IMAGE_TAG"),
        )
        try:
            result = await mgr.clone_and_deploy(repo_cfg, deploy_cfg)
            if result.ok:
                logger.info(f"Autodeploy success: {result.details}")
            else:
                logger.error(f"Autodeploy failed: {result.details}")
        except Exception as e:
            logger.error(f"Autodeploy exception: {e}", exc_info=True)

    # Handle signals for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, mgr.stop)
        except NotImplementedError:
            # Windows or restricted env
            pass

    await mgr.monitor_loop(interval_sec=int(os.getenv("JULES_MONITOR_INTERVAL", "30")))


def main() -> None:
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()