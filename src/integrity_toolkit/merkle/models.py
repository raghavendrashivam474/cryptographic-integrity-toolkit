"""Data models for the integrity_toolkit.merkle subsystem."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MerkleTree:
    """Immutable representation of a constructed Merkle tree.

    Attributes:
        algorithm: Canonical hash algorithm name used (e.g. 'sha256').
        leaf_count: Total number of leaf nodes in the tree (N >= 1).
        root: Hexadecimal Merkle root digest string.
        levels: Complete level-by-level node structure stored as a tuple of tuples.
                `levels[0]` contains Level 0 leaf hashes.
                `levels[-1]` contains the single-element tuple `(root,)`.
    """

    algorithm: str
    leaf_count: int
    root: str
    levels: tuple[tuple[str, ...], ...]
