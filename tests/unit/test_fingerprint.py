"""Unit tests for single-file fingerprinting service."""

import hashlib
from unittest.mock import patch

import pytest

from integrity_toolkit.crypto import UnsupportedAlgorithmError
from integrity_toolkit.integrity.exceptions import FileAccessError, FingerprintError
from integrity_toolkit.integrity.fingerprint import fingerprint_file


def test_fingerprint_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")

    fp = fingerprint_file(f)
    assert fp.path == str(f)
    assert fp.size == 0
    assert fp.algorithm == "sha256"
    assert fp.digest == hashlib.sha256(b"").hexdigest()
    assert fp.mtime is not None


def test_fingerprint_small_text_file(tmp_path):
    f = tmp_path / "hello.txt"
    data = b"Hello, World!\n"
    f.write_bytes(data)

    fp = fingerprint_file(f, algorithm="sha256")
    assert fp.size == len(data)
    assert fp.digest == hashlib.sha256(data).hexdigest()


def test_fingerprint_binary_file(tmp_path):
    f = tmp_path / "data.bin"
    data = bytes(range(256))
    f.write_bytes(data)

    fp = fingerprint_file(f, algorithm="sha256")
    assert fp.size == 256
    assert fp.digest == hashlib.sha256(data).hexdigest()


def test_fingerprint_large_file(tmp_path):
    f = tmp_path / "large.bin"
    # Write 200 KB chunked file
    data = b"X" * (200 * 1024)
    f.write_bytes(data)

    fp = fingerprint_file(f, algorithm="sha256", chunk_size=8192)
    assert fp.size == len(data)
    assert fp.digest == hashlib.sha256(data).hexdigest()


def test_fingerprint_sha512_and_blake2b(tmp_path):
    f = tmp_path / "test.txt"
    data = b"Cryptographic Integrity Toolkit"
    f.write_bytes(data)

    fp_512 = fingerprint_file(f, algorithm="sha512")
    assert fp_512.algorithm == "sha512"
    assert fp_512.digest == hashlib.sha512(data).hexdigest()

    fp_b2 = fingerprint_file(f, algorithm="blake2b")
    assert fp_b2.algorithm == "blake2b"
    assert fp_b2.digest == hashlib.blake2b(data).hexdigest()


def test_fingerprint_accepts_str_and_path(tmp_path):
    f = tmp_path / "test.txt"
    f.write_bytes(b"sample content")

    fp_str = fingerprint_file(str(f))
    fp_path = fingerprint_file(f)

    assert fp_str.digest == fp_path.digest
    assert fp_str.size == fp_path.size


def test_fingerprint_nonexistent_file_raises():
    with pytest.raises(FileAccessError, match="File not found"):
        fingerprint_file("nonexistent_file_12345.xyz")


def test_fingerprint_directory_raises(tmp_path):
    with pytest.raises(FileAccessError, match="directory"):
        fingerprint_file(tmp_path)


def test_fingerprint_unsupported_algorithm_raises(tmp_path):
    f = tmp_path / "test.txt"
    f.write_bytes(b"content")

    with pytest.raises(UnsupportedAlgorithmError):
        fingerprint_file(f, algorithm="md5")


def test_fingerprint_race_condition_modification_detected(tmp_path):
    f = tmp_path / "changing.txt"
    f.write_bytes(b"initial state")

    real_stat = f.stat()

    fake_stat_after = type(real_stat)(
        (real_stat.st_mode, real_stat.st_ino, real_stat.st_dev, real_stat.st_nlink,
         real_stat.st_uid, real_stat.st_gid, real_stat.st_size + 10,
         real_stat.st_atime, real_stat.st_mtime + 5, real_stat.st_ctime)
    )

    call_count = 0
    def mock_stat(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return real_stat
        return fake_stat_after

    with patch("pathlib.Path.stat", side_effect=mock_stat):
        with pytest.raises(FingerprintError, match="modified during hashing"):
            fingerprint_file(f)


def test_fingerprint_hash_stream_ioerror_raises(tmp_path):
    f = tmp_path / "test.txt"
    f.write_bytes(b"data")

    with patch("integrity_toolkit.integrity.fingerprint.hash_stream", side_effect=OSError("Read error")):
        with pytest.raises(FingerprintError, match="Failed to hash file"):
            fingerprint_file(f)
