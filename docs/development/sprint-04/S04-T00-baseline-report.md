# Sprint CL-04 / S04 — Baseline Report (T00)
**Project:** Cryptographic Integrity Toolkit
**Sprint:** CL-04 / S04 — Merkle Inclusion Proofs
**Date:** 2026-11-21
**Baseline Tag:** v-CL-03
**Commit Hash:** 52a9936 (feat(merkle): add end-to-end subsystem integration demo)

---

## 1. Repository & Environment Status
* **Branch:** main
* **Remote:** origin/main (up-to-date)
* **Working Tree:** Clean
* **Python Version:** 3.13.14
* **Test Runner:** pytest 8.3.5
* **Platform:** Windows 10 (win32)
* **Dependency Status:** Standard library only. No external runtime dependencies introduced.

---

## 2. Baseline Test Verification
* **Total Tests:** 182
* **Passed:** 182
* **Failures:** 0
* **Regressions:** None detected.
* **Existing Milestones Verified:** CL-00 (Foundation), CL-01 (Crypto), CL-02 (Integrity), CL-03 (Merkle Tree).

---

## 3. Merkle Subsystem Architecture Summary (from S03)
The existing integrity_toolkit.merkle package is immutable, well-tested, and follows strict domain separation.

### 3.1. Hashing Primitives
* **Leaf Hashing:** `H(0x00 || payload)`
* **Internal Hashing:** `H(0x01 || left_digest_bytes || right_digest_bytes)`
* **Algorithm Support:** SHA-256, SHA-512, BLAKE2b.

### 3.2. Tree Construction
* **Method:** `build_merkle_tree(leaves, algorithm)`
* **Model:** `MerkleTree` (immutable dataclass) containing:
    * `algorithm`: Canonical algorithm name.
    * `leaf_count`: Number of leaves.
    * `root`: Final root digest.
    * `levels`: Tuple of tuples representing every level of the tree (0 to root).

### 3.3. Odd-Node Policy
* **Promotion:** Unpaired nodes are promoted to the next level *unchanged* (not duplicated/hashed with themselves). This is a strict rule to preserve.

### 3.4. Manifest Integration
* **Format:** CIT-MLF1 (Canonical binary encoding).
* **Ordering:** Deterministic sorting by normalized POSIX path.
* **Adapter:** `build_merkle_tree_from_manifest` bridges `IntegrityManifest` to `MerkleTree`.

---

## 4. Identified Risks & Observations for CL-04
1. **Proof Generation Complexity:** Since the tree is immutable and stores all `levels`, proof generation can be implemented without re-hashing, but it requires careful index tracking across levels.
2. **Odd-Node Verification:** The verifier must strictly derive the expected sibling/promotion operation from the tree structure (leaf index and level width) rather than blindly trusting the proof object.
3. **Manifest Path Normalization:** The proof system must use the same path normalization (POSIX style) as the S03 adapter to ensure consistency.
4. **Dependency Direction:** Generic proof modules must remain independent of the `Integrity` subsystem. Manifest proofs must use the adapter layer.

---

## 5. Conclusion
The repository is in a stable state at v-CL-03. All 182 tests are passing, and the Merkle tree engine is correctly implemented with domain separation and odd-node promotion. The baseline is ready for Sprint CL-04 development.

**Recommendation:** Proceed to S04-T01 (Architecture & Contract Design) to finalize the proof model, verification logic, and serialization format before implementation.
