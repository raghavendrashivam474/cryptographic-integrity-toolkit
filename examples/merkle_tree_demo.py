"""Runnable demonstration of generic Merkle tree construction (CL-03)."""

from integrity_toolkit.merkle import build_merkle_tree, hash_leaf, hash_internal


def main() -> None:
    print("==================================================")
    print("   Generic Merkle Tree Construction Demonstration ")
    print("==================================================")

    payloads = [
        b"Transaction 1: Alice pays Bob 10 BTC",
        b"Transaction 2: Bob pays Charlie 2.5 BTC",
        b"Transaction 3: Charlie pays Dave 0.5 BTC",
    ]

    print(f"\n1. Input Payloads ({len(payloads)} items):")
    for idx, p in enumerate(payloads):
        print(f"   Leaf [{idx}]: {p.decode('utf-8')}")

    # Build Merkle Tree using SHA-256
    tree = build_merkle_tree(payloads, algorithm="sha256")

    print(f"\n2. Constructed Merkle Tree Properties:")
    print(f"   Algorithm:  {tree.algorithm.upper()}")
    print(f"   Leaf Count: {tree.leaf_count}")
    print(f"   Tree Root:  {tree.root}")

    print(f"\n3. Structural Levels ({len(tree.levels)} levels):")
    for lvl_idx, level in enumerate(tree.levels):
        print(f"   Level {lvl_idx} ({len(level)} nodes):")
        for node_idx, node in enumerate(level):
            print(f"     Node [{node_idx}]: {node[:16]}...{node[-16:]}")

    # Verify determinism
    tree_rebuilt = build_merkle_tree(payloads, algorithm="sha256")
    assert tree.root == tree_rebuilt.root
    print("\n[SUCCESS] Rebuilt tree root is identical (Determinism Verified).")


if __name__ == "__main__":
    main()
