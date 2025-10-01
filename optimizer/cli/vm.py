"""
CLI commands for managing containerized agent deployments.
"""
import asyncio
import typer
from rich.console import Console
from rich.table import Table

from optimizer.vm_integration.enhanced_vm_manager import (
EnhancedVMManager,
RepoCloneConfig,
DeploymentConfig,
)

app = typer.Typer(
name="vm",
help="Manage containerized agent deployments (clone, build, run).",
no_args_is_help=True,
)
console = Console()

@app.command()
def deploy(
repo_url: str = typer.Option(..., "--repo", help="The Git repository URL to clone."),
branch: str = typer.Option("main", "--branch", help="The branch to clone."),
agent_name: str = typer.Option(..., "--agent", help="A unique name for the agent deployment."),
auth_token: str = typer.Option(None, "--token", help="HTTPS auth token for private repositories."),
ssh_key_path: str = typer.Option(None, "--ssh-key", help="Path to an SSH private key for private repositories."),
):
    """
    Clone a repository, build a Docker image, and run it as a containerized agent.
    """
    console.print(f"🚀 Starting deployment for agent '{agent_name}' from '{repo_url}'...")

    repo_cfg = RepoCloneConfig(
        repo_url=repo_url,
        branch=branch,
        auth_token=auth_token,
        ssh_key_path=ssh_key_path,
    )

    dep_cfg = DeploymentConfig(
        agent_name=agent_name,
        # These could also be exposed as CLI options
    )

    async def _deploy():
        mgr = EnhancedVMManager()
        result = await mgr.deploy_containerized_agent(repo_cfg, dep_cfg)
        if result.ok:
            console.print("[green]✅ Deployment successful![/green]")
            table = Table("Attribute", "Value")
            for key, value in result.details.items():
                table.add_row(key, str(value))
            console.print(table)
        else:
            console.print("[red]❌ Deployment failed.[/red]")
            console.print(result.details.get("error", "An unknown error occurred."))

    asyncio.run(_deploy())

@app.command(name="list")
def list_deployments():
    """List all active agent deployments managed by the service."""
    console.print("Listing active deployments...")

    async def _list():
        mgr = EnhancedVMManager()
        deployments = await mgr.list_deployments()
        if not deployments:
            console.print("No active deployments found.")
            return

        table = Table("Container Name", "Image", "Status", "Host Port")
        for name, details in deployments.items():
            table.add_row(
                name,
                details.get("image", "N/A"),
                details.get("status", "N/A"),
                str(details.get("host_port", "N/A")),
            )
        console.print(table)

    asyncio.run(_list())

@app.command()
def stop(
    container_name: str = typer.Argument(..., help="The name of the container to stop."),
    remove: bool = typer.Option(True, "--remove/--no-remove", help="Also remove the container after stopping."),
):
    """Stop and optionally remove a running agent container."""
    console.print(f"Stopping container '{container_name}' (Remove: {remove})...")

    async def _stop():
        mgr = EnhancedVMManager()
        await mgr.stop_deployment(container_name, remove=remove)
        console.print("[green]✅ Operation complete.[/green]")

    asyncio.run(_stop())

@app.command()
def health(
    container_name: str = typer.Argument(..., help="The name of the container to check."),
):
    """Check the health of a running agent container."""
    console.print(f"Checking health of '{container_name}'...")

    async def _health():
        mgr = EnhancedVMManager()
        result = await mgr.health_check(container_name)

        table = Table("Metric", "Status")
        table.add_row("Docker Status", result.get("docker_status", "unknown"))

        http_ok = result.get("http_ok")
        if http_ok is True:
            status = "[green]OK[/green]"
        elif http_ok is False:
            status = "[red]Failed[/red]"
        else:
            status = "N/A"
        table.add_row("HTTP Health Probe", status)

        console.print(table)

    asyncio.run(_health())