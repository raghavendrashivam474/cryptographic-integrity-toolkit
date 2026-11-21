"""Unit tests for file manifest Merkle inclusion proofs."""

import pytest
from integrity_toolkit.integrity.models import IntegrityManifest, ManifestEntry
from integrity_toolkit.merkle.adapters import (
    build_merkle_tree_from_manifest,
    generate_manifest_inclusion_proof,
    verify_manifest_inclusion_proof,
)
from integrity_toolkit.merkle.exceptions import AdapterError


@pytest.fixture
def sample_manifest():
    entries = [
        ManifestEntry(path="file_a.txt", size=100, digest="a" * 64),
        ManifestEntry(path="dir/file_b.txt", size=200, digest="b" * 64),
        ManifestEntry(path="dir/file_c.txt", size=300, digest="c" * 64),
    ]
    return IntegrityManifest(algorithm="sha256", entries=entries)


def test_generate_and_verify_manifest_proof(sample_manifest):
    tree = build_merkle_tree_from_manifest(sample_manifest)

    # Prove file_a.txt
    proof_a = generate_manifest_inclusion_proof(sample_manifest, "file_a.txt")
    assert proof_a.leaf_count == 3
    assert verify_manifest_inclusion_proof(sample_manifest.entries[0], proof_a, tree.root) is True

    # Prove dir/file_b.txt
    proof_b = generate_manifest_inclusion_proof(sample_manifest, "dir/file_b.txt")
    assert verify_manifest_inclusion_proof(sample_manifest.entries[1], proof_b, tree.root) is True


def test_manifest_proof_path_normalization(sample_manifest):
    tree = build_merkle_tree_from_manifest(sample_manifest)

    # Normalization should handle Windows backslashes or redundant relative components
    proof = generate_manifest_inclusion_proof(sample_manifest, "dir\\file_b.txt")
    assert verify_manifest_inclusion_proof(sample_manifest.entries[1], proof, tree.root) is True


def test_manifest_proof_nonexistent_path_raises(sample_manifest):
    with pytest.raises(AdapterError, match="not found in manifest"):
        generate_manifest_inclusion_proof(sample_manifest, "nonexistent.txt")


def test_manifest_proof_modified_entry_fails_verification(sample_manifest):
    tree = build_merkle_tree_from_manifest(sample_manifest)
    entry_a = sample_manifest.entries[0]
    proof_a = generate_manifest_inclusion_proof(sample_manifest, entry_a.path)

    # 1. Modified digest
    tampered_digest_entry = ManifestEntry(path=entry_a.path, size=entry_a.size, digest="f" * 64)
    assert verify_manifest_inclusion_proof(tampered_digest_entry, proof_a, tree.root) is False

    # 2. Modified size
    tampered_size_entry = ManifestEntry(path=entry_a.path, size=entry_a.size + 10, digest=entry_a.digest)
    assert verify_manifest_inclusion_proof(tampered_size_entry, proof_a, tree.root) is False

    # 3. Modified path
    tampered_path_entry = ManifestEntry(path="file_x.txt", size=entry_a.size, digest=entry_a.digest)
    assert verify_manifest_inclusion_proof(tampered_path_entry, proof_a, tree.root) is False
