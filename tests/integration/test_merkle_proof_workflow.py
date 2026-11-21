"""Integration and architectural boundary tests for Merkle inclusion proofs."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from integrity_toolkit.integrity.manifest import create_manifest
from integrity_toolkit.merkle.adapters import (
    build_merkle_tree_from_manifest,
    generate_manifest_inclusion_proof,
    verify_manifest_inclusion_proof,
)
from integrity_toolkit.merkle.proof_serialization import (
    deserialize_proof_from_json,
    serialize_proof_to_json,
)
from integrity_toolkit.merkle.proofs import generate_inclusion_proof
from integrity_toolkit.merkle.tree import build_merkle_tree
from integrity_toolkit.merkle.verification import verify_inclusion_proof


@pytest.mark.parametrize("algorithm", ["sha256", "sha512", "blake2b"])
def test_end_to_end_proof_lifecycle(algorithm):
    records = [b"Record 1", b"Record 2", b"Record 3", b"Record 4", b"Record 5"]

    # 1. Build Merkle tree
    tree = build_merkle_tree(records, algorithm=algorithm)

    # 2. Generate proof for target leaf (Record 3, index 2)
    proof = generate_inclusion_proof(tree, 2)

    # 3. Serialize proof to JSON
    json_proof = serialize_proof_to_json(proof)

    # 4. Deserialize proof
    loaded_proof = deserialize_proof_from_json(json_proof)

    # 5. Verify against trusted root
    assert verify_inclusion_proof(records[2], loaded_proof, tree.root) is True

    # 6. Verify tampered record fails
    assert verify_inclusion_proof(b"Tampered Record 3", loaded_proof, tree.root) is False


def test_end_to_end_manifest_proof_workflow():
    with tempfile.TemporaryDirectory() as tmp_dir:
        dir_path = Path(tmp_dir)

        (dir_path / "a.txt").write_text("Hello World", encoding="utf-8")
        (dir_path / "sub").mkdir()
        (dir_path / "sub" / "b.txt").write_text("Nested File Content", encoding="utf-8")

        # 1. Create Manifest
        manifest = create_manifest(dir_path, algorithm="sha256")

        # 2. Build Tree from Manifest
        tree = build_merkle_tree_from_manifest(manifest)

        # 3. Generate Proof for nested file
        proof_b = generate_manifest_inclusion_proof(manifest, "sub/b.txt")

        # 4. Find entry in manifest
        entry_b = next(e for e in manifest.entries if e.path == "sub/b.txt")

        # 5. Verify proof
        assert verify_manifest_inclusion_proof(entry_b, proof_b, tree.root) is True


def test_merkle_generic_proof_modules_independent_of_integrity():
    """Verify generic proof modules never import integrity_toolkit.integrity."""
    python_code = """
import sys
from integrity_toolkit.merkle import models, hashing, tree, proofs, verification, proof_serialization

imported_modules = list(sys.modules.keys())
integrity_imports = [m for m in imported_modules if m.startswith('integrity_toolkit.integrity')]
if integrity_imports:
    print(f'VIOLATION: Found integrity imports: {integrity_imports}')
    sys.exit(1)
print('SUCCESS')
"""
    result = subprocess.run(
        [sys.executable, "-c", python_code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Module independence check failed: {result.stdout}\n{result.stderr}"
    assert "SUCCESS" in result.stdout
