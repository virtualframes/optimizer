"""
Tests for the build helper utility.
"""

import pytest
from optimizer.utils.build_helper import (
    DependencyChecker,
    check_build_dependencies,
    analyze_build_error,
    BuildDependencyError,
)


def test_dependency_checker_init():
    """Test DependencyChecker initialization."""
    checker = DependencyChecker()
    assert checker.pkg_manager in ["apt-get", "yum", "apk", "unknown"]
    assert isinstance(checker.missing_deps, list)


def test_command_exists():
    """Test that _command_exists detects available commands."""
    checker = DependencyChecker()
    # 'python' should exist in the test environment
    assert checker._command_exists("python") or checker._command_exists("python3")


def test_check_command():
    """Test check_command method."""
    checker = DependencyChecker()
    # Check for a command that should exist
    result = checker.check_command("python")
    # Either python or python3 should exist
    if not result:
        result = checker.check_command("python3")
    # At least one should exist
    assert result or "python" in checker.missing_deps


def test_check_all_build_tools():
    """Test check_all_build_tools method."""
    checker = DependencyChecker()
    result = checker.check_all_build_tools()
    # Should return a boolean
    assert isinstance(result, bool)


def test_get_installation_command():
    """Test get_installation_command returns appropriate command."""
    checker = DependencyChecker()
    checker.missing_deps = ["gcc"]
    cmd = checker.get_installation_command()
    assert isinstance(cmd, str)
    assert len(cmd) > 0
    # Should contain package manager or installation instruction
    assert any(
        pm in cmd.lower() for pm in ["apt-get", "yum", "apk", "install", "package"]
    )


def test_get_detailed_suggestions():
    """Test get_detailed_suggestions returns list of commands."""
    checker = DependencyChecker()
    checker.missing_deps = ["gcc", "g++"]
    suggestions = checker.get_detailed_suggestions()
    assert isinstance(suggestions, list)
    assert len(suggestions) == 2


def test_verify_and_suggest():
    """Test verify_and_suggest method."""
    checker = DependencyChecker()
    all_present, message = checker.verify_and_suggest(raise_error=False)
    assert isinstance(all_present, bool)
    assert isinstance(message, str)


def test_verify_and_suggest_with_error():
    """Test verify_and_suggest raises error when dependencies missing."""
    checker = DependencyChecker()
    # Mock missing dependencies
    checker.check_command = lambda cmd: False
    checker.missing_deps = ["gcc"]

    with pytest.raises(BuildDependencyError):
        checker.verify_and_suggest(raise_error=True)


def test_format_error_message():
    """Test _format_error_message formats properly."""
    checker = DependencyChecker()
    checker.missing_deps = ["gcc"]
    message = checker._format_error_message()
    assert isinstance(message, str)
    assert "gcc" in message
    assert "ERROR" in message or "Missing" in message


def test_check_build_dependencies_function():
    """Test the convenience function check_build_dependencies."""
    result = check_build_dependencies(raise_error=False)
    assert isinstance(result, bool)


def test_analyze_build_error_detects_gcc():
    """Test analyze_build_error detects gcc errors."""
    error_output = "error: command 'gcc' failed with exit status 1"
    suggestion = analyze_build_error(error_output)
    assert suggestion is not None
    assert "gcc" in suggestion.lower()


def test_analyze_build_error_detects_gpp():
    """Test analyze_build_error detects g++ errors."""
    error_output = "g++: command not found"
    suggestion = analyze_build_error(error_output)
    assert suggestion is not None
    assert "g++" in suggestion.lower()


def test_analyze_build_error_no_match():
    """Test analyze_build_error returns None for unrelated errors."""
    error_output = "ImportError: No module named 'foo'"
    suggestion = analyze_build_error(error_output)
    assert suggestion is None


def test_dependency_map_has_required_managers():
    """Test that DEPENDENCY_MAP has common package managers."""
    assert "apt-get" in DependencyChecker.DEPENDENCY_MAP
    assert "yum" in DependencyChecker.DEPENDENCY_MAP
    assert "apk" in DependencyChecker.DEPENDENCY_MAP


def test_dependency_map_has_required_tools():
    """Test that DEPENDENCY_MAP has required tools for each manager."""
    for manager, deps in DependencyChecker.DEPENDENCY_MAP.items():
        assert "gcc" in deps
        assert "g++" in deps
        assert "make" in deps
