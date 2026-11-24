"""Domain-separated leaf and internal node cryptographic hashing primitives."""

from typing import Union
from integrity_toolkit.crypto import (
    CryptoError,
    get_algorithm_spec,
    hash_bytes,
)
from integrity_toolkit.merkle.exceptions import (
    InvalidNodeDigestError,
    MerkleError,
)

# Domain separation byte identifiers
LEAF_DOMAIN_PREFIX = b"\x00"
INTERNAL_DOMAIN_PREFIX = b"\x01"


def hash_leaf(data: Union[bytes, bytearray, memoryview], algorithm: str = "sha256") -> str:
    """Calculate the domain-separated Merkle leaf digest for input data.

    Leaf Hash = H(0x00 || data)

    Args:
        data: Raw input bytes, bytearray, or memoryview.
        algorithm: Registered hash algorithm identifier (default: "sha256").

    Returns:
        Lowercase hexadecimal digest string.

    Raises:
        InvalidInputError: If data is not bytes, bytearray, or memoryview (from crypto subsystem).
        UnsupportedAlgorithmError: If algorithm is not supported (from crypto subsystem).
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        from integrity_toolkit.crypto.exceptions import InvalidInputError
        raise InvalidInputError(
            f"Leaf payload must be bytes, bytearray, or memoryview, got {type(data).__name__}"
        )

    payload = LEAF_DOMAIN_PREFIX + bytes(data)
    return hash_bytes(payload, algorithm=algorithm)


def hash_internal(
    left_digest: str, right_digest: str, algorithm: str = "sha256"
) -> str:
    """Calculate the domain-separated Merkle internal parent digest from two child digests.

    Internal Hash = H(0x01 || raw_bytes(left_digest) || raw_bytes(right_digest))

    Args:
        left_digest: Lowercase hexadecimal digest string of left child.
        right_digest: Lowercase hexadecimal digest string of right child.
        algorithm: Registered hash algorithm identifier (default: "sha256").

    Returns:
        Lowercase hexadecimal digest string of parent node.

    Raises:
        InvalidNodeDigestError: If either digest is not a valid hex string or has invalid byte length.
        UnsupportedAlgorithmError: If algorithm is not supported.
    """
    spec = get_algorithm_spec(algorithm)
    expected_hex_len = spec.digest_size * 2

    # Validate digest format and length
    for label, digest in (("Left", left_digest), ("Right", right_digest)):
        if not isinstance(digest, str):
            raise InvalidNodeDigestError(
                f"{label} child digest must be a string, got {type(digest).__name__}"
            )
        if len(digest) != expected_hex_len:
            raise InvalidNodeDigestError(
                f"{label} child digest length ({len(digest)}) invalid for algorithm '{algorithm}' "
                f"(expected {expected_hex_len} characters)"
            )
        try:
            bytes.fromhex(digest)
        except ValueError as err:
            raise InvalidNodeDigestError(
                f"{label} child digest is not valid hexadecimal string: {err}"
            ) from err

    left_raw = bytes.fromhex(left_digest)
    right_raw = bytes.fromhex(right_digest)
    payload = INTERNAL_DOMAIN_PREFIX + left_raw + right_raw
    return hash_bytes(payload, algorithm=algorithm)
