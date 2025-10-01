"""CLI entrypoint for optimizer."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from optimizer.config import get_settings, load_settings_from_yaml, setup_logging
from optimizer.core import Node
from optimizer.engine import PyBulletEngine
from optimizer.auth import AuthMatrix
import numpy as np


console = Console()


@click.group()
@click.option("--config", type=click.Path(exists=True), help="Path to YAML config file")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def cli(config, debug):
    """Optimizer: Virtual node and game engine authentication matrix simulation."""
    if config:
        settings = load_settings_from_yaml(Path(config))
    else:
        settings = get_settings()
    
    if debug:
        settings.debug = True
        settings.logging.level = "DEBUG"
    
    setup_logging(
        level=settings.logging.level,
        format_type=settings.logging.format,
        output_file=settings.logging.output_file
    )


@cli.command()
@click.option("--nodes", type=int, default=10, help="Number of nodes to simulate")
@click.option("--steps", type=int, default=100, help="Number of simulation steps")
@click.option("--gui", is_flag=True, help="Use PyBullet GUI")
def simulate(nodes, steps, gui):
    """Run a physics simulation with virtual nodes."""
    console.print(f"[bold green]Starting simulation with {nodes} nodes for {steps} steps[/bold green]")
    
    # Create nodes
    node_list = []
    for i in range(nodes):
        position = np.random.uniform(-10, 10, 3)
        velocity = np.random.uniform(-1, 1, 3)
        node = Node(
            position=position,
            velocity=velocity,
            mass=np.random.uniform(0.5, 2.0),
            metadata={"index": i}
        )
        node_list.append(node)
    
    console.print(f"[cyan]Created {len(node_list)} nodes[/cyan]")
    
    # Run simulation
    with PyBulletEngine(gui=gui) as engine:
        # Add nodes to simulation
        for node in node_list:
            engine.add_node(node)
        
        console.print("[cyan]Running simulation...[/cyan]")
        
        # Simulate
        for step in range(steps):
            engine.step_simulation()
            
            if step % 10 == 0:
                console.print(f"Step {step}/{steps}", end="\r")
        
        console.print()
        
        # Update nodes from simulation
        for node in node_list:
            engine.update_node_from_simulation(node)
        
        # Display results
        table = Table(title="Simulation Results")
        table.add_column("Node ID", style="cyan")
        table.add_column("Position", style="magenta")
        table.add_column("Velocity", style="green")
        
        for node in node_list[:5]:  # Show first 5 nodes
            table.add_row(
                node.id[:8] + "...",
                f"({node.position[0]:.2f}, "
                f"{node.position[1]:.2f}, {node.position[2]:.2f})",
                f"({node.velocity[0]:.2f}, "
                f"{node.velocity[1]:.2f}, {node.velocity[2]:.2f})"
            )
        
        console.print(table)
    
    console.print("[bold green]Simulation complete![/bold green]")


@cli.command()
@click.option("--nodes", type=int, default=5, help="Number of nodes")
@click.option("--credentials", type=int, default=10, help="Number of credentials")
def auth(nodes, credentials):
    """Demonstrate authentication matrix functionality."""
    console.print(f"[bold green]Creating authentication matrix with {nodes} nodes[/bold green]")
    
    auth_matrix = AuthMatrix()
    
    # Create nodes
    node_ids = [f"node_{i}" for i in range(nodes)]
    for node_id in node_ids:
        auth_matrix.add_node(node_id)
    
    # Create random credentials
    import random
    for _ in range(credentials):
        source = random.choice(node_ids)
        target = random.choice(node_ids)
        if source != target:
            trust_level = random.uniform(0.5, 1.0)
            auth_matrix.add_credential(
                source,
                target,
                "trust",
                trust_level=trust_level
            )
    
    console.print(f"[cyan]Created {auth_matrix.get_node_count()} nodes and {auth_matrix.get_credential_count()} credentials[/cyan]")
    
    # Show trust relationships
    table = Table(title="Trust Relationships")
    table.add_column("Source", style="cyan")
    table.add_column("Target", style="magenta")
    table.add_column("Trust Level", style="green")
    
    for (source, target), cred in list(auth_matrix.credentials.items())[:10]:
        table.add_row(source, target, f"{cred.trust_level:.2f}")
    
    console.print(table)
    
    # Verify trust paths
    if len(node_ids) >= 2:
        source = node_ids[0]
        target = node_ids[-1]
        path = auth_matrix.verify_trust_path(source, target)
        
        if path:
            trust_score = auth_matrix.get_trust_score(source, target)
            console.print(f"[green]Trust path from {source} to {target}: {' -> '.join(path)}[/green]")
            console.print(f"[green]Trust score: {trust_score:.2f}[/green]")
        else:
            console.print(f"[yellow]No trust path from {source} to {target}[/yellow]")


@cli.command()
def info():
    """Display system information."""
    settings = get_settings()
    
    table = Table(title="Optimizer Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("App Name", settings.app_name)
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("API Host", settings.api.host)
    table.add_row("API Port", str(settings.api.port))
    table.add_row("Log Level", settings.logging.level)
    table.add_row("Simulation Time Step", str(settings.simulation.time_step))
    table.add_row("Use GUI", str(settings.simulation.use_gui))
    
    console.print(table)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
