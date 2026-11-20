"""Algorithm registry and metadata management for cryptographic hashing."""

import hashlib
from typing import Any, Callable, Dict, List, NamedTuple, Optional

from integrity_toolkit.crypto.exceptions import UnsupportedAlgorithmError


class AlgorithmSpec(NamedTuple):
    """Metadata specification for a supported hash algorithm."""

    canonical_name: str
    digest_size: int
    factory: Callable[[], Any]


# Authoritative registry of supported cryptographic hash algorithms
_ALGORITHM_REGISTRY: Dict[str, AlgorithmSpec] = {
    "sha256": AlgorithmSpec(
        canonical_name="sha256",
        digest_size=32,
        factory=hashlib.sha256,
    ),
    "sha512": AlgorithmSpec(
        canonical_name="sha512",
        digest_size=64,
        factory=hashlib.sha512,
    ),
    "blake2b": AlgorithmSpec(
        canonical_name="blake2b",
        digest_size=64,
        factory=hashlib.blake2b,
    ),
}


def normalize_algorithm_name(name: str) -> str:
    """Normalize algorithm input strings (case-insensitive, strip whitespace/hyphens/underscores).

    Args:
        name: Raw algorithm identifier string.

    Returns:
        Normalized algorithm key.
    """
    if not isinstance(name, str):
        raise UnsupportedAlgorithmError(
            f"Algorithm name must be a string, got {type(name).__name__}"
        )
    cleaned = name.strip().lower().replace("-", "").replace("_", "")
    return cleaned


def is_algorithm_supported(algorithm: str) -> bool:
    """Check whether a given algorithm name is supported.

    Args:
        algorithm: Algorithm identifier string.

    Returns:
        True if supported, False otherwise.
    """
    try:
        norm_name = normalize_algorithm_name(algorithm)
        return norm_name in _ALGORITHM_REGISTRY
    except UnsupportedAlgorithmError:
        return False


def get_supported_algorithms() -> List[str]:
    """Retrieve list of canonical supported algorithm names.

    Returns:
        List of supported algorithm names.
    """
    return [spec.canonical_name for spec in _ALGORITHM_REGISTRY.values()]


def get_algorithm_spec(algorithm: str) -> AlgorithmSpec:
    """Retrieve the specification for a supported algorithm.

    Args:
        algorithm: Algorithm identifier string.

    Returns:
        AlgorithmSpec for requested algorithm.

    Raises:
        UnsupportedAlgorithmError: If algorithm is not supported.
    """
    norm_name = normalize_algorithm_name(algorithm)
    if norm_name not in _ALGORITHM_REGISTRY:
        supported = ", ".join(get_supported_algorithms())
        raise UnsupportedAlgorithmError(
            f"Unsupported algorithm: '{algorithm}'. Supported algorithms are: {supported}"
        )
    return _ALGORITHM_REGISTRY[norm_name]


def create_hasher(algorithm: str) -> Any:
    """Create a new standard-library hasher instance for the given algorithm.

    Args:
        algorithm: Name of hashing algorithm (e.g. 'sha256', 'sha512', 'blake2b').

    Returns:
        Fresh hashlib hash object instance.

    Raises:
        UnsupportedAlgorithmError: If algorithm is not supported.
    """
    spec = get_algorithm_spec(algorithm)
    return spec.factory()
