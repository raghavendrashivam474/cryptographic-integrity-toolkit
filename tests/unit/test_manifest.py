"""Unit tests for integrity manifest creation, validation, loading, and persistence."""

import json
import pytest

from integrity_toolkit.integrity.exceptions import (
    FileAccessError,
    InvalidManifestError,
    ManifestVersionError,
    UnsafePathError,
)
from integrity_toolkit.integrity.manifest import (
    create_manifest,
    load_manifest,
    save_manifest,
    validate_manifest,
    validate_manifest_entry_path,
)
from integrity_toolkit.integrity.models import IntegrityManifest, ManifestEntry


def test_validate_manifest_entry_path_valid():
    assert validate_manifest_entry_path("src/main.py") == "src/main.py"
    assert validate_manifest_entry_path(r"src\main.py") == "src/main.py"


def test_validate_manifest_entry_path_unsafe_rejections():
    with pytest.raises(UnsafePathError):
        validate_manifest_entry_path("/etc/passwd")

    with pytest.raises(UnsafePathError):
        validate_manifest_entry_path("C:/Windows/System32")

    with pytest.raises(UnsafePathError):
        validate_manifest_entry_path("../secrets.txt")

    with pytest.raises(UnsafePathError):
        validate_manifest_entry_path("dir/../../secrets.txt")


def test_create_manifest_from_directory(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_bytes(b"world")

    m = create_manifest(tmp_path, algorithm="sha256")
    assert m.algorithm == "sha256"
    assert len(m.entries) == 2
    assert m.entries[0].path == "a.txt"
    assert m.entries[1].path == "sub/b.txt"


def test_create_manifest_excludes_destination(tmp_path):
    (tmp_path / "file1.txt").write_bytes(b"1")
    (tmp_path / "manifest.json").write_bytes(b"{}")

    m = create_manifest(tmp_path, exclude_paths=["manifest.json"])
    assert len(m.entries) == 1
    assert m.entries[0].path == "file1.txt"


def test_save_and_load_manifest_round_trip(tmp_path):
    (tmp_path / "file.txt").write_bytes(b"data")
    manifest = create_manifest(tmp_path, algorithm="sha256")

    manifest_file = tmp_path / "manifest.json"
    save_path = save_manifest(manifest, manifest_file)
    assert save_path == manifest_file.resolve()

    loaded = load_manifest(manifest_file)
    assert loaded.algorithm == manifest.algorithm
    assert loaded.entries == manifest.entries


def test_validate_manifest_invalid_format():
    m = IntegrityManifest(format="wrong-format")
    with pytest.raises(InvalidManifestError, match="Invalid manifest format"):
        validate_manifest(m)


def test_validate_manifest_unsupported_version():
    m = IntegrityManifest(version=99)
    with pytest.raises(ManifestVersionError, match="Unsupported manifest version"):
        validate_manifest(m)


def test_validate_manifest_unsupported_algorithm():
    m = IntegrityManifest(algorithm="md5")
    with pytest.raises(InvalidManifestError, match="Unsupported hash algorithm"):
        validate_manifest(m)


def test_validate_manifest_duplicate_paths():
    m = IntegrityManifest(
        entries=[
            ManifestEntry(path="a.txt", size=1, digest="a" * 64),
            ManifestEntry(path="a.txt", size=1, digest="a" * 64),
        ]
    )
    with pytest.raises(InvalidManifestError, match="Duplicate entry path"):
        validate_manifest(m)


def test_validate_manifest_invalid_digest_length():
    m = IntegrityManifest(
        entries=[ManifestEntry(path="a.txt", size=1, digest="short_hex")]
    )
    with pytest.raises(InvalidManifestError, match="Invalid digest"):
        validate_manifest(m)


def test_load_manifest_malformed_json(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("{ this is not json }", encoding="utf-8")

    with pytest.raises(InvalidManifestError, match="Malformed manifest JSON"):
        load_manifest(f)


def test_load_manifest_nonexistent_file():
    with pytest.raises(FileAccessError, match="Manifest file not found"):
        load_manifest("nonexistent_manifest_99.json")
