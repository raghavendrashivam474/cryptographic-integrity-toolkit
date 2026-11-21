# Architectural Decision Record (ADR-001): Unified CLI Integration Architecture

**Status**: Approved
**Date**: 2026-11-21
**Context**: Milestone CL-05 / Sprint S05
**Deciders**: Lead Architect & Engineering Team

---

## Context and Problem Statement

Prior milestones (CL-00 through CL-04) established isolated cryptographic capabilities:
- Stream and byte hashing (`crypto`)
- File fingerprinting, directory traversal, manifest management, and integrity verification (`integrity`)
- Domain-separated Merkle tree construction, inclusion proof generation, versioned serialization (`CIT-MLF1`), and verification (`merkle`)

While basic CLI commands (`hash`, `fingerprint`, `verify`) were implemented in Sprint 02 under the executable `integrity`, the Merkle engine and advanced file stream hashing capabilities were not accessible via the CLI. Furthermore, the product required a unified executable name (`cit`).

We needed an architectural design that:
1. Unifies all capabilities under a cohesive `cit` command hierarchy (`hash`, `fingerprint`, `verify`, `merkle`).
2. Preserves 100% backward compatibility with existing tests relying on `integrity` command lines and `integrity_toolkit.cli.main` helper functions (`build_parser`, `create_parser`).
3. Retains Python Standard Library only runtime dependency policy.
4. Enforces strict cryptographic isolation (the CLI never reimplements cryptographic or hashing logic).

---

## Decision Drivers

- **Zero-Regression Policy**: All 220 existing unit and integration tests must pass without modification.
- **Security Requirement**: Proof verification CLI commands must require explicit trusted roots (`--root`) to prevent trust-on-first-use vulnerabilities from untrusted JSON artifacts.
- **Maintainability**: CLI handlers should be modularized to avoid an unmaintainable monolith in `main.py`.
- **Executable Alias Policy**: Both `cit` and `integrity` entry points must be supported simultaneously.

---

## Considered Options

1. **Option A: Reimplement CLI using Click / Typer**
   - *Pros*: Cleaner decorator syntax, automatic sub-command routing.
   - *Cons*: Violates the **Python Standard Library only** runtime dependency policy (§11 of project brief).
   - *Outcome*: Rejected.

2. **Option B: Monolithic extension of `src/integrity_toolkit/cli/main.py`**
   - *Pros*: Simple, all logic in one file.
   - *Cons*: Exceeds 500+ lines, difficult to maintain, high risk of regression.
   - *Outcome*: Rejected.

3. **Option C: Modular `argparse` Subcommand Architecture with Entry Point Dual-Registration (Chosen)**
   - *Pros*: Uses Standard Library `argparse`, modularizes command execution into `cli/handlers/`, preserves existing public entry functions (`build_parser`, `create_parser`, `main`), adds `cit` executable entry point while retaining `integrity`.
   - *Outcome*: **Selected**.

---

## Architectural Details of Selected Decision

### 1. Dual Entry Point Mapping (`pyproject.toml`)

```toml
[project.scripts]
cit = "integrity_toolkit.cli.main:main"
integrity = "integrity_toolkit.cli.main:main"

```

### 2. Standardized Exit Code Mapping

* **`0`**: Success (Operation completed, or verification passed).
* **`1`**: Integrity or proof verification failure (Data mismatch).
* **`2`**: CLI argument error, invalid manifest/proof format, or unsupported algorithm.
* **`3`**: File access or filesystem path error.

### 3. Proof Verification Trust Boundary

The `merkle verify-proof` handler accepts `--root TRUSTED_ROOT`. It deliberately ignores any `claimed_root` field embedded inside the proof JSON artifact, satisfying security requirements against root spoofing attacks.

---

## Consequences

### Positive

* Full feature set accessible through a single unified executable (`cit`).
* Strict preservation of existing unit test baseline (220/220 passing).
* Clean separation between argument parsing and underlying cryptographic APIs.
* Zero external dependencies introduced.

### Negative / Risks

* Requires maintaining subcommand dispatch logic across handler modules, requiring comprehensive integration testing (addressed in `S05-T06`).

```