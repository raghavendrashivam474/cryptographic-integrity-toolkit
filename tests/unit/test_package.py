"""Unit tests for package imports and version metadata."""

import integrity_toolkit
import integrity_toolkit.cli
import integrity_toolkit.crypto
import integrity_toolkit.merkle


def test_package_import():
    """Test that root package and subpackages import successfully."""
    assert integrity_toolkit is not None
    assert integrity_toolkit.crypto is not None
    assert integrity_toolkit.merkle is not None
    assert integrity_toolkit.cli is not None


def test_package_version():
    """Test package version string matches release target."""
    assert integrity_toolkit.__version__ == "0.0.1"