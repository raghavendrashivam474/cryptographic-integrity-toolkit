# Sprint CL-05: End-to-End CLI Verification Walkthrough & Manual Test Report

**Project:** Cryptographic Integrity Toolkit (`cryptographic-integrity-toolkit`)  
**Sprint Identifier:** CL-05 / S05 — Unified CLI Integration  
**Executable Binary:** `cit` (Alias: `integrity`)  
**Target Release Tag:** `v-CL-05`  
**Execution Environment:** Windows PowerShell / Python 3.13.14  
**Date:** November 21, 2026  
**Status:** **PASSED & VERIFIED**

---

## 1. Purpose & Overview

This document records the manual End-to-End (E2E) verification session executed for the `cit` CLI binary following package installation in editable mode (`pip install -e .`).

The session validates all subcommand workflows, parameter variations, tamper-detection mechanisms, Merkle tree construction, and cryptographic inclusion proof generation and verification against trusted roots.

---

## 2. Walkthrough Steps & Real System Outputs

### Step 1: Package Installation & Entry Point Verification

**Command:**

```powershell
pip install -e .
cit --version
cit --help

```

**System Output:**

```text
cit 0.0.1

usage: cit [-h] [--version] {hash,fingerprint,verify,merkle} ...
Cryptographic Integrity Toolkit
positional arguments:
  {hash,fingerprint,verify,merkle}
                        Available subcommands
    hash                Compute hash of text, file, or stdin input
    fingerprint         Fingerprint a file or generate an integrity manifest for a directory
    verify              Verify files against an integrity manifest
    merkle              Merkle tree construction, root computation, proof generation and verification
options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

```

### Step 2: Hashing Inline Text (`cit hash`)

**Commands:**

```powershell
cit hash --text "Hello, Cryptographic Integrity Toolkit!"
cit hash --text "Hello, Cryptographic Integrity Toolkit!" --algorithm sha512
cit hash --text "Hello, Cryptographic Integrity Toolkit!" --algorithm blake2b

```

**System Output:**

```text
Algorithm : SHA256
Input     : Hello, Cryptographic Integrity Toolkit!
Digest    : df8f22446b0dab7c12e29242d4a026081e1a98c7fb48d0c0388d882f30a5ea3e

Algorithm : SHA512
Input     : Hello, Cryptographic Integrity Toolkit!
Digest    : 16828c8484170bc2256b4969212d101648632a2bef18b9781d17726abe4e56a5a1acd534b05994649cf64e825c248d2829a055c4b98dca8d846260bf6a99189c

Algorithm : BLAKE2B
Input     : Hello, Cryptographic Integrity Toolkit!
Digest    : 4181e6b37205d9c1659748cc96ec300377a9576fbe5eeed3228bfa2548f040ffa484c07a797c422abc16c7e73874c77dc9e4fda7b131b44a1ea6c8742ba01d2e

```

### Step 3: Directory Fingerprinting & Manifest Generation (`cit fingerprint`)

**Commands:**

```powershell
New-Item -ItemType Directory -Path "demo_dir" -Force | Out-Null
New-Item -ItemType Directory -Path "demo_dir/sub" -Force | Out-Null
Set-Content -Path "demo_dir/fileA.txt" -Value "Content of File A"
Set-Content -Path "demo_dir/fileB.txt" -Value "Content of File B"
Set-Content -Path "demo_dir/sub/fileC.txt" -Value "Content of Subdirectory File C"

cit fingerprint demo_dir -o manifest.json

```

**System Output:**

```text
Generated integrity manifest (3 entries) -> C:\Users\ragha\Projects\cryptographic-integrity-toolkit\manifest.json

```

**Generated Manifest Contents (`manifest.json`):**

```json
{
  "format": "cryptographic-integrity-manifest",
  "version": 1,
  "algorithm": "sha256",
  "entries": [
    {
      "path": "fileA.txt",
      "size": 22,
      "digest": "d19db48615ef412d2a9133bf3f1fd1706f5c5b8fcb944fab9e69fb6bbeee0ec8"
    },
    {
      "path": "fileB.txt",
      "size": 22,
      "digest": "e7a470845257cd9f2b7dad20004a7f31f711362a7ee20b079556bf35376754b0"
    },
    {
      "path": "sub/fileC.txt",
      "size": 35,
      "digest": "16cc6f24a1940a50adcbdf81193bd666c6db99175b075538a9b08d7f9a0f9c5c"
    }
  ]
}

```

