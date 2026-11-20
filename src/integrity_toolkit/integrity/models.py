"""Data contracts for the integrity_toolkit.integrity subsystem.

These models are the structured records exchanged between the
fingerprinting, manifest, verification, and CLI layers. They are pure
data containers: no filesystem access and no CLI/printing logic lives
in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

MANIFEST_FORMAT = "cryptographic-integrity-manifest"
MANIFEST_VERSION = 1
DEFAULT_ALGORITHM = "sha256"


class VerificationStatus(str, Enum):
    """Classification of a single file's verification outcome."""

    MATCH = "MATCH"
    MODIFIED = "MODIFIED"
    MISSING = "MISSING"
    UNEXPECTED = "UNEXPECTED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class FileFingerprint:
    """Cryptographic fingerprint of a single file.

    ``mtime`` is informational audit metadata only; it is never used
    as a substitute for cryptographic content verification.
    """

    path: str
    size: int
    algorithm: str
    digest: str
    mtime: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the fingerprint."""
        return {
            "path": self.path,
            "size": self.size,
            "algorithm": self.algorithm,
            "digest": self.digest,
            "mtime": self.mtime,
        }


@dataclass(frozen=True)
class ManifestEntry:
    """A single deterministic manifest record.

    ``path`` is always a normalized relative POSIX-style path using
    forward slashes. Structural validation (digest format, path
    safety, duplicates) is performed by ``integrity.manifest``.
    """

    path: str
    size: int
    digest: str

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON-serializable entry mapping."""
        return {"path": self.path, "size": self.size, "digest": self.digest}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ManifestEntry:
        """Build an entry from a decoded mapping.

        Raises ``KeyError`` for missing fields; callers in
        ``integrity.manifest`` convert this into ``InvalidManifestError``.
        """
        return cls(path=data["path"], size=data["size"], digest=data["digest"])


@dataclass
class IntegrityManifest:
    """Structured integrity manifest (schema version 1)."""

    algorithm: str = DEFAULT_ALGORITHM
    entries: list[ManifestEntry] = field(default_factory=list)
    format: str = MANIFEST_FORMAT
    version: int = MANIFEST_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON-serializable manifest mapping."""
        return {
            "format": self.format,
            "version": self.version,
            "algorithm": self.algorithm,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IntegrityManifest:
        """Build a manifest from a decoded mapping (no validation here)."""
        return cls(
            algorithm=data["algorithm"],
            entries=[ManifestEntry.from_dict(item) for item in data["entries"]],
            format=data["format"],
            version=data["version"],
        )


@dataclass(frozen=True)
class FileVerificationResult:
    """Outcome of verifying a single file against a manifest entry."""

    path: str
    status: VerificationStatus
    expected_digest: str | None = None
    actual_digest: str | None = None
    expected_size: int | None = None
    actual_size: int | None = None
    message: str = ""


@dataclass
class VerificationReport:
    """Aggregated, structured result of a verification run.

    ``is_success`` is true only when there are no MODIFIED, MISSING,
    UNEXPECTED, or ERROR results. An empty manifest therefore verifies
    vacuously; policy about empty sets belongs to callers (e.g. CLI).
    """

    manifest_path: str
    root_path: str
    algorithm: str
    results: list[FileVerificationResult] = field(default_factory=list)

    def count(self, status: VerificationStatus) -> int:
        """Return the number of results with the given status."""
        return sum(1 for r in self.results if r.status == status)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def matched(self) -> int:
        return self.count(VerificationStatus.MATCH)

    @property
    def modified(self) -> int:
        return self.count(VerificationStatus.MODIFIED)

    @property
    def missing(self) -> int:
        return self.count(VerificationStatus.MISSING)

    @property
    def unexpected(self) -> int:
        return self.count(VerificationStatus.UNEXPECTED)

    @property
    def error(self) -> int:
        return self.count(VerificationStatus.ERROR)

    @property
    def failures(self) -> int:
        return self.total - self.matched

    @property
    def is_success(self) -> bool:
        return self.failures == 0
