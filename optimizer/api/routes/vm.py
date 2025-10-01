from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Import will be available when vm_integration module is created
# from optimizer.vm_integration.enhanced_vm_manager import (
#     EnhancedVMManager,
#     RepoCloneConfig,
#     DeploymentConfig,
# )

router = APIRouter(tags=["vm"])

# --------- Request models ---------

class DeployRequest(BaseModel):
    repo_url: str = Field(..., description="Git repository URL")
    branch: str = Field("main", description="Git branch to clone")
    agent_name: str = Field(..., description="Unique name for the agent")
    auth_token: Optional[str] = Field(
        None, description="HTTPS token for private repos (optional)"
    )
    ssh_key_path: Optional[str] = Field(
        None, description="Path to SSH private key for private repos (optional)"
    )
    python_version: str = Field("3.11", description="Python base image version")
    expose_port: int = Field(8080, description="Service port exposed by the container")
    startup_cmd: Optional[List[str]] = Field(
        None, description='Startup command, e.g. ["python","main.py"]'
    )
    environment: Dict[str, str] = Field(default_factory=dict)

class StopRequest(BaseModel):
    container_name: str
    remove: bool = True

# --------- Routes ---------

@router.post("/deploy")
async def deploy(req: DeployRequest):
    """
    Clone repo -> build image -> run containerized agent.
    Returns container details on success.
    """
    # Placeholder until EnhancedVMManager is implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
    )
    
    # Future implementation:
    # mgr = EnhancedVMManager()
    # 
    # repo_cfg = RepoCloneConfig(
    #     repo_url=req.repo_url,
    #     branch=req.branch,
    #     auth_token=req.auth_token,
    #     ssh_key_path=req.ssh_key_path,
    # )
    # dep_cfg = DeploymentConfig(
    #     agent_name=req.agent_name,
    #     python_version=req.python_version,
    #     expose_port=req.expose_port,
    #     startup_cmd=req.startup_cmd or ["python", "main.py"],
    #     environment=req.environment,
    # )
    # 
    # result = await mgr.deploy_containerized_agent(repo_cfg, dep_cfg)
    # if not result.ok:
    #     raise HTTPException(
    #         status_code=status.HTTP_502_BAD_GATEWAY,
    #         detail=result.details.get("error", "deployment_failed"),
    #     )
    # return result.details

@router.get("/list")
async def list_deployments():
    """List active Jules-managed containers (by label)."""
    # Placeholder until EnhancedVMManager is implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
    )
    
    # Future implementation:
    # mgr = EnhancedVMManager()
    # return await mgr.list_deployments()

@router.post("/stop")
async def stop(req: StopRequest):
    """Stop (and optionally remove) a running container."""
    # Placeholder until EnhancedVMManager is implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
    )
    
    # Future implementation:
    # mgr = EnhancedVMManager()
    # await mgr.stop_deployment(req.container_name, remove=req.remove)
    # return {"stopped": req.container_name, "removed": req.remove}

@router.get("/health/{container_name}")
async def health(container_name: str, path: str = "/health"):
    """
    Docker status + optional HTTP probe (uses mapped host port).
    """
    # Placeholder until EnhancedVMManager is implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
    )
    
    # Future implementation:
    # mgr = EnhancedVMManager()
    # return await mgr.health_check(container_name, path=path)
