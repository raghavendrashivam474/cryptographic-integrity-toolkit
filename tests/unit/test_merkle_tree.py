"""Unit tests for the generic Merkle tree construction engine."""

import pytest

from integrity_toolkit.crypto import UnsupportedAlgorithmError
from integrity_toolkit.merkle.exceptions import EmptyTreeError
from integrity_toolkit.merkle.hashing import hash_internal, hash_leaf
from integrity_toolkit.merkle.tree import build_merkle_tree


def test_build_merkle_tree_empty_leaves_raises():
    """Verify empty input raises EmptyTreeError."""
    with pytest.raises(EmptyTreeError, match="empty leaf collection"):
        build_merkle_tree([])


def test_build_merkle_tree_single_leaf():
    """Verify single-leaf tree has root equal to leaf hash and single level."""
    payload = b"single entry"
    tree = build_merkle_tree([payload], algorithm="sha256")

    expected_leaf_hash = hash_leaf(payload, algorithm="sha256")
    assert tree.leaf_count == 1
    assert tree.algorithm == "sha256"
    assert tree.root == expected_leaf_hash
    assert len(tree.levels) == 1
    assert tree.levels[0] == (expected_leaf_hash,)


def test_build_merkle_tree_two_leaves():
    """Verify two-leaf tree generates 1 internal parent node."""
    payload_a = b"leaf A"
    payload_b = b"leaf B"

    tree = build_merkle_tree([payload_a, payload_b], algorithm="sha256")

    hash_a = hash_leaf(payload_a, algorithm="sha256")
    hash_b = hash_leaf(payload_b, algorithm="sha256")
    expected_root = hash_internal(hash_a, hash_b, algorithm="sha256")

    assert tree.leaf_count == 2
    assert tree.root == expected_root
    assert len(tree.levels) == 2
    assert tree.levels[0] == (hash_a, hash_b)
    assert tree.levels[1] == (expected_root,)


def test_build_merkle_tree_three_leaves_odd_promotion():
    """Verify odd-node promotion policy for 3 leaves."""
    p0, p1, p2 = b"leaf 0", b"leaf 1", b"leaf 2"

    tree = build_merkle_tree([p0, p1, p2], algorithm="sha256")

    h0 = hash_leaf(p0, algorithm="sha256")
    h1 = hash_leaf(p1, algorithm="sha256")
    h2 = hash_leaf(p2, algorithm="sha256")

    # Level 1: pair (h0, h1) -> parent_01; promote h2 unchanged -> h2
    parent_01 = hash_internal(h0, h1, algorithm="sha256")
    # Level 2 (Root): pair (parent_01, h2) -> root
    expected_root = hash_internal(parent_01, h2, algorithm="sha256")

    assert tree.leaf_count == 3
    assert tree.root == expected_root
    assert len(tree.levels) == 3
    assert tree.levels[0] == (h0, h1, h2)
    assert tree.levels[1] == (parent_01, h2)  # h2 promoted
    assert tree.levels[2] == (expected_root,)


def test_build_merkle_tree_four_leaves_balanced():
    """Verify balanced 4-leaf tree construction."""
    payloads = [b"A", b"B", b"C", b"D"]
    tree = build_merkle_tree(payloads, algorithm="sha256")

    h = [hash_leaf(p, algorithm="sha256") for p in payloads]
    p01 = hash_internal(h[0], h[1], algorithm="sha256")
    p23 = hash_internal(h[2], h[3], algorithm="sha256")
    expected_root = hash_internal(p01, p23, algorithm="sha256")

    assert tree.leaf_count == 4
    assert tree.root == expected_root
    assert len(tree.levels) == 3
    assert tree.levels[0] == tuple(h)
    assert tree.levels[1] == (p01, p23)
    assert tree.levels[2] == (expected_root,)


def test_build_merkle_tree_five_leaves():
    """Verify 5-leaf tree structure and determinism."""
    payloads = [b"1", b"2", b"3", b"4", b"5"]
    tree = build_merkle_tree(payloads, algorithm="sha256")

    assert tree.leaf_count == 5
    assert len(tree.levels) == 4  # L0: 5, L1: 3, L2: 2, L3: 1 (root)
    assert len(tree.levels[0]) == 5
    assert len(tree.levels[1]) == 3  # (H(1,2), H(3,4), 5)
    assert len(tree.levels[2]) == 2  # (H(H(1,2), H(3,4)), 5)
    assert len(tree.levels[3]) == 1  # Root


def test_build_merkle_tree_order_sensitivity():
    """Verify changing payload order produces a different root."""
    list1 = [b"A", b"B", b"C"]
    list2 = [b"B", b"A", b"C"]

    tree1 = build_merkle_tree(list1, algorithm="sha256")
    tree2 = build_merkle_tree(list2, algorithm="sha256")

    assert tree1.root != tree2.root


def test_build_merkle_tree_sha512_and_blake2b():
    """Verify Merkle tree construction with SHA-512 and BLAKE2b."""
    payloads = [b"record1", b"record2", b"record3"]

    tree_sha512 = build_merkle_tree(payloads, algorithm="sha512")
    assert tree_sha512.algorithm == "sha512"
    assert len(tree_sha512.root) == 128

    tree_blake = build_merkle_tree(payloads, algorithm="blake2b")
    assert tree_blake.algorithm == "blake2b"
    assert len(tree_blake.root) == 128


def test_build_merkle_tree_unsupported_algorithm():
    """Verify unsupported algorithm raises UnsupportedAlgorithmError."""
    with pytest.raises(UnsupportedAlgorithmError):
        build_merkle_tree([b"test"], algorithm="md5")
