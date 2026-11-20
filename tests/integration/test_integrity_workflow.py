"""End-to-end integration tests for the file fingerprinting and integrity verification subsystem."""

import pytest

from integrity_toolkit.cli.main import main
from integrity_toolkit.integrity import (
    VerificationStatus,
    create_manifest,
    load_manifest,
    save_manifest,
    verify_manifest,
)


@pytest.mark.parametrize("algorithm", ["sha256", "sha512", "blake2b"])
def test_full_integrity_lifecycle(tmp_path, algorithm):
    # Setup file hierarchy
    root = tmp_path / "project"
    root.mkdir()

    (root / "README.md").write_bytes(b"# Sample Project\n")
    (root / "data.bin").write_bytes(bytes(range(100)))
    sub = root / "src" / "pkg"
    sub.mkdir(parents=True)
    (sub / "module.py").write_bytes(b"print('hello')\n")

    manifest_path = tmp_path / f"manifest_{algorithm}.json"

    # Step 1: Create manifest
    manifest = create_manifest(root, algorithm=algorithm)
    assert len(manifest.entries) == 3
    assert manifest.algorithm == algorithm

    # Step 2: Save and reload manifest
    save_manifest(manifest, manifest_path)
    reloaded = load_manifest(manifest_path)
    assert reloaded.entries == manifest.entries

    # Step 3: Initial verification must succeed 100%
    report = verify_manifest(root, reloaded)
    assert report.is_success
    assert report.total == 3
    assert report.matched == 3

    # Step 4: Introduce modifications
    # a) Modify README.md
    (root / "README.md").write_bytes(b"# Modified Title\n")
    # b) Delete data.bin
    (root / "data.bin").unlink()
    # c) Add unexpected file
    (root / "unexpected.log").write_bytes(b"log data\n")

    # Step 5: Verification after changes must report failures
    report2 = verify_manifest(root, reloaded)
    assert not report2.is_success
    assert report2.matched == 1  # module.py
    assert report2.modified == 1  # README.md
    assert report2.missing == 1  # data.bin
    assert report2.unexpected == 1  # unexpected.log


def test_cli_end_to_end_workflow(tmp_path, capsys):
    root = tmp_path / "demo_app"
    root.mkdir()

    (root / "file1.txt").write_bytes(b"Content 1")
    (root / "file2.txt").write_bytes(b"Content 2")

    manifest_file = root / "integrity-manifest.json"

    # 1. CLI fingerprint directory
    exit_fp = main(["fingerprint", str(root), "-o", str(manifest_file)])
    assert exit_fp == 0
    assert manifest_file.exists()

    # 2. CLI verify success
    exit_ver1 = main(["verify", str(root), "-m", str(manifest_file)])
    assert exit_ver1 == 0
    out1 = capsys.readouterr().out
    assert "Overall Status: SUCCESS" in out1
    assert "MATCH       : 2" in out1

    # 3. Modify a file
    (root / "file1.txt").write_bytes(b"Altered Content 1")

    # 4. CLI verify failure (exit code 1)
    exit_ver2 = main(["verify", str(root), "-m", str(manifest_file)])
    assert exit_ver2 == 1
    out2 = capsys.readouterr().out
    assert "Overall Status: FAILED" in out2
    assert "MODIFIED    : 1" in out2
