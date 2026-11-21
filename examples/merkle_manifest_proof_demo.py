"""Demonstration: File manifest Merkle inclusion proof generation and verification."""

import tempfile
from pathlib import Path

from integrity_toolkit.integrity import create_manifest
from integrity_toolkit.merkle import (
    build_merkle_tree_from_manifest,
    generate_manifest_inclusion_proof,
    verify_manifest_inclusion_proof,
)


def main():
    print("=== Cryptographic Integrity Toolkit — Manifest Proof Demo ===")

    with tempfile.TemporaryDirectory() as tmp_dir:
        root_dir = Path(tmp_dir)

        # Create dummy directory structure
        (root_dir / "config.json").write_text('{"setting": "enabled"}', encoding="utf-8")
        (root_dir / "data").mkdir()
        (root_dir / "data" / "records.csv").write_text("id,val\n1,100\n2,200\n", encoding="utf-8")

        print("1. Fingerprinting directory and creating manifest...")
        manifest = create_manifest(root_dir, algorithm="sha256")
        print(f"   Created manifest with {len(manifest.entries)} file entries.")

        print("2. Constructing Merkle tree from manifest (CIT-MLF1)...")
        tree = build_merkle_tree_from_manifest(manifest)
        print(f"   Merkle Root: {tree.root}")

        target_rel_path = "data/records.csv"
        print(f"\n3. Generating inclusion proof for target file '{target_rel_path}'...")
        proof = generate_manifest_inclusion_proof(manifest, target_rel_path)
        print(f"   Proof generated successfully with {len(proof.steps)} evaluation steps.")

        target_entry = next(e for e in manifest.entries if e.path == target_rel_path)
        print("\n4. Verifying authentic manifest record against Merkle root...")
        valid = verify_manifest_inclusion_proof(target_entry, proof, expected_root=tree.root)
        print(f"   Verification Result: {valid} (Expected: True)")


if __name__ == "__main__":
    main()
