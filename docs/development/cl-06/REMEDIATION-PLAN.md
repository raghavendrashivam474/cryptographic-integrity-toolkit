# Remediation Plan & Architecture Approval

**Project:** Cryptographic Integrity Toolkit (cit)  
**Milestone:** CL-06 (Product Readiness & Security Audit)  
**Target Release:** 1.0.0  
**Status:** Approved for S06-T04 Implementation  

---

## 1. Executive Summary

Following the completion of S06-T01 (Threat Model) and S06-T02 (Security & Reliability Audit), this Remediation Plan outlines the specific, minimal, contract-preserving code and test updates required to address all findings prior to the 1.0.0 release.

No critical or high-severity vulnerabilities were identified. All identified items represent low-to-medium severity improvements that maintain 100% backward compatibility with existing public Python APIs and CLI contracts.

---

## 2. ADR Threshold Assessment

Per Section 10 (S06-T03 Policy):
- **Schema & Format Integrity:** No changes to manifest JSON schema (1), proof JSON schema (1), or binary leaf formatting (CIT-MLF1).
- **API Stability:** No existing functions or dataclass models are modified or removed.
- **CLI Backward Compatibility:** All existing flags and exit codes remain intact.

**ADR Decision:** An Architectural Decision Record (ADR) is **NOT required** because all remediations are non-breaking, additive, or internal bug fixes.

---

## 3. Targeted Remediation Schedule (S06-T04)

### Remediation Item 1: FIX-SEC-01 — CLI Relative Path Parameter for merkle verify-proof
- **Audit Finding:** FINDING-SEC-01
- **Target File:** src/integrity_toolkit/cli/main.py, src/integrity_toolkit/cli/handlers/merkle_cmd.py
- **Description:** Add optional --relative-path / --relpath parameter to cit merkle verify-proof parser.
- **Behavior:** When provided, el_path uses --relative-path instead of defaulting to Path(data).name. This enables seamless proof verification for files located in nested manifest subdirectories.
- **Compatibility:** Fully backward-compatible; defaults to existing behavior if omitted.

### Remediation Item 2: FIX-SEC-02 — Native memoryview Support in Crypto & Merkle Hashing
- **Audit Finding:** FINDING-SEC-02
- **Target Files:** src/integrity_toolkit/crypto/engine.py, src/integrity_toolkit/merkle/hashing.py
- **Description:** Update isinstance(data, (bytes, bytearray)) checks in hash_bytes and hash_leaf to (bytes, bytearray, memoryview).
- **Behavior:** Accepts memoryview buffers directly without requiring manual caller byte casting or raising InvalidInputError.
- **Compatibility:** Backward-compatible extension of allowed types.

### Remediation Item 3: FIX-REL-01 & FIX-REL-02 — Extended Unit & Integration Test Coverage
- **Audit Finding:** FINDING-REL-01, FINDING-REL-02
- **Target Files:** 	ests/unit/
- **Description:** Add explicit test cases for memoryview inputs, nested relative path CLI proof verification, and atomic write tempfile cleanup.

---

## 4. Verification Checkpoints

After S06-T04 remediation:
1. Re-run complete 226-test baseline suite.
2. Execute new targeted regression tests.
3. Verify CLI help output and exit codes.
4. Execute examples/cli_end_to_end_demo.py.
