# Cryptographic Integrity Toolkit — Unified CLI Reference (`cit`)

The `cit` command-line tool provides access to stream hashing, file fingerprinting, directory manifest creation, integrity verification, and Merkle tree inclusion-proof generation and verification.

---

## Command Syntax Overview

```bash
cit [GLOBAL OPTIONS] COMMAND [ARGS]

```

### Registered Executables

* `cit` (Primary product executable)
* `integrity` (Backward-compatibility alias)
* `python -m integrity_toolkit` (Module execution)
* `python -m integrity_toolkit.cli` (CLI package execution)

---

## Subcommands

### 1. `cit hash`

Computes cryptographic hash digests for text strings, files, or standard input.

```bash
# Hash a text string
cit hash --text "Hello World" --algorithm sha256

# Hash a file on disk (streamed)
cit hash --file ./document.pdf --algorithm sha512

# Hash data piped via stdin
echo "Hello World" | cit hash --algorithm blake2b

```

### 2. `cit fingerprint`

Generates a fingerprint for a single file or builds an integrity manifest for a directory.

```bash
# Fingerprint a single file
cit fingerprint ./report.pdf --algorithm sha256

# Generate directory integrity manifest
cit fingerprint ./dataset --algorithm sha256 -o manifest.json

```

### 3. `cit verify`

Verifies directory contents against an existing manifest JSON file.

```bash
cit verify ./dataset -m manifest.json
cit verify ./dataset -m manifest.json --ignore-unexpected

```

### 4. `cit merkle` (Subcommand Group)

#### `cit merkle build`

Constructs a Merkle tree from a manifest and optionally saves summary JSON metadata.

```bash
cit merkle build manifest.json -o tree_summary.json

```

#### `cit merkle root`

Computes and displays the Merkle tree root commitment.

```bash
cit merkle root manifest.json

```

#### `cit merkle prove`

Generates a versioned Merkle inclusion-proof JSON artifact (`CIT-MLF1`) for a target file.

```bash
cit merkle prove manifest.json documents/report.pdf -o proof.json

```

#### `cit merkle verify-proof`

Verifies an inclusion proof independently against an explicitly provided trusted root.

```bash
cit merkle verify-proof proof.json --data ./documents/report.pdf --root <TRUSTED_ROOT_HASH>

```

---

## Exit Code Reference

| Exit Code | Description |
| --- | --- |
| **`0`** | Success / Verification Passed |
| **`1`** | Verification Mismatch / Tampering Detected |
| **`2`** | Parameter Error / Invalid Format / Unsupported Algorithm |
| **`3`** | Filesystem I/O Error / Path Not Found |

```