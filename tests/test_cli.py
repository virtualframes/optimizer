import logging
import unittest
from click.testing import CliRunner
from optimizer.cli.main import cli


class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_cli_run_command_no_config(self):
        result = self.runner.invoke(cli, ["run", "--config-path", "nonexistent.yml"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Error: Configuration file not found at 'nonexistent.yml'", result.output)

    def test_cli_run_command_with_real_config(self):
        # Reset logging to a clean state to prevent test pollution
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            handler.close()

        with self.runner.isolated_filesystem():
            with open("config.yml", "w") as f:
                f.write(
                    """
simulation:
  engine: "pybullet"
  gravity: -9.8
  time_step: 0.01

api:
  host: "0.0.0.0"
  port: 8000

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "optimizer.log"

# Add new, optional sections to match the updated Settings model
openai: {}
milvus: {}
temporal: {}
"""
                )
            # The 'run' command might not be implemented yet in the merged code,
            # so we check for a graceful exit or a NotImplementedError.
            # For now, we assume it runs and exits cleanly.
            result = self.runner.invoke(cli, ["run"])
            self.assertEqual(result.exit_code, 0)
            # The actual output might vary, so we check for a generic success message.
            # If the command is not fully implemented, this might need adjustment.
            self.assertIn("Simulation complete.", result.output)