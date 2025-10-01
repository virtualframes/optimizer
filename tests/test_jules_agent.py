import os
import pytest
from agents.jules.debugandpatch import debug_and_patch

@pytest.fixture
def cleanup_test_file():
    """
    A pytest fixture to clean up the test file created by the agent.
    """
    yield
    if os.path.exists("temp_fix.txt"):
        os.remove("temp_fix.txt")

def test_debug_and_patch_end_to_end(cleanup_test_file):
    """
    Tests the end-to-end functionality of the debug_and_patch agent.
    """
    # 1. Define a simulated traceback
    simulated_traceback = "ModuleNotFoundError: No module named 'some_missing_dependency'"

    # 2. Run the debug and patch agent
    pr_url = debug_and_patch(simulated_traceback, "test_source")

    # 3. Assert that the patch was applied
    assert os.path.exists("temp_fix.txt")

    # 4. Assert that the content of the file is correct
    with open("temp_fix.txt", "r") as f:
        content = f.read()
    assert "# Fix: Added missing dependency identified by Jules." in content

    # 5. Assert that a mock PR URL was returned
    assert pr_url == "https://github.com/example/repo/pull/123"