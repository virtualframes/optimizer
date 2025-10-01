import click
import os

from optimizer.config.settings import load_config
from optimizer.core.engine import Engine
from optimizer.logging_config import setup_logging, get_logger


@click.group()
def cli():
    """Optimizer CLI for running simulations."""
    pass


@cli.command()
@click.option(
    "--config-path", default="config.yml", help="Path to the configuration file."
)
def run(config_path):
    """
    Run a simulation.
    """
    if not os.path.exists(config_path):
        click.echo(f"Error: Configuration file not found at '{config_path}'")
        raise click.Abort()
    settings = load_config(config_path)

    setup_logging()
    logger = get_logger(__name__)

    logger.info(f"Starting simulation from CLI with config from {config_path}...")

    engine = Engine()

    # This is a placeholder for a simulation loop.
    # In a real application, you would load nodes and run the simulation for a specified duration.
    logger.info("Running a short simulation loop...")
    for i in range(100):  # Simulate 100 steps
        engine.step_simulation()

    engine.disconnect()

    logger.info("Simulation finished.")
    click.echo("Simulation complete.")


if __name__ == "__main__":
    cli()
