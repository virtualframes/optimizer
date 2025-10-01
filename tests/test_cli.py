from typer.testing import CliRunner
from optimizer.cli.main import app

runner = CliRunner()

def test_jules_benchmark():
    result = runner.invoke(app, ["jules-benchmark", "--trials", "1"])
    assert result.exit_code == 0
    assert "stress complete" in result.stdout