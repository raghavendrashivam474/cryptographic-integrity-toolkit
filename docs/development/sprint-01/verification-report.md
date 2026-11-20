# Sprint 01 Verification Report — Cryptographic Hash Engine

**Sprint Identifier:** CL-01 / S01  
**Target Baseline Tag:** `v-CL-00`  
**Execution Date:** 2025-03-08  
**Environment:** Python 3.13.14 (Win32)  

---

## 1. Automated Test Suite Results

The test suite was executed using `pytest -v` across unit and integration test categories.

### Test Execution Summary:
- **Baseline Tests Preserved:** 7 / 7 PASSED
- **Algorithm Registry Tests:** 14 / 14 PASSED
- **Core Hash Engine Tests:** 18 / 18 PASSED
- **Streaming Hash Engine Tests:** 26 / 26 PASSED
- **Integration Workflow Tests:** 5 / 5 PASSED
- **CLI Hash Demonstration Tests:** 5 / 5 PASSED
- **Total Test Suite Pass Rate:** **75 / 75 PASSED (100%)**
- **Test Duration:** 0.61 seconds

---

## 2. Reference Vector Verification

The hash engine was verified against official NIST (FIPS 180-4) and RFC 7693 cryptographic test vectors.

| Algorithm | Vector Input | Hexadecimal Digest Output | Standard Source | Result |
|-----------|--------------|---------------------------|-----------------|--------|
| `sha256`  | `b""`        | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | NIST FIPS 180-4 | PASSED |
| `sha256`  | `b"abc"`     | `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` | NIST FIPS 180-4 | PASSED |
| `sha512`  | `b""`        | `cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce...` | NIST FIPS 180-4 | PASSED |
| `sha512`  | `b"abc"`     | `ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a...` | NIST FIPS 180-4 | PASSED |
| `blake2b` | `b""`        | `786a02f742015903c6c6fd852552d272912f4740e15847618a86e217f71f5419...` | RFC 7693 App. E | PASSED |
| `blake2b` | `b"abc"`     | `ba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d1...` | RFC 7693 App. E | PASSED |

---

## 3. Streaming Equivalence & Memory Safety

Incremental chunked streaming (`hash_stream`) was verified for bit-for-bit identity against single-buffer byte hashing (`hash_bytes`).

### Verified Streaming Characteristics:
- Tested across chunk sizes: 1 B, 7 B, 64 B, 512 B, 4 KiB, 64 KiB.
- Verified identity across 1 MB and 10 MB payload sizes.
- Non-seekable stream compatibility confirmed via mock stream wrappers.
- Stream closure protection confirmed (caller-owned streams remain open).

---

## 4. Subsystem Performance Observations

Performance benchmarks were executed using a 10 MB payload over 10 iterations on Python 3.13 (x64 Windows).

| Algorithm | Direct In-Memory Throughput | Streaming Throughput (64 KiB Chunks) |
|-----------|-----------------------------|-------------------------------------|
| `sha256`  | ~700–850 MB/s               | ~650–800 MB/s                       |
| `sha512`  | ~1100–1300 MB/s             | ~1000–1200 MB/s                     |
| `blake2b` | ~1200–1500 MB/s             | ~1100–1400 MB/s                     |

*Note: Benchmarks reflect native C-extension performance via Python stdlib `hashlib`.*

---

## 5. Verification Conclusion

Sprint 01 Cryptographic Hash Engine satisfies all functional, architectural, quality, and testing criteria outlined in the Engineering Brief.