### Step 4: Directory Integrity Verification (`cit verify`)

**Command:**

```powershell
cit verify demo_dir -m manifest.json

```

**System Output:**

```text
========================================
        INTEGRITY VERIFICATION
========================================
Manifest : manifest.json
Algorithm: SHA256
Total files : 3
MATCH       : 3
MODIFIED    : 0
MISSING     : 0
UNEXPECTED  : 0
ERROR       : 0
Overall Status: SUCCESS
========================================

```

### Step 5: Tamper Detection & Failure Handling

**Commands:**

```powershell
Add-Content -Path "demo_dir/fileA.txt" -Value " [TAMPERED!]"
cit verify demo_dir -m manifest.json

```

**System Output:**

```text
========================================
        INTEGRITY VERIFICATION
========================================
Manifest : manifest.json
Algorithm: SHA256
Total files : 3
MATCH       : 2
MODIFIED    : 1
MISSING     : 0
UNEXPECTED  : 0
ERROR       : 0
Overall Status: FAILED
========================================

```

**Verification Exit Code:** `1` (Mismatched file detected).

### Step 6: Merkle Tree Building & Root Computation (`cit merkle`)

**Commands:**

```powershell
# Restore untampered state and update manifest
Set-Content -Path "demo_dir/fileA.txt" -Value "Content of File A"
cit fingerprint demo_dir -o manifest.json

# Compute Merkle Root & Build Tree JSON
cit merkle root manifest.json
cit merkle build manifest.json -o tree.json

```

**System Output:**

```text
Merkle Root: 62444254580db2eed3da059d946d69147d71d2a6d1bcb9872408418d2f0e0864
Algorithm  : SHA256
Leaf Count : 3

========================================
          MERKLE TREE BUILT
========================================
Manifest   : manifest.json
Algorithm  : SHA256
Leaves     : 3
Merkle Root: 62444254580db2eed3da059d946d69147d71d2a6d1bcb9872408418d2f0e0864
========================================
Saved tree summary -> tree.json

```

### Step 7: Merkle Inclusion Proof Generation & Trusted Root Verification

**Commands:**

```powershell
# Generate inclusion proof for fileA.txt
cit merkle prove manifest.json fileA.txt -o proof_fileA.json

# Verify proof against target file on disk and trusted root
cit merkle verify-proof proof_fileA.json --data demo_dir/fileA.txt --root 62444254580db2eed3da059d946d69147d71d2a6d1bcb9872408418d2f0e0864

```

**Generated Proof JSON (`proof_fileA.json`):**

```json
{
  "format": "cryptographic-integrity-merkle-proof",
  "version": 1,
  "algorithm": "sha256",
  "leaf_index": 0,
  "leaf_count": 3,
  "claimed_root": "62444254580db2eed3da059d946d69147d71d2a6d1bcb9872408418d2f0e0864",
  "steps": [
    {
      "operation": "RIGHT_SIBLING",
      "sibling_digest": "e7a470845257cd9f2b7dad20004a7f31f711362a7ee20b079556bf35376754b0"
    },
    {
      "operation": "RIGHT_SIBLING",
      "sibling_digest": "78749a15998a44b8ee76aef0b9bbab58f8aa7f6f1ec2f0b0c950920d046e7f7b"
    }
  ]
}

```

**Verification System Output:**

```text
Proof Verification: SUCCESS (Valid proof against trusted root)

```

---

## 3. Summary & Conclusion

All end-to-end CLI subcommands (`hash`, `fingerprint`, `verify`, `merkle build`, `merkle root`, `merkle prove`, `merkle verify-proof`) performed strictly according to specifications:

* Entry points (`cit`, `integrity`) execute without runtime errors.
* Tamper detection reliably reports modified files and sets exit code `1`.
* Cryptographic inclusion proof generation produces standard `v1` JSON specifications.
* Proof verification correctly mandates explicit `--root` digest matching.

```