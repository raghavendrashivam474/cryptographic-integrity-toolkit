"""Engine for validating and verifying Merkle inclusion proofs."""

from typing import Union

from integrity_toolkit.crypto import get_algorithm_spec
from integrity_toolkit.merkle.exceptions import InvalidNodeDigestError, InvalidProofError
from integrity_toolkit.merkle.hashing import hash_internal, hash_leaf
from integrity_toolkit.merkle.models import MerkleProof, ProofOperation


def verify_inclusion_proof(
    leaf_data: Union[bytes, bytearray],
    proof: MerkleProof,
    expected_root: str,
) -> bool:
    """Verify a Merkle inclusion proof against a trusted expected root.

    Security Rule: The expected_root must be independently supplied by the caller.
    The claimed_root inside the MerkleProof is strictly UNTRUSTED.

    Verification performs structural geometry validation to verify that proof step
    operations match the deterministic Merkle tree shape before hashing.

    Args:
        leaf_data: Raw byte payload of the leaf to verify.
        proof: Structurally validated MerkleProof object.
        expected_root: Lowercase hexadecimal trusted Merkle root digest.

    Returns:
        True if the proof is valid and reconstructs expected_root.
        False if the proof is valid but reconstructs a different root.

    Raises:
        InvalidProofError: If proof structure, operations, or leaf payload is malformed.
        InvalidNodeDigestError: If digests or expected_root are malformed hex strings.
    """
    if not isinstance(leaf_data, (bytes, bytearray)):
        raise InvalidProofError(
            f"leaf_data must be bytes or bytearray, got {type(leaf_data).__name__}"
        )

    if not isinstance(proof, MerkleProof):
        raise InvalidProofError(f"Expected MerkleProof object, got {type(proof).__name__}")

    if not isinstance(expected_root, str):
        raise InvalidProofError(
            f"expected_root must be a hex string, got {type(expected_root).__name__}"
        )

    spec = get_algorithm_spec(proof.algorithm)
    expected_hex_len = spec.digest_size * 2

    # Validate expected_root hex formatting
    if len(expected_root) != expected_hex_len:
        raise InvalidNodeDigestError(
            f"expected_root length ({len(expected_root)}) invalid for algorithm '{proof.algorithm}' "
            f"(expected {expected_hex_len} characters)"
        )

    try:
        bytes.fromhex(expected_root)
    except ValueError as err:
        raise InvalidNodeDigestError(
            f"expected_root is not a valid hexadecimal string: {err}"
        ) from err

    # 1. Compute initial leaf hash with domain separation 0x00
    current_digest = hash_leaf(leaf_data, algorithm=proof.algorithm)

    current_index = proof.leaf_index
    current_width = proof.leaf_count
    step_idx = 0
    num_steps = len(proof.steps)

    # 2. Reconstruct root level by level, validating structural tree geometry
    while current_width > 1:
        if step_idx >= num_steps:
            raise InvalidProofError(
                f"Proof missing step at level with width {current_width} (processed {step_idx}/{num_steps} steps)"
            )

        step = proof.steps[step_idx]

        # Determine expected operation based on deterministic tree geometry
        if current_index % 2 == 0:
            if current_index + 1 < current_width:
                expected_op = ProofOperation.RIGHT_SIBLING.value
            else:
                expected_op = ProofOperation.PROMOTE.value
        else:
            expected_op = ProofOperation.LEFT_SIBLING.value

        if step.operation != expected_op:
            raise InvalidProofError(
                f"Structural mismatch at step {step_idx}: proof declared '{step.operation}', "
                f"but tree geometry requires '{expected_op}' for index {current_index} of width {current_width}"
            )

        # Execute step operation
        if step.operation == ProofOperation.RIGHT_SIBLING.value:
            if not step.sibling_digest:
                raise InvalidProofError(f"Missing sibling_digest for RIGHT_SIBLING step at index {step_idx}")
            current_digest = hash_internal(
                current_digest, step.sibling_digest, algorithm=proof.algorithm
            )
        elif step.operation == ProofOperation.LEFT_SIBLING.value:
            if not step.sibling_digest:
                raise InvalidProofError(f"Missing sibling_digest for LEFT_SIBLING step at index {step_idx}")
            current_digest = hash_internal(
                step.sibling_digest, current_digest, algorithm=proof.algorithm
            )
        elif step.operation == ProofOperation.PROMOTE.value:
            # Unpaired odd node promoted unchanged
            pass

        current_index //= 2
        current_width = (current_width + 1) // 2
        step_idx += 1

    if step_idx != num_steps:
        raise InvalidProofError(
            f"Proof contains {num_steps} steps, but tree structure required only {step_idx} steps"
        )

    # 3. Secure comparison against trusted root
    return current_digest.lower() == expected_root.lower()
