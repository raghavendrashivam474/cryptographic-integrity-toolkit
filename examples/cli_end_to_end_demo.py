"""Sprint CL-05 End-to-End CLI Demonstration Script.

Demonstrates full workflow capabilities of the `cit` CLI executable:
  1. File and text hashing (`cit hash`)
  2. Directory fingerprinting and manifest generation (`cit fingerprint`)
  3. Directory state auditing and verification (`cit verify`)
  4. Merkle root calculation and tree serialization (`cit merkle root`, `cit merkle build`)
  5. Cryptographic inclusion proof generation (`cit merkle prove`)
  6. Independent proof verification against explicit trusted root (`cit merkle verify-proof`)
  7. Tamper detection on modified data files.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Helper to run CLI commands and print output."""
    print(f"\n[EXEC]: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip():
        print(f"STDERR: {res.stderr.strip()}", file=sys.stderr)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {res.returncode}")
    return res


def main() -> None:
    print("=" * 60)
    print(" CRYPTOGRAPHIC INTEGRITY TOOLKIT (`cit`) — END-TO-END DEMO")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="cit_demo_") as tmp_dir:
        base = Path(tmp_dir)
        dataset = base / "dataset"
        dataset.mkdir()
        sub = dataset / "sub"
        sub.mkdir()

        print("\n--- 1. Creating Sample Dataset ---")
        (dataset / "file1.txt").write_text("Alpha Dataset Payload", encoding="utf-8")
        (dataset / "file2.txt").write_text("Beta Dataset Payload", encoding="utf-8")
        (sub / "file3.txt").write_text("Gamma Subdirectory Payload", encoding="utf-8")
        print(f"Created dataset at: {dataset}")

        print("\n--- 2. Direct Hashing (`cit hash`) ---")
        run_cmd([sys.executable, "-m", "integrity_toolkit", "hash", "--text", "Cryptographic Toolkit Demo"])
        run_cmd([sys.executable, "-m", "integrity_toolkit", "hash", "--file", str(dataset / "file1.txt"), "--algorithm", "sha512"])

        print("\n--- 3. Directory Fingerprinting (`cit fingerprint`) ---")
        manifest_file = base / "manifest.json"
        run_cmd([sys.executable, "-m", "integrity_toolkit", "fingerprint", str(dataset), "-o", str(manifest_file)])

        print("\n--- 4. Verify Unaltered State (`cit verify`) ---")
        run_cmd([sys.executable, "-m", "integrity_toolkit", "verify", str(dataset), "-m", str(manifest_file)])

        print("\n--- 5. Merkle Tree & Root Calculation (`cit merkle`) ---")
        res_root = run_cmd([sys.executable, "-m", "integrity_toolkit", "merkle", "root", str(manifest_file)])
        
        trusted_root = None
        for line in res_root.stdout.splitlines():
            if "Merkle Root:" in line:
                trusted_root = line.split("Merkle Root:")[1].strip()
        print(f"\n[EXTRACTED TRUSTED ROOT]: {trusted_root}")

        tree_file = base / "tree.json"
        run_cmd([sys.executable, "-m", "integrity_toolkit", "merkle", "build", str(manifest_file), "-o", str(tree_file)])

        print("\n--- 6. Merkle Inclusion Proof Generation (`cit merkle prove`) ---")
        proof_file = base / "file1.proof.json"
        run_cmd([
            sys.executable, "-m", "integrity_toolkit", "merkle", "prove",
            str(manifest_file), "file1.txt", "-o", str(proof_file)
        ])

        print("\n--- 7. Verify Proof Against Explicit Trusted Root (`cit merkle verify-proof`) ---")
        run_cmd([
            sys.executable, "-m", "integrity_toolkit", "merkle", "verify-proof",
            str(proof_file), "--data", str(dataset / "file1.txt"), "--root", trusted_root
        ])

        print("\n--- 8. Tamper Detection & Failure Verification ---")
        print("Modifying 'file1.txt' payload...")
        (dataset / "file1.txt").write_text("Alpha Dataset Payload [TAMPERED!]", encoding="utf-8")

        print("\n[Audit A]: Verifying Directory State against Manifest (Expected Failure, Exit Code 1)")
        res_tampered_verify = run_cmd(
            [sys.executable, "-m", "integrity_toolkit", "verify", str(dataset), "-m", str(manifest_file)],
            check=False
        )
        assert res_tampered_verify.returncode == 1, "Expected exit code 1 on tampered manifest audit"

        print("\n[Audit B]: Verifying Merkle Inclusion Proof for Tampered File (Expected Failure, Exit Code 1)")
        res_tampered_proof = run_cmd(
            [
                sys.executable, "-m", "integrity_toolkit", "merkle", "verify-proof",
                str(proof_file), "--data", str(dataset / "file1.txt"), "--root", trusted_root
            ],
            check=False
        )
        assert res_tampered_proof.returncode == 1, "Expected exit code 1 on tampered proof verification"

        print("\n" + "=" * 60)
        print(" SUCCESS: ALL END-TO-END CLI WORKFLOWS VERIFIED PERFECTLY!")
        print("=" * 60)


if __name__ == "__main__":
    main()