# Risk Register

**Project:** Cryptographic Integrity Toolkit (cit)  
**Milestone:** sprint-06 (Product Readiness & Security Audit)  
**Target Release:** 1.0.0  

---

## Risk Inventory & Remediation Classification

| Risk ID | Title / Finding | Severity | Category | Remediation Plan |
|---|---|---|---|---|
| **SEC-01** | CLI merkle verify-proof relative path option | **Medium** | CLI Safety | Add optional --relative-path flag to erify-proof command handler. |
| **SEC-02** | memoryview support in hash_bytes | **Low** | Crypto Primitive | Extend type validation in hash_bytes to accept memoryview. |
| **REL-01** | Manifest atomic file replace robustness | **Low** | Filesystem Safety | Retain existing os.replace atomic guarantee and add mock regression test. |
| **REL-02** | Traversal exclude path resolution | **Low** | Filesystem Traversal | Validate relative path normalization in discover_files. |

---

## Acceptance of Residual Risks

- **No Critical or High Severity Risks Found.**
- All Medium and Low findings have simple, contract-preserving remediation paths in S06-T03/S06-T04.

