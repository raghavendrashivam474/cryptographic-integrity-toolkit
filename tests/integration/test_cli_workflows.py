"""Integration tests executing complete end-to-end CLI workflows."""
import subprocess
import sys
import json
from pathlib import Path

def test_cli_end_to_end_merkle_proof_workflow(tmp_path):
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    doc1 = dataset / "doc1.txt"
    doc2 = dataset / "doc2.txt"
    doc1.write_text("Secret Document 1", encoding="utf-8")
    doc2.write_text("Secret Document 2", encoding="utf-8")

    manifest_path = tmp_path / "manifest.json"
    proof_path = tmp_path / "doc1.proof.json"

    # Step 1: fingerprint directory
    res_fp = subprocess.run(
        [sys.executable, "-m", "integrity_toolkit", "fingerprint", str(dataset), "-o", str(manifest_path)],
        capture_output=True,
        text=True,
    )
    assert res_fp.returncode == 0
    assert manifest_path.exists()

    # Step 2: obtain Merkle root
    res_root = subprocess.run(
        [sys.executable, "-m", "integrity_toolkit", "merkle", "root", str(manifest_path)],
        capture_output=True,
        text=True,
    )
    assert res_root.returncode == 0
    root_hash = None
    for line in res_root.stdout.splitlines():
        if "Merkle Root:" in line:
            root_hash = line.split("Merkle Root:")[1].strip()
    assert root_hash is not None

    # Step 3: generate proof for doc1.txt
    res_prove = subprocess.run(
        [sys.executable, "-m", "integrity_toolkit", "merkle", "prove", str(manifest_path), "doc1.txt", "-o", str(proof_path)],
        capture_output=True,
        text=True,
    )
    assert res_prove.returncode == 0
    assert proof_path.exists()

    # Step 4: verify proof independently against trusted root
    res_verify = subprocess.run(
        [
            sys.executable, "-m", "integrity_toolkit", "merkle", "verify-proof",
            str(proof_path), "--data", str(doc1), "--root", root_hash
        ],
        capture_output=True,
        text=True,
    )
    assert res_verify.returncode == 0
    assert "SUCCESS" in res_verify.stdout

    # Step 5: modify doc1.txt on disk and confirm verification fails
    doc1.write_text("Tampered Secret Document 1", encoding="utf-8")
    res_verify_tampered = subprocess.run(
        [
            sys.executable, "-m", "integrity_toolkit", "merkle", "verify-proof",
            str(proof_path), "--data", str(doc1), "--root", root_hash
        ],
        capture_output=True,
        text=True,
    )
    assert res_verify_tampered.returncode == 1
