"""Unit tests for algorithm registry, normalization, and factory functionality."""

import pytest
from integrity_toolkit.crypto.algorithms import (
    create_hasher,
    get_algorithm_spec,
    get_supported_algorithms,
    is_algorithm_supported,
    normalize_algorithm_name,
)
from integrity_toolkit.crypto.exceptions import UnsupportedAlgorithmError


def test_supported_algorithms_list():
    """Verify registry returns expected canonical supported algorithm names."""
    algorithms = get_supported_algorithms()
    assert "sha256" in algorithms
    assert "sha512" in algorithms
    assert "blake2b" in algorithms
    assert len(algorithms) == 3


@pytest.mark.parametrize(
    "raw_input, expected",
    [
        ("sha256", "sha256"),
        ("SHA256", "sha256"),
        ("SHA-256", "sha256"),
        ("SHA_256", "sha256"),
        ("  sha512  ", "sha512"),
        ("BLAKE2b", "blake2b"),
        ("blake-2b", "blake2b"),
    ],
)
def test_normalize_algorithm_name_valid(raw_input, expected):
    """Verify name normalization handles capitalization, spaces, and hyphens correctly."""
    assert normalize_algorithm_name(raw_input) == expected


def test_normalize_algorithm_name_invalid_type():
    """Verify non-string algorithm names raise UnsupportedAlgorithmError."""
    with pytest.raises(UnsupportedAlgorithmError):
        normalize_algorithm_name(123)  # type: ignore


def test_is_algorithm_supported():
    """Verify algorithm support checking."""
    assert is_algorithm_supported("sha256") is True
    assert is_algorithm_supported("SHA-512") is True
    assert is_algorithm_supported("blake2b") is True
    assert is_algorithm_supported("md5") is False
    assert is_algorithm_supported("sha3_256") is False


def test_get_algorithm_spec_valid():
    """Verify metadata resolution for valid algorithms."""
    spec_sha256 = get_algorithm_spec("sha256")
    assert spec_sha256.canonical_name == "sha256"
    assert spec_sha256.digest_size == 32

    spec_sha512 = get_algorithm_spec("sha512")
    assert spec_sha512.canonical_name == "sha512"
    assert spec_sha512.digest_size == 64

    spec_blake2b = get_algorithm_spec("blake2b")
    assert spec_blake2b.canonical_name == "blake2b"
    assert spec_blake2b.digest_size == 64


def test_get_algorithm_spec_unsupported():
    """Verify requesting an unsupported algorithm spec raises UnsupportedAlgorithmError."""
    with pytest.raises(UnsupportedAlgorithmError) as exc_info:
        get_algorithm_spec("unsupported_algo")
    assert "Unsupported algorithm: 'unsupported_algo'" in str(exc_info.value)


def test_create_hasher_valid():
    """Verify hasher creation for supported algorithms."""
    hasher_sha256 = create_hasher("sha256")
    assert hasher_sha256.digest_size == 32

    hasher_sha512 = create_hasher("SHA-512")
    assert hasher_sha512.digest_size == 64

    hasher_blake2b = create_hasher("blake2b")
    assert hasher_blake2b.digest_size == 64


def test_create_hasher_unsupported():
    """Verify hasher creation for unsupported algorithm raises UnsupportedAlgorithmError."""
    with pytest.raises(UnsupportedAlgorithmError):
        create_hasher("invalid_algo")
