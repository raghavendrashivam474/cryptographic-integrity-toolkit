"""Unit tests for the command-line interface."""

import pytest

from integrity_toolkit.cli.main import create_parser, main


def test_parser_creation():
    """Test argument parser initialization."""
    parser = create_parser()
    assert parser.prog == "integrity"


def test_cli_version_flag(capsys):
    """Test integrity --version flag outputs version and exits cleanly."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "integrity 0.0.1" in captured.out


def test_cli_help_flag(capsys):
    """Test integrity --help flag outputs help string."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "usage: integrity" in captured.out
    assert "Cryptographic Integrity Toolkit" in captured.out


def test_cli_no_args_displays_help(capsys):
    """Test running integrity with no arguments defaults to help output."""
    exit_code = main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage: integrity" in captured.out


def test_cli_invalid_argument(capsys):
    """Test running integrity with invalid options fails with exit code 2."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--invalid-flag"])

    assert exc_info.value.code != 0
    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err