# S04-ADR-001: Merkle Inclusion Proof Subsystem Architecture

* **Status:** APPROVED
* **Date:** 2026-11-21
* **Author:** Senior Developer / Project Owner
* **Milestone:** CL-04 / Sprint S04
* **Applies To:** integrity_toolkit.merkle

---

## 1. Context and Problem Statement
In Sprint CL-03, the Cryptographic Integrity Toolkit gained the capability to construct deterministic Merkle trees from arbitrary byte streams and file manifests (CIT-MLF1). However, to verify that a specific record or file belongs to a dataset, a verifier currently needs access to the entire tree or dataset.

The objective of CL-04 is to enable **compact inclusion proofs**: allowing a verifier with only a target leaf payload and a trusted Merkle root to cryptographically verify leaf membership in O(log N) time and space without reconstructing the full tree.

---

## 2. Architectural Decisions

### 2.1. Proof Representation and Models
We introduce two dataclasses in integrity_toolkit.merkle.models:

1. **MerkleProofStep** (immutable dataclass):
   * operation: str — Must be one of "LEFT_SIBLING", "RIGHT_SIBLING", or "PROMOTE".
   * sibling_digest: Optional[str] — Lowercase hexadecimal digest string.
     * Mandatory for "LEFT_SIBLING" and "RIGHT_SIBLING".
     * Must be None for "PROMOTE".

2. **MerkleProof** (immutable dataclass):
   * ormat_version: int = 1
   * lgorithm: str — Canonical hash algorithm name (e.g. 'sha256').
   * leaf_index: int — Zero-based index of the target leaf (0 <= leaf_index < leaf_count).
   * leaf_count: int — Total leaves in the tree (N >= 1).
   * steps: 	uple[MerkleProofStep, ...] — Level-by-level evaluation steps.
   * claimed_root: Optional[str] — Optional declared root (convenience field; strictly untrusted).

### 2.2. Positional Derivation and Structural Validation
To prevent position-spoofing attacks, **the verifier must derive expected operations mathematically** from (current_index, current_level_width) and compare them against the proof's declared steps:

At level L (with width W and current node index i):
* If W == 1: Reached root (no further steps allowed).
* If i % 2 == 0:
  * If i + 1 < W: Expected operation is RIGHT_SIBLING with sibling index i + 1.
  * If i + 1 == W: Expected operation is PROMOTE (unpaired odd node promoted unchanged).
* If i % 2 == 1: Expected operation is LEFT_SIBLING with sibling index i - 1.

Next level index: i_next = i // 2.  
Next level width: W_next = (W + 1) // 2.

If a proof step's operation or presence fails to match these mathematical tree constraints, the verifier rejects the proof immediately by raising InvalidProofError.

### 2.3. Trusted Root Handling and Verification Result Boundary
* **Security Rule:** Verification must take an explicit, externally supplied expected_root parameter. The claimed_root stored in a proof payload is never trusted for verification.
* **Exception vs Boolean Boundary:**
  * **InvalidProofError / InvalidNodeDigestError / ValueError:** Raised when the proof object or arguments are structurally malformed, corrupted, out-of-bounds, or structurally inconsistent with tree geometry.
  * **True:** Returned when the proof is structurally valid AND the reconstructed root matches expected_root.
  * **False:** Returned when the proof is structurally valid, but the reconstructed root does NOT match expected_root (e.g., target payload was modified).

### 2.4. Odd-Node Promotion Handling
In accordance with CL-03 policy (S03-ADR-001), unpaired nodes in odd-width levels are promoted unchanged without hashing or duplication. Proof steps for promoted nodes use operation="PROMOTE" and sibling_digest=None. Reconstruction passes the intermediate digest through without modification.

### 2.5. Manifest Adapter Integration
File manifest inclusion proofs are provided via:
* generate_manifest_inclusion_proof(manifest, relative_path)
* erify_manifest_inclusion_proof(entry, proof, expected_root)

Manifest entry canonical serialization remains CIT-MLF1 from CL-03. File relative paths are normalized using 
ormalize_posix_path, and manifest entries are sorted by path to derive deterministic leaf indices.

### 2.6. Module Separation and Independence
* integrity_toolkit.merkle.proofs — Proof generation from MerkleTree.
* integrity_toolkit.merkle.verification — Standalone proof validation and root reconstruction.
* integrity_toolkit.merkle.proof_serialization — JSON serialization/deserialization.
* Generic Merkle proof modules (proofs, erification, proof_serialization) must **NEVER** import from integrity_toolkit.integrity.
* Only integrity_toolkit.merkle.adapters bridges manifest objects to Merkle proofs.

---

## 3. Consequences and Compatibility
* **Backward Compatibility:** Fully retains existing MerkleTree, hash_leaf, hash_internal, and uild_merkle_tree contracts.
* **Performance:** Proof generation reads existing 	ree.levels in O(log N) without rebuilding the tree. Proof verification executes in O(log N) time and O(log N) memory.
* **Dependencies:** 0 runtime external dependencies (standard library only).
