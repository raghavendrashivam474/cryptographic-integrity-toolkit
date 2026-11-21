"""Merkle Tree Construction and Inclusion Proof Subsystem."""

from typing import Any

from integrity_toolkit.merkle.exceptions import (
    AdapterError,
    EmptyTreeError,
    InvalidNodeDigestError,
    InvalidProofError,
    MerkleError,
)
from integrity_toolkit.merkle.hashing import hash_internal, hash_leaf
from integrity_toolkit.merkle.models import MerkleProof, MerkleProofStep, MerkleTree, ProofOperation
from integrity_toolkit.merkle.proofs import generate_inclusion_proof
from integrity_toolkit.merkle.tree import build_merkle_tree
from integrity_toolkit.merkle.verification import verify_inclusion_proof

__all__ = [
    "MerkleError",
    "EmptyTreeError",
    "InvalidNodeDigestError",
    "AdapterError",
    "InvalidProofError",
    "MerkleTree",
    "MerkleProof",
    "MerkleProofStep",
    "ProofOperation",
    "hash_leaf",
    "hash_internal",
    "build_merkle_tree",
    "generate_inclusion_proof",
    "verify_inclusion_proof",
    "serialize_manifest_entry",
    "build_merkle_tree_from_manifest",
    "generate_manifest_inclusion_proof",
    "verify_manifest_inclusion_proof",
]


def __getattr__(name: str) -> Any:
    """Lazy-load manifest adapter exports on-demand to maintain strict package boundaries."""
    if name in (
        "serialize_manifest_entry",
        "build_merkle_tree_from_manifest",
        "generate_manifest_inclusion_proof",
        "verify_manifest_inclusion_proof",
    ):
        import integrity_toolkit.merkle.adapters as adapters

        return getattr(adapters, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
