"""Exception classes for the integrity_toolkit.integrity package.

The hierarchy mirrors the conventions established by
integrity_toolkit.crypto.exceptions: a package-specific base class,
with subclasses also deriving from suitable built-in exception types
so existing ``except ValueError`` / ``except OSError`` style handling
keeps working for callers.
"""


class IntegrityError(Exception):
    """Base exception for all integrity subsystem errors."""


class FileAccessError(IntegrityError, IOError):
    """Raised when file access, reading, or metadata capture fails."""


class FingerprintError(IntegrityError, RuntimeError):
    """Raised when fingerprinting fails (e.g. file changed during hashing)."""


class InvalidManifestError(IntegrityError, ValueError):
    """Raised when a manifest is malformed, corrupt, or fails validation."""


class ManifestVersionError(InvalidManifestError):
    """Raised when a manifest declares an unsupported schema version."""


class UnsafePathError(IntegrityError, ValueError):
    """Raised when a path would escape the designated verification root."""
