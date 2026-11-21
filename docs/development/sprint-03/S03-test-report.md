# Sprint CL-03 / S03 — Merkle Tree Engine Test Report

**Project:** Cryptographic Integrity Toolkit  
**Execution Date:** March 2025  
**Environment:** Python 3.13.14 (`win32`), Pytest 8.3.5  
**Target Release:** `v-CL-03`  

---

## 1. Executive Summary

All automated test suites executed successfully with **100% pass rate** and **zero failures or errors**.

| Suite | Category | Collected Items | Passed | Failed | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `test_merkle_hashing.py` | Unit (Primitives) | 10 | 10 | 0 | PASSED |
| `test_merkle_tree.py` | Unit (Tree Engine) | 9 | 9 | 0 | PASSED |
| `test_merkle_adapters.py` | Unit (Manifest Adapter)| 7 | 7 | 0 | PASSED |
| `test_merkle_workflow.py` | Integration & Isolation| 5 | 5 | 0 | PASSED |
| *Baseline Regression* | CL-00 / CL-01 / CL-02 | 151 | 151 | 0 | PASSED |
| **TOTAL** | **Full Repository** | **182** | **182** | **0** | **PASSED** |

---

## 2. Tested Functional Capabilities

1. **Domain-Separated Cryptographic Primitives:**
   * Leaf hashing ($H(0x00 \parallel D)$) verified across SHA-256, SHA-512, BLAKE2b.
   * Internal node parent hashing ($H(0x01 \parallel L_{raw} \parallel R_{raw})$) verified with length & format validation.
   * Isolation between leaf payloads and internal preimages confirmed.
2. **Generic Merkle Tree Construction Engine:**
   * Single-leaf tree root equals single leaf hash.
   * Balanced 2-leaf and 4-leaf tree construction.
   * Odd-node levels (3, 5 leaves) properly promote unpaired nodes unchanged according to ADR-001.
   * Empty input handling raises `EmptyTreeError`.
   * Order-sensitivity verified.
3. **File-Manifest Adapter (`CIT-MLF1` Encoding):**
   * Deterministic path sorting guarantees identical roots for reordered manifests.
   * Serialization includes POSIX path, canonical algorithm, file size, and raw digest bytes.
   * Field changes (path, size, digest) reliably alter Merkle root.
4. **Architectural Isolation:**
   * Generic Merkle engine imports (`merkle.hashing`, `merkle.tree`) executed without loading `integrity` package into memory.
