"""Serialization and deserialization engine for versioned JSON Merkle inclusion proofs."""

import json
from typing import Any, Dict, Optional

from integrity_toolkit.crypto import get_algorithm_spec, is_algorithm_supported
from integrity_toolkit.merkle.exceptions import InvalidProofError
from integrity_toolkit.merkle.models import MerkleProof, MerkleProofStep, ProofOperation

FORMAT_NAME = "cryptographic-integrity-merkle-proof"
CURRENT_VERSION = 1


def serialize_proof_to_dict(proof: MerkleProof) -> Dict[str, Any]:
    """Serialize a MerkleProof instance into a standard Python dictionary.

    Args:
        proof: Validated MerkleProof instance.

    Returns:
        Dictionary representation adhering to the version 1 proof format schema.

    Raises:
        InvalidProofError: If proof object is invalid.
    """
    if not isinstance(proof, MerkleProof):
        raise InvalidProofError(f"Expected MerkleProof instance, got {type(proof).__name__}")

    steps_data = [
        {
            "operation": step.operation,
            "sibling_digest": step.sibling_digest,
        }
        for step in proof.steps
    ]

    return {
        "format": FORMAT_NAME,
        "version": proof.format_version,
        "algorithm": proof.algorithm,
        "leaf_index": proof.leaf_index,
        "leaf_count": proof.leaf_count,
        "claimed_root": proof.claimed_root,
        "steps": steps_data,
    }


def serialize_proof_to_json(proof: MerkleProof, indent: Optional[int] = 2) -> str:
    """Serialize a MerkleProof instance into a JSON string.

    Args:
        proof: Validated MerkleProof instance.
        indent: Indentation level for formatted JSON output.

    Returns:
        JSON string representation.
    """
    data = serialize_proof_to_dict(proof)
    return json.dumps(data, indent=indent)


def deserialize_proof_from_dict(data: Dict[str, Any]) -> MerkleProof:
    """Deserialize a dictionary payload into a validated MerkleProof object.

    Args:
        data: Dictionary payload conforming to version 1 schema.

    Returns:
        Validated MerkleProof dataclass instance.

    Raises:
        InvalidProofError: If format, version, fields, or step structures are invalid.
    """
    if not isinstance(data, dict):
        raise InvalidProofError(f"Expected dictionary payload, got {type(data).__name__}")

    fmt = data.get("format")
    if fmt != FORMAT_NAME:
        raise InvalidProofError(f"Invalid proof format identifier: '{fmt}' (expected '{FORMAT_NAME}')")

    version = data.get("version")
    if version != CURRENT_VERSION:
        raise InvalidProofError(f"Unsupported proof format version: {version} (expected {CURRENT_VERSION})")

    algorithm = data.get("algorithm")
    if not isinstance(algorithm, str) or not is_algorithm_supported(algorithm):
        raise InvalidProofError(f"Unsupported or missing hash algorithm in proof: '{algorithm}'")

    leaf_count = data.get("leaf_count")
    if not isinstance(leaf_count, int) or leaf_count < 1:
        raise InvalidProofError(f"Invalid leaf_count in proof payload: {leaf_count}")

    leaf_index = data.get("leaf_index")
    if not isinstance(leaf_index, int) or not (0 <= leaf_index < leaf_count):
        raise InvalidProofError(
            f"Invalid leaf_index {leaf_index} for leaf_count {leaf_count} in proof payload"
        )

    claimed_root = data.get("claimed_root")
    if claimed_root is not None and not isinstance(claimed_root, str):
        raise InvalidProofError(f"Invalid claimed_root type in proof payload: {type(claimed_root).__name__}")

    raw_steps = data.get("steps")
    if not isinstance(raw_steps, list):
        raise InvalidProofError(f"Field 'steps' must be a list, got {type(raw_steps).__name__}")

    spec = get_algorithm_spec(algorithm)
    expected_hex_len = spec.digest_size * 2

    steps = []
    for idx, raw_step in enumerate(raw_steps):
        if not isinstance(raw_step, dict):
            raise InvalidProofError(f"Step at index {idx} must be a dict, got {type(raw_step).__name__}")

        op = raw_step.get("operation")
        sibling_digest = raw_step.get("sibling_digest")

        valid_ops = {o.value for o in ProofOperation}
        if op not in valid_ops:
            raise InvalidProofError(f"Step at index {idx} contains invalid operation '{op}'")

        if op in (ProofOperation.LEFT_SIBLING.value, ProofOperation.RIGHT_SIBLING.value):
            if not isinstance(sibling_digest, str) or len(sibling_digest) != expected_hex_len:
                raise InvalidProofError(
                    f"Step at index {idx} ({op}) requires a valid hex sibling digest string of length {expected_hex_len}"
                )
            try:
                bytes.fromhex(sibling_digest)
            except ValueError as err:
                raise InvalidProofError(
                    f"Step at index {idx} sibling digest is not valid hex: {err}"
                ) from err
        elif op == ProofOperation.PROMOTE.value:
            if sibling_digest is not None:
                raise InvalidProofError(f"Step at index {idx} (PROMOTE) must have sibling_digest set to null/None")

        steps.append(MerkleProofStep(operation=op, sibling_digest=sibling_digest))

    return MerkleProof(
        format_version=version,
        algorithm=algorithm,
        leaf_index=leaf_index,
        leaf_count=leaf_count,
        steps=tuple(steps),
        claimed_root=claimed_root,
    )


def deserialize_proof_from_json(json_str: str) -> MerkleProof:
    """Deserialize a JSON string into a validated MerkleProof object.

    Args:
        json_str: JSON formatted string payload.

    Returns:
        Validated MerkleProof dataclass instance.

    Raises:
        InvalidProofError: If JSON syntax is invalid or schema validation fails.
    """
    if not isinstance(json_str, str):
        raise InvalidProofError(f"Expected JSON string payload, got {type(json_str).__name__}")

    try:
        data = json.loads(json_str)
    except Exception as err:
        raise InvalidProofError(f"Failed to parse proof JSON string: {err}") from err

    return deserialize_proof_from_dict(data)
