"""
A robust, container-centric manager for deploying and monitoring agents.

This module provides the EnhancedVMManager, a class designed to handle the
end-to-end lifecycle of an agent:
1.  **Clone**: Fetches the agent's source code from a Git repository.
2.  **Build**: Creates a Docker image from the source, auto-generating a
    Dockerfile if one doesn't exist.
3.  **Run**: Deploys the agent as a Docker container with health checks and
    restart policies.
4.  **Monitor**: Provides utilities to list, inspect, and check the health of
    running agent containers.

It uses industry-standard tools like GitPython for cloning and the Docker SDK
for container orchestration, providing a resilient and reproducible foundation
for the Jules Mission Ω agent ecosystem.
"""

import asyncio
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import docker
from docker.errors import DockerException, ImageNotFound, NotFound
from docker.models.containers import Container

# Attempt to import GitPython, but fall back to a manual subprocess call if it's not available.
# This makes the core cloning functionality more resilient to environment changes.
try:
    import git
    from git.exc import GitCommandError
except ImportError:
    git = None
    GitCommandError = Exception  # Define for consistent exception handling.

# --- Configuration Data Classes ---

@dataclass
class RepoCloneConfig:
    """Configuration for cloning a Git repository."""
    repo_url: str
    branch: str = "main"
    auth_token: Optional[str] = None
    ssh_key_path: Optional[str] = None
    clone_depth: int = 1  # Default to a shallow clone for efficiency.

@dataclass
class DeploymentConfig:
    """Configuration for deploying a container."""
    agent_name: str
    base_image: str = "python:3.11-slim"
    http_health_check_port: Optional[int] = 8080  # Port for HTTP health checks.
    dockerfile_path: Optional[str] = None  # Path to an existing Dockerfile.
    env_vars: Dict[str, str] = field(default_factory=dict)
    restart_policy: Dict[str, Any] = field(
        default_factory=lambda: {"Name": "on-failure", "MaximumRetryCount": 3}
    )

@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    ok: bool
    details: Dict[str, Any]

# --- Core Manager Class ---

