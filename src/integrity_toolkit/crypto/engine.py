"""Core in-memory byte and text hashing engine."""

from typing import Union
from integrity_toolkit.crypto.algorithms import create_hasher
from integrity_toolkit.crypto.exceptions import InvalidInputError


def hash_bytes(
    data: Union[bytes, bytearray, memoryview], algorithm: str = "sha256"
) -> str:
    """Calculate the hexadecimal cryptographic digest of a byte sequence or buffer view.

    Args:
        data: Input bytes, bytearray, or memoryview to hash.
        algorithm: Hashing algorithm identifier (default: "sha256").

    Returns:
        Hexadecimal digest string.

    Raises:
        InvalidInputError: If data is not a bytes, bytearray, or memoryview instance.
        UnsupportedAlgorithmError: If requested algorithm is not supported.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise InvalidInputError(
            f"Input data must be bytes, bytearray, or memoryview, got {type(data).__name__}. "
            "Use hash_text() for string hashing with an explicit encoding."
        )

    hasher = create_hasher(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def hash_text(
    text: str, algorithm: str = "sha256", encoding: str = "utf-8"
) -> str:
    """Calculate the hexadecimal cryptographic digest of a text string.

    Args:
        text: Input text string to hash.
        algorithm: Hashing algorithm identifier (default: "sha256").
        encoding: String encoding to convert text to bytes (default: "utf-8").

    Returns:
        Hexadecimal digest string.

    Raises:
        InvalidInputError: If text is not a string or encoding fails.
        UnsupportedAlgorithmError: If requested algorithm is not supported.
    """
    if not isinstance(text, str):
        raise InvalidInputError(
            f"Input text must be a str, got {type(text).__name__}."
        )

    try:
        encoded_bytes = text.encode(encoding)
    except (UnicodeEncodeError, LookupError) as err:
        raise InvalidInputError(
            f"Failed to encode text with encoding '{encoding}': {err}"
        ) from err

    return hash_bytes(encoded_bytes, algorithm=algorithm)
