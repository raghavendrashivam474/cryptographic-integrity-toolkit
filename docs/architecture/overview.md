# Architecture Overview

**Project:** Cryptographic Integrity Toolkit  
**Sprint ID:** CL-00 / S00  
**Target Release:** `v0.0.1` — Development Foundation  

---

## 1. System Design Principles

1. **Strict Subpackage Separation:** Application features are isolated into discrete domain packages (`crypto`, `merkle`, `cli`).
2. **Standard Library Primacy:** Standard Python libraries (such as `hashlib` and `argparse`) are prioritized for core mechanisms to eliminate external security dependencies.
3. **Explicit Dependency Flow:** Unidirectional layer imports prevent circular dependencies across modules.
4. **Extensibility & Future-Proofing:** Interfaces and CLI routing are structured for incremental feature addition across sprint milestones.

---

## 2. Package Organization & Module Boundaries

```text
src/integrity_toolkit/
│
├── init.py # Package version (version = "0.0.1")
│
├── crypto/ # Module Boundary 1: Cryptographic Primitives
│ └── init.py # (Reserved for Sprint 01 - Hash Engine)
│
├── merkle/ # Module Boundary 2: Merkle Tree & Inclusion Proofs
│ └── init.py # (Reserved for Sprint 03/04 - Merkle Engine)
│
└── cli/ # Module Boundary 3: User Interface Layer
├── init.py
└── main.py # Argument parsing & subcommand dispatcher
```

---

## 3. Subpackage Responsibilities

### 3.1 `integrity_toolkit.crypto` (Sprint 01+)
- **Scope:** Hashing engine, file fingerprinting, cryptographic checksum generation, and payload integrity checking.
- **Constraints:** Zero dependencies on CLI or Merkle modules. Serves as a pure cryptographic primitive library.

### 3.2 `integrity_toolkit.merkle` (Sprint 03+)
- **Scope:** Leaf hashing, Merkle tree node construction, audit path / inclusion proof generation, and root signature verification.
- **Dependencies:** Imports primitives from `crypto` for hashing; no dependency on `cli`.

### 3.3 `integrity_toolkit.cli` (Sprint 00 / Sprint 06)
- **Scope:** Entry point parsing, CLI argument routing, output formatting, and top-level error handling.
- **Dependencies:** May import from `crypto` and `merkle` to bridge commands to business logic.

---

## 4. Layer Dependency Direction

```text
[ CLI Layer ] (integrity_toolkit.cli)
      │
      ▼
[ Merkle Engine ] (integrity_toolkit.merkle)
      │
      ▼
[ Cryptographic Engine ] (integrity_toolkit.crypto)
```

**Rule**: Dependencies flow strictly downward. Lower-level cryptographic primitives must never depend on higher-level CLI or Merkle constructs.