"""Runnable demonstration of file-manifest to Merkle tree construction (CL-03)."""

import tempfile
from pathlib import Path

from integrity_toolkit.integrity import create_manifest
from integrity_toolkit.integrity.models import IntegrityManifest
from integrity_toolkit.merkle import build_merkle_tree_from_manifest


def main() -> None:
    print("==================================================")
    print("   File-Manifest to Merkle Tree Integration Demo  ")
    print("==================================================")

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        (root / "alpha.txt").write_text("Alpha content", encoding="utf-8")
        (root / "beta.txt").write_text("Beta content", encoding="utf-8")

        sub = root / "folder"
        sub.mkdir()
        (root / "folder" / "gamma.txt").write_text("Gamma content", encoding="utf-8")

        print("\n1. Generating Integrity Manifest from directory...")
        manifest = create_manifest(root, algorithm="sha256")
        print(f"   Discovered {len(manifest.entries)} file entries.")

        print("\n2. Building Merkle Tree from Manifest...")
        tree = build_merkle_tree_from_manifest(manifest)

        print(f"   Algorithm:   {tree.algorithm.upper()}")
        print(f"   Leaf Count:  {tree.leaf_count}")
        print(f"   Merkle Root: {tree.root}")

        print("\n3. Testing Entry Order Invariance...")
        # Reverse entries list to verify deterministic ordering by path
        reversed_entries = list(reversed(manifest.entries))
        reordered_manifest = IntegrityManifest(
            algorithm=manifest.algorithm,
            entries=reversed_entries,
        )

        reordered_tree = build_merkle_tree_from_manifest(reordered_manifest)
        print(f"   Reordered Manifest Merkle Root: {reordered_tree.root}")
        assert tree.root == reordered_tree.root
        print("   [SUCCESS] Merkle Root is invariant to manifest entry ordering!")


if __name__ == "__main__":
    main()
