"""Unit tests for Merkle inclusion proof generation."""

import pytest
from integrity_toolkit.merkle.exceptions import InvalidProofError
from integrity_toolkit.merkle.proofs import generate_inclusion_proof
from integrity_toolkit.merkle.tree import build_merkle_tree


def test_generate_proof_single_leaf_tree():
    tree = build_merkle_tree([b"payload1"])
    proof = generate_inclusion_proof(tree, 0)

    assert proof.leaf_index == 0
    assert proof.leaf_count == 1
    assert proof.algorithm == "sha256"
    assert len(proof.steps) == 0
    assert proof.claimed_root == tree.root


def test_generate_proof_two_leaves():
    tree = build_merkle_tree([b"payload1", b"payload2"])

    # Proof for index 0 (has right sibling)
    p0 = generate_inclusion_proof(tree, 0)
    assert len(p0.steps) == 1
    assert p0.steps[0].operation == "RIGHT_SIBLING"
    assert p0.steps[0].sibling_digest == tree.levels[0][1]

    # Proof for index 1 (has left sibling)
    p1 = generate_inclusion_proof(tree, 1)
    assert len(p1.steps) == 1
    assert p1.steps[0].operation == "LEFT_SIBLING"
    assert p1.steps[0].sibling_digest == tree.levels[0][0]


def test_generate_proof_three_leaves_odd_promotion():
    # 3 leaves -> Level 0: [L0, L1, L2]. Level 1: [H(L0,L1), L2]. Level 2: [Root]
    tree = build_merkle_tree([b"A", b"B", b"C"])

    # Proof for C (index 2) -> Level 0: PROMOTE, Level 1: LEFT_SIBLING (H(A,B))
    p2 = generate_inclusion_proof(tree, 2)
    assert len(p2.steps) == 2
    assert p2.steps[0].operation == "PROMOTE"
    assert p2.steps[0].sibling_digest is None
    assert p2.steps[1].operation == "LEFT_SIBLING"
    assert p2.steps[1].sibling_digest == tree.levels[1][0]


def test_generate_proof_five_leaves_odd_promotion():
    # 5 leaves -> L0: [A, B, C, D, E], L1: [AB, CD, E], L2: [ABCD, E], L3: [Root]
    leaves = [b"A", b"B", b"C", b"D", b"E"]
    tree = build_merkle_tree(leaves)

    # Index 4 (E) should undergo two promotions and one final LEFT_SIBLING
    p4 = generate_inclusion_proof(tree, 4)
    assert len(p4.steps) == 3
    assert p4.steps[0].operation == "PROMOTE"
    assert p4.steps[1].operation == "PROMOTE"
    assert p4.steps[2].operation == "LEFT_SIBLING"
    assert p4.steps[2].sibling_digest == tree.levels[2][0]


def test_generate_proof_out_of_bounds_index():
    tree = build_merkle_tree([b"A", b"B"])

    with pytest.raises(InvalidProofError, match="out of bounds"):
        generate_inclusion_proof(tree, -1)

    with pytest.raises(InvalidProofError, match="out of bounds"):
        generate_inclusion_proof(tree, 2)


def test_generate_proof_invalid_tree_type():
    with pytest.raises(InvalidProofError, match="Expected MerkleTree object"):
        generate_inclusion_proof("not a tree", 0)  # type: ignore
