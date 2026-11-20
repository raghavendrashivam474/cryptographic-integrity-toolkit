"""Unit tests for streaming hash engine."""

from io import BytesIO
import pytest
from integrity_toolkit.crypto.engine import hash_bytes
from integrity_toolkit.crypto.exceptions import (
    InvalidChunkSizeError,
    InvalidInputError,
    StreamReadError,
    UnsupportedAlgorithmError,
)
from integrity_toolkit.crypto.streaming import hash_stream


def test_hash_stream_empty_stream():
    """Verify hash_stream correctly processes an empty binary stream."""
    stream = BytesIO(b"")
    digest = hash_stream(stream, algorithm="sha256")
    assert digest == hash_bytes(b"", algorithm="sha256")


@pytest.mark.parametrize("algorithm", ["sha256", "sha512", "blake2b"])
def test_hash_stream_equivalence_with_hash_bytes(algorithm):
    """Verify hash_stream digest is identical to hash_bytes for exact same payload."""
    payload = b"Streaming Cryptographic Hash Engine Verification Payload " * 100
    stream = BytesIO(payload)

    direct_digest = hash_bytes(payload, algorithm=algorithm)
    stream_digest = hash_stream(stream, algorithm=algorithm, chunk_size=64)

    assert stream_digest == direct_digest


@pytest.mark.parametrize("chunk_size", [1, 7, 64, 512, 4096, 65536])
def test_hash_stream_various_chunk_sizes(chunk_size):
    """Verify streaming results remain identical regardless of chunk size selection."""
    payload = b"Payload for testing chunk size boundaries. " * 500
    direct_digest = hash_bytes(payload, algorithm="sha256")

    stream = BytesIO(payload)
    stream_digest = hash_stream(stream, algorithm="sha256", chunk_size=chunk_size)

    assert stream_digest == direct_digest


def test_hash_stream_does_not_close_stream():
    """Verify caller-owned stream remains open after hash_stream completes."""
    stream = BytesIO(b"Data in open stream")
    _ = hash_stream(stream, algorithm="sha256")
    assert not stream.closed


class NonSeekableStream:
    """Mock binary stream wrapper that rejects seeking."""

    def __init__(self, data: bytes):
        self._bio = BytesIO(data)

    def read(self, size: int = -1) -> bytes:
        return self._bio.read(size)

    def seek(self, *args, **kwargs):
        raise OSError("Seek operation not supported on pipe/socket")


def test_hash_stream_non_seekable_stream():
    """Verify streaming operates correctly on non-seekable streams."""
    payload = b"Non-seekable pipe or socket payload data"
    stream = NonSeekableStream(payload)

    digest = hash_stream(stream, algorithm="sha256", chunk_size=8)
    assert digest == hash_bytes(payload, algorithm="sha256")


@pytest.mark.parametrize("invalid_chunk", [0, -1, -65536, "64k", None, True, False, 3.14])
def test_hash_stream_invalid_chunk_size(invalid_chunk):
    """Verify hash_stream raises InvalidChunkSizeError for non-positive or non-int chunk sizes."""
    stream = BytesIO(b"test data")
    with pytest.raises(InvalidChunkSizeError):
        hash_stream(stream, chunk_size=invalid_chunk)  # type: ignore


@pytest.mark.parametrize("invalid_stream", [123, "not_a_stream", None, [b"chunk"]])
def test_hash_stream_invalid_stream_object(invalid_stream):
    """Verify hash_stream raises InvalidInputError if stream object has no read method."""
    with pytest.raises(InvalidInputError):
        hash_stream(invalid_stream)  # type: ignore


class FaultyStream:
    """Mock stream that raises IOError during read."""

    def read(self, size: int = -1):
        raise IOError("Disk read error hardware fault")


def test_hash_stream_read_error():
    """Verify I/O errors during streaming are wrapped in StreamReadError."""
    faulty = FaultyStream()
    with pytest.raises(StreamReadError) as exc_info:
        hash_stream(faulty, algorithm="sha256")
    assert "Failed to read from stream" in str(exc_info.value)


class InvalidTypeStream:
    """Mock stream that yields text instead of bytes."""

    def read(self, size: int = -1):
        return "This is string, not bytes"


def test_hash_stream_invalid_return_type():
    """Verify streams returning non-bytes raise InvalidInputError."""
    stream = InvalidTypeStream()
    with pytest.raises(InvalidInputError) as exc_info:
        hash_stream(stream)
    assert "expected bytes or bytearray" in str(exc_info.value)
