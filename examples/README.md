# Cryptographic Integrity Toolkit Examples

This directory contains executable usage examples demonstrating how to use the toolkit programmatically via Python and via the CLI.

---

## Planned Example Suites

- **Sprint 01:** File and byte-string cryptographic hashing (`01_hashing_basics.py`).
- **Sprint 02:** Directory manifest generation and integrity verification (`02_directory_verification.py`).
- **Sprint 03:** Merkle tree construction from dataset leaves (`03_merkle_tree_construction.py`).
- **Sprint 04 & 05:** Merkle inclusion proof generation and verification (`04_merkle_proof_audit.py`).

---

## Running Examples

Ensure your virtual environment is activated and the package is installed in editable mode before executing any example script:

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Run an example script (Sprint 01+)
python examples/01_hashing_basics.py
```