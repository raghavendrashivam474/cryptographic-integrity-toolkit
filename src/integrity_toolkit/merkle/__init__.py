"""Merkle Tree Construction Subsystem."""

from typing import Any

from integrity_toolkit.merkle.exceptions import (
    AdapterError,
    EmptyTreeError,
    InvalidNodeDigestError,
    MerkleError,
)
from integrity_toolkit.merkle.hashing import hash_internal, hash_leaf
from integrity_toolkit.merkle.models import MerkleTree
from integrity_toolkit.merkle.tree import build_merkle_tree

__all__ = [
    "MerkleError",
    "EmptyTreeError",
    "InvalidNodeDigestError",
    "AdapterError",
    "MerkleTree",
    "hash_leaf",
    "hash_internal",
    "build_merkle_tree",
    "serialize_manifest_entry",
    "build_merkle_tree_from_manifest",
]


def __getattr__(name: str) -> Any:
    """Lazy-load manifest adapter exports on-demand to maintain strict package boundaries."""
    if name in ("serialize_manifest_entry", "build_merkle_tree_from_manifest"):
        import integrity_toolkit.merkle.adapters as adapters
        return getattr(adapters, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
