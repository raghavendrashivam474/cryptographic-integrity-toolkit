"""Verification engine for the integrity subsystem.

Compares current filesystem state against a loaded or specified manifest,
identifying matching, modified, missing, unexpected, or errored files without
modifying any files on disk.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from integrity_toolkit.integrity.exceptions import (
    FileAccessError,
    IntegrityError,
    UnsafePathError,
)
from integrity_toolkit.integrity.fingerprint import fingerprint_file
from integrity_toolkit.integrity.manifest import load_manifest, validate_manifest_entry_path
from integrity_toolkit.integrity.models import (
    FileVerificationResult,
    IntegrityManifest,
    VerificationReport,
    VerificationStatus,
)
from integrity_toolkit.integrity.traversal import discover_files, normalize_posix_path


def verify_manifest(
    root: Union[str, Path],
    manifest: Union[IntegrityManifest, str, Path],
    ignore_unexpected: bool = False,
) -> VerificationReport:
    """Verify filesystem contents under root against an integrity manifest.

    Args:
        root: Root directory containing files to verify.
        manifest: Loaded IntegrityManifest instance or file path to JSON manifest.
        ignore_unexpected: If True, files present on disk but absent from manifest
          are omitted from the final report (default: False).

    Returns:
        VerificationReport containing per-file verification outcomes and summary metrics.

    Raises:
        FileAccessError: If root directory does not exist or is not a directory.
        UnsafePathError: If a manifest entry path escapes the verification root.
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        raise FileAccessError(f"Verification root directory not found: {root}")

    if not root_path.is_dir():
        raise FileAccessError(f"Verification root is not a directory: {root}")

    manifest_obj: IntegrityManifest
    manifest_source_label: str

    if isinstance(manifest, (str, Path)):
        manifest_source_label = str(manifest)
        manifest_obj = load_manifest(manifest)
    else:
        manifest_source_label = "<in-memory-manifest>"
        manifest_obj = manifest

    algorithm = manifest_obj.algorithm.lower()
    results: list[FileVerificationResult] = []
    expected_paths: set[str] = set()

    # Phase 1: Verify all files recorded in the manifest
    for entry in manifest_obj.entries:
        norm_rel = validate_manifest_entry_path(entry.path)
        expected_paths.add(norm_rel)

        target_path = (root_path / norm_rel).resolve()

        # Path safety containment check
        try:
            target_path.relative_to(root_path)
        except ValueError:
            raise UnsafePathError(
                f"Manifest entry path '{entry.path}' resolves outside verification root '{root_path}'"
            )

        if not target_path.exists():
            results.append(
                FileVerificationResult(
                    path=norm_rel,
                    status=VerificationStatus.MISSING,
                    expected_digest=entry.digest,
                    expected_size=entry.size,
                    message="File missing on disk",
                )
            )
            continue

        if not target_path.is_file():
            results.append(
                FileVerificationResult(
                    path=norm_rel,
                    status=VerificationStatus.ERROR,
                    expected_digest=entry.digest,
                    expected_size=entry.size,
                    message="Path exists but is not a regular file",
                )
            )
            continue

        try:
            fp = fingerprint_file(target_path, algorithm=algorithm)

            if fp.size != entry.size or fp.digest.lower() != entry.digest.lower():
                results.append(
                    FileVerificationResult(
                        path=norm_rel,
                        status=VerificationStatus.MODIFIED,
                        expected_digest=entry.digest,
                        actual_digest=fp.digest,
                        expected_size=entry.size,
                        actual_size=fp.size,
                        message="File content or size differs from manifest",
                    )
                )
            else:
                results.append(
                    FileVerificationResult(
                        path=norm_rel,
                        status=VerificationStatus.MATCH,
                        expected_digest=entry.digest,
                        actual_digest=fp.digest,
                        expected_size=entry.size,
                        actual_size=fp.size,
                        message="File integrity verified",
                    )
                )
        except IntegrityError as err:
            results.append(
                FileVerificationResult(
                    path=norm_rel,
                    status=VerificationStatus.ERROR,
                    expected_digest=entry.digest,
                    expected_size=entry.size,
                    message=f"Read/fingerprint error: {err}",
                )
            )

    # Phase 2: Discover unexpected files if requested
    if not ignore_unexpected:
        exclude_manifest_file = []
        if isinstance(manifest, (str, Path)):
            exclude_manifest_file.append(manifest)

        discovered = discover_files(root_path, exclude_paths=exclude_manifest_file)
        for disc_rel in discovered:
            if disc_rel not in expected_paths:
                results.append(
                    FileVerificationResult(
                        path=disc_rel,
                        status=VerificationStatus.UNEXPECTED,
                        message="File exists on filesystem but is not listed in manifest",
                    )
                )

    return VerificationReport(
        manifest_path=manifest_source_label,
        root_path=str(root_path),
        algorithm=algorithm,
        results=results,
    )
