"""Unit tests for the integrity subsystem exception hierarchy."""

import pytest

from integrity_toolkit.integrity.exceptions import (
    FileAccessError,
    FingerprintError,
    IntegrityError,
    InvalidManifestError,
    ManifestVersionError,
    UnsafePathError,
)


def test_integrity_error_is_exception():
    assert issubclass(IntegrityError, Exception)


def test_file_access_error_hierarchy():
    assert issubclass(FileAccessError, IntegrityError)
    assert issubclass(FileAccessError, OSError)


def test_fingerprint_error_hierarchy():
    assert issubclass(FingerprintError, IntegrityError)
    assert issubclass(FingerprintError, RuntimeError)


def test_invalid_manifest_error_hierarchy():
    assert issubclass(InvalidManifestError, IntegrityError)
    assert issubclass(InvalidManifestError, ValueError)


def test_manifest_version_error_hierarchy():
    assert issubclass(ManifestVersionError, InvalidManifestError)
    assert issubclass(ManifestVersionError, IntegrityError)


def test_unsafe_path_error_hierarchy():
    assert issubclass(UnsafePathError, IntegrityError)
    assert issubclass(UnsafePathError, ValueError)


def test_base_exception_catches_all_subclasses():
    for exc_type in (
        FileAccessError,
        FingerprintError,
        InvalidManifestError,
        ManifestVersionError,
        UnsafePathError,
    ):
        with pytest.raises(IntegrityError):
            raise exc_type("boom")


def test_exception_message_preserved():
    exc = UnsafePathError("path escapes root")
    assert str(exc) == "path escapes root"
