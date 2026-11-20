"""Manifest management service for the integrity subsystem.

Handles generation, validation, JSON serialization, safe atomic persistence,
and deserialization of integrity manifests according to schema v1.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Iterable, Union

from integrity_toolkit.crypto import is_algorithm_supported, get_algorithm_spec
from integrity_toolkit.integrity.exceptions import (
    FileAccessError,
    InvalidManifestError,
    ManifestVersionError,
    UnsafePathError,
)
from integrity_toolkit.integrity.fingerprint import fingerprint_file
from integrity_toolkit.integrity.models import (
    DEFAULT_ALGORITHM,
    MANIFEST_FORMAT,
    MANIFEST_VERSION,
    IntegrityManifest,
    ManifestEntry,
)
from integrity_toolkit.integrity.traversal import discover_files, normalize_posix_path

HEX_PATTERN = re.compile(r"^[0-9a-fA-F]+$")


def validate_manifest_entry_path(path_str: str) -> str:
    """Validate that a manifest relative path string is safe.

    Rejects absolute paths, parent directory traversal ('..'), drive letters,
    and invalid characters.
    """
    if not path_str or not path_str.strip():
        raise UnsafePathError("Manifest entry path cannot be empty")

    norm = path_str.replace("\\", "/")

    if norm.startswith("/") or re.match(r"^[a-zA-Z]:", norm):
        raise UnsafePathError(f"Absolute path not allowed in manifest: {path_str}")

    parts = norm.split("/")
    if ".." in parts:
        raise UnsafePathError(f"Parent directory traversal ('..') prohibited: {path_str}")

    return norm


def validate_manifest(manifest: IntegrityManifest) -> None:
    """Validate structural, cryptographic, and security rules for a manifest object.

    Raises:
        InvalidManifestError: If structure, algorithm, or digest format is invalid.
        ManifestVersionError: If schema version is unsupported.
        UnsafePathError: If path contains safety violations.
    """
    if manifest.format != MANIFEST_FORMAT:
        raise InvalidManifestError(
            f"Invalid manifest format identifier: '{manifest.format}' (expected '{MANIFEST_FORMAT}')"
        )

    if manifest.version != MANIFEST_VERSION:
        raise ManifestVersionError(
            f"Unsupported manifest version: {manifest.version} (expected {MANIFEST_VERSION})"
        )

    if not is_algorithm_supported(manifest.algorithm):
        raise InvalidManifestError(f"Unsupported hash algorithm in manifest: '{manifest.algorithm}'")

    spec = get_algorithm_spec(manifest.algorithm)
    expected_hex_len = spec.digest_size * 2

    seen_paths: set[str] = set()

    for idx, entry in enumerate(manifest.entries):
        if not isinstance(entry, ManifestEntry):
            raise InvalidManifestError(f"Entry {idx} is not a valid ManifestEntry object")

        norm_path = validate_manifest_entry_path(entry.path)

        if norm_path in seen_paths:
            raise InvalidManifestError(f"Duplicate entry path found in manifest: '{norm_path}'")
        seen_paths.add(norm_path)

        if entry.size < 0:
            raise InvalidManifestError(f"Invalid negative file size in manifest for '{entry.path}'")

        if not entry.digest or len(entry.digest) != expected_hex_len or not HEX_PATTERN.match(entry.digest):
            raise InvalidManifestError(
                f"Invalid digest for algorithm '{manifest.algorithm}' in entry '{entry.path}'"
            )


def create_manifest(
    root: Union[str, Path],
    algorithm: str = DEFAULT_ALGORITHM,
    exclude_paths: Iterable[Union[str, Path]] | None = None,
    follow_symlinks: bool = False,
) -> IntegrityManifest:
    """Generate an IntegrityManifest for all discovered files in a directory root.

    Files are discovered and fingerprinted in deterministic order.
    """
    root_path = Path(root).resolve()
    files = discover_files(root_path, exclude_paths=exclude_paths, follow_symlinks=follow_symlinks)

    entries: list[ManifestEntry] = []
    for rel_path in files:
        full_path = root_path / rel_path
        fp = fingerprint_file(full_path, algorithm=algorithm)
        entries.append(
            ManifestEntry(
                path=rel_path,
                size=fp.size,
                digest=fp.digest,
            )
        )

    manifest = IntegrityManifest(
        algorithm=algorithm.lower(),
        entries=entries,
    )

    validate_manifest(manifest)
    return manifest


def save_manifest(manifest: IntegrityManifest, destination: Union[str, Path]) -> Path:
    """Serialize and safely save an IntegrityManifest to a destination file using atomic replacement.

    Guarantees no partially written manifest files are left if writing fails.
    """
    validate_manifest(manifest)
    dest_path = Path(destination).resolve()

    dest_dir = dest_path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    data = manifest.to_dict()
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    # Atomic write pattern: temporary file in same directory, flush, close, replace
    temp_fd, temp_path = tempfile.mkstemp(dir=dest_dir, prefix=".manifest_tmp_")
    try:
        with os.fdopen(temp_fd, "wb") as f:
            f.write(json_bytes)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, dest_path)
    except Exception as err:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise FileAccessError(f"Failed to save manifest to {dest_path}: {err}") from err

    return dest_path


def load_manifest(source: Union[str, Path]) -> IntegrityManifest:
    """Load, parse, and validate an IntegrityManifest from a JSON file.

    Raises:
        FileAccessError: If manifest file cannot be read.
        InvalidManifestError: If JSON is malformed or schema validation fails.
    """
    source_path = Path(source)

    if not source_path.exists():
        raise FileAccessError(f"Manifest file not found: {source_path}")

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise InvalidManifestError(f"Malformed manifest JSON in {source_path}: {err}") from err
    except OSError as err:
        raise FileAccessError(f"Failed to read manifest file {source_path}: {err}") from err

    if not isinstance(data, dict):
        raise InvalidManifestError(f"Root JSON element in {source_path} must be an object")

    try:
        manifest = IntegrityManifest.from_dict(data)
    except (KeyError, TypeError) as err:
        raise InvalidManifestError(f"Missing or invalid field in manifest {source_path}: {err}") from err

    validate_manifest(manifest)
    return manifest
