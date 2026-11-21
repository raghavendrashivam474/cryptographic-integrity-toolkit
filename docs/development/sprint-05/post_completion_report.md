# Engineering Handover & Post-Completion Report: Sprint CL-05 — Unified CLI Integration

**To:** Senior Developer / Software Architect  
**From:** Lead Developer / Implementation Engineer  
**Date:** November 21, 2026  
**Project:** Cryptographic Integrity Toolkit (`cryptographic-integrity-toolkit`)  
**Sprint Identifier:** CL-05 / S05 — Unified CLI Integration  
**Target Release Tag:** `v-CL-05`  
**Baseline Tag:** `v-CL-04`  
**Target Branch:** `main`  
**Status:** **COMPLETE — READY FOR SENIOR ACCEPTANCE & TAG AUTHORIZATION**

---

## 1. Executive Overview

Sprint **CL-05** completes the core architectural roadmap of the Cryptographic Integrity Toolkit by delivering a unified, production-grade Command-Line Interface (CLI) binary executable named `cit`, alongside a backward-compatible `integrity` alias and module-level entry points (`python -m integrity_toolkit` and `python -m integrity_toolkit.cli`).

Prior to Sprint CL-05, toolkit subsystems (hashing engines, directory fingerprinting, manifest auditing, and Merkle tree/proof utilities) were accessible via Python library imports and dedicated demo scripts. Sprint CL-05 wraps all capabilities into a clean, zero-dependency, standardized subcommand hierarchy enforcing deterministic exit code semantics, strict input validation, and explicit root trust boundaries.

### Key Milestones Achieved
* **Executable Entry Points:** Configured `cit` and `integrity` binary entry points in `pyproject.toml` and package execution entry points via `__main__.py`.
* **Subcommand Suite Implemented:** Engineered handlers for `hash`, `fingerprint`, `verify`, and the nested `merkle` subcommand family (`build`, `root`, `prove`, `verify-proof`).
* **Explicit Root Security Gate:** Enforced mandatory `--root` parameter in `cit merkle verify-proof` to eliminate implicit root reliance and guarantee cryptographically sound inclusion proof validation.
* **Deterministic Exit Codes:** Formalized standardized exit codes across all subcommands (`0=SUCCESS`, `1=MISMATCH`, `2=USAGE_ERROR`, `3=NOT_FOUND`, `4=CORRUPT`, `5=SYSTEM_ERROR`).
* **Zero Regression & Full Compatibility:** All 220 pre-existing tests across sprints CL-00 through CL-04 pass without modification.
* **Expanded Test Coverage:** Added 6 CLI unit and end-to-end integration tests, raising total suite coverage to **226 passing tests** in ~3.50 seconds.
* **Strict Dependency Policy:** 100% Python Standard Library implementation (`argparse`, `sys`, `pathlib`, `json`, `typing`).

---

## 2. Technical Architecture & Implementation Details

### 2.1 Entry Point Routing & Package Structure
The CLI architecture uses a modular dispatcher pattern designed to isolate parser configuration from business logic handlers:

```
src/integrity_toolkit/
├── __main__.py                      # Enables `python -m integrity_toolkit`
└── cli/
    ├── __init__.py
    ├── __main__.py                  # Enables `python -m integrity_toolkit.cli`
    ├── main.py                      # Parser builder, global error trapping, dispatch logic
    └── handlers/
        ├── __init__.py
        ├── hash_cmd.py              # Handler for `cit hash`
        ├── fingerprint_cmd.py       # Handler for `cit fingerprint`
        ├── verify_cmd.py            # Handler for `cit verify`
        └── merkle_cmd.py            # Handlers for `cit merkle` subcommands
```

### 2.2 Implemented Subcommand Specifications

#### 1. File & Text Hashing (`cit hash`)
* **Signature:** `cit hash [--text TEXT | --file PATH] [--algorithm ALG]`
* **Implementation:** `hash_cmd.py` utilizes `hash_bytes` for inline text and `hash_stream` for streamed file hashing. Implements a mutually exclusive group requiring exactly one input source. Default algorithm: `sha256`.

#### 2. Directory & File Fingerprinting (`cit fingerprint`)
* **Signature:** `cit fingerprint <target> [--algorithm ALG] [-o OUTPUT]`
* **Implementation:** `fingerprint_cmd.py` handles single file targets by emitting a raw digest to `stdout` or file, and directory targets by traversing files using `discover_files` and writing an `IntegrityManifest` JSON file to `-o/--output`.

