"""Cryptographic Primitives and Hashing Subsystem."""

from integrity_toolkit.crypto.algorithms import (
    create_hasher,
    get_algorithm_spec,
    get_supported_algorithms,
    is_algorithm_supported,
)
from integrity_toolkit.crypto.engine import hash_bytes, hash_text
from integrity_toolkit.crypto.exceptions import (
    CryptoError,
    InvalidChunkSizeError,
    InvalidInputError,
    StreamReadError,
    UnsupportedAlgorithmError,
)
from integrity_toolkit.crypto.streaming import hash_stream

__all__ = [
    "hash_bytes",
    "hash_text",
    "hash_stream",
    "create_hasher",
    "get_supported_algorithms",
    "get_algorithm_spec",
    "is_algorithm_supported",
    "CryptoError",
    "UnsupportedAlgorithmError",
    "InvalidInputError",
    "InvalidChunkSizeError",
    "StreamReadError",
]
