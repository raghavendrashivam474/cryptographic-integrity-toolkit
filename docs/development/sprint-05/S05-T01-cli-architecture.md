# S05-T01 Unified CLI Architecture Specification

**Project**: Cryptographic Integrity Toolkit
**Milestone**: CL-05
**Sprint**: S05
**Date**: 2026-11-21

---

## 1. Overview & Purpose

The objective of milestone CL-05 is to provide a single, cohesive command-line product interface (`cit`) while preserving complete backward compatibility with the existing `integrity` CLI executable and public Python APIs.

The CLI acts purely as an **orchestration and presentation boundary**. All business logic (hashing, directory traversal, manifest persistence, Merkle tree construction, proof generation, and verification) continues to reside entirely in the underlying public core packages (`integrity_toolkit.crypto`, `integrity_toolkit.integrity`, `integrity_toolkit.merkle`).

---

## 2. Command Hierarchy Specification

```text
cit [GLOBAL OPTIONS]
│
├── --version / --help
│
├── hash [--text TEXT | --file PATH] [--algorithm ALG]
│
├── fingerprint <target> [--algorithm ALG] [-o OUTPUT]
│
├── verify <root> -m MANIFEST [--ignore-unexpected]
│
└── merkle
├── build <manifest> [-o OUTPUT]
├── root <manifest>
├── prove <manifest> <relative_path> -o PROOF_FILE
└── verify-proof <proof.json> --data DATA_PATH --root TRUSTED_ROOT
```

### 2.1 Global Options
- `-h`, `--help`: Show context-aware command and subcommand help.
- `--version`: Print product version string (`integrity 0.0.1` / `cit 0.0.1`).

### 2.2 `hash` Subcommand
- **Arguments**:
  - `--text TEXT`: Text string to hash.
  - `--file PATH`: Path to a file on disk to stream-hash.
  - `--algorithm ALG`: Hashing algorithm (`sha256` default, `sha512`, `blake2b`).
- **Input Rule**: If neither `--text` nor `--file` is supplied, reads from `sys.stdin`.
- **API Mapping**:
  - String input: `crypto.hash_text()`
  - File input: `crypto.hash_stream()` via `open(path, "rb")`
  - Stdin input: `crypto.hash_stream()` via `sys.stdin.buffer`

### 2.3 `fingerprint` Subcommand
- **Arguments**:
  - `target`: File or directory path.
  - `--algorithm ALG`: Hashing algorithm (`sha256` default).
  - `-o`, `--output OUTPUT`: Required when `target` is a directory.
- **API Mapping**:
  - File: `integrity.fingerprint_file()`
  - Directory: `integrity.create_manifest()` and `integrity.save_manifest()`

### 2.4 `verify` Subcommand
- **Arguments**:
  - `root`: Root directory path.
  - `-m`, `--manifest MANIFEST`: Path to manifest JSON.
  - `--ignore-unexpected`: Flag to ignore unmanifested disk files.
- **API Mapping**: `integrity.verify_manifest()`

### 2.5 `merkle` Subcommand Group

#### 2.5.1 `merkle build`
- **Arguments**: `manifest` (Path to manifest JSON), `[-o OUTPUT]` (Optional output path for tree JSON artifact).
- **Behavior**: Loads manifest via `integrity.load_manifest()`, constructs tree via `merkle.build_merkle_tree_from_manifest()`, outputs summary (Root, Algorithm, Leaf count).

#### 2.5.2 `merkle root`
- **Arguments**: `manifest` (Path to manifest JSON).
- **Behavior**: Loads manifest, computes Merkle tree root commitment, prints root hash, algorithm, and leaf count to standard output.

#### 2.5.3 `merkle prove`
- **Arguments**: `manifest` (Path to manifest), `relative_path` (Normalized target path in manifest), `-o`, `--output PROOF_FILE` (Output JSON destination).
- **Behavior**: Loads manifest, invokes `merkle.generate_manifest_inclusion_proof()`, serializes proof to versioned JSON via `merkle.serialize_proof_to_json()`, writes to disk.

#### 2.5.4 `merkle verify-proof`
- **Arguments**: `proof` (Path to proof JSON), `--data DATA_PATH` (Target file on disk to re-hash or manifest entry input), `--root TRUSTED_ROOT` (Explicit trusted Merkle root hash).
- **Security Rule**: The `claimed_root` in proof JSON is ignored for verification. Verification is strictly executed against `--root TRUSTED_ROOT`.
- **Behavior**: Loads proof JSON, deserializes via `merkle.deserialize_proof_from_json()`, computes target file's leaf record, verifies via `merkle.verify_manifest_inclusion_proof()`. Returns exit code 0 if valid, exit code 1 if invalid.

---

## 3. Exit Code Contract

| Code | Meaning | Triggers |
| :--- | :--- | :--- |
| **`0`** | **Success** | Operation completed successfully, or integrity/proof verification passed. |
| **`1`** | **Verification Mismatch** | Integrity report contains modified/missing files, or Merkle inclusion proof verification returned `False`. |
| **`2`** | **User / System Invocation Error** | Missing required CLI parameters, invalid manifest JSON format, malformed proof JSON structure, unsupported cryptographic algorithm, or unsafe path rejection. |
| **`3`** | **Filesystem / I/O Error** | Target path not found, file access permission denied, or disk write failure. |

---

## 4. Module Layout & Backward Compatibility

- `src/integrity_toolkit/cli/main.py`: Main parser builder (`build_parser()`, `create_parser()`) and entry point dispatcher (`main()`).
- `src/integrity_toolkit/cli/handlers/`:
  - `hash_cmd.py`
  - `fingerprint_cmd.py`
  - `verify_cmd.py`
  - `merkle_cmd.py`
- `src/integrity_toolkit/cli/__main__.py`: Package executable module for `python -m integrity_toolkit.cli`.
- `src/integrity_toolkit/__main__.py`: Package executable module for `python -m integrity_toolkit`.
- Entry points registered in `pyproject.toml`:
  - `cit = "integrity_toolkit.cli.main:main"`
  - `integrity = "integrity_toolkit.cli.main:main"`