#### 3. Manifest Integrity Verification (`cit verify`)
* **Signature:** `cit verify <root> -m MANIFEST [--ignore-unexpected]`
* **Implementation:** `verify_cmd.py` loads the integrity manifest, executes `verify_manifest()`, and prints a detailed verification report (matching, modified, missing, unexpected files). Exits with `0` on full match or `1` on any mismatch.

#### 4. Merkle Tree Construction (`cit merkle build`)
* **Signature:** `cit merkle build <manifest> [-o OUTPUT]`
* **Implementation:** `merkle_cmd.py` (`handle_build`) loads the target manifest, builds a `MerkleTree` via manifest adapters, serializes the tree structure to JSON, and outputs to file or `stdout`.

#### 5. Merkle Root Inspection (`cit merkle root`)
* **Signature:** `cit merkle root <manifest>`
* **Implementation:** `merkle_cmd.py` (`handle_root`) builds the Merkle tree from the manifest and prints the hex-encoded root digest to `stdout`.

#### 6. Merkle Inclusion Proof Generation (`cit merkle prove`)
* **Signature:** `cit merkle prove <manifest> <relative_path> -o PROOF_FILE`
* **Implementation:** `merkle_cmd.py` (`handle_prove`) generates a portable JSON inclusion proof for the specified relative path entry within the manifest.

#### 7. Merkle Inclusion Proof Verification (`cit merkle verify-proof`)
* **Signature:** `cit merkle verify-proof <proof.json> --data DATA_PATH --root TRUSTED_ROOT`
* **Implementation:** `merkle_cmd.py` (`handle_verify_proof`) deserializes the proof payload, hashes the target file at `DATA_PATH`, constructs a `ManifestEntry`, and verifies the leaf path and hash against the trusted `--root` digest. Exits with `0` if valid, `1` if invalid.

---

## 3. Key Technical Challenges & Mitigation Strategies

During the implementation of Sprint CL-05, several structural, parser, and type-system challenges arose. The table below details how each problem was addressed:

| Challenge / Technical Issue | Root Cause | Engineering Mitigation & Solution |
| :--- | :--- | :--- |
| **1. CLI Exception Leakage & Unhandled Tracebacks** | Generic exceptions (`FileNotFoundError`, `InvalidProofError`, `json.JSONDecodeError`) bubbling up to `sys.stderr` with python tracebacks. | Implemented a centralized exception handler in `cli/main.py`. Mapped domain exceptions to standardized exit codes (`IntegrityError` $\rightarrow$ 1, `FileNotFoundError` $\rightarrow$ 3, `JSONDecodeError` $\rightarrow$ 4, generic `Exception` $\rightarrow$ 5) with clean single-line stderr error messages. |
| **2. Manifest Inclusion Proof Target Type Mismatch** | `verify_manifest_inclusion_proof()` requires a formal `ManifestEntry` instance, but CLI verification initially attempted to pass primitive file payloads. | Enhanced `merkle_cmd.py` to compute file size via standard file stat and calculate file digest using `hash_stream()`, constructing a validated `ManifestEntry` object before invoking proof verification. |
| **3. Execution Ambiguity (`cit` vs `python -m`)** | Discrepancy in execution context between installed console scripts (`cit`, `integrity`) and direct module execution (`python -m integrity_toolkit`). | Structured entry point forwarders in `src/integrity_toolkit/__main__.py` and `src/integrity_toolkit/cli/__main__.py` that invoke `cli.main.main()`, ensuring identical behavior across all execution contexts. |
| **4. Subcommand Argument Mutually Exclusive Validation** | `cit hash` required ensuring either `--text` or `--file` is supplied without allowing both or neither. | Utilized `argparse.add_mutually_exclusive_group(required=True)`, enforcing clean CLI parser error messages (Exit Code 2) upon invalid flag combinations. |
| **5. Cross-Platform Heredoc Escaping in Windows PowerShell** | Executing complex Python one-liners directly via `python -c` in PowerShell caused string escaping syntax errors during test file generation. | Solved by creating small temporary Python script writers using PowerShell `@'...'@` heredocs to generate test files cleanly and safely. |

---

## 4. Quality Assurance & Test Suite Verification

