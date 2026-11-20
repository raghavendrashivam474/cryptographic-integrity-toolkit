"""Unit tests for directory traversal and file discovery."""

import pytest

from integrity_toolkit.integrity.exceptions import FileAccessError
from integrity_toolkit.integrity.traversal import discover_files, normalize_posix_path


def test_normalize_posix_path():
    assert normalize_posix_path(r"sub\dir\file.txt") == "sub/dir/file.txt"
    assert normalize_posix_path("./sub/file.txt") == "sub/file.txt"
    assert normalize_posix_path(r".\sub\file.txt") == "sub/file.txt"


def test_discover_files_empty_directory(tmp_path):
    assert discover_files(tmp_path) == []


def test_discover_files_flat_directory(tmp_path):
    (tmp_path / "b.txt").write_bytes(b"b")
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "c.txt").write_bytes(b"c")

    res = discover_files(tmp_path)
    # Must be deterministically sorted
    assert res == ["a.txt", "b.txt", "c.txt"]


def test_discover_files_nested_directories(tmp_path):
    sub = tmp_path / "src" / "pkg"
    sub.mkdir(parents=True)

    (tmp_path / "README.md").write_bytes(b"readme")
    (sub / "mod.py").write_bytes(b"mod")
    (tmp_path / "src" / "main.py").write_bytes(b"main")

    res = discover_files(tmp_path)
    assert res == ["README.md", "src/main.py", "src/pkg/mod.py"]


def test_discover_files_excludes_specified_file(tmp_path):
    (tmp_path / "file1.txt").write_bytes(b"1")
    (tmp_path / "manifest.json").write_bytes(b"{}")

    res = discover_files(tmp_path, exclude_paths=["manifest.json"])
    assert res == ["file1.txt"]


def test_discover_files_nonexistent_directory_raises():
    with pytest.raises(FileAccessError, match="Directory not found"):
        discover_files("nonexistent_dir_12345")


def test_discover_files_file_passed_instead_of_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_bytes(b"content")

    with pytest.raises(FileAccessError, match="not a directory"):
        discover_files(f)


def test_discover_files_ignores_symlinks_by_default(tmp_path):
    target = tmp_path / "real.txt"
    target.write_bytes(b"real content")

    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks not supported in this test environment")

    res = discover_files(tmp_path, follow_symlinks=False)
    assert res == ["real.txt"]
