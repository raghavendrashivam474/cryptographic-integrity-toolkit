"""Generic Merkle tree construction engine."""

from typing import Iterable, List, Sequence, Union

from integrity_toolkit.crypto import get_algorithm_spec
from integrity_toolkit.merkle.exceptions import EmptyTreeError
from integrity_toolkit.merkle.hashing import hash_internal, hash_leaf
from integrity_toolkit.merkle.models import MerkleTree


def build_merkle_tree(
    leaves: Iterable[Union[bytes, bytearray]],
    algorithm: str = "sha256",
) -> MerkleTree:
    """Build a deterministic Merkle Tree from an ordered collection of byte payloads.

    Construction follows the approved specification (S03-ADR-001):
    1. Leaf hashing applies domain separation prefix `0x00` via `hash_leaf`.
    2. Internal node hashing applies prefix `0x01` via `hash_internal`.
    3. Odd-node levels promote the final unpaired node unchanged to the next level.
    4. Input leaf order is strictly preserved.
    5. Single-leaf trees have root equal to their single leaf hash.
    6. Empty leaf collections raise `EmptyTreeError`.

    Args:
        leaves: Ordered sequence or iterable of byte payloads.
        algorithm: Hash algorithm identifier (default: "sha256").

    Returns:
        Immutable `MerkleTree` object.

    Raises:
        EmptyTreeError: If `leaves` iterable is empty.
        InvalidInputError: If any item in `leaves` is not bytes/bytearray.
        UnsupportedAlgorithmError: If `algorithm` is not supported.
    """
    spec = get_algorithm_spec(algorithm)
    canonical_algo = spec.canonical_name

    leaf_list: List[Union[bytes, bytearray]] = list(leaves)
    if not leaf_list:
        raise EmptyTreeError(
            "Cannot build a Merkle tree from an empty leaf collection."
        )

    # Level 0: Hash all leaves with domain separation (0x00)
    level_0: List[str] = [hash_leaf(payload, algorithm=canonical_algo) for payload in leaf_list]

    levels: List[tuple[str, ...]] = [tuple(level_0)]
    current_level = level_0

    # Build intermediate levels until reaching root (single element level)
    while len(current_level) > 1:
        next_level: List[str] = []
        i = 0
        n = len(current_level)

        while i < n:
            if i + 1 < n:
                # Pair adjacent nodes
                parent = hash_internal(
                    current_level[i], current_level[i + 1], algorithm=canonical_algo
                )
                next_level.append(parent)
                i += 2
            else:
                # Odd node promotion policy (ADR-001): promote unpaired node unchanged
                next_level.append(current_level[i])
                i += 1

        levels.append(tuple(next_level))
        current_level = next_level

    root_digest = current_level[0]

    return MerkleTree(
        algorithm=canonical_algo,
        leaf_count=len(leaf_list),
        root=root_digest,
        levels=tuple(levels),
    )
