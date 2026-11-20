"""Exception classes for the integrity_toolkit.crypto package."""


class CryptoError(Exception):
    """Base exception class for all cryptographic toolkit errors."""


class UnsupportedAlgorithmError(CryptoError, ValueError):
    """Raised when an unsupported or unrecognized hash algorithm is requested."""


class InvalidInputError(CryptoError, TypeError):
    """Raised when data input to a crypto operation is of invalid type or structure."""


class InvalidChunkSizeError(CryptoError, ValueError):
    """Raised when an invalid chunk size is specified for streaming operations."""


class StreamReadError(CryptoError, IOError):
    """Raised when reading from an input data stream fails."""
