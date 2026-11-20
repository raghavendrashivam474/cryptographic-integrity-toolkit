"""Unit tests for Sprint 02 CLI subcommands (fingerprint and verify)."""

import pytest

from integrity_toolkit.cli.main import main
from integrity_toolkit.integrity import create_manifest, save_manifest


def test_cli_fingerprint_single_file(tmp_path, capsys):
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"pdf content bytes")

    exit_code = main(["fingerprint", str(f)])
    assert exit_code == 0

    captured = capsys.readouterr().out
    assert "FILE FINGERPRINT" in captured
    assert f"File       : {f}" in captured
    assert "Algorithm  : SHA256" in captured
    assert "Status     : SUCCESS" in captured


def test_cli_fingerprint_directory_creates_manifest(tmp_path, capsys):
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "b.txt").write_bytes(b"b")

    manifest_file = tmp_path / "out_manifest.json"

    exit_code = main(["fingerprint", str(tmp_path), "--output", str(manifest_file)])
    assert exit_code == 0
    assert manifest_file.exists()

    captured = capsys.readouterr().out
    assert "Generated integrity manifest (2 entries)" in captured


def test_cli_fingerprint_directory_without_output_fails(tmp_path, capsys):
    exit_code = main(["fingerprint", str(tmp_path)])
    assert exit_code == 2

    err = capsys.readouterr().err
    assert "--output manifest path is required" in err


def test_cli_fingerprint_nonexistent_target(capsys):
    exit_code = main(["fingerprint", "nonexistent_file_999.xyz"])
    assert exit_code == 3

    err = capsys.readouterr().err
    assert "Target path not found" in err


def test_cli_verify_success(tmp_path, capsys):
    (tmp_path / "file.txt").write_bytes(b"content")

    manifest = create_manifest(tmp_path, algorithm="sha256")
    manifest_file = tmp_path / "manifest.json"
    save_manifest(manifest, manifest_file)

    exit_code = main(["verify", str(tmp_path), "--manifest", str(manifest_file)])
    assert exit_code == 0

    captured = capsys.readouterr().out
    assert "INTEGRITY VERIFICATION" in captured
    assert "MATCH       : 1" in captured
    assert "Overall Status: SUCCESS" in captured


def test_cli_verify_detects_modification_exit_code_1(tmp_path, capsys):
    f = tmp_path / "file.txt"
    f.write_bytes(b"content")

    manifest = create_manifest(tmp_path, algorithm="sha256")
    manifest_file = tmp_path / "manifest.json"
    save_manifest(manifest, manifest_file)

    # Modify file after manifest generation
    f.write_bytes(b"modified content")

    exit_code = main(["verify", str(tmp_path), "--manifest", str(manifest_file)])
    assert exit_code == 1

    captured = capsys.readouterr().out
    assert "MODIFIED    : 1" in captured
    assert "Overall Status: FAILED" in captured


def test_cli_verify_missing_manifest_exit_code_3(tmp_path, capsys):
    exit_code = main(["verify", str(tmp_path), "--manifest", "missing_manifest.json"])
    assert exit_code == 3

    err = capsys.readouterr().err
    assert "File Error" in err
