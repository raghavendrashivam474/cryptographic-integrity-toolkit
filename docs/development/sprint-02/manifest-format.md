# Integrity Manifest Format Specification (v1)

## Format Identification
- **Format Name**: `cryptographic-integrity-manifest`
- **Current Version**: `1`
- **Default Algorithm**: `sha256` (also supports `sha512`, `blake2b`)

## JSON Schema Example
```json
{
  "format": "cryptographic-integrity-manifest",
  "version": 1,
  "algorithm": "sha256",
  "entries": [
    {
      "path": "src/main.py",
      "size": 4096,
      "digest": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    }
  ]
}
```

## Security & Integrity Rules

  - Paths MUST be relative to the manifest root using forward slashes (/).
  - Absolute paths and parent path traversal (..) are strictly rejected.
  - Digests MUST match valid hex format for the recorded algorithm.
