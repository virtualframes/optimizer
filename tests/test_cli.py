from click.testing import CliRunner
from optimizer.cli.main import cli

def test_cli_run_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['run', '--config-path', 'nonexistent.yml'])
    assert result.exit_code != 0
    assert "Error: Configuration file not found at 'nonexistent.yml'" in result.output

def test_cli_run_command_with_real_config():
    runner = CliRunner()
    # Create a dummy config file for the test
    with runner.isolated_filesystem():
        with open('config.yml', 'w') as f:
            f.write("""
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
""")
        result = runner.invoke(cli, ['run'])
        assert result.exit_code == 0
        assert "Simulation complete." in result.output