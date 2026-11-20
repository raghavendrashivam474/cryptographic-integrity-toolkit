# ADR 0001: Python Package Structure and Build System Architecture

* **Status:** Accepted
* **Date:** 2025-02-23
* **Authors:** Engineering Team
* **Sprint ID:** CL-01 / S00

---

## 1. Context and Problem Statement

The Cryptographic Integrity Toolkit requires a clean, reproducible, and extensible development foundation to support multi-sprint engineering (cryptographic hashing, file verification, Merkle tree operations, and CLI integration).

Without an explicit structural design:
1. Implicit imports from the repository root can introduce hidden import bugs during packaging.
2. Direct command-line execution without proper package installation leads to path resolution errors.
3. Future subpackages (`crypto`, `merkle`) risk tight coupling and circular dependencies.

---

## 2. Decision Drivers

- **Reproducibility:** The environment must be easily setup and installed by any engineer using standard Python tools.
- **Isolation:** Tests must run against installed package code rather than ambient root files.
- **Zero Heavy External Dependencies:** Minimal reliance on non-standard build wrappers or heavy third-party CLI frameworks for core foundation.
- **PEP Compliance:** Alignment with modern packaging standards (PEP 517, PEP 518, PEP 621).

---

## 3. Considered Options

1. **Flat Layout (`integrity_toolkit/` in repository root):**
   - *Pros:* Simpler directory depth.
   - *Cons:* Prone to import masking where test runners accidentally import local source instead of installed packages; poor isolation.

2. **Standard `src/` Layout (`src/integrity_toolkit/`):**
   - *Pros:* Forces explicit editable installation (`pip install -e .`); isolates tests from source; aligns with modern Python distribution best practices.
   - *Cons:* Slightly deeper folder structure.

---

## 4. Decision

We adopt Option 2: **Standard `src/` Layout** defined by `pyproject.toml` using `setuptools`:

1. **Source Package:** Placed strictly inside `src/integrity_toolkit/`.
2. **Subpackage Boundaries:** Explicit directories for `crypto/`, `merkle/`, and `cli/`.
3. **Packaging Configuration:** `pyproject.toml` configured with `setuptools.build_meta`.
4. **CLI Dispatcher:** Built using standard-library `argparse` registered via `project.scripts` as `integrity`.
5. **Testing Harness:** `pytest` configured with explicit package discovery paths pointing to `src/`.

---

## 5. Consequences

### Positive
- Enforces editable package installation (`pip install -e .`), eliminating `PYTHONPATH` hacks.
- Clear structural separation prevents non-CLI modules from depending on UI logic.
- Standardized package registration enables execution of `integrity --version` and `integrity --help` anywhere within the activated virtual environment.

### Negative / Risks
- Developers must execute `pip install -e .` in their `.venv` before running CLI commands directly from terminal environments. (Mitigated via detailed documentation in `docs/development/setup.md`).