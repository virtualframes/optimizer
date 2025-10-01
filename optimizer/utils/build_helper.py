"""
Build helper utility to detect missing system dependencies.

This module provides functionality to detect when builds fail due to missing
system dependencies and suggests installation commands for required packages.
"""

import subprocess
import sys
from typing import List, Tuple, Optional


class BuildDependencyError(Exception):
    """Raised when required build dependencies are missing."""

    pass


class DependencyChecker:
    """Check for missing system dependencies and suggest installation commands."""

    # Map of common build tools to their package names
    DEPENDENCY_MAP = {
        "apt-get": {
            "gcc": "gcc",
            "g++": "g++",
            "make": "make",
            "build-essential": "build-essential",
        },
        "yum": {
            "gcc": "gcc",
            "g++": "gcc-c++",
            "make": "make",
            "development-tools": "Development Tools",
        },
        "apk": {
            "gcc": "gcc",
            "g++": "g++",
            "make": "make",
            "build-base": "build-base",
        },
    }

    def __init__(self):
        self.pkg_manager = self._detect_package_manager()
        self.missing_deps: List[str] = []

    def _detect_package_manager(self) -> str:
        """Detect the system's package manager."""
        managers = ["apt-get", "yum", "apk"]
        for manager in managers:
            if self._command_exists(manager):
                return manager
        return "unknown"

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        try:
            subprocess.run(
                ["which", command],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def check_command(self, command: str) -> bool:
        """
        Check if a specific command is available.

        Args:
            command: The command to check (e.g., 'gcc', 'g++')

        Returns:
            True if the command exists, False otherwise
        """
        exists = self._command_exists(command)
        if not exists:
            self.missing_deps.append(command)
        return exists

    def check_all_build_tools(self) -> bool:
        """
        Check for all essential build tools.

        Returns:
            True if all tools are present, False otherwise
        """
        required_tools = ["gcc", "g++", "make"]
        all_present = all(self.check_command(tool) for tool in required_tools)
        return all_present

    def get_installation_command(self) -> str:
        """
        Get the installation command for missing dependencies.

        Returns:
            A string containing the installation command
        """
        if not self.missing_deps:
            return ""

        if self.pkg_manager == "apt-get":
            return "sudo apt-get update && sudo apt-get install -y build-essential"
        elif self.pkg_manager == "yum":
            return "sudo yum groupinstall -y 'Development Tools'"
        elif self.pkg_manager == "apk":
            return "apk add --no-cache build-base"
        else:
            return "Please install build tools using your system's package manager"

    def get_detailed_suggestions(self) -> List[str]:
        """
        Get detailed installation suggestions for each missing dependency.

        Returns:
            A list of installation command suggestions
        """
        suggestions = []

        if not self.missing_deps:
            return suggestions

        dep_map = self.DEPENDENCY_MAP.get(self.pkg_manager, {})

        for dep in self.missing_deps:
            package = dep_map.get(dep, dep)

            if self.pkg_manager == "apt-get":
                cmd = f"sudo apt-get install -y {package}"
            elif self.pkg_manager == "yum":
                cmd = f"sudo yum install -y {package}"
            elif self.pkg_manager == "apk":
                cmd = f"apk add --no-cache {package}"
            else:
                cmd = f"Install {package} using your system's package manager"

            suggestions.append(cmd)

        return suggestions

    def verify_and_suggest(self, raise_error: bool = False) -> Tuple[bool, str]:
        """
        Verify all dependencies and return suggestions if any are missing.

        Args:
            raise_error: If True, raises BuildDependencyError when dependencies are missing

        Returns:
            A tuple of (all_present, suggestion_message)

        Raises:
            BuildDependencyError: If raise_error is True and dependencies are missing
        """
        all_present = self.check_all_build_tools()

        if all_present:
            return True, ""

        message = self._format_error_message()

        if raise_error:
            raise BuildDependencyError(message)

        return False, message

    def _format_error_message(self) -> str:
        """Format a detailed error message with installation suggestions."""
        lines = [
            "=" * 60,
            "ERROR: Missing required build dependencies!",
            "=" * 60,
            "",
            "The following build tools are required but not found:",
        ]

        for dep in self.missing_deps:
            lines.append(f"  ✗ {dep}")

        lines.extend(
            [
                "",
                "These tools are needed to compile Python packages like pybullet.",
                "",
                "To install all required dependencies, run:",
                f"  {self.get_installation_command()}",
                "",
                "After installing dependencies, try again with:",
                "  pip install -r requirements.txt",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    def print_status(self):
        """Print the dependency check status to stdout."""
        if self.check_all_build_tools():
            print("✓ All required build dependencies are installed")
        else:
            print(self._format_error_message())


def check_build_dependencies(raise_error: bool = False) -> bool:
    """
    Convenience function to check build dependencies.

    Args:
        raise_error: If True, raises BuildDependencyError when dependencies are missing

    Returns:
        True if all dependencies are present, False otherwise

    Raises:
        BuildDependencyError: If raise_error is True and dependencies are missing
    """
    checker = DependencyChecker()
    all_present, message = checker.verify_and_suggest(raise_error=raise_error)

    if not all_present and message:
        print(message, file=sys.stderr)

    return all_present


def analyze_build_error(error_output: str) -> Optional[str]:
    """
    Analyze build error output to detect missing dependencies.

    Args:
        error_output: The error output from a failed build

    Returns:
        A suggestion string if missing dependencies are detected, None otherwise
    """
    # Common error patterns that indicate missing build tools
    error_patterns = [
        ("gcc: command not found", "gcc"),
        ("g++: command not found", "g++"),
        ("make: command not found", "make"),
        ("error: command 'gcc' failed", "gcc"),
        ("error: command 'g++' failed", "g++"),
        ("unable to execute 'gcc'", "gcc"),
        ("unable to execute 'g++'", "g++"),
    ]

    error_lower = error_output.lower()

    for pattern, tool in error_patterns:
        if pattern in error_lower:
            checker = DependencyChecker()
            checker.missing_deps.append(tool)
            return checker._format_error_message()

    return None


if __name__ == "__main__":
    # When run as a script, check dependencies and exit with appropriate code
    checker = DependencyChecker()
    checker.print_status()
    sys.exit(0 if checker.check_all_build_tools() else 1)
