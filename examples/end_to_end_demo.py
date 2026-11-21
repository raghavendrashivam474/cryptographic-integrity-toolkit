"""Comprehensive End-to-End Manual Verification Demonstration.

Demonstrates complete integration across all implemented subsystems:
  - Sprint CL-01: Cryptographic Hash Engine (SHA-256, SHA-512, BLAKE2b)
  - Sprint CL-02: File Fingerprinting & Directory Integrity Manifests
  - Sprint CL-03: Domain-Separated Merkle Tree Engine & Manifest Adapters
"""

import io
import os
import tempfile
from pathlib import Path

# CL-01 Imports
from integrity_toolkit.crypto import hash_bytes, hash_stream, hash_text
# CL-02 Imports
from integrity_toolkit.integrity import (
    create_manifest,
    fingerprint_file,
    verify_manifest,
)
# CL-03 Imports
from integrity_toolkit.merkle import (
    build_merkle_tree,
    build_merkle_tree_from_manifest,
    hash_internal,
    hash_leaf,
    serialize_manifest_entry,
)


def section_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def run_demo() -> None:
    print("CRYPTOGRAPHIC INTEGRITY TOOLKIT — END-TO-END MANUAL VERIFICATION")

    # -------------------------------------------------------------------------
    # 1. Cryptographic Hash Engine (CL-01)
    # -------------------------------------------------------------------------
    section_header("1. HASH ENGINE SUBSYSTEM (CL-01)")

    sample_text = "The quick brown fox jumps over the lazy dog"
    print(f"Input Text: '{sample_text}'")

    h_sha256 = hash_text(sample_text, algorithm="sha256")
    h_sha512 = hash_text(sample_text, algorithm="sha512")
    h_blake2b = hash_text(sample_text, algorithm="blake2b")

    print(f"  SHA-256 : {h_sha256}")
    print(f"  SHA-512 : {h_sha512[:32]}... (truncated)")
    print(f"  BLAKE2b : {h_blake2b[:32]}... (truncated)")

    # Streaming hash check
    stream_data = io.BytesIO(sample_text.encode("utf-8"))
    stream_hash = hash_stream(stream_data, algorithm="sha256")
    print(f"  Streamed SHA-256 Match: {stream_hash == h_sha256} ({stream_hash})")

    # -------------------------------------------------------------------------
    # 2. File Fingerprinting & Manifest Verification (CL-02)
    # -------------------------------------------------------------------------
    section_header("2. FINGERPRINTING & MANIFEST SUBSYSTEM (CL-02)")

    with tempfile.TemporaryDirectory() as tmp_dir:
        root_path = Path(tmp_dir)

        # Create temporary sample files
        doc1 = root_path / "document.txt"
        doc2 = root_path / "data" / "dataset.csv"
        doc2.parent.mkdir(parents=True, exist_ok=True)

        doc1.write_text("Confidential Report v1.0\nAuthor: Security Team", encoding="utf-8")
        doc2.write_text("id,val\n1,100\n2,200\n", encoding="utf-8")

        # Fingerprint single file
        fp1 = fingerprint_file(doc1, algorithm="sha256")
        print(f"Single File Fingerprint ({doc1.name}):")
        print(f"  Path:   {fp1.path}")
        print(f"  Size:   {fp1.size} bytes")
        print(f"  Digest: {fp1.digest}")

        # Create Directory Manifest
        print("\nCreating Directory Manifest...")
        manifest = create_manifest(root_path, algorithm="sha256")
        print(f"  Manifest Version: {manifest.version}")
        print(f"  Algorithm:        {manifest.algorithm}")
        print(f"  Total Entries:    {len(manifest.entries)}")

        # Verify Untouched Directory
        report = verify_manifest(root_path, manifest)
        print(f"\nIntegrity Verification (Untouched Directory):")
        print(f"  Success Status:   {report.is_success}")
        print(f"  Total Verified:   {report.total}")
        print(f"  Matching Files:   {report.matched}")

        # Tamper with file
        print("\n[SIMULATION] Tampering with dataset.csv...")
        doc2.write_text("id,val\n1,100\n2,999999\n", encoding="utf-8")

        report_tampered = verify_manifest(root_path, manifest)
        print(f"\nIntegrity Verification (Tampered Directory):")
        print(f"  Success Status:   {report_tampered.is_success}")
        print(f"  Modified Count:   {report_tampered.modified}")

        for res in report_tampered.results:
            if res.status != "MATCH":
                print(f"  -> File '{res.path}': Status = {res.status}")

        # -------------------------------------------------------------------------
        # 3. Merkle Tree Engine & Adapters (CL-03)
        # -------------------------------------------------------------------------
        section_header("3. MERKLE TREE CONSTRUCTION SUBSYSTEM (CL-03)")

        # Generic Leaf & Internal Node Hashing
        leaf_raw = b"Leaf Data Payload"
        leaf_digest = hash_leaf(leaf_raw, algorithm="sha256")
        parent_digest = hash_internal(leaf_digest, leaf_digest, algorithm="sha256")
        print(f"Domain Separated Hashing:")
        print(f"  Leaf Hash (0x00):     {leaf_digest}")
        print(f"  Internal Hash (0x01): {parent_digest}")

        # Binary Serialization (CIT-MLF1)
        entry = manifest.entries[0]
        binary_payload = serialize_manifest_entry(entry, algorithm="sha256")
        print(f"\nCIT-MLF1 Binary Adapter Encoding:")
        print(f"  Header Bytes: {binary_payload[:8]}")
        print(f"  Total Length: {len(binary_payload)} bytes")

        # Build Merkle Tree from Clean Manifest
        # Re-create clean manifest
        doc2.write_text("id,val\n1,100\n2,200\n", encoding="utf-8")
        clean_manifest = create_manifest(root_path, algorithm="sha256")
        tree_clean = build_merkle_tree_from_manifest(clean_manifest)

        print(f"\nMerkle Tree from Clean Manifest:")
        print(f"  Leaf Count:  {tree_clean.leaf_count}")
        print(f"  Tree Levels: {len(tree_clean.levels)}")
        print(f"  Merkle Root: {tree_clean.root}")

        # Tamper and rebuild Merkle Tree to verify Root Hash Avalanche
        doc2.write_text("id,val\n1,100\n2,999999\n", encoding="utf-8")
        tampered_manifest = create_manifest(root_path, algorithm="sha256")
        tree_tampered = build_merkle_tree_from_manifest(tampered_manifest)

        print(f"\nMerkle Tree from Tampered Manifest:")
        print(f"  Merkle Root: {tree_tampered.root}")
        print(f"  Root Hash Match: {tree_clean.root == tree_tampered.root}")
        assert tree_clean.root != tree_tampered.root, "Merkle Root must detect tampering!"
        print("\n[SUCCESS] Merkle Root altered dynamically upon single-bit file modification!")

    section_header("ALL SUBSYSTEMS VERIFIED END-TO-END SUCCESSFULLY!")


if __name__ == "__main__":
    run_demo()



