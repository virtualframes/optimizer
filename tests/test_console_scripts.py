import importlib.metadata as md
import pytest

def test_console_scripts_present():
    """
    Tests that all console scripts defined in pyproject.toml are properly registered.
    """
    expected_scripts = {
        "optimizer",
        "map-tree",
        "api-map",
        "api-health",
        "api-heal",
        "api-debug",
        "jules-export-neo4j",
        "jules-service-overlay",
        "jules-risk-scan",
        "jules-run-agent",
        "omega-inject",
        "omega-stress",
        "jules-index-context",
        "jules-retrieve-context",
        "jules-auto-mutate",
        "jules-generate-dashboard",
    }

    # Use the modern .select() method, which is correct for Python 3.10+
    registered_scripts = {ep.name for ep in md.entry_points().select(group="console_scripts")}

    missing_scripts = expected_scripts - registered_scripts

    assert not missing_scripts, f"Missing console scripts: {sorted(list(missing_scripts))}"