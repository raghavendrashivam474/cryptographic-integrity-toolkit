"""Unit tests for integrity verification engine."""

import pytest

from integrity_toolkit.integrity.exceptions import FileAccessError
from integrity_toolkit.integrity.manifest import create_manifest, save_manifest
from integrity_toolkit.integrity.models import (
    IntegrityManifest,
    ManifestEntry,
    VerificationStatus,
)
from integrity_toolkit.integrity.verifier import verify_manifest


def test_verify_manifest_all_matching(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")
    (tmp_path / "b.txt").write_bytes(b"world")

    manifest = create_manifest(tmp_path, algorithm="sha256")
    manifest_path = tmp_path / "manifest.json"
    save_manifest(manifest, manifest_path)

    report = verify_manifest(tmp_path, manifest_path)

    assert report.is_success
    assert report.matched == 2
    assert report.modified == 0
    assert report.missing == 0
    assert report.unexpected == 0


def test_verify_manifest_detects_modified_content(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"initial")

    manifest = create_manifest(tmp_path, algorithm="sha256")

    # Modify file after manifest creation
    f.write_bytes(b"altered content")

    report = verify_manifest(tmp_path, manifest, ignore_unexpected=True)

    assert not report.is_success
    assert report.modified == 1
    assert report.results[0].status == VerificationStatus.MODIFIED


def test_verify_manifest_detects_missing_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"data")

    manifest = create_manifest(tmp_path, algorithm="sha256")

    # Delete file
    f.unlink()

    report = verify_manifest(tmp_path, manifest, ignore_unexpected=True)

    assert not report.is_success
    assert report.missing == 1
    assert report.results[0].status == VerificationStatus.MISSING


def test_verify_manifest_detects_unexpected_file(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"a")
    manifest = create_manifest(tmp_path, algorithm="sha256")

    # Add unexpected file after manifest creation
    (tmp_path / "extra.txt").write_bytes(b"extra")

    report = verify_manifest(tmp_path, manifest, ignore_unexpected=False)

    assert not report.is_success
    assert report.matched == 1
    assert report.unexpected == 1


def test_verify_manifest_ignore_unexpected_option(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"a")
    manifest = create_manifest(tmp_path, algorithm="sha256")

    (tmp_path / "extra.txt").write_bytes(b"extra")

    report = verify_manifest(tmp_path, manifest, ignore_unexpected=True)

    assert report.is_success
    assert report.matched == 1
    assert report.unexpected == 0


def test_verify_manifest_multiple_simultaneous_mismatches(tmp_path):
    (tmp_path / "match.txt").write_bytes(b"match")
    (tmp_path / "modified.txt").write_bytes(b"original")
    (tmp_path / "missing.txt").write_bytes(b"missing")

    manifest = create_manifest(tmp_path, algorithm="sha256")

    # Alter modified, remove missing, add unexpected
    (tmp_path / "modified.txt").write_bytes(b"changed")
    (tmp_path / "missing.txt").unlink()
    (tmp_path / "unexpected.txt").write_bytes(b"unexp")

    report = verify_manifest(tmp_path, manifest)

    assert not report.is_success
    assert report.matched == 1
    assert report.modified == 1
    assert report.missing == 1
    assert report.unexpected == 1
    assert report.total == 4


def test_verify_manifest_nonexistent_root_raises():
    m = IntegrityManifest()
    with pytest.raises(FileAccessError, match="Verification root directory not found"):
        verify_manifest("nonexistent_root_dir_999", m)
