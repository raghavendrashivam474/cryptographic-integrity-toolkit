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


# Sprint 01 CLI Demonstration Tests
def test_cli_hash_text_sha256(capsys):
    """Test integrity hash --text "Hello World" --algorithm sha256 output format."""
    exit_code = main(["hash", "--text", "Hello World", "--algorithm", "sha256"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Algorithm : SHA256" in captured.out
    assert "Input     : Hello World" in captured.out
    assert "Digest    : a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e" in captured.out


def test_cli_hash_text_sha512(capsys):
    """Test integrity hash --text "Hello World" --algorithm sha512."""
    exit_code = main(["hash", "--text", "Hello World", "--algorithm", "sha512"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Algorithm : SHA512" in captured.out


def test_cli_hash_text_blake2b(capsys):
    """Test integrity hash --text "Hello World" --algorithm blake2b."""
    exit_code = main(["hash", "--text", "Hello World", "--algorithm", "blake2b"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Algorithm : BLAKE2B" in captured.out


def test_cli_hash_unsupported_algorithm(capsys):
    """Test integrity hash with unsupported algorithm returns error exit code 1."""
    exit_code = main(["hash", "--text", "Hello World", "--algorithm", "md5"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Unsupported algorithm: 'md5'" in captured.err


def test_cli_hash_no_input_provided(capsys, monkeypatch):
    """Test running hash with no --text and isatty() True outputs error message."""
    # Force stdin.isatty() to return True
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    exit_code = main(["hash"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Either --text must be provided or data must be piped via stdin." in captured.err
