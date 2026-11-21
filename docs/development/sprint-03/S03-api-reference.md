# Merkle Subsystem API Reference Specification

## Module: integrity_toolkit.merkle

### Data Models (integrity_toolkit.merkle.models)

#### MerkleTree
Immutable container representing a constructed Merkle tree.
* algorithm: str — Canonical algorithm name (e.g., 'sha256').
* leaf_count: int — Number of leaves in the tree (N >= 1).
* 
oot: str — Lowercase hexadecimal string of the Merkle root digest.
* levels: tuple[tuple[str, ...], ...] — Complete tree structure ordered from leaf level (levels[0]) to root (levels[-1]).

### Core Cryptographic Hashing (integrity_toolkit.merkle.hashing)

#### hash_leaf(data: bytes | bytearray, algorithm: str = "sha256") -> str
Computes domain-separated leaf hash H(0x00 || data).

#### hash_internal(left_digest: str, right_digest: str, algorithm: str = "sha256") -> str
Computes domain-separated internal node hash H(0x01 || raw_left || raw_right).

### Generic Tree Construction Engine (integrity_toolkit.merkle.tree)

#### build_merkle_tree(leaves: Iterable[bytes | bytearray], algorithm: str = "sha256") -> MerkleTree
Constructs a deterministic Merkle Tree from an iterable of byte payloads.

### Manifest Adapter (integrity_toolkit.merkle.adapters)

#### serialize_manifest_entry(entry: ManifestEntry, algorithm: str) -> bytes
Encodes a manifest entry into binary format CIT-MLF1.

#### build_merkle_tree_from_manifest(manifest: IntegrityManifest) -> MerkleTree
Sorts manifest entries deterministically by path, serializes entries to CIT-MLF1 byte payloads, and constructs a MerkleTree.

### Exceptions (integrity_toolkit.merkle.exceptions)
* MerkleError(Exception) — Base exception for Merkle subsystem errors.
* EmptyTreeError(MerkleError, ValueError) — Raised when leaf sequence is empty.
* InvalidNodeDigestError(MerkleError, ValueError) — Raised when child hex digest length or hex format is invalid.
* AdapterError(MerkleError, ValueError) — Raised when manifest entry conversion fails.
