"""Demonstration: Generic Merkle inclusion proof generation, serialization, and verification."""

from integrity_toolkit.merkle import (
    build_merkle_tree,
    deserialize_proof_from_json,
    generate_inclusion_proof,
    serialize_proof_to_json,
    verify_inclusion_proof,
)


def main():
    print("=== Cryptographic Integrity Toolkit — Merkle Proof Demo ===")

    records = [
        b"Transaction A: Send $100",
        b"Transaction B: Send $200",
        b"Transaction C: Send $300",
        b"Transaction D: Send $400",
        b"Transaction E: Send $500",
    ]

    print(f"Constructing Merkle tree from {len(records)} byte payloads...")
    tree = build_merkle_tree(records, algorithm="sha256")
    print(f"Merkle Root: {tree.root}")

    # Generate proof for index 2 ("Transaction C")
    target_idx = 2
    target_payload = records[target_idx]
    print(f"\nGenerating inclusion proof for leaf index {target_idx} ('{target_payload.decode()}')...")
    proof = generate_inclusion_proof(tree, target_idx)

    # Serialize to JSON
    json_proof = serialize_proof_to_json(proof, indent=2)
    print(f"Serialized Proof JSON:\n{json_proof}")

    # Deserialize back
    loaded_proof = deserialize_proof_from_json(json_proof)

    # Verify original payload
    print("Verifying proof with authentic leaf payload against trusted root...")
    is_valid = verify_inclusion_proof(target_payload, loaded_proof, expected_root=tree.root)
    print(f"Verification Result: {is_valid} (Expected: True)")

    # Verify tampered payload
    tampered_payload = b"Transaction C: Send $9999"
    print(f"\nVerifying proof with TAMPERED leaf payload ('{tampered_payload.decode()}')...")
    is_tampered_valid = verify_inclusion_proof(tampered_payload, loaded_proof, expected_root=tree.root)
    print(f"Verification Result: {is_tampered_valid} (Expected: False)")


if __name__ == "__main__":
    main()
