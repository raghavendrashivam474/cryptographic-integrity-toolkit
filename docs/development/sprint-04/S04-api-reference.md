# Sprint CL-04 / S04 — Public API Reference

## 1. Proof Models (integrity_toolkit.merkle.models)

### ProofOperation (Enum)
* LEFT_SIBLING = "LEFT_SIBLING"
* RIGHT_SIBLING = "RIGHT_SIBLING"
* PROMOTE = "PROMOTE"

### MerkleProofStep (dataclass, frozen)
* operation: str — Operation identifier (LEFT_SIBLING, RIGHT_SIBLING, or PROMOTE).
* sibling_digest: Optional[str] — Lowercase hex string of sibling (must be None for PROMOTE).

### MerkleProof (dataclass, frozen)
* lgorithm: str — Canonical algorithm name.
* leaf_index: int — Zero-based index of target leaf.
* leaf_count: int — Total leaves in original tree.
* steps: tuple[MerkleProofStep, ...] — Level evaluation steps.
* ormat_version: int = 1 — Version integer.
* claimed_root: Optional[str] = None — Optional declared root (strictly untrusted).

---

## 2. Proof Generation (integrity_toolkit.merkle.proofs)

### generate_inclusion_proof(tree: MerkleTree, leaf_index: int) -> MerkleProof
Generates a compact Merkle inclusion proof for a target leaf index from an existing MerkleTree object in O(log N) time.

---

## 3. Proof Verification (integrity_toolkit.merkle.verification)

### erify_inclusion_proof(leaf_data: bytes | bytearray, proof: MerkleProof, expected_root: str) -> bool
Verifies an inclusion proof against an independently supplied trusted expected_root. Reconstructs the root level by level, validating structural tree geometry before hashing.

---

## 4. Manifest Adapter Proofs (integrity_toolkit.merkle.adapters)

### generate_manifest_inclusion_proof(manifest: IntegrityManifest, relative_path: str) -> MerkleProof
Generates a Merkle inclusion proof for a file path within an IntegrityManifest.

### erify_manifest_inclusion_proof(entry: ManifestEntry, proof: MerkleProof, expected_root: str) -> bool
Verifies a manifest entry inclusion proof against a trusted Merkle root.

---

## 5. Serialization (integrity_toolkit.merkle.proof_serialization)

* serialize_proof_to_dict(proof: MerkleProof) -> dict
* serialize_proof_to_json(proof: MerkleProof, indent: Optional[int] = 2) -> str
* deserialize_proof_from_dict(data: dict) -> MerkleProof
* deserialize_proof_from_json(json_str: str) -> MerkleProof
"@

 = @"
# Sprint CL-04 / S04 — Test Report

## Summary
* **Baseline Tests (v-CL-03):** 182 / 182 passing.
* **New CL-04 Tests:** 38 passing.
* **Total Suite:** 220 / 220 passing (100% pass rate).
* **Execution Time:** ~1.87 seconds.

## Breakdown of New Test Files
1. 	ests/unit/test_merkle_proof_models.py — 10 tests (Model field validation, operation rules, index bounds).
2. 	ests/unit/test_merkle_proof_generation.py — 6 tests (1, 2, 3, 5-leaf trees, odd node promotion, index errors).
3. 	ests/unit/test_merkle_proof_verification.py — 8 tests (Verification success, tamper detection, wrong root, multi-algorithm).
4. 	ests/unit/test_merkle_manifest_proofs.py — 4 tests (Manifest entry proofs, path normalization, tampering).
5. 	ests/unit/test_merkle_proof_serialization.py — 5 tests (JSON round-trip, schema validation, malformed input).
6. 	ests/integration/test_merkle_proof_workflow.py — 5 tests (End-to-end lifecycle, manifest workflow, subsystem architectural isolation).
