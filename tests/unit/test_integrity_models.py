"""Unit tests for the integrity subsystem data contracts."""

import pytest
from dataclasses import FrozenInstanceError

from integrity_toolkit.integrity.models import (
    DEFAULT_ALGORITHM,
    MANIFEST_FORMAT,
    MANIFEST_VERSION,
    FileFingerprint,
    FileVerificationResult,
    IntegrityManifest,
    ManifestEntry,
    VerificationReport,
    VerificationStatus,
)


def test_verification_status_values():
    assert [s.value for s in VerificationStatus] == [
        "MATCH", "MODIFIED", "MISSING", "UNEXPECTED", "ERROR",
    ]


def test_verification_status_str_compat():
    assert VerificationStatus.MATCH == "MATCH"
    assert VerificationStatus.MATCH.value == "MATCH"


def test_file_fingerprint_creation():
    fp = FileFingerprint(path="a.txt", size=3, algorithm="sha256", digest="ab" * 32)
    assert fp.path == "a.txt"
    assert fp.size == 3
    assert fp.algorithm == "sha256"
    assert fp.mtime is None


def test_file_fingerprint_frozen():
    fp = FileFingerprint(path="a.txt", size=3, algorithm="sha256", digest="ab" * 32)
    with pytest.raises(FrozenInstanceError):
        fp.size = 99


def test_file_fingerprint_to_dict():
    fp = FileFingerprint(path="a.txt", size=3, algorithm="sha256", digest="ab" * 32, mtime=1.5)
    assert fp.to_dict() == {
        "path": "a.txt", "size": 3, "algorithm": "sha256",
        "digest": "ab" * 32, "mtime": 1.5,
    }


def test_manifest_entry_to_dict():
    e = ManifestEntry(path="src/main.py", size=10, digest="cd" * 32)
    assert e.to_dict() == {"path": "src/main.py", "size": 10, "digest": "cd" * 32}


def test_manifest_entry_from_dict_round_trip():
    e = ManifestEntry(path="src/main.py", size=10, digest="cd" * 32)
    assert ManifestEntry.from_dict(e.to_dict()) == e


def test_manifest_entry_from_dict_missing_field():
    with pytest.raises(KeyError):
        ManifestEntry.from_dict({"path": "a.txt", "size": 1})


def test_integrity_manifest_defaults():
    m = IntegrityManifest()
    assert m.format == MANIFEST_FORMAT
    assert m.version == MANIFEST_VERSION
    assert m.algorithm == DEFAULT_ALGORITHM
    assert m.entries == []


def test_integrity_manifest_to_dict():
    m = IntegrityManifest(
        algorithm="sha512",
        entries=[ManifestEntry(path="a.txt", size=1, digest="ef" * 64)],
    )
    data = m.to_dict()
    assert data["format"] == "cryptographic-integrity-manifest"
    assert data["version"] == 1
    assert data["algorithm"] == "sha512"
    assert data["entries"] == [{"path": "a.txt", "size": 1, "digest": "ef" * 64}]


def test_integrity_manifest_from_dict_round_trip():
    m = IntegrityManifest(
        algorithm="blake2b",
        entries=[
            ManifestEntry(path="a.txt", size=1, digest="ab" * 64),
            ManifestEntry(path="b/c.txt", size=2, digest="cd" * 64),
        ],
    )
    assert IntegrityManifest.from_dict(m.to_dict()) == m


def test_file_verification_result_defaults():
    r = FileVerificationResult(path="a.txt", status=VerificationStatus.MATCH)
    assert r.expected_digest is None
    assert r.actual_digest is None
    assert r.message == ""


def _report(results):
    return VerificationReport(
        manifest_path="m.json", root_path="/root",
        algorithm="sha256", results=results,
    )


def test_verification_report_counts():
    r = _report([
        FileVerificationResult("a", VerificationStatus.MATCH),
        FileVerificationResult("b", VerificationStatus.MATCH),
        FileVerificationResult("c", VerificationStatus.MODIFIED),
        FileVerificationResult("d", VerificationStatus.MISSING),
        FileVerificationResult("e", VerificationStatus.UNEXPECTED),
        FileVerificationResult("f", VerificationStatus.ERROR),
    ])
    assert r.total == 6
    assert r.matched == 2
    assert r.modified == 1
    assert r.missing == 1
    assert r.unexpected == 1
    assert r.error == 1
    assert r.failures == 4
    assert not r.is_success


def test_verification_report_is_success_true():
    r = _report([FileVerificationResult("a", VerificationStatus.MATCH)])
    assert r.is_success
    assert r.failures == 0


def test_verification_report_failure_on_modified():
    r = _report([
        FileVerificationResult("a", VerificationStatus.MATCH),
        FileVerificationResult("b", VerificationStatus.MODIFIED),
    ])
    assert not r.is_success


def test_verification_report_failure_on_missing():
    assert not _report([FileVerificationResult("a", VerificationStatus.MISSING)]).is_success


def test_verification_report_failure_on_unexpected():
    assert not _report([FileVerificationResult("a", VerificationStatus.UNEXPECTED)]).is_success


def test_verification_report_failure_on_error():
    assert not _report([FileVerificationResult("a", VerificationStatus.ERROR)]).is_success


def test_verification_report_empty_manifest_is_vacuous_success():
    r = _report([])
    assert r.total == 0
    assert r.is_success
