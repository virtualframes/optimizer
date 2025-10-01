import click

from optimizer.core.engine import Engine
from optimizer.core.settings import JulesSettings
from optimizer.logging_config import setup_logging, get_logger


@click.group()
def cli():
    """Optimizer CLI for running simulations."""
    pass


@cli.command()
def run():
    """
    Run a simulation.
    """
    # Settings are now loaded automatically from .env
    settings = JulesSettings()

    setup_logging()
    logger = get_logger(__name__)

    logger.info("Starting simulation from CLI...")
    logger.info(f"Running in '{settings.jules_env}' environment.")

    engine = Engine()

    # This is a placeholder for a simulation loop.
    logger.info("Running a short simulation loop...")
    for i in range(100):  # Simulate 100 steps
        engine.step_simulation()

    engine.disconnect()

    logger.info("Simulation finished.")
    click.echo("Simulation complete.")


if __name__ == "__main__":
    cli()