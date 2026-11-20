# Sprint 01 Implementation Plan — Cryptographic Hash Engine

## Milestone Summary
- **Sprint Identifier:** CL-01 / S01
- **Sprint Name:** Cryptographic Hash Engine
- **Baseline Commit:** cc7588a (tag: v-CL-00)
- **Primary Objective:** Build a modular, stream-capable Cryptographic Hash Engine using Python stdlib `hashlib`.

## Subsystem Architecture
1. `integrity_toolkit.crypto.exceptions`: Custom exception hierarchy (`CryptoError`, `UnsupportedAlgorithmError`, `InvalidInputError`, `InvalidChunkSizeError`, `StreamReadError`).
2. `integrity_toolkit.crypto.algorithms`: Algorithm registry for SHA-256, SHA-512, BLAKE2b with string normalization and hasher factory.
3. `integrity_toolkit.crypto.engine`: Core byte hashing API (`hash_bytes`).
4. `integrity_toolkit.crypto.streaming`: Streaming hash engine for chunked stream processing (`hash_stream`).
5. `integrity_toolkit.crypto.__init__`: Clean top-level exports for the crypto package.

## Task Breakdown & Status
- [x] S01-T00: Repository Baseline Inspection & Baseline Test Run (7/7 passed)
- [x] S01-T01: Implementation of Exceptions & Algorithm Registry (`algorithms.py`)
- [ ] S01-T02: Core Byte Hashing Engine (`engine.py`)
- [ ] S01-T03: Streaming Hash Engine (`streaming.py`)
- [ ] S01-T04: Package Exports (`crypto/__init__.py`)
- [ ] S01-T05: Integration Testing (`test_hash_workflow.py`)
- [ ] S01-T06: Minimal CLI Hashing Demonstration (`cli/main.py`)
- [ ] S01-T07: Technical Architecture Documentation & Verification
