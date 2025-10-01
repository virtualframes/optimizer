import logging
from click.testing import CliRunner
from optimizer.cli.main import cli


def test_cli_run_command_loads_env_settings():
    """
    Tests that the `run` command correctly loads settings from environment variables.
    """
    # Reset logging to a clean state to prevent test pollution from other tests
    # that might have configured file-based logging. This is a known issue.
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    runner = CliRunner()

    # Define a custom environment for the test
    test_env_name = "test-execution-environment"

    # Use the `env` parameter of `invoke` to set the environment variable for the test run
    # and capture the output.
    result = runner.invoke(cli, ["run"], env={"JULES_ENV": test_env_name})

    # Assert that the command executed successfully
    assert result.exit_code == 0
    assert "Simulation complete." in result.output

    # Assert that the log output confirms the correct environment was loaded
    assert f"Running in '{test_env_name}' environment." in result.output