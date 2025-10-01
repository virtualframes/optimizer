from typer.testing import CliRunner
from optimizer.cli.main import app

runner = CliRunner()

def test_run_command():
    """
    Tests the placeholder 'run' command.
    """
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 0
    assert "Running main agent... (to be implemented)" in result.stdout