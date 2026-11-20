"""Single-file fingerprinting service for the integrity subsystem.

Computes cryptographic digests of files via memory-efficient streaming I/O,
reusing the cryptographic hashing engine from ``integrity_toolkit.crypto``.
Includes metadata race-detection checks to ensure file integrity during hashing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from integrity_toolkit.crypto import (
    CryptoError,
    UnsupportedAlgorithmError,
    hash_stream,
)
from integrity_toolkit.integrity.exceptions import (
    FileAccessError,
    FingerprintError,
)
from integrity_toolkit.integrity.models import DEFAULT_ALGORITHM, FileFingerprint

DEFAULT_CHUNK_SIZE = 65536


def fingerprint_file(
    path: Union[str, Path],
    algorithm: str = DEFAULT_ALGORITHM,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> FileFingerprint:
    """Generate a cryptographic fingerprint for a single regular file.

    Args:
        path: Path to the target file (string or Path object).
        algorithm: Registered hash algorithm name (default: "sha256").
        chunk_size: Read buffer size in bytes for streaming (default: 65536).

    Returns:
        FileFingerprint containing normalized path string, size in bytes,
        algorithm name, hex digest, and modification timestamp.

    Raises:
        FileAccessError: If file does not exist, is a directory, or cannot be accessed.
        FingerprintError: If file streaming fails or file changes during hashing.
        UnsupportedAlgorithmError: If requested algorithm is not supported.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileAccessError(f"File not found: {file_path}")

    if file_path.is_dir():
        raise FileAccessError(f"Path is a directory, not a regular file: {file_path}")

    if not file_path.is_file():
        raise FileAccessError(f"Path is not a regular file: {file_path}")

    # Capture initial metadata for race-condition check (brief §7.3)
    try:
        stat_before = file_path.stat()
    except OSError as err:
        raise FileAccessError(f"Failed to access metadata for {file_path}: {err}") from err

    pre_size = stat_before.st_size
    pre_mtime = stat_before.st_mtime

    # Stream hash computation
    try:
        with open(file_path, "rb") as stream:
            digest = hash_stream(stream, algorithm=algorithm, chunk_size=chunk_size)
    except UnsupportedAlgorithmError:
        raise
    except (CryptoError, OSError, TypeError, ValueError) as err:
        raise FingerprintError(f"Failed to hash file {file_path}: {err}") from err

    # Post-hashing stat check to detect concurrent modification during read
    try:
        stat_after = file_path.stat()
    except OSError as err:
        raise FileAccessError(f"Failed to re-verify metadata for {file_path}: {err}") from err

    if stat_after.st_size != pre_size or stat_after.st_mtime != pre_mtime:
        raise FingerprintError(
            f"File content modified during hashing operation: {file_path}"
        )

    return FileFingerprint(
        path=str(file_path),
        size=pre_size,
        algorithm=algorithm.lower(),
        digest=digest,
        mtime=pre_mtime,
    )
