"""Unit tests for Merkle proof models and validation rules."""

import pytest
from integrity_toolkit.merkle.exceptions import InvalidProofError
from integrity_toolkit.merkle.models import (
    MerkleProof,
    MerkleProofStep,
    ProofOperation,
)


def test_merkle_proof_step_valid_siblings():
    step_left = MerkleProofStep(
        operation="LEFT_SIBLING", sibling_digest="a" * 64
    )
    assert step_left.operation == "LEFT_SIBLING"
    assert step_left.sibling_digest == "a" * 64

    step_right = MerkleProofStep(
        operation="RIGHT_SIBLING", sibling_digest="b" * 64
    )
    assert step_right.operation == "RIGHT_SIBLING"
    assert step_right.sibling_digest == "b" * 64


def test_merkle_proof_step_valid_promote():
    step_promote = MerkleProofStep(operation="PROMOTE")
    assert step_promote.operation == "PROMOTE"
    assert step_promote.sibling_digest is None


def test_merkle_proof_step_invalid_operation():
    with pytest.raises(InvalidProofError, match="Invalid proof step operation"):
        MerkleProofStep(operation="MIDDLE_SIBLING", sibling_digest="a" * 64)


def test_merkle_proof_step_missing_sibling_digest():
    with pytest.raises(InvalidProofError, match="Sibling digest string is required"):
        MerkleProofStep(operation="LEFT_SIBLING", sibling_digest=None)


def test_merkle_proof_step_promote_with_sibling_digest_raises():
    with pytest.raises(InvalidProofError, match="Sibling digest must be None for 'PROMOTE'"):
        MerkleProofStep(operation="PROMOTE", sibling_digest="a" * 64)


def test_merkle_proof_valid_construction():
    step = MerkleProofStep(operation="RIGHT_SIBLING", sibling_digest="a" * 64)
    proof = MerkleProof(
        algorithm="sha256",
        leaf_index=0,
        leaf_count=2,
        steps=(step,),
        claimed_root="b" * 64,
    )
    assert proof.algorithm == "sha256"
    assert proof.leaf_index == 0
    assert proof.leaf_count == 2
    assert len(proof.steps) == 1
    assert proof.claimed_root == "b" * 64


def test_merkle_proof_out_of_bounds_leaf_index():
    step = MerkleProofStep(operation="RIGHT_SIBLING", sibling_digest="a" * 64)

    # Negative index
    with pytest.raises(InvalidProofError, match="out of bounds"):
        MerkleProof(algorithm="sha256", leaf_index=-1, leaf_count=2, steps=(step,))

    # Index equal to leaf count
    with pytest.raises(InvalidProofError, match="out of bounds"):
        MerkleProof(algorithm="sha256", leaf_index=2, leaf_count=2, steps=(step,))


def test_merkle_proof_invalid_leaf_count():
    step = MerkleProofStep(operation="RIGHT_SIBLING", sibling_digest="a" * 64)
    with pytest.raises(InvalidProofError, match="Leaf count must be an integer >= 1"):
        MerkleProof(algorithm="sha256", leaf_index=0, leaf_count=0, steps=(step,))


def test_merkle_proof_unsupported_algorithm():
    step = MerkleProofStep(operation="RIGHT_SIBLING", sibling_digest="a" * 64)
    with pytest.raises(InvalidProofError, match="Unsupported algorithm in proof"):
        MerkleProof(algorithm="invalid_hash", leaf_index=0, leaf_count=2, steps=(step,))


def test_merkle_proof_unsupported_version():
    step = MerkleProofStep(operation="RIGHT_SIBLING", sibling_digest="a" * 64)
    with pytest.raises(InvalidProofError, match="Unsupported proof format version"):
        MerkleProof(
            algorithm="sha256",
            leaf_index=0,
            leaf_count=2,
            steps=(step,),
            format_version=99,
        )
