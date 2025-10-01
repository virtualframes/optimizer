"""
CLI entrypoint for the optimizer package.

Command-line interface for launching and configuring optimizer simulations.
"""

import argparse
import sys
from typing import Optional

from . import __version__
from .node import Node
from .engine import Engine
from .auth_matrix import AuthMatrix, PermissionLevel


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="optimizer",
        description="Augmented optimizer for virtual node simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  optimizer run --nodes 10 --duration 5.0
  optimizer run --gui --nodes 5
  optimizer version
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument(
        "--nodes",
        type=int,
        default=5,
        help="Number of nodes to simulate (default: 5)"
    )
    run_parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Simulation duration in seconds (default: 10.0)"
    )
    run_parser.add_argument(
        "--gui",
        action="store_true",
        help="Show PyBullet GUI"
    )
    run_parser.add_argument(
        "--auth",
        action="store_true",
        help="Enable authentication matrix"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    return parser


def run_simulation(args) -> int:
    """
    Run a simulation with the specified parameters.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success)
    """
    print(f"Starting optimizer simulation with {args.nodes} nodes...")
    print(f"Duration: {args.duration} seconds")
    print(f"GUI: {'enabled' if args.gui else 'disabled'}")
    print(f"Authentication: {'enabled' if args.auth else 'disabled'}")
    
    # Create nodes
    nodes = []
    for i in range(args.nodes):
        node = Node(
            position=(i * 2.0, 0.0, 5.0),
            mass=1.0,
            metadata={"index": i}
        )
        nodes.append(node)
        print(f"Created {node}")
    
    # Setup authentication if requested
    auth_matrix = None
    if args.auth:
        auth_matrix = AuthMatrix()
        print("\nSetting up authentication matrix...")
        for node in nodes:
            token = auth_matrix.register_node(node.node_id)
            # Verify the node
            auth_matrix.verify_node(node.node_id, token)
            print(f"  Registered and verified node {node.node_id}")
        
        # Grant permissions between nodes (example: full mesh with READ permission)
        for node1 in nodes:
            for node2 in nodes:
                if node1.node_id != node2.node_id:
                    auth_matrix.grant_permission(
                        node1.node_id,
                        node2.node_id,
                        PermissionLevel.READ
                    )
    
    # Run physics simulation
    print("\nStarting physics engine...")
    with Engine(gui=args.gui) as engine:
        # Add nodes to simulation
        for node in nodes:
            engine.add_node(node)
        
        # Calculate number of steps
        steps = int(args.duration / engine.time_step)
        print(f"Simulating {steps} steps...")
        
        # Run simulation
        for step in range(steps):
            engine.step()
            
            # Print progress every 10%
            if (step + 1) % (steps // 10) == 0 or step == 0:
                progress = (step + 1) / steps * 100
                print(f"  Progress: {progress:.0f}%")
        
        # Sync final states
        print("\nFinal node states:")
        for node in nodes:
            engine.sync_node(node)
            print(f"  {node}")
    
    print("\nSimulation completed successfully!")
    return 0


def show_version(args) -> int:
    """
    Show version information.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0)
    """
    print(f"optimizer version {__version__}")
    return 0


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.command == "run":
        return run_simulation(args)
    elif args.command == "version":
        return show_version(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
