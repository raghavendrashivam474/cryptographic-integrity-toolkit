# Cryptographic Hash Engine Architecture

**Subsystem:** `integrity_toolkit.crypto`  
**Sprint:** CL-01 / S01  
**Status:** Implemented & Verified  

---

## 1. System Responsibilities & Boundaries

The Cryptographic Hash Engine provides the foundational data-integrity capabilities for the Toolkit.
Per the system design principles in `docs/architecture/overview.md`, the `crypto` subpackage operates as a pure cryptographic primitive library with **zero dependencies** on higher-level modules (`merkle` or `cli`).

### Primary Responsibilities:
- Centralized algorithm registry with name normalization and metadata access.
- In-memory hashing of byte arrays (`bytes` / `bytearray`) and string text (with explicit UTF-8 encoding).
- High-throughput, chunked streaming hashing of arbitrary binary stream inputs (`io.BytesIO`, file streams, stdin).
- Standardized exception hierarchy for cryptographic operations.
- Uniform, deterministic hexadecimal digest generation.

---

## 2. Supported Cryptographic Hash Algorithms

The registry strictly manages supported algorithm primitives using Python's standard library `hashlib`.

| Identifier | Digest Size | Standard Reference | Operational Purpose |
|------------|-------------|-------------------|---------------------|
| `sha256`   | 256 bits (32 bytes) | NIST FIPS 180-4 | Primary integrity hashing & default algorithm |
| `sha512`   | 512 bits (64 bytes) | NIST FIPS 180-4 | High-security 512-bit digest alternative |
| `blake2b`  | 512 bits (64 bytes) | RFC 7693 | High-performance 64-byte digest alternative |

### Algorithm Identifier Normalization:
Algorithm lookup is case-insensitive and strips spaces, hyphens, and underscores:
- `"SHA-256"`, `"SHA_256"`, `"SHA256"`, `" sha256 "` $\rightarrow$ `"sha256"`
- `"BLAKE-2B"`, `"BLAKE2b"`, `"blake_2b"` $\rightarrow$ `"blake2b"`


---

## 3. Submodule Layout & Interface Design

```text
src/integrity_toolkit/crypto/
│
├── __init__.py         # Public exports (hash_bytes, hash_stream, exceptions)
├── algorithms.py       # Algorithm registry, specification, and hasher factory
├── engine.py           # Core in-memory byte and text hashing engine
├── streaming.py        # Chunked stream hashing engine
└── exceptions.py       # Crypto subpackage exception hierarchy

```

**Unidirectional Data Flow:**

```text
[ Calling Client / Merkle Subsystem / CLI ]
                      │
                      ▼
        [ Public Crypto Package API ]
         (integrity_toolkit.crypto)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
[ In-Memory Engine ]      [ Streaming Engine ]
   (engine.py)              (streaming.py)
        │                           │
        └─────────────┬─────────────┘
                      ▼
         [ Algorithm Registry ]
            (algorithms.py)
                      │
                      ▼
          [ Python stdlib hashlib ]

```

---

## 4. Streaming Hash Architecture

To process large files or incoming network streams without loading whole payloads into RAM, `hash_stream()` processes input in chunked buffers.

**Design Guarantees:**

* **Constant Memory Footprint:** Allocates memory proportional only to `chunk_size` (default: 64 KiB / 65,536 bytes).
* **Stream Ownership Preserved:** Streams are never closed or seeked by the hash engine.
* **Non-Seekable Compatibility:** Fully compatible with pipes, sockets, and non-seekable file descriptors.

---

## 5. Exception Hierarchy

All cryptographic errors derive from `CryptoError`:

```text
CryptoError (Base Exception)
├── UnsupportedAlgorithmError (ValueError)  — Requested algorithm not in registry
├── InvalidInputError (TypeError)          — Non-bytes/non-string passed to engine
├── InvalidChunkSizeError (ValueError)     — Chunk size <= 0 or non-integer
└── StreamReadError (IOError)               — Underlying I/O read failure during streaming

```

---

## 6. Public API Usage Summary

```python
from integrity_toolkit.crypto import (
    hash_bytes,
    hash_text,
    hash_stream,
    get_supported_algorithms,
)

# 1. Byte Hashing
digest = hash_bytes(b"Hello World", algorithm="sha256")

# 2. Text Hashing (explicit UTF-8)
digest = hash_text("Hello World", algorithm="sha512")

# 3. Stream Hashing
with open("data.bin", "rb") as f:
    digest = hash_stream(f, algorithm="blake2b", chunk_size=65536)

# 4. Algorithm Discovery
supported = get_supported_algorithms()  # ['sha256', 'sha512', 'blake2b']

```

```