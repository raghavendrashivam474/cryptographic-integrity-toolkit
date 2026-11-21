# S05-T00 Baseline Inspection Report

**Project**: Cryptographic Integrity Toolkit  
**Milestone**: CL-05 (Unified CLI Integration)  
**Sprint**: S05  
**Date**: 2026-11-21  
**Author**: Engineering Team  

---

## 1. Repository & Git Baseline State

| Property | Recorded Value | Verification Status |
| :--- | :--- | :--- |
| **Repository Path** | C:\Users\ragha\Projects\cryptographic-integrity-toolkit | Confirmed |
| **Target Branch** | main | Confirmed (main) |
| **Starting Commit** | 8a795a7e549d571309501173e4e85e32789df647 | Confirmed matches brief 8a795a7 |
| **Starting Release Tag** | v-CL-04 | Confirmed (HEAD is at v-CL-04) |
| **Historical Release Tags** | v-CL-00, v-CL-01, v-CL-02, v-CL-03, v-CL-04 | Confirmed all present |
| **Working Tree Status** | Clean (no modified or uncommitted files) | Confirmed |

---

## 2. Environment & Test Baseline

| Property | Value |
| :--- | :--- |
| **Python Version** | Python 3.13.14 |
| **pytest Version** | pytest 8.3.5 |
| **Installed Package** | cryptographic-integrity-toolkit 0.0.1 (editable/local) |
| **Test Execution Command** | $env:PYTHONPATH = "src"; pytest -v --tb=short |
| **Total Test Count** | **220 passed** |
| **Execution Duration** | 2.45 seconds |
| **Test Baseline Status** | **100% Match with Historical Baseline (220/220)** |


---

## 3. Existing CLI & Entry-Point Architecture

### 3.1 Packaging Entry Points (`pyproject.toml`)

Currently registered script entry point:

```toml
[project.scripts]
integrity = "integrity_toolkit.cli.main:main"

```

### 3.2 File System Structure (`src/integrity_toolkit/cli/`)

* `src/integrity_toolkit/cli/__init__.py` (Package init)
* `src/integrity_toolkit/cli/main.py` (Main parser, handlers, and exit code management)

### 3.3 Existing Commands & Functionality

* `integrity --version` / `integrity --help`
* `integrity hash --text "..." [--algorithm sha256]` (Supports text string or stdin piping)
* `integrity fingerprint <target> [--algorithm sha256] [-o manifest.json]` (File or directory manifest generation)
* `integrity verify <root> -m manifest.json [--ignore-unexpected]` (Integrity verification against manifest)

### 3.4 Observed Exit Code Conventions

* **`0`**: Operational success.
* **`1`**: Integrity verification mismatch, file comparison failure, or general runtime error.
* **`2`**: Invalid argument, invalid manifest format, unsupported algorithm, or safety rejection.
* **`3`**: Filesystem access error or path missing error.

---

## 4. Integration Gaps & Target Product Plan (CL-05)

* **Console Script Entry Point:**
* Add `cit = "integrity_toolkit.cli.main:main"` alongside `integrity` alias for full backward compatibility.


* **Module Execution (`python -m`):**
* Add `src/integrity_toolkit/__main__.py` and `src/integrity_toolkit/cli/__main__.py` to allow direct invocation.


* **Command Hierarchy Extensions:**
* `hash`: Add `--file <path>` flag alongside `--text` and stdin support.
* `fingerprint`: Standardize `--output` / `-o` behavior and path normalization.
* `verify`: Retain exact verification behavior and status report output.


* **`merkle` (New subcommand tree):**
* `merkle build <manifest>` (Construct tree, report root, algorithm, leaf count)
* `merkle root <manifest>` (Report Merkle root commitment)
* `merkle prove <manifest> <relative_path> --output proof.json` (Generate versioned JSON proof)
* `merkle verify-proof <proof.json> --data <path> --root <trusted_root>` (Verify proof against trusted root)



---

## 5. Architectural Compatibility Risk Assessment

* **Risk 1:** Breaking existing `integrity` CLI tests.
* **Mitigation:** Ensure `build_parser()` / `create_parser()` and existing flag contracts (`--text`, `--algorithm`, `-o`, `-m`) remain identical.


* **Risk 2:** Modifying public API contracts of `crypto`, `integrity`, or `merkle` packages.
* **Mitigation:** The CLI strictly acts as an orchestrator/presentation layer over public APIs (`hash_text`, `hash_stream`, `create_manifest`, `save_manifest`, `verify_manifest`, `build_merkle_tree_from_manifest`, `generate_manifest_inclusion_proof`, `verify_manifest_inclusion_proof`, `serialize_proof_to_json`, `deserialize_proof_from_json`).


* **Risk 3:** Security vulnerability in proof verification by trusting proof artifact root.
* **Mitigation:** CLI `merkle verify-proof` explicitly requires `--root <trusted_root>` as an independent parameter.



---

## 6. Baseline Verification Sign-off

* [x] Repository location & commit verified (`8a795a7`).
* [x] All 5 historical tags (`v-CL-00` .. `v-CL-04`) present.
* [x] Test baseline verified (220 passing tests).
* [x] Existing CLI inspected and cataloged.
* [x] Zero uncommitted workspace changes.

> `S05-T00` completed successfully.

```