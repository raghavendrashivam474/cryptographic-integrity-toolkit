# Sprint CL-04 / S04 — Implementation Plan

## Overview
This document maps out the exact module and task roadmap for implementing Merkle Inclusion Proofs in Sprint CL-04.

## Task Roadmap
1. **S04-T00 — Baseline Inspection:** (Completed) Repo verified at -CL-03, 182 tests passing.
2. **S04-T01 — Design Review & ADR:** (Current) ADR-001, implementation plan, proof specification.
3. **S04-T02 — Proof Models & Exceptions:** Implement MerkleProofStep, MerkleProof, InvalidProofError in integrity_toolkit.merkle.models and exceptions.py.
4. **S04-T03 — Proof Generation Engine:** Implement generate_inclusion_proof in integrity_toolkit.merkle.proofs.
5. **S04-T04 — Proof Verification Engine:** Implement erify_inclusion_proof in integrity_toolkit.merkle.verification.
6. **S04-T05 — Manifest Adapter Proofs:** Extend integrity_toolkit.merkle.adapters with manifest inclusion proofs.
7. **S04-T06 — Proof Serialization:** Implement JSON export/import functions in integrity_toolkit.merkle.proof_serialization.
8. **S04-T07 — Integration & Architectural Isolation Tests:** Validate boundary restrictions and complete test suite (0 regressions).
9. **S04-T08 — Demonstrations & API Reference:** Create runnable proof examples (examples/merkle_proof_demo.py, examples/merkle_manifest_proof_demo.py) and API documentation.
10. **S04-T09 — Final Handover & Tagging:** Handover report and authorization for release tag -CL-04.
