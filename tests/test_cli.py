"""Tests for the CLI module."""

import pytest
from optimizer.cli import create_parser, main


def test_create_parser():
    """Test creating the argument parser."""
    parser = create_parser()
    
    assert parser is not None
    assert parser.prog == "optimizer"


def test_parser_version():
    """Test the --version flag."""
    parser = create_parser()
    
    # This would normally exit, so we just check the parser has the action
    actions = [action.dest for action in parser._actions]
    assert "version" in actions


def test_parser_run_command_defaults():
    """Test parsing run command with defaults."""
    parser = create_parser()
    args = parser.parse_args(["run"])
    
    assert args.command == "run"
    assert args.nodes == 5
    assert args.duration == 10.0
    assert args.gui is False
    assert args.auth is False


def test_parser_run_command_custom():
    """Test parsing run command with custom arguments."""
    parser = create_parser()
    args = parser.parse_args(["run", "--nodes", "10", "--duration", "20.0", "--gui", "--auth"])
    
    assert args.command == "run"
    assert args.nodes == 10
    assert args.duration == 20.0
    assert args.gui is True
    assert args.auth is True


def test_parser_version_command():
    """Test parsing version command."""
    parser = create_parser()
    args = parser.parse_args(["version"])
    
    assert args.command == "version"


def test_main_version_command(capsys):
    """Test main function with version command."""
    result = main(["version"])
    
    assert result == 0
    
    captured = capsys.readouterr()
    assert "optimizer version" in captured.out


def test_main_no_command(capsys):
    """Test main function without a command."""
    result = main([])
    
    assert result == 1
    
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower() or "usage:" in captured.err.lower()


def test_main_run_command_basic(capsys):
    """Test main function with basic run command."""
    # Use very short duration to keep test fast
    result = main(["run", "--nodes", "2", "--duration", "0.1"])
    
    assert result == 0
    
    captured = capsys.readouterr()
    assert "Starting optimizer simulation" in captured.out
    assert "Simulation completed successfully" in captured.out