The full test suite was executed against Python 3.13.14. All pre-existing unit and integration tests passed without modification, confirming zero regressions.

```
================================ test session starts ================================
platform win32 -- Python 3.13.14, pytest-8.3.5, pluggy-1.6.0
rootdir: C:\Users\ragha\Projects\cryptographic-integrity-toolkit
configfile: pyproject.toml
collected 226 items

tests/integration/test_cli_workflows.py::test_cli_end_to_end_merkle_proof_workflow PASSED
tests/unit/test_cli_sprint05.py::test_cli_hash_file PASSED
tests/unit/test_cli_sprint05.py::test_cli_hash_file_nonexistent PASSED
tests/unit/test_cli_sprint05.py::test_cli_hash_file_and_text_mutually_exclusive PASSED
tests/unit/test_cli_sprint05.py::test_cli_merkle_no_subcommand PASSED
tests/unit/test_cli_sprint05.py::test_cli_merkle_lifecycle PASSED
[... 220 baseline tests PASSED ...]

================================ 226 passed in 3.47s ================================
```

### Coverage Distribution
* **CLI Unit Tests (`test_cli.py`, `test_cli_sprint02.py`, `test_cli_sprint05.py`):** 17 tests verifying parameter parsing, flag combinations, and failure modes.
* **CLI Workflow Integration (`test_cli_workflows.py`):** End-to-end integration test covering directory fingerprinting $\rightarrow$ Merkle build $\rightarrow$ Merkle root $\rightarrow$ Merkle prove $\rightarrow$ Merkle proof verification via the CLI dispatcher.
* **Subsystem Unit & Integration Tests (CL-00..CL-04):** 208 tests covering hashing, directory traversal, manifest generation, verifier operations, and generic Merkle trees/proofs.

---

## 5. Standardized Exit Code Specification

The CLI establishes the following exit codes across all commands:

| Exit Code | Constant Label | Description / Trigger Scenario |
| :---: | :--- | :--- |
| **0** | `SUCCESS` | Operational completion without errors or integrity mismatches. |
| **1** | `MISMATCH` | Integrity verification failure (modified/missing files) or invalid Merkle proof. |
| **2** | `USAGE_ERROR` | Command-line parameter validation failure or missing required arguments. |
| **3** | `NOT_FOUND` | Specified target file, manifest, or proof file path does not exist. |
| **4** | `CORRUPT` | Invalid JSON structure, malformed manifest format, or corrupt proof payload. |
| **5** | `SYSTEM_ERROR` | Unexpected internal exception, permission denied, or system I/O error. |

---

## 6. Sprint Deliverables & Documentation Inventory

The following documentation and engineering artifacts have been produced and verified under Sprint CL-05:

1. **Architecture & ADRs:**
   - `docs/development/sprint-05/S05-T00-baseline-report.md` (Pre-implementation baseline verification)
   - `docs/development/sprint-05/S05-T01-cli-architecture.md` (CLI Subsystem Architecture & Dispatch Design)
   - `docs/development/sprint-05/ADR-001-unified-cli-architecture.md` (Architectural Decision Record for CLI Dispatcher & Exit Codes)
2. **User & Developer Guides:**
   - `docs/development/sprint-05/CLI-REFERENCE.md` (Complete CLI Reference Guide with usage examples)
   - `README.md` (Updated primary project README with `cit` usage section)
3. **Completion & Handover Briefs:**
   - `docs/development/sprint-05/S05-HANDOVER-REPORT.md` (Engineering handover summary)
   - `docs/development/sprint-05/S05-completion-report.md` (Sprint completion report)

---

## 7. Handover & Recommendation

All acceptance criteria defined for **Sprint CL-05 (Unified CLI Integration)** have been satisfied:
1. `cit` and `integrity` binary executables configured and operational.
2. `python -m integrity_toolkit` and `python -m integrity_toolkit.cli` functional.
3. Subcommands (`hash`, `fingerprint`, `verify`, `merkle build`, `merkle root`, `merkle prove`, `merkle verify-proof`) implemented and verified.
4. Mandatory `--root` enforced for proof verification.
5. 100% test pass rate (226/226 tests) with zero runtime external dependencies.

**Recommendation:** The implementation is complete, fully tested, and documented. The codebase on branch `main` is recommended for immediate release authorization under release tag **`v-CL-05`**.