# Cryptographic Integrity Toolkit

**Sprint ID:** CL-00 / S00  
**Target Version:** `v0.0.1` — Development Foundation  
**Language:** Python 3.11+  
**License:** Internal / Collaborative Engineering  

---

## 1. Project Overview

The **Cryptographic Integrity Toolkit** is an extensible Python framework designed to implement and demonstrate core cryptographic data-integrity mechanisms. It serves as a foundational library and command-line application for verifying file integrity, constructing Merkle trees, generating inclusion proofs, and verifying cryptographic state over time.

---

## 2. Scope & Status

### 2.1 Current Release (`v0.0.1`)
Sprint 00 establishes the foundational engineering infrastructure required for subsequent cryptographic development:
- Standardized Python package structure (`src/integrity_toolkit/`).
- Isolated module boundaries (`crypto/`, `merkle/`, `cli/`).
- Reproducible virtual environment setup and dependency isolation.
- Packaging configuration via `pyproject.toml`.
- Minimal CLI entry point (`integrity`).
- Automated testing infrastructure via `pytest`.

### 2.2 Functional Roadmap
- **Sprint 01:** Cryptographic Hash Engine
- **Sprint 02:** File Fingerprinting & Verification Engine
- **Sprint 03:** Merkle Tree Construction Engine
- **Sprint 04:** Merkle Proof Generator
- **Sprint 05:** Proof Verification Engine
- **Sprint 06:** Unified Command-Line Interface

---

## 3. Quickstart & Installation

### 3.1 Prerequisites
- Python `3.11` or higher
- Git
- PowerShell (Windows) or Bash (Linux/macOS)

### 3.2 Setup Virtual Environment
```powershell
# Create local virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3.3 Development Installation

Install development dependencies and the package in editable mode:

```PowerShell
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

## 4. Usage

The toolkit exposes the integrity command-line executable.

```PowerShell

# Check toolkit version
integrity --version

# Display top-level help
integrity --help
```

>**Note**: Domain-specific subcommands (hash, scan, merkle, verify) will be introduced in subsequent sprints.

## 5. Testing & Quality Assurance

Automated tests are executed using pytest.

```PowerShell
# Run all unit and integration tests
pytest -v
```

## 6. Project Architecture

```text
cryptographic-integrity-toolkit/
├── src/
│   └── integrity_toolkit/
│       ├── __init__.py
│       ├── crypto/      # Cryptographic primitives (Sprint 01+)
│       ├── merkle/      # Merkle trees & inclusion proofs (Sprint 03+)
│       └── cli/         # Command-line entry points & subcommands
├── tests/
│   ├── unit/            # Isolated unit tests
│   ├── integration/     # Inter-module integration tests
│   └── conftest.py
├── docs/                # Architecture, setup, and research documentation
├── examples/            # Example scripts and usage demonstrations
├── scripts/             # Maintenance and development scripts
└── pyproject.toml       # Build system and metadata
```
## Unified CLI Usage (`cit`)

The toolkit provides a single unified executable `cit` (or `integrity` alias):

```bash
# Stream hash a file
cit hash --file report.pdf --algorithm sha256

# Create directory integrity manifest
cit fingerprint ./dataset -o manifest.json

# Verify directory against manifest
cit verify ./dataset -m manifest.json

# Compute Merkle tree root
cit merkle root manifest.json

# Generate inclusion proof for a file
cit merkle prove manifest.json report.pdf -o proof.json

# Verify inclusion proof against trusted root
cit merkle verify-proof proof.json --data ./dataset/report.pdf --root <TRUSTED_ROOT>
```
