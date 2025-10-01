import click

from intel_harvester.config.settings import load_config_into_global_settings
from intel_harvester.core.engine import Engine
from intel_harvester.logging_config import setup_logging, get_logger

@click.group()
def cli():
    """Optimizer CLI for running simulations."""
    pass

@cli.command()
@click.option('--config-path', help='Path to the configuration file.')
def run(config_path):
    """
    Run a simulation.
    """
    if config_path:
        try:
            load_config_into_global_settings(config_path)
        except FileNotFoundError:
            click.echo(f"Error: Configuration file not found at '{config_path}'")
            return

    setup_logging()
    logger = get_logger(__name__)

    logger.info(f"Starting simulation from CLI...")

    engine = Engine()

    logger.info("Running a short simulation loop...")
    for i in range(100):
        engine.step_simulation()

    engine.disconnect()

    logger.info("Simulation finished.")
    click.echo("Simulation complete.")

if __name__ == "__main__":
    cli()