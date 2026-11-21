# Cryptographic Merkle Specification (Format CIT-MLF1)

## 1. Domain Separation Strategy

To protect against second-preimage vulnerability (where an internal node preimage can be structured to impersonate a leaf payload or vice versa), every hash input is prefixed with an explicit domain-separation byte identifier before passing to the standard algorithm primitive ($H$).

### 1.1 Leaf Node Hashing

For leaf payload bytes $D$:

```text
hash_leaf(D, algo) = H(0x00 || D)

```

* **Prefix:** Single byte `0x00`.
* **Input:** Raw `bytes` or `bytearray` $D$.

### 1.2 Internal Parent Node Hashing

For left child hex digest $L$ and right child hex digest $R$:

```text
hash_internal(L, R, algo) = H(0x01 || bytes.fromhex(L) || bytes.fromhex(R))

```

* **Prefix:** Single byte `0x01`.
* **Inputs:** $L$ and $R$ decoded from hexadecimal string into raw byte arrays matching algorithm digest size (32 bytes for SHA-256, 64 bytes for SHA-512/BLAKE2b).

---

## 2. Tree Construction Rules

1. **Ordering Preservation:** Input leaf order $[D_0, D_1, \dots, D_{n-1}]$ must be strictly preserved.
2. **Level Construction:**
* **Level 0 leaves:** $N_0[i] = \text{hash\_leaf}(D_i)$ for $i \in [0, n-1]$.
* **Level $k+1$ from Level $k$:**
* For pair at indices $(2j, 2j+1)$: $N_{k+1}[j] = \text{hash\_internal}(N_k[2j], N_k[2j+1])$.
* **Odd-Node Promotion Policy:** If Level $k$ has odd length $M$, the last unpaired node $N_k[M-1]$ is promoted unchanged into $N_{k+1}$ as the final item of level $k+1$.




3. **Single Leaf:** If $n = 1$, root is $N_0[0] = \text{hash\_leaf}(D_0)$, and `levels = ((leaf_hash,),)`.
4. **Empty Input:** $n = 0$ raises `EmptyTreeError`.

---

## 3. Canonical Manifest Leaf Format (CIT-MLF1)

When constructing a Merkle Tree from an `IntegrityManifest`, entries are sorted deterministically by normalized POSIX `entry.path`. Each entry is serialized into a byte payload using format `CIT-MLF1`:

```text
+-----------------------------------------------------------------------+
| Magic Header (8 bytes ASCII): "CIT-MLF1"                              |
+-----------------------------------------------------------------------+
| Path Length (4 bytes, uint32 big-endian): P_len                       |
+-----------------------------------------------------------------------+
| Path Bytes (P_len bytes UTF-8): entry.path                            |
+-----------------------------------------------------------------------+
| Algorithm Name Length (2 bytes, uint16 big-endian): A_len             |
+-----------------------------------------------------------------------+
| Algorithm Name Bytes (A_len bytes UTF-8): manifest.algorithm          |
+-----------------------------------------------------------------------+
| File Size (8 bytes, uint64 big-endian): entry.size                    |
+-----------------------------------------------------------------------+
| Digest Raw Bytes (D_len bytes): bytes.fromhex(entry.digest)           |
+-----------------------------------------------------------------------+

```

``````markdown
# Cryptographic Merkle Specification (Format CIT-MLF1)

## 1. Domain Separation Strategy

To protect against second-preimage vulnerability (where an internal node preimage can be structured to impersonate a leaf payload or vice versa), every hash input is prefixed with an explicit domain-separation byte identifier before passing to the standard algorithm primitive ($H$).

### 1.1 Leaf Node Hashing

For leaf payload bytes $D$:

```text
hash_leaf(D, algo) = H(0x00 || D)

```

* **Prefix:** Single byte `0x00`.
* **Input:** Raw `bytes` or `bytearray` $D$.

### 1.2 Internal Parent Node Hashing

For left child hex digest $L$ and right child hex digest $R$:

```text
hash_internal(L, R, algo) = H(0x01 || bytes.fromhex(L) || bytes.fromhex(R))

```

* **Prefix:** Single byte `0x01`.
* **Inputs:** $L$ and $R$ decoded from hexadecimal string into raw byte arrays matching algorithm digest size (32 bytes for SHA-256, 64 bytes for SHA-512/BLAKE2b).

---

## 2. Tree Construction Rules

1. **Ordering Preservation:** Input leaf order $[D_0, D_1, \dots, D_{n-1}]$ must be strictly preserved.
2. **Level Construction:**
* **Level 0 leaves:** $N_0[i] = \text{hash\_leaf}(D_i)$ for $i \in [0, n-1]$.
* **Level $k+1$ from Level $k$:**
* For pair at indices $(2j, 2j+1)$: $N_{k+1}[j] = \text{hash\_internal}(N_k[2j], N_k[2j+1])$.
* **Odd-Node Promotion Policy:** If Level $k$ has odd length $M$, the last unpaired node $N_k[M-1]$ is promoted unchanged into $N_{k+1}$ as the final item of level $k+1$.




3. **Single Leaf:** If $n = 1$, root is $N_0[0] = \text{hash\_leaf}(D_0)$, and `levels = ((leaf_hash,),)`.
4. **Empty Input:** $n = 0$ raises `EmptyTreeError`.

---

## 3. Canonical Manifest Leaf Format (CIT-MLF1)

When constructing a Merkle Tree from an `IntegrityManifest`, entries are sorted deterministically by normalized POSIX `entry.path`. Each entry is serialized into a byte payload using format `CIT-MLF1`:

```text
+-----------------------------------------------------------------------+
| Magic Header (8 bytes ASCII): "CIT-MLF1"                              |
+-----------------------------------------------------------------------+
| Path Length (4 bytes, uint32 big-endian): P_len                       |
+-----------------------------------------------------------------------+
| Path Bytes (P_len bytes UTF-8): entry.path                            |
+-----------------------------------------------------------------------+
| Algorithm Name Length (2 bytes, uint16 big-endian): A_len             |
+-----------------------------------------------------------------------+
| Algorithm Name Bytes (A_len bytes UTF-8): manifest.algorithm          |
+-----------------------------------------------------------------------+
| File Size (8 bytes, uint64 big-endian): entry.size                    |
+-----------------------------------------------------------------------+
| Digest Raw Bytes (D_len bytes): bytes.fromhex(entry.digest)           |
+-----------------------------------------------------------------------+

```

```