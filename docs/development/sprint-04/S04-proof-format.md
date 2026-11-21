# S04 — Merkle Inclusion Proof Format Specification

## Schema Specification (JSON Format)

Version: 1
Format Name: cryptographic-integrity-merkle-proof

```json
{
  "format": "cryptographic-integrity-merkle-proof",
  "version": 1,
  "algorithm": "sha256",
  "leaf_index": 2,
  "leaf_count": 5,
  "claimed_root": "a3b2c1...",
  "steps": [
    {
      "operation": "RIGHT_SIBLING",
      "sibling_digest": "4f5e6d..."
    },
    {
      "operation": "LEFT_SIBLING",
      "sibling_digest": "7a8b9c..."
    },
    {
      "operation": "PROMOTE",
      "sibling_digest": null
    }
  ]
}
```

## Step Operations

- **LEFT_SIBLING**: Sibling node sits on the left. Calculated digest = hash_internal(sibling_digest, current_digest)
- **RIGHT_SIBLING**: Sibling node sits on the right. Calculated digest = hash_internal(current_digest, sibling_digest)
- **PROMOTE**: Node is promoted unchanged (unpaired node in odd-width level). Calculated digest = current_digest
