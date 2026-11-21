"""File-manifest integration adapter for constructing Merkle trees from integrity manifests."""

import struct

from integrity_toolkit.crypto import get_algorithm_spec
from integrity_toolkit.integrity.models import IntegrityManifest, ManifestEntry
from integrity_toolkit.integrity.traversal import normalize_posix_path
from integrity_toolkit.merkle.exceptions import AdapterError
from integrity_toolkit.merkle.models import MerkleTree
from integrity_toolkit.merkle.tree import build_merkle_tree

# Binary format identifier (S03-ADR-001 / S03-merkle-format.md)
FORMAT_MAGIC = b"CIT-MLF1"


def serialize_manifest_entry(entry: ManifestEntry, algorithm: str) -> bytes:
    """Encode a ManifestEntry into canonical binary format CIT-MLF1.

    Binary Format Layout:
    - FORMAT_MAGIC: 8 bytes ASCII ("CIT-MLF1")
    - PATH_LEN: 4 bytes uint32 big-endian (>I)
    - PATH_BYTES: UTF-8 encoded relative POSIX path
    - ALGO_LEN: 2 bytes uint16 big-endian (>H)
    - ALGO_BYTES: UTF-8 encoded canonical algorithm identifier
    - FILE_SIZE: 8 bytes uint64 big-endian (>Q)
    - DIGEST_BYTES: Raw digest bytes from hex string

    Args:
        entry: Validated ManifestEntry instance.
        algorithm: Registered algorithm identifier (e.g. 'sha256').

    Returns:
        Canonical byte payload for Merkle leaf construction.

    Raises:
        AdapterError: If path, size, or digest string is invalid.
    """
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
    """Construct a MerkleTree from an IntegrityManifest.

    Manifest entries are deterministically ordered by normalized path
    before serialization to guarantee identical Merkle roots for equivalent
    manifests regardless of initial entry order.

    Args:
        manifest: IntegrityManifest instance.

    Returns:
        Constructed MerkleTree instance.

    Raises:
        AdapterError: If manifest parameter is invalid.
        EmptyTreeError: If manifest entries list is empty.
    """
    if not isinstance(manifest, IntegrityManifest):
        raise AdapterError(
            f"Expected IntegrityManifest instance, got {type(manifest).__name__}"
        )

    # Sort entries deterministically by normalized POSIX path
    sorted_entries = sorted(manifest.entries, key=lambda e: normalize_posix_path(e.path))

    leaf_payloads = [
        serialize_manifest_entry(entry, manifest.algorithm)
        for entry in sorted_entries
    ]

    return build_merkle_tree(leaf_payloads, algorithm=manifest.algorithm)
