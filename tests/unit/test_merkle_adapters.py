"""Unit tests for file-manifest to Merkle tree adapter."""

import pytest

from integrity_toolkit.crypto import hash_bytes
from integrity_toolkit.integrity.models import IntegrityManifest, ManifestEntry
from integrity_toolkit.merkle.adapters import (
    FORMAT_MAGIC,
    build_merkle_tree_from_manifest,
    serialize_manifest_entry,
)
from integrity_toolkit.merkle.exceptions import AdapterError, EmptyTreeError


def test_serialize_manifest_entry_structure():
    """Verify CIT-MLF1 binary serialization layout."""
    digest_hex = hash_bytes(b"content", algorithm="sha256")
    entry = ManifestEntry(path="docs/readme.txt", size=1024, digest=digest_hex)

    payload = serialize_manifest_entry(entry, algorithm="sha256")

    assert payload.startswith(FORMAT_MAGIC)
    assert b"docs/readme.txt" in payload
    assert b"sha256" in payload
    assert bytes.fromhex(digest_hex) in payload


def test_build_merkle_tree_from_manifest_basic():
    """Verify building a Merkle tree from a simple manifest."""
    e1 = ManifestEntry(path="file1.txt", size=10, digest="00" * 32)
    e2 = ManifestEntry(path="file2.txt", size=20, digest="11" * 32)
    manifest = IntegrityManifest(algorithm="sha256", entries=[e1, e2])

    tree = build_merkle_tree_from_manifest(manifest)

    assert tree.leaf_count == 2
    assert tree.algorithm == "sha256"
    assert len(tree.root) == 64


def test_build_merkle_tree_from_manifest_reordering_invariance():
    """Verify that manifests with identical entries in different order yield identical Merkle roots."""
    e1 = ManifestEntry(path="a.txt", size=10, digest="00" * 32)
    e2 = ManifestEntry(path="b.txt", size=20, digest="11" * 32)
    e3 = ManifestEntry(path="c.txt", size=30, digest="22" * 32)

    m1 = IntegrityManifest(algorithm="sha256", entries=[e1, e2, e3])
    m2 = IntegrityManifest(algorithm="sha256", entries=[e3, e1, e2])

    tree1 = build_merkle_tree_from_manifest(m1)
    tree2 = build_merkle_tree_from_manifest(m2)

    assert tree1.root == tree2.root


def test_build_merkle_tree_from_manifest_path_sensitivity():
    """Verify changing entry path changes the Merkle root."""
    e1_a = ManifestEntry(path="dir_a/file.txt", size=10, digest="00" * 32)
    e1_b = ManifestEntry(path="dir_b/file.txt", size=10, digest="00" * 32)

    m_a = IntegrityManifest(algorithm="sha256", entries=[e1_a])
    m_b = IntegrityManifest(algorithm="sha256", entries=[e1_b])

    assert build_merkle_tree_from_manifest(m_a).root != build_merkle_tree_from_manifest(m_b).root


def test_build_merkle_tree_from_manifest_size_sensitivity():
    """Verify changing entry file size changes the Merkle root."""
    e1_a = ManifestEntry(path="file.txt", size=10, digest="00" * 32)
    e1_b = ManifestEntry(path="file.txt", size=99, digest="00" * 32)

    m_a = IntegrityManifest(algorithm="sha256", entries=[e1_a])
    m_b = IntegrityManifest(algorithm="sha256", entries=[e1_b])

    assert build_merkle_tree_from_manifest(m_a).root != build_merkle_tree_from_manifest(m_b).root


def test_build_merkle_tree_from_manifest_empty_raises():
    """Verify empty manifest raises EmptyTreeError."""
    m = IntegrityManifest(algorithm="sha256", entries=[])
    with pytest.raises(EmptyTreeError):
        build_merkle_tree_from_manifest(m)


def test_serialize_manifest_entry_invalid_digest_raises():
    """Verify invalid digest string in entry raises AdapterError."""
    entry = ManifestEntry(path="file.txt", size=10, digest="invalid_hex")
    with pytest.raises(AdapterError, match="Invalid hex digest"):
        serialize_manifest_entry(entry, algorithm="sha256")
