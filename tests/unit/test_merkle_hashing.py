"""Unit tests for domain-separated Merkle hashing primitives."""

import pytest

from integrity_toolkit.crypto import (
    InvalidInputError,
    UnsupportedAlgorithmError,
    hash_bytes,
)
from integrity_toolkit.merkle.exceptions import InvalidNodeDigestError
from integrity_toolkit.merkle.hashing import (
    INTERNAL_DOMAIN_PREFIX,
    LEAF_DOMAIN_PREFIX,
    hash_internal,
    hash_leaf,
)


def test_hash_leaf_sha256_domain_separation():
    """Verify that hash_leaf prepends 0x00 byte before hashing."""
    data = b"hello world"
    expected = hash_bytes(LEAF_DOMAIN_PREFIX + data, algorithm="sha256")
    result = hash_leaf(data, algorithm="sha256")
    assert result == expected


def test_hash_leaf_sha512_and_blake2b():
    """Verify hash_leaf works across all supported algorithm primitives."""
    data = b"test payload"

    sha512_result = hash_leaf(data, algorithm="sha512")
    assert len(sha512_result) == 128
    assert sha512_result == hash_bytes(LEAF_DOMAIN_PREFIX + data, algorithm="sha512")

    blake_result = hash_leaf(data, algorithm="blake2b")
    assert len(blake_result) == 128
    assert blake_result == hash_bytes(LEAF_DOMAIN_PREFIX + data, algorithm="blake2b")


def test_hash_leaf_accepts_bytearray():
    """Verify hash_leaf handles bytearray inputs identically to bytes."""
    data_bytes = b"sample data"
    data_arr = bytearray(data_bytes)
    assert hash_leaf(data_bytes) == hash_leaf(data_arr)


def test_hash_leaf_invalid_input_type():
    """Verify hash_leaf rejects non-bytes inputs with InvalidInputError."""
    with pytest.raises(InvalidInputError):
        hash_leaf("string payload")  # type: ignore

    with pytest.raises(InvalidInputError):
        hash_leaf(12345)  # type: ignore


def test_hash_leaf_unsupported_algorithm():
    """Verify hash_leaf raises UnsupportedAlgorithmError for unknown algorithms."""
    with pytest.raises(UnsupportedAlgorithmError):
        hash_leaf(b"data", algorithm="md5")


def test_hash_internal_sha256():
    """Verify hash_internal combines left and right raw digest bytes with 0x01 prefix."""
    data_left = b"leaf 1"
    data_right = b"leaf 2"

    leaf_left = hash_leaf(data_left, algorithm="sha256")
    leaf_right = hash_leaf(data_right, algorithm="sha256")

    raw_left = bytes.fromhex(leaf_left)
    raw_right = bytes.fromhex(leaf_right)
    expected = hash_bytes(INTERNAL_DOMAIN_PREFIX + raw_left + raw_right, algorithm="sha256")

    result = hash_internal(leaf_left, leaf_right, algorithm="sha256")
    assert result == expected
    assert len(result) == 64


def test_domain_separation_prevents_leaf_internal_collision():
    """Verify that a leaf payload containing internal raw bytes produces a different hash."""
    left = "00" * 32
    right = "11" * 32

    # Internal node hash: H(0x01 || left_raw || right_raw)
    internal_hash = hash_internal(left, right, algorithm="sha256")

    # Construct leaf payload matching internal preimage: (left_raw || right_raw)
    leaf_payload = bytes.fromhex(left) + bytes.fromhex(right)
    leaf_hash = hash_leaf(leaf_payload, algorithm="sha256")

    # Domain separation (0x00 vs 0x01) guarantees hashes are distinct
    assert internal_hash != leaf_hash


def test_hash_internal_invalid_digest_length():
    """Verify hash_internal rejects child digests of incorrect length."""
    valid_sha256 = "00" * 32
    short_digest = "00" * 31

    with pytest.raises(InvalidNodeDigestError, match="Left child digest length"):
        hash_internal(short_digest, valid_sha256, algorithm="sha256")

    with pytest.raises(InvalidNodeDigestError, match="Right child digest length"):
        hash_internal(valid_sha256, short_digest, algorithm="sha256")


def test_hash_internal_invalid_hex_characters():
    """Verify hash_internal rejects non-hexadecimal digest strings."""
    valid = "00" * 32
    invalid_hex = "zz" * 32

    with pytest.raises(InvalidNodeDigestError, match="not valid hexadecimal"):
        hash_internal(invalid_hex, valid, algorithm="sha256")


def test_hash_internal_invalid_type():
    """Verify hash_internal rejects non-string digest arguments."""
    valid = "00" * 32
    with pytest.raises(InvalidNodeDigestError, match="must be a string"):
        hash_internal(b"bytes", valid, algorithm="sha256")  # type: ignore
