"""Integration tests verifying full hash engine workflow and public exports."""

from io import BytesIO
import pytest

from integrity_toolkit.crypto import (
    CryptoError,
    UnsupportedAlgorithmError,
    get_supported_algorithms,
    hash_bytes,
    hash_stream,
    hash_text,
)


def test_public_package_imports():
    """Verify all expected symbols are exposed at integrity_toolkit.crypto package level."""
    from integrity_toolkit.crypto import (
        InvalidChunkSizeError,
        InvalidInputError,
        StreamReadError,
        create_hasher,
        get_algorithm_spec,
        is_algorithm_supported,
    )

    assert callable(hash_bytes)
    assert callable(hash_text)
    assert callable(hash_stream)
    assert callable(create_hasher)
    assert callable(get_supported_algorithms)
    assert callable(get_algorithm_spec)
    assert callable(is_algorithm_supported)
    assert issubclass(UnsupportedAlgorithmError, CryptoError)
    assert issubclass(InvalidChunkSizeError, CryptoError)
    assert issubclass(InvalidInputError, CryptoError)
    assert issubclass(StreamReadError, CryptoError)


@pytest.mark.parametrize("algo", ["sha256", "sha512", "blake2b"])
def test_end_to_end_byte_vs_stream_consistency(algo):
    """Verify complete hash workflow gives bit-identical output for bytes vs stream for all algorithms."""
    # Generate 1 MB test payload
    chunk = b"Cryptographic integrity verification payload chunk 0123456789\n"
    large_payload = chunk * (1024 * 1024 // len(chunk))

    direct_digest = hash_bytes(large_payload, algorithm=algo)

    stream = BytesIO(large_payload)
    stream_digest = hash_stream(stream, algorithm=algo, chunk_size=8192)

    assert direct_digest == stream_digest, f"Digest mismatch for algorithm {algo}"


def test_workflow_algorithm_discovery_and_execution():
    """Verify programmatic discovery of algorithms followed by hashing execution."""
    supported = get_supported_algorithms()
    assert len(supported) >= 3

    sample_text = "Sample payload for dynamic discovery verification"
    digests = {}

    for algo in supported:
        digests[algo] = hash_text(sample_text, algorithm=algo)
        assert isinstance(digests[algo], str)
        assert len(digests[algo]) in (64, 128)  # SHA-256 is 64 hex chars, 512-bit algos are 128 hex chars
