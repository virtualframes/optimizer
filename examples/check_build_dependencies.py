#!/usr/bin/env python
"""
Example script demonstrating the build dependency checker.

This script shows how to use the build_helper module to check for
missing system dependencies before attempting to install Python packages.
"""

from optimizer.utils.build_helper import (
    DependencyChecker,
    check_build_dependencies,
    analyze_build_error,
)


def main():
    print("=" * 70)
    print("Build Dependency Checker - Example Demonstration")
    print("=" * 70)
    print()

    # Example 1: Simple check
    print("Example 1: Simple dependency check")
    print("-" * 70)
    if check_build_dependencies():
        print("✓ All build dependencies are installed!")
    else:
        print("✗ Some dependencies are missing. See messages above.")
    print()

    # Example 2: Detailed checking
    print("Example 2: Detailed dependency checking")
    print("-" * 70)
    checker = DependencyChecker()
    print(f"Detected package manager: {checker.pkg_manager}")
    print()

    # Check individual tools
    tools = ["gcc", "g++", "make", "python"]
    for tool in tools:
        exists = checker.check_command(tool)
        status = "✓ Found" if exists else "✗ Missing"
        print(f"{status}: {tool}")
    print()

    # Show installation command if needed
    if checker.missing_deps:
        print("Installation command:")
        print(f"  {checker.get_installation_command()}")
    print()

    # Example 3: Analyzing build errors
    print("Example 3: Analyzing build error messages")
    print("-" * 70)

    # Simulate some error messages
    error_examples = [
        "error: command 'gcc' failed with exit status 1",
        "g++: command not found",
        "unable to execute 'gcc': No such file or directory",
        "ImportError: No module named 'numpy'",  # Non-build error
    ]

    for error in error_examples:
        print(f"Error: {error}")
        suggestion = analyze_build_error(error)
        if suggestion:
            print("  → Detected missing build dependency!")
            print("  → Suggestion provided (see error message)")
        else:
            print("  → Not a build dependency issue")
        print()

    # Example 4: Using verify_and_suggest
    print("Example 4: Using verify_and_suggest method")
    print("-" * 70)
    checker = DependencyChecker()
    all_present, message = checker.verify_and_suggest()

    if all_present:
        print("✓ All dependencies verified!")
    else:
        print("Some dependencies need attention:")
        print(message)

    print()
    print("=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
