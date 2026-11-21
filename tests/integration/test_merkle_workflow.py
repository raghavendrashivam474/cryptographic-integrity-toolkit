"""Integration tests for Merkle tree construction and architectural boundaries."""

import subprocess
import sys
import pytest

from integrity_toolkit.integrity import create_manifest
from integrity_toolkit.merkle import (
    build_merkle_tree,
    build_merkle_tree_from_manifest,
)


def test_end_to_end_directory_manifest_to_merkle(tmp_path):
    """Verify end-to-end workflow: real directory -> manifest -> Merkle Tree."""
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()

    (tmp_path / "file_a.txt").write_text("Hello World A", encoding="utf-8")
    (tmp_path / "file_b.txt").write_text("Hello World B", encoding="utf-8")
    (sub_dir / "file_c.txt").write_text("Hello World C", encoding="utf-8")

    manifest = create_manifest(tmp_path, algorithm="sha256")
    assert len(manifest.entries) == 3

    tree = build_merkle_tree_from_manifest(manifest)

    assert tree.leaf_count == 3
    assert tree.algorithm == "sha256"
    assert len(tree.root) == 64
    assert len(tree.levels) == 3


@pytest.mark.parametrize("algo", ["sha256", "sha512", "blake2b"])
def test_end_to_end_multi_algorithm_support(tmp_path, algo):
    """Verify manifest-to-Merkle tree pipeline for all supported hash algorithms."""
    (tmp_path / "data.bin").write_bytes(b"\x00\x01\x02\x03")

    manifest = create_manifest(tmp_path, algorithm=algo)
    tree = build_merkle_tree_from_manifest(manifest)

    assert tree.algorithm == algo
    assert tree.leaf_count == 1
    assert tree.root == tree.levels[0][0]


def test_merkle_generic_module_independence_from_integrity():
    """Architectural boundary assertion: importing generic merkle engine must NOT load integrity package."""
    code = (
        "import sys; "
        "import integrity_toolkit.merkle.hashing; "
        "import integrity_toolkit.merkle.tree; "
        "tree = integrity_toolkit.merkle.tree.build_merkle_tree([b'payload']); "
        "integrity_loaded = any(m.startswith('integrity_toolkit.integrity') for m in sys.modules); "
        "assert not integrity_loaded, 'integrity subsystem loaded unexpectedly'; "
        "print('ISOLATION_OK')"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "ISOLATION_OK" in result.stdout
