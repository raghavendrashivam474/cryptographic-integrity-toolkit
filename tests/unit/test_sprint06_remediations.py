"""Regression and verification tests for Sprint 06 security and reliability remediations."""

import tempfile
from pathlib import Path
from integrity_toolkit.crypto import hash_bytes, hash_text
from integrity_toolkit.integrity import create_manifest, save_manifest, load_manifest
from integrity_toolkit.merkle import (
    hash_leaf,
    build_merkle_tree_from_manifest,
    generate_manifest_inclusion_proof,
    serialize_proof_to_json,
)
from integrity_toolkit.cli.main import main


def test_hash_bytes_memoryview_support():
    """Verify that hash_bytes and hash_leaf natively accept memoryview objects."""
    raw_data = b"Memoryview buffer test payload"
    mv = memoryview(raw_data)

    expected_hex = hash_bytes(raw_data, algorithm="sha256")
    mv_hex = hash_bytes(mv, algorithm="sha256")

    assert mv_hex == expected_hex, "hash_bytes failed to process memoryview buffer correctly"

    # Test Merkle hash_leaf with memoryview
    expected_leaf = hash_leaf(raw_data, algorithm="sha256")
    mv_leaf = hash_leaf(mv, algorithm="sha256")

    assert mv_leaf == expected_leaf, "hash_leaf failed to process memoryview buffer correctly"


def test_cli_merkle_verify_proof_relative_path_option(capsys):
    """Verify that 'cit merkle verify-proof' accepts --relative-path for subdirectory files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        sub_dir = tmp_path / "sub"
        sub_dir.mkdir(parents=True)

        target_file = sub_dir / "item.txt"
        target_file.write_text("Subdirectory file content", encoding="utf-8")

        # 1. Create manifest for root
        manifest = create_manifest(tmp_path, algorithm="sha256")
        manifest_path = tmp_path / "manifest.json"
        save_manifest(manifest, manifest_path)

        # 2. Build tree and get root
        tree = build_merkle_tree_from_manifest(manifest)
        root_digest = tree.root

        # 3. Generate proof for "sub/item.txt"
        rel_path = "sub/item.txt"
        proof = generate_manifest_inclusion_proof(manifest, rel_path)
        proof_path = tmp_path / "item.proof.json"
        proof_path.write_text(serialize_proof_to_json(proof), encoding="utf-8")

        # 4. Invoke CLI verify-proof with explicit --relative-path
        cli_args = [
            "merkle",
            "verify-proof",
            str(proof_path),
            "--data",
            str(target_file),
            "--root",
            root_digest,
            "--relative-path",
            rel_path,
        ]

        exit_code = main(cli_args)
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "Proof Verification: SUCCESS" in captured.out
