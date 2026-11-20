# Sprint 02 — Implementation Plan: File Fingerprinting & Integrity Verification

## Overview
Sprint 02 builds the file-integrity subsystem (`integrity_toolkit.integrity`) on top of the cryptographic hash engine delivered in Sprint 01.

## Package Architecture
- `integrity_toolkit.integrity`
  - `exceptions.py`: Integrity exception hierarchy
  - `models.py`: Dataclasses (`FileFingerprint`, `ManifestEntry`, `IntegrityManifest`, `FileVerificationResult`, `VerificationReport`) and `VerificationStatus` enum
  - `fingerprint.py`: Single-file streaming fingerprint service with race/modification detection
  - `traversal.py`: Safe directory file discovery and deterministic relative path sorting
  - `manifest.py`: Manifest creation, serialization, deserialization, validation, and atomic storage
  - `verifier.py`: Core verification engine comparing filesystem state against manifests
  - `__init__.py`: Public subsystem exports

## Design Guarantees
1. Memory-efficient streaming hashing via `crypto.hash_stream()`.
2. Safe path resolution ensuring no path traversal outside designated verification roots.
3. Deterministic manifest generation (sorted paths, normalized POSIX slashes).
4. Full CLI integration for `integrity fingerprint` and `integrity verify`.