class EnhancedVMManager:
    """Manages the lifecycle of containerized agents."""

    def __init__(self, docker_client: Optional[docker.DockerClient] = None):
        """
        Initializes the manager with a Docker client.

        Args:
            docker_client: An optional pre-configured Docker client. If not provided,
                           a new client will be created from the environment.
        """
        try:
            self.docker = docker_client or docker.from_env()
        except DockerException as e:
            raise RuntimeError(
                "Docker is not available or configured correctly. "
                "Please ensure the Docker daemon is running."
            ) from e

    async def deploy_containerized_agent(
        self, repo_config: RepoCloneConfig, deploy_config: DeploymentConfig
    ) -> DeploymentResult:
        """
        Orchestrates the full deployment pipeline: clone, build, and run.

        Args:
            repo_config: Configuration for the repository to clone.
            deploy_config: Configuration for the container deployment.

        Returns:
            A DeploymentResult indicating success or failure.
        """
        clone_dir = Path(f"./jules_agents/{deploy_config.agent_name}")

        # 1. Clone Repository
        clone_ok, clone_details = await self._clone_repo(repo_config, clone_dir)
        if not clone_ok:
            return DeploymentResult(ok=False, details={"error": clone_details})

        # 2. Build Docker Image
        image_tag = f"jules-agent/{deploy_config.agent_name}:latest"
        build_ok, build_details = await self._build_image(
            clone_dir, image_tag, deploy_config
        )
        if not build_ok:
            return DeploymentResult(ok=False, details={"error": build_details})

        # 3. Run Docker Container
        container_name = f"jules-agent-{deploy_config.agent_name}-{int(time.time())}"
        run_ok, run_details = await self._run_container(
            image_tag, container_name, deploy_config
        )
        if not run_ok:
            return DeploymentResult(ok=False, details={"error": run_details})

        return DeploymentResult(
            ok=True,
            details={
                "container_name": container_name,
                "image_tag": image_tag,
                "clone_directory": str(clone_dir),
                "host_port": run_details.get("host_port"),
            },
        )

    async def _clone_repo(
        self, config: RepoCloneConfig, target_dir: Path
    ) -> Tuple[bool, str]:
        """
        Clones a Git repository using GitPython with a fallback to subprocess.
        """
        if target_dir.exists():
            # For simplicity, we'll start fresh each time.
            # A more advanced implementation might `git pull`.
            subprocess.run(["rm", "-rf", str(target_dir)], check=True)

        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            if git:
                # Use GitPython if available
                git.Repo.clone_from(
                    config.repo_url,
                    to_path=str(target_dir),
                    branch=config.branch,
                    depth=config.clone_depth,
                )
            else:
                # Fallback to subprocess if GitPython is not installed
                cmd = [
                    "git", "clone", "--depth", str(config.clone_depth),
                    "--branch", config.branch, config.repo_url, str(target_dir)
                ]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True, f"Cloned to {target_dir}"
        except (GitCommandError, subprocess.CalledProcessError) as e:
            error_msg = f"Failed to clone repo: {e}"
            return False, error_msg

    async def _build_image(
        self, context_path: Path, tag: str, config: DeploymentConfig
    ) -> Tuple[bool, str]:
        """
        Builds a Docker image, auto-generating a Dockerfile if needed.
        """
        dockerfile = config.dockerfile_path or "Dockerfile"
        dockerfile_path = context_path / dockerfile

        if not dockerfile_path.exists():
            # Auto-generate a basic Dockerfile
            generated_dockerfile = self._generate_dockerfile(config, context_path)
            dockerfile_path.write_text(generated_dockerfile)

        try:
            self.docker.images.build(
                path=str(context_path),
                tag=tag,
                rm=True,       # Remove intermediate containers
                pull=True,     # Pull base image
                dockerfile=dockerfile
            )
            return True, f"Image '{tag}' built successfully."
        except DockerException as e:
            return False, f"Docker build failed: {e}"

    def _generate_dockerfile(self, config: DeploymentConfig, context_path: Path) -> str:
        """
        Generates a minimal Dockerfile for a Python agent.
        """
        dockerfile_content = [
            f"FROM {config.base_image}",
            "WORKDIR /app",
        ]

        # Check for requirements.txt and install dependencies
        if (context_path / "requirements.txt").exists():
            dockerfile_content.append("COPY requirements.txt .")
            dockerfile_content.append("RUN pip install --no-cache-dir -r requirements.txt")

        dockerfile_content.append("COPY . .")

        # Basic command - assumes a main.py entry point.
        # A more robust solution might inspect pyproject.toml for entry points.
        dockerfile_content.append('CMD ["python", "-u", "main.py"]')

        return "\n".join(dockerfile_content)

    async def _run_container(
        self, image_tag: str, name: str, config: DeploymentConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs a Docker container from a given image.
        """
        ports = {}
        host_port = None
        if config.http_health_check_port:
            # Bind to a dynamic host port
            ports[f"{config.http_health_check_port}/tcp"] = None

        healthcheck = (
            {
                "test": [
                    "CMD", "curl", "--fail",
                    f"http://localhost:{config.http_health_check_port}/health"
                ],
                "interval": 30 * 1_000_000_000,  # 30s
                "timeout": 10 * 1_000_000_000,   # 10s
                "retries": 3,
            }
            if config.http_health_check_port
            else None
        )

        try:
            container = self.docker.containers.run(
                image=image_tag,
                name=name,
                detach=True,
                environment=config.env_vars,
                ports=ports,
                restart_policy=config.restart_policy,
                healthcheck=healthcheck,
            )
            # Retrieve the dynamically assigned host port
            if config.http_health_check_port:
                container.reload()
                host_port = container.ports[f"{config.http_health_check_port}/tcp"][0]["HostPort"]

            return True, {"container_id": container.id, "host_port": host_port}
        except DockerException as e:
            return False, {"error": f"Failed to run container: {e}"}

    async def list_deployments(self) -> Dict[str, Dict[str, Any]]:
        """
        Lists all active agent deployments (containers with 'jules-agent-' prefix).
        """
        deployments = {}
        try:
            containers = self.docker.containers.list(
                filters={"name": "jules-agent-"}
            )
            for container in containers:
                port_data = container.ports.get(next(iter(container.ports), ""), None)
                host_port = port_data[0]['HostPort'] if port_data else "N/A"

                deployments[container.name] = {
                    "id": container.short_id,
                    "image": ", ".join(container.image.tags),
                    "status": container.status,
                    "host_port": host_port,
                }
        except DockerException as e:
            print(f"Error listing containers: {e}")
        return deployments

    async def stop_deployment(self, container_name: str, remove: bool = True) -> None:
        """
        Stops and optionally removes a container.
        """
        try:
            container = self.docker.containers.get(container_name)
            container.stop()
            if remove:
                container.remove()
            print(f"Container '{container_name}' stopped and removed.")
        except NotFound:
            print(f"Container '{container_name}' not found.")
        except DockerException as e:
            print(f"Error stopping container '{container_name}': {e}")

    async def health_check(self, container_name: str) -> Dict[str, Any]:
        """
        Checks the health of a specific container.
        """
        result = {"docker_status": "not_found", "http_ok": None}
        try:
            container: Container = self.docker.containers.get(container_name)
            container.reload() # Get the latest state

            status = container.status
            result["docker_status"] = status

            # Check the internal health status if available
            health_state = container.attrs.get("State", {}).get("Health", {})
            if health_state:
                result["docker_status"] = f"{status} ({health_state.get('Status')})"

            # If an HTTP port is configured, try a direct health check
            if any("8080" in k for k in container.ports):
                port_key = next(k for k in container.ports if "8080" in k)
                host_port = container.ports[port_key][0]["HostPort"]

                try:
                    # This is a synchronous check, but acceptable for a CLI command
                    import requests
                    response = requests.get(f"http://localhost:{host_port}/health", timeout=5)
                    result["http_ok"] = response.ok
                except requests.RequestException:
                    result["http_ok"] = False

        except NotFound:
            pass # Already marked as not_found
        except (DockerException, ImportError) as e:
            result["docker_status"] = f"error: {e}"

        return result