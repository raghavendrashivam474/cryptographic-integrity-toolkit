"""Unit tests for Merkle proof JSON serialization and deserialization."""

import pytest
from integrity_toolkit.merkle.exceptions import InvalidProofError
from integrity_toolkit.merkle.proof_serialization import (
    deserialize_proof_from_dict,
    deserialize_proof_from_json,
    serialize_proof_to_dict,
    serialize_proof_to_json,
)
from integrity_toolkit.merkle.proofs import generate_inclusion_proof
from integrity_toolkit.merkle.tree import build_merkle_tree
from integrity_toolkit.merkle.verification import verify_inclusion_proof


def test_proof_serialization_round_trip():
    leaves = [b"alpha", b"beta", b"gamma"]
    tree = build_merkle_tree(leaves)
    original_proof = generate_inclusion_proof(tree, 2)

    # Serialize to JSON
    json_str = serialize_proof_to_json(original_proof)
    assert "cryptographic-integrity-merkle-proof" in json_str

    # Deserialize from JSON
    deserialized_proof = deserialize_proof_from_json(json_str)
    assert deserialized_proof == original_proof

    # Verify deserialized proof
    assert verify_inclusion_proof(leaves[2], deserialized_proof, tree.root) is True


def test_deserialize_invalid_format_name_raises():
    valid_dict = serialize_proof_to_dict(
        generate_inclusion_proof(build_merkle_tree([b"a", b"b"]), 0)
    )
    valid_dict["format"] = "invalid_format_name"

    with pytest.raises(InvalidProofError, match="Invalid proof format identifier"):
        deserialize_proof_from_dict(valid_dict)


def test_deserialize_invalid_version_raises():
    valid_dict = serialize_proof_to_dict(
        generate_inclusion_proof(build_merkle_tree([b"a", b"b"]), 0)
    )
    valid_dict["version"] = 99

    with pytest.raises(InvalidProofError, match="Unsupported proof format version"):
        deserialize_proof_from_dict(valid_dict)


def test_deserialize_malformed_json_raises():
    with pytest.raises(InvalidProofError, match="Failed to parse proof JSON string"):
        deserialize_proof_from_json("{ malformed json }")


def test_deserialize_step_digest_length_mismatch_raises():
    valid_dict = serialize_proof_to_dict(
        generate_inclusion_proof(build_merkle_tree([b"a", b"b"]), 0)
    )
    valid_dict["steps"][0]["sibling_digest"] = "short_hex"

    with pytest.raises(InvalidProofError, match="requires a valid hex sibling digest string"):
        deserialize_proof_from_dict(valid_dict)
