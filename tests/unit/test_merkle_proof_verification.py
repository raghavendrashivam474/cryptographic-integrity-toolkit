"""Unit tests for Merkle inclusion proof verification."""

import pytest
from integrity_toolkit.merkle.exceptions import InvalidNodeDigestError, InvalidProofError
from integrity_toolkit.merkle.models import MerkleProof, MerkleProofStep
from integrity_toolkit.merkle.proofs import generate_inclusion_proof
from integrity_toolkit.merkle.tree import build_merkle_tree
from integrity_toolkit.merkle.verification import verify_inclusion_proof


def test_verify_valid_proof_single_leaf():
    payload = b"single leaf payload"
    tree = build_merkle_tree([payload])
    proof = generate_inclusion_proof(tree, 0)

    assert verify_inclusion_proof(payload, proof, tree.root) is True


def test_verify_valid_proof_multi_leaves():
    leaves = [b"A", b"B", b"C", b"D", b"E"]
    tree = build_merkle_tree(leaves, algorithm="sha256")

    for i, leaf in enumerate(leaves):
        proof = generate_inclusion_proof(tree, i)
        assert verify_inclusion_proof(leaf, proof, tree.root) is True


def test_verify_modified_leaf_payload_returns_false():
    leaves = [b"A", b"B", b"C"]
    tree = build_merkle_tree(leaves)
    proof = generate_inclusion_proof(tree, 1)  # leaf B

    # Wrong payload
    assert verify_inclusion_proof(b"TAMPERED_B", proof, tree.root) is False


def test_verify_wrong_expected_root_returns_false():
    leaves = [b"A", b"B"]
    tree = build_merkle_tree(leaves)
    proof = generate_inclusion_proof(tree, 0)

    wrong_root = "f" * 64
    assert verify_inclusion_proof(leaves[0], proof, wrong_root) is False


def test_verify_multi_algorithm_support():
    for algo in ("sha256", "sha512", "blake2b"):
        leaves = [b"one", b"two", b"three"]
        tree = build_merkle_tree(leaves, algorithm=algo)
        proof = generate_inclusion_proof(tree, 1)
        assert verify_inclusion_proof(leaves[1], proof, tree.root) is True


def test_verify_structural_mismatch_wrong_operation_raises():
    leaves = [b"A", b"B"]
    tree = build_merkle_tree(leaves)
    proof = generate_inclusion_proof(tree, 0)  # expects RIGHT_SIBLING

    # Tamper step operation to LEFT_SIBLING
    tampered_step = MerkleProofStep(
        operation="LEFT_SIBLING", sibling_digest=proof.steps[0].sibling_digest
    )
    tampered_proof = MerkleProof(
        algorithm=proof.algorithm,
        leaf_index=proof.leaf_index,
        leaf_count=proof.leaf_count,
        steps=(tampered_step,),
        claimed_root=proof.claimed_root,
    )

    with pytest.raises(InvalidProofError, match="Structural mismatch"):
        verify_inclusion_proof(leaves[0], tampered_proof, tree.root)


def test_verify_extra_step_raises():
    leaves = [b"A", b"B"]
    tree = build_merkle_tree(leaves)
    proof = generate_inclusion_proof(tree, 0)

    extra_step = MerkleProofStep(operation="RIGHT_SIBLING", sibling_digest="a" * 64)
    tampered_proof = MerkleProof(
        algorithm=proof.algorithm,
        leaf_index=proof.leaf_index,
        leaf_count=proof.leaf_count,
        steps=proof.steps + (extra_step,),
    )

    with pytest.raises(InvalidProofError, match="Proof contains 2 steps, but tree structure required only 1"):
        verify_inclusion_proof(leaves[0], tampered_proof, tree.root)


def test_verify_invalid_expected_root_hex_raises():
    leaves = [b"A", b"B"]
    tree = build_merkle_tree(leaves)
    proof = generate_inclusion_proof(tree, 0)

    with pytest.raises(InvalidNodeDigestError, match="length .* invalid"):
        verify_inclusion_proof(leaves[0], proof, "short_hex")
