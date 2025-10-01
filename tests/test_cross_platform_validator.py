import os
import stat
import subprocess
from unittest.mock import patch, mock_open, AsyncMock, MagicMock

import pytest

# Since `cross_platform_validator` is a proper package and the root is on the pythonpath,
# these imports should work without any special path manipulation.
from cross_platform_validator.validator import CrossPlatformValidator
from cross_platform_validator.workflow import CrossPlatformValidationWorkflow, run_validation_activity

# Mark all workflow/activity tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# --- Fixtures ---

@pytest.fixture
def validator():
    """Fixture to create a CrossPlatformValidator instance with a dummy repo path."""
    test_repo_path = "/tmp/test_repo"
    os.makedirs(test_repo_path, exist_ok=True)
    return CrossPlatformValidator(test_repo_path)

# --- Validator Tests ---

@patch("os.walk")
def test_validate_line_endings_crlf(mock_walk, validator, capsys):
    """Test that CRLF line endings are detected."""
    repo_path = validator.repo_path
    mock_walk.return_value = [(repo_path, [], ["script.sh"])]
    with patch("builtins.open", mock_open(read_data=b"#!/bin/bash\r\necho 'hello'")):
        validator.validate_line_endings()
    captured = capsys.readouterr()
    assert f"[WARNING] CRLF line endings found in: {repo_path}/script.sh" in captured.out

@patch("os.walk")
@patch("os.stat")
def test_validate_permissions_missing(mock_stat, mock_walk, validator, capsys):
    """Test that missing executable permissions are detected."""
    repo_path = validator.repo_path
    mock_walk.return_value = [(repo_path, [], ["script.sh"])]
    mock_stat.return_value.st_mode = 0o644
    validator.validate_permissions()
    captured = capsys.readouterr()
    assert f"[WARNING] Missing executable permission on: {repo_path}/script.sh" in captured.out

@patch("os.walk")
def test_validate_case_sensitivity_collision(mock_walk, validator, capsys):
    """Test that case sensitivity collisions are detected."""
    repo_path = validator.repo_path
    mock_walk.return_value = [(repo_path, [], ["File.txt", "file.txt"])]
    validator.validate_case_sensitivity()
    captured = capsys.readouterr()
    assert "Potential case-sensitivity collision" in captured.out
    assert "'file.txt'" in captured.out
    assert "'File.txt'" in captured.out

# --- Workflow and Activity Tests ---

@patch("cross_platform_validator.workflow.workflow", new_callable=MagicMock)
async def test_workflow_run(mock_workflow_module):
    """Test the main run method of the CrossPlatformValidationWorkflow."""
    mock_workflow_module.execute_activity = AsyncMock(return_value="Validation complete.")
    mock_workflow_module.logger = MagicMock()
    workflow_instance = CrossPlatformValidationWorkflow()
    result = await workflow_instance.run("/test/repo")
    mock_workflow_module.execute_activity.assert_called_once()
    assert result == "Validation complete."

@patch("cross_platform_validator.workflow.CrossPlatformValidator")
@patch("cross_platform_validator.workflow.activity", new_callable=MagicMock)
async def test_activity_run(mock_activity_module, MockValidator):
    """Test the `run_validation_activity` function."""
    mock_activity_module.logger = MagicMock()
    mock_validator_instance = MockValidator.return_value
    result = await run_validation_activity("/test/repo")
    MockValidator.assert_called_once_with("/test/repo")
    mock_validator_instance.run_all.assert_called_once()
    assert "Validation completed for /test/repo" in result