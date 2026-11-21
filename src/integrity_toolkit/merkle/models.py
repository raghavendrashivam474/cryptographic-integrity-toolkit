"""Data models for the integrity_toolkit.merkle subsystem."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ProofOperation(str, Enum):
    """Supported proof step operations."""

    LEFT_SIBLING = "LEFT_SIBLING"
    RIGHT_SIBLING = "RIGHT_SIBLING"
    PROMOTE = "PROMOTE"


@dataclass(frozen=True)
class MerkleProofStep:
    """Immutable representation of a single level step in a Merkle inclusion proof.

    Attributes:
        operation: Direction or promotion operation ('LEFT_SIBLING', 'RIGHT_SIBLING', or 'PROMOTE').
        sibling_digest: Hexadecimal hash string of the sibling node (None if operation is PROMOTE).
    """

    operation: str
    sibling_digest: Optional[str] = None

    def __post_init__(self) -> None:
        valid_ops = {op.value for op in ProofOperation}
        if self.operation not in valid_ops:
            from integrity_toolkit.merkle.exceptions import InvalidProofError

            raise InvalidProofError(
                f"Invalid proof step operation '{self.operation}'. Expected one of {sorted(valid_ops)}"
            )

        if self.operation in (ProofOperation.LEFT_SIBLING, ProofOperation.RIGHT_SIBLING):
            if not self.sibling_digest or not isinstance(self.sibling_digest, str):
                from integrity_toolkit.merkle.exceptions import InvalidProofError

                raise InvalidProofError(
                    f"Sibling digest string is required for operation '{self.operation}'"
                )
        elif self.operation == ProofOperation.PROMOTE:
            if self.sibling_digest is not None:
                from integrity_toolkit.merkle.exceptions import InvalidProofError

                raise InvalidProofError(
                    "Sibling digest must be None for 'PROMOTE' step operation"
                )


@dataclass(frozen=True)
class MerkleTree:
    """Immutable representation of a constructed Merkle tree.

    Attributes:
        algorithm: Canonical hash algorithm name used (e.g. 'sha256').
        leaf_count: Total number of leaf nodes in the tree (N >= 1).
        root: Hexadecimal Merkle root digest string.
        levels: Complete level-by-level node structure stored as a tuple of tuples.
                levels[0] contains Level 0 leaf hashes.
                levels[-1] contains the single-element tuple (root,).
    """

    algorithm: str
    leaf_count: int
    root: str
    levels: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class MerkleProof:
    """Immutable representation of a Merkle inclusion proof.

    Attributes:
        format_version: Version integer (default 1).
        algorithm: Canonical hash algorithm identifier.
        leaf_index: Zero-based index of target leaf.
        leaf_count: Total leaf count of original Merkle tree.
        steps: Level-by-level sibling and promotion steps from leaf to root.
        claimed_root: Optional claimed Merkle root (strictly UNTRUSTED for verification).
    """

    algorithm: str
    leaf_index: int
    leaf_count: int
    steps: Tuple[MerkleProofStep, ...]
    format_version: int = 1
    claimed_root: Optional[str] = None

    def __post_init__(self) -> None:
        from integrity_toolkit.crypto import is_algorithm_supported
        from integrity_toolkit.merkle.exceptions import InvalidProofError

        if self.format_version != 1:
            raise InvalidProofError(f"Unsupported proof format version: {self.format_version}")

        if not is_algorithm_supported(self.algorithm):
            raise InvalidProofError(f"Unsupported algorithm in proof: '{self.algorithm}'")

        if not isinstance(self.leaf_count, int) or self.leaf_count < 1:
            raise InvalidProofError(f"Leaf count must be an integer >= 1, got {self.leaf_count}")

        if not isinstance(self.leaf_index, int) or not (0 <= self.leaf_index < self.leaf_count):
            raise InvalidProofError(
                f"Leaf index {self.leaf_index} out of bounds for leaf count {self.leaf_count}"
            )

        if not isinstance(self.steps, tuple):
            object.__setattr__(self, "steps", tuple(self.steps))
