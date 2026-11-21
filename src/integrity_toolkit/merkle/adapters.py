"""File-manifest integration adapter for constructing Merkle trees and generating manifest inclusion proofs."""

import struct
from integrity_toolkit.crypto import get_algorithm_spec
from integrity_toolkit.integrity.models import IntegrityManifest, ManifestEntry
from integrity_toolkit.integrity.traversal import normalize_posix_path
from integrity_toolkit.merkle.exceptions import AdapterError, InvalidProofError
from integrity_toolkit.merkle.models import MerkleProof, MerkleTree
from integrity_toolkit.merkle.proofs import generate_inclusion_proof
from integrity_toolkit.merkle.tree import build_merkle_tree
from integrity_toolkit.merkle.verification import verify_inclusion_proof

# Binary format identifier (S03-ADR-001 / S03-merkle-format.md)
FORMAT_MAGIC = b"CIT-MLF1"


def serialize_manifest_entry(entry: ManifestEntry, algorithm: str) -> bytes:
    """Encode a ManifestEntry into canonical binary format CIT-MLF1."""
    if not isinstance(entry, ManifestEntry):
        raise AdapterError(f"Expected ManifestEntry object, got {type(entry).__name__}")

    try:
        norm_path = normalize_posix_path(entry.path)
        path_bytes = norm_path.encode("utf-8")
    except Exception as err:
        raise AdapterError(f"Failed to encode manifest entry path: {err}") from err

    spec = get_algorithm_spec(algorithm)
    algo_bytes = spec.canonical_name.encode("utf-8")

    if entry.size < 0:
        raise AdapterError(f"Negative file size in entry for '{entry.path}': {entry.size}")

    try:
        digest_bytes = bytes.fromhex(entry.digest)
    except (ValueError, TypeError) as err:
        raise AdapterError(
            f"Invalid hex digest string in manifest entry for '{entry.path}': {err}"
        ) from err

    if len(digest_bytes) != spec.digest_size:
        raise AdapterError(
            f"Digest length mismatch for entry '{entry.path}': "
            f"expected {spec.digest_size} bytes, got {len(digest_bytes)}"
        )

    payload = (
        FORMAT_MAGIC
        + struct.pack(">I", len(path_bytes))
        + path_bytes
        + struct.pack(">H", len(algo_bytes))
        + algo_bytes
        + struct.pack(">Q", entry.size)
        + digest_bytes
    )
    return payload


def build_merkle_tree_from_manifest(manifest: IntegrityManifest) -> MerkleTree:
    """Construct a MerkleTree from an IntegrityManifest."""
    if not isinstance(manifest, IntegrityManifest):
        raise AdapterError(
            f"Expected IntegrityManifest instance, got {type(manifest).__name__}"
        )

    sorted_entries = sorted(manifest.entries, key=lambda e: normalize_posix_path(e.path))
    leaf_payloads = [
        serialize_manifest_entry(entry, manifest.algorithm)
        for entry in sorted_entries
    ]
    return build_merkle_tree(leaf_payloads, algorithm=manifest.algorithm)


def generate_manifest_inclusion_proof(
    manifest: IntegrityManifest,
    relative_path: str,
) -> MerkleProof:
    """Generate a Merkle inclusion proof for a file entry within an IntegrityManifest.

    Args:
        manifest: IntegrityManifest instance.
        relative_path: Relative file path to prove membership for.

    Returns:
        MerkleProof object.

    Raises:
        AdapterError: If manifest is invalid or target path is not found in manifest.
    """
    if not isinstance(manifest, IntegrityManifest):
        raise AdapterError(
            f"Expected IntegrityManifest instance, got {type(manifest).__name__}"
        )

    try:
        norm_target_path = normalize_posix_path(relative_path)
    except Exception as err:
        raise AdapterError(f"Invalid relative_path '{relative_path}': {err}") from err

    sorted_entries = sorted(manifest.entries, key=lambda e: normalize_posix_path(e.path))

    leaf_index = -1
    for idx, entry in enumerate(sorted_entries):
        if normalize_posix_path(entry.path) == norm_target_path:
            leaf_index = idx
            break

    if leaf_index == -1:
        raise AdapterError(f"File path '{relative_path}' not found in manifest.")

    tree = build_merkle_tree_from_manifest(manifest)
    return generate_inclusion_proof(tree, leaf_index)


def verify_manifest_inclusion_proof(
    entry: ManifestEntry,
    proof: MerkleProof,
    expected_root: str,
) -> bool:
    """Verify a manifest entry inclusion proof against a trusted Merkle root.

    Args:
        entry: ManifestEntry instance.
        proof: MerkleProof instance.
        expected_root: Trusted Merkle root hex string.

    Returns:
        True if valid and matches expected_root, False otherwise.

    Raises:
        AdapterError: If entry object is invalid.
        InvalidProofError: If proof or root format is structurally invalid.
    """
    if not isinstance(entry, ManifestEntry):
        raise AdapterError(f"Expected ManifestEntry object, got {type(entry).__name__}")

    leaf_payload = serialize_manifest_entry(entry, algorithm=proof.algorithm)
    return verify_inclusion_proof(leaf_payload, proof, expected_root)
