# Sprint CL-03 / S03 — Merkle Tree Construction Engine Implementation Plan

**Target Release:** -CL-03  
**Baseline Release:** -CL-02  
**Language:** Python 3.11+ (Standard Library Only)  

---

## Task Breakdown

### S03-T00: Repository Baseline Inspection
* **Status:** COMPLETE
* **Deliverable:** S03-T00-baseline-report.md (Commit 6568407)

### S03-T01: Architecture & Data-Contract Review
* **Status:** IN PROGRESS / AWAITING GATE APPROVAL
* **Deliverables:**
  * S03-ADR-001-merkle-tree-architecture.md
  * S03-implementation-plan.md
  * S03-merkle-format.md
  * S03-api-reference.md

### S03-T02: Core Merkle Hashing Primitives
* **Target Modules:** merkle/exceptions.py, merkle/hashing.py
* **Deliverables:**
  * MerkleError, EmptyTreeError, InvalidNodeDigestError, AdapterError
  * hash_leaf(data: bytes | bytearray, algorithm: str = "sha256") -> str
  * hash_internal(left_digest: str, right_digest: str, algorithm: str = "sha256") -> str
* **Tests:** 	ests/unit/test_merkle_hashing.py

### S03-T03: Merkle Tree Construction Engine
* **Target Modules:** merkle/models.py, merkle/tree.py
* **Deliverables:**
  * MerkleTree dataclass model (immutable)
  * uild_merkle_tree(leaves: Sequence[bytes | bytearray], algorithm: str = "sha256") -> MerkleTree
  * Level-by-level construction, odd-node promotion policy, empty-tree guard, single-leaf handling.
* **Tests:** 	ests/unit/test_merkle_tree.py

### S03-T04: File-Manifest Integration Adapter
* **Target Module:** merkle/adapters.py
* **Deliverables:**
  * serialize_manifest_entry(entry: ManifestEntry, algorithm: str) -> bytes (CIT-MLF1 binary encoding)
  * uild_merkle_tree_from_manifest(manifest: IntegrityManifest) -> MerkleTree
* **Tests:** 	ests/unit/test_merkle_adapters.py

### S03-T05: Integration and Regression Testing
* **Target Modules:** 	ests/integration/test_merkle_workflow.py
* **Deliverables:**
  * Cross-package non-leakage verification (ensure importing merkle.tree does not load integrity).
  * End-to-end manifest-to-Merkle verification.
  * Determinism & entry re-ordering invariants.

### S03-T06: Documentation & Demonstrations
* **Target Modules:** examples/merkle_tree_demo.py, examples/merkle_manifest_demo.py, S03-test-report.md, S03-completion-report.md

### S03-T07: Senior Review & Release Preparation
* **Deliverables:** Final release readiness report for -CL-03.
