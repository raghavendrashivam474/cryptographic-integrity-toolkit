# ADR-001: Merkle Tree Construction Engine Architecture

* **Status:** PROPOSED (Pending Senior Developer Approval)
* **Date:** March 2025
* **Author:** Senior Developer / Cryptographic Software Engineer
* **Sprint:** CL-03 / S03
* **Context:** Cryptographic Integrity Toolkit

---

## 1. Context and Problem Statement

The Cryptographic Integrity Toolkit currently supports single-file fingerprinting, directory traversal, and JSON file-integrity manifests (CL-02). To prepare for cryptographic inclusion proofs (CL-04), the system requires a reusable, deterministic **Merkle Tree Construction Engine**.

Key architectural requirements:
1. **Generic Usability:** The Merkle engine must accept arbitrary byte payloads and construct a tree independent of file manifests or directory structures.
2. **Strict Package Boundaries:** The merkle subsystem must depend *only* on the lower-level crypto subsystem. It must NOT import or depend on integrity.
3. **Manifest Integration Adapter:** Manifest integration must live in a separate adapter module (merkle.adapters) that translates IntegrityManifest records into canonical byte payloads.
4. **Cryptographic Security:** Leaf hashing and internal-node hashing must implement domain separation to prevent second-preimage attacks.
5. **Determinism:** Given identical ordered inputs and algorithm, the engine must produce identical Merkle roots on all operating systems.

---

## 2. Decision Outcomes and Architectural Principles

### Decision 1: Domain Separation
* **Leaves:** Prepend 0x00 (1 byte) to payload bytes before hashing:
  cls\text{LeafHash}(D) = H(0x00 \parallel D)cls
* **Internal Nodes:** Prepend 0x01 (1 byte) to raw byte concatenation of left and right child digests:
  cls\text{InternalHash}(L, R) = H(0x01 \parallel \text{bytes}(L) \parallel \text{bytes}(R))cls
  *Child digests $ and $ are hex strings; they must be decoded to raw bytes ($\text{bytes.fromhex}$) before concatenation.*

### Decision 2: Odd-Node Promotion Policy
When a tree level contains an odd number of nodes ( > 1$ and  \pmod 2 \neq 0$), the final unpaired node is **promoted unchanged** to the next tree level. It is *not* duplicated or combined with itself ((X, X)$ is rejected).

**Example (3 leaves)**:

```text
Level 0: L0 L1 L2
\ / | (promoted)
Level 1: N(L0,L1) L2
\ /
Level 2: Root(N, L2)
```

### Decision 3: Single-Leaf and Empty-Tree Rules
* **Single Leaf:** Root equals the leaf hash: (0x00 \parallel D)$.
* **Empty Collection:** Constructing a tree from zero leaves raises EmptyTreeError (a subclass of MerkleError and ValueError).

### Decision 4: Immutable Tree Model (MerkleTree)
The result of a tree construction is an immutable dataclass MerkleTree:
```python
@dataclass(frozen=True)
class MerkleTree:
    algorithm: str
    leaf_count: int
    root: str
    levels: tuple[tuple[str, ...], ...]
```

levels stores all levels from leaf level (levels[0]) up to root level (levels[-1] == (root,)). This guarantees structural completeness for future proof generation in CL-04.

### Decision 5: Manifest Leaf Serialization Standard (Binary Length-Prefixed)

To convert a `ManifestEntry` into a Merkle leaf byte payload deterministically across platforms, merkle.adapters encodes entries using a versioned length-prefixed binary format:

Format Identifier: CIT-MLF1 (8 bytes ASCII: 0x43 0x49 0x54 0x2D 0x4D 0x4C 0x46 0x31)

Structure:

FORMAT_MAGIC: 8 bytes (CIT-MLF1)
PATH_LENGTH: 4 bytes uint32 big-endian (>I)
PATH_BYTES: UTF-8 encoded normalized relative POSIX path
ALGO_LENGTH: 2 bytes uint16 big-endian (>H)
ALGO_BYTES: UTF-8 encoded canonical algorithm name (lowercase, e.g. sha256)
FILE_SIZE: 8 bytes uint64 big-endian (>Q)
DIGEST_BYTES: Raw bytes converted from entry hexadecimal digest string (bytes.fromhex(entry.digest))
Manifest entries are sorted by entry.path before serialization.

3. Package Structure and Import Rules
text

src/integrity_toolkit/merkle/
├── __init__.py        # Public API exports
├── models.py          # MerkleTree dataclass
├── hashing.py         # hash_leaf, hash_internal (domain-separated primitives)
├── tree.py            # build_merkle_tree (generic algorithm)
├── adapters.py        # build_merkle_tree_from_manifest, serialize_manifest_entry
└── exceptions.py      # MerkleError exception hierarchy
Import Restrictions:

merkle.hashing, merkle.tree, merkle.models MAY import integrity_toolkit.crypto.
merkle.hashing, merkle.tree, merkle.models MUST NOT import integrity_toolkit.integrity.
merkle.adapters MAY import both integrity_toolkit.merkle and integrity_toolkit.integrity.
4. Exception Hierarchy
text

CryptoError (from crypto.exceptions)
    └── ...
IntegrityError (from integrity.exceptions)
    └── ...

MerkleError(Exception)
    ├── EmptyTreeError(MerkleError, ValueError)
    ├── InvalidNodeDigestError(MerkleError, ValueError)
    └── AdapterError(MerkleError, ValueError)
5. Security Implications
Second-Preimage Resistance: Domain separation (0x00 vs 0x01) guarantees that internal node preimage concatenated raw bytes cannot be crafted to match a leaf data payload.
Digest Verification: hash_internal validates that left and right child digests are valid hex strings matching the expected byte length for the algorithm (e.g. 64 hex chars for SHA-256).
Platform Independence: Big-endian integer encoding and POSIX path normalization guarantee identical binary representations across Linux, Windows, and macOS.
