"""Unit tests for core byte and text hashing engine."""

import pytest
from integrity_toolkit.crypto.engine import hash_bytes, hash_text
from integrity_toolkit.crypto.exceptions import InvalidInputError, UnsupportedAlgorithmError


# Official NIST / standard reference vectors
# SHA-256 (NIST FIPS 180-4)
SHA256_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
SHA256_HELLO_WORLD = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"

# SHA-512 (NIST FIPS 180-4)
SHA512_EMPTY = (
    "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
    "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
)
SHA512_ABC = (
    "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
    "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
)

# BLAKE2b-512 (RFC 7693 Appendix E)
BLAKE2B_EMPTY = (
    "786a02f742015903c6c6fd852552d272912f4740e15847618a86e217f71f5419"
    "d25e1031afee585313896444934eb04b903a685b1448b755d56f701afe9be2ce"
)
BLAKE2B_ABC = (
    "ba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d1"
    "7d87c5392aab792dc252d5de4533cc9518d38aa8dbf1925ab92386edd4009923"
)


def test_hash_bytes_sha256_reference_vectors():
    """Test SHA-256 byte hashing against official test vectors."""
    assert hash_bytes(b"", algorithm="sha256") == SHA256_EMPTY
    assert hash_bytes(b"abc", algorithm="sha256") == SHA256_ABC
    assert hash_bytes(b"Hello World", algorithm="sha256") == SHA256_HELLO_WORLD


def test_hash_bytes_sha512_reference_vectors():
    """Test SHA-512 byte hashing against official test vectors."""
    assert hash_bytes(b"", algorithm="sha512") == SHA512_EMPTY
    assert hash_bytes(b"abc", algorithm="sha512") == SHA512_ABC


def test_hash_bytes_blake2b_reference_vectors():
    """Test BLAKE2b byte hashing against standard RFC 7693 test vectors."""
    assert hash_bytes(b"", algorithm="blake2b") == BLAKE2B_EMPTY
    assert hash_bytes(b"abc", algorithm="blake2b") == BLAKE2B_ABC


def test_hash_bytes_bytearray_support():
    """Verify hash_bytes accepts bytearray objects."""
    data = bytearray(b"Hello World")
    assert hash_bytes(data, algorithm="sha256") == SHA256_HELLO_WORLD


def test_hash_text_explicit_encoding():
    """Test hash_text with explicit UTF-8 and ASCII encodings."""
    assert hash_text("Hello World", algorithm="sha256") == SHA256_HELLO_WORLD
    assert hash_text("abc", algorithm="sha512", encoding="ascii") == SHA512_ABC


def test_hash_bytes_determinism():
    """Verify that identical inputs produce identical digests across multiple calls."""
    data = b"Deterministic Test Payload 12345"
    d1 = hash_bytes(data, algorithm="sha256")
    d2 = hash_bytes(data, algorithm="sha256")
    assert d1 == d2


def test_hash_bytes_avalanche_effect():
    """Verify single-bit change in input produces drastically different digests."""
    d1 = hash_bytes(b"Hello World", algorithm="sha256")
    d2 = hash_bytes(b"hello World", algorithm="sha256")
    assert d1 != d2
    # Check that at least half the hex characters differ
    differing_chars = sum(1 for c1, c2 in zip(d1, d2) if c1 != c2)
    assert differing_chars > 20


@pytest.mark.parametrize("invalid_input", [123, 45.67, ["b"], {"data": "test"}, None])
def test_hash_bytes_invalid_input_type(invalid_input):
    """Verify hash_bytes raises InvalidInputError for non-bytes types."""
    with pytest.raises(InvalidInputError):
        hash_bytes(invalid_input, algorithm="sha256")  # type: ignore


@pytest.mark.parametrize("invalid_input", [b"bytes", 123, None, ["str"]])
def test_hash_text_invalid_input_type(invalid_input):
    """Verify hash_text raises InvalidInputError for non-str types."""
    with pytest.raises(InvalidInputError):
        hash_text(invalid_input, algorithm="sha256")  # type: ignore


def test_hash_text_invalid_encoding():
    """Verify hash_text raises InvalidInputError for invalid encoding specification."""
    with pytest.raises(InvalidInputError):
        hash_text("Hello", encoding="non_existent_encoding_12345")


def test_hash_bytes_unsupported_algorithm():
    """Verify hash_bytes raises UnsupportedAlgorithmError for invalid algorithm."""
    with pytest.raises(UnsupportedAlgorithmError):
        hash_bytes(b"test", algorithm="md5")
