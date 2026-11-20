# Contributing Guidelines

**Project:** Cryptographic Integrity Toolkit  
**Sprint Model:** Two-engineer collaborative project with independent task ownership  

---

## 1. Development Workflow

### 1.1 Branch Conventions
All work must be developed on short-lived feature branches created from `main`. Do not push unreviewed commits directly to `main`.

Recommended branch naming format:
- `feature/S<sprint>-<ticket>-<short-description>` (e.g., `feature/S00-01-project-structure`)
- `docs/S<sprint>-<ticket>-<short-description>` (e.g., `docs/S00-04-foundation-docs`)
- `fix/S<sprint>-<ticket>-<short-description>`

### 1.2 Git Commit Guidelines
- Write imperative, concise commit messages (e.g., `Add CLI argument parser for --version`).
- Commit frequently in small, cohesive atomic units.
- **Never** perform destructive Git operations (`git reset --hard`, `git clean -fd`, force pushing) on shared branches.

---

## 2. Python Code Standards

- **Python Version:** Python 3.11+
- **Style Guide:** Adhere strictly to PEP 8.
- **Type Annotations:** Use explicit type hints (`typing` / standard generics) for function parameters and return values.
- **Docstrings:** Provide Google-style docstrings for all public modules, functions, classes, and methods.

Example:
```python
def calculate_hash(data: bytes, algorithm: str = "sha256") -> str:
    """Calculate cryptographic hash for given binary data.

    Args:
        data: Raw input bytes to hash.
        algorithm: Hashing algorithm identifier (default: 'sha256').

    Returns:
        Hexadecimal hash string.
    """
    ...
```

## 3. Testing Requirements

- Every new feature, module, or bug fix must include corresponding unit tests under 
  tests/unit/ or integration tests under tests/integration/.
- All tests must pass before opening a Pull Request:

```PowerShell
pytest -v
```

- Tests must be deterministic and isolated, with no reliance on unmanaged external services.

## 4. Architectural Decision Process

If proposing a structural or architectural change to the codebase:

   1. Do not overwrite or delete existing working configuration without authorization.
   2. Draft an Architecture Decision Record (ADR) under docs/architecture/decisions/NNNN-title.md.
   3. Obtain senior engineering review prior to implementation.