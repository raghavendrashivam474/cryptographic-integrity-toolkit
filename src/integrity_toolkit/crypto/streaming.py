"""Streaming hash engine for incremental processing of large binary streams."""

from typing import Any, BinaryIO

from integrity_toolkit.crypto.algorithms import create_hasher
from integrity_toolkit.crypto.exceptions import (
    InvalidChunkSizeError,
    InvalidInputError,
    StreamReadError,
)

# Standard default chunk size: 64 KiB (65,536 bytes)
DEFAULT_CHUNK_SIZE = 65536


def hash_stream(
    stream: Any,
    algorithm: str = "sha256",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> str:
    """Calculate the hexadecimal cryptographic digest of a binary stream incrementally.

    Args:
        stream: Readable binary stream object (e.g. io.BytesIO, open binary file).
        algorithm: Hashing algorithm identifier (default: "sha256").
        chunk_size: Size of chunks in bytes to read per iteration (default: 65536).

    Returns:
        Hexadecimal digest string.

    Raises:
        InvalidChunkSizeError: If chunk_size is not a positive integer > 0.
        InvalidInputError: If stream lacks a callable read method or yields non-bytes.
        StreamReadError: If an I/O error occurs while reading the stream.
        UnsupportedAlgorithmError: If requested algorithm is not supported.
    """
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise InvalidChunkSizeError(
            f"Chunk size must be a positive integer, got {chunk_size!r} ({type(chunk_size).__name__})"
        )

    if not hasattr(stream, "read") or not callable(getattr(stream, "read")):
        raise InvalidInputError(
            f"Stream object must have a callable 'read' method, got {type(stream).__name__}"
        )

    hasher = create_hasher(algorithm)

    try:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            if not isinstance(chunk, (bytes, bytearray)):
                raise InvalidInputError(
                    f"Stream read() returned {type(chunk).__name__}, expected bytes or bytearray"
                )
            hasher.update(chunk)
    except (IOError, OSError) as err:
        raise StreamReadError(f"Failed to read from stream: {err}") from err

    return hasher.hexdigest()
