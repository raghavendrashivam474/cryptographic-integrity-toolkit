"""Engine for generating Merkle inclusion proofs from constructed trees."""

from typing import List

from integrity_toolkit.merkle.exceptions import InvalidProofError
from integrity_toolkit.merkle.models import MerkleProof, MerkleProofStep, MerkleTree, ProofOperation


def generate_inclusion_proof(tree: MerkleTree, leaf_index: int) -> MerkleProof:
    """Generate a compact Merkle inclusion proof for a target leaf index.

    This function reads the existing level structures from 	ree.levels in O(log N)
    time without re-hashing original leaf payloads or reconstructing the Merkle tree.

    Args:
        tree: Immutable constructed MerkleTree object.
        leaf_index: Zero-based index of the target leaf payload (0 <= leaf_index < leaf_count).

    Returns:
        Immutable MerkleProof instance.

    Raises:
        InvalidProofError: If tree is invalid, or leaf_index is out of bounds.
    """
    if not isinstance(tree, MerkleTree):
        raise InvalidProofError(f"Expected MerkleTree object, got {type(tree).__name__}")

    if not isinstance(leaf_index, int) or not (0 <= leaf_index < tree.leaf_count):
        raise InvalidProofError(
            f"Target leaf_index {leaf_index} out of bounds for tree with {tree.leaf_count} leaves."
        )

    steps: List[MerkleProofStep] = []
    current_index = leaf_index
    num_levels = len(tree.levels)

    # Traverse levels from Level 0 (leaves) up to Level N-2 (root is at levels[-1])
    for lvl_idx in range(num_levels - 1):
        level_nodes = tree.levels[lvl_idx]
        level_width = len(level_nodes)

        if level_width == 1:
            # Level width 1 means root reached; no more sibling steps
            break

        if current_index % 2 == 0:
            if current_index + 1 < level_width:
                # Right sibling exists
                sibling_digest = level_nodes[current_index + 1]
                steps.append(
                    MerkleProofStep(
                        operation=ProofOperation.RIGHT_SIBLING.value,
                        sibling_digest=sibling_digest,
                    )
                )
            else:
                # Odd node promotion
                steps.append(
                    MerkleProofStep(
                        operation=ProofOperation.PROMOTE.value,
                        sibling_digest=None,
                    )
                )
        else:
            # Left sibling exists
            sibling_digest = level_nodes[current_index - 1]
            steps.append(
                MerkleProofStep(
                    operation=ProofOperation.LEFT_SIBLING.value,
                    sibling_digest=sibling_digest,
                )
            )

        current_index //= 2

    return MerkleProof(
        algorithm=tree.algorithm,
        leaf_index=leaf_index,
        leaf_count=tree.leaf_count,
        steps=tuple(steps),
        claimed_root=tree.root,
    )
