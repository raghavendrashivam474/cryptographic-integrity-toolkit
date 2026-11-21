"""Handler for 'merkle' CLI commands (build, root, prove, verify-proof)."""
import sys
import json
from pathlib import Path
from integrity_toolkit.integrity import (
    FileAccessError,
    IntegrityError,
    InvalidManifestError,
    ManifestEntry,
    fingerprint_file,
    load_manifest,
)
from integrity_toolkit.crypto import UnsupportedAlgorithmError
from integrity_toolkit.merkle import (
    InvalidProofError,
    MerkleError,
    build_merkle_tree_from_manifest,
    deserialize_proof_from_json,
    generate_manifest_inclusion_proof,
    serialize_proof_to_json,
    verify_manifest_inclusion_proof,
)

def handle_merkle(args) -> int:
    """Dispatch merkle subcommands."""
    merkle_subcommand = getattr(args, "merkle_command", None)
    if not merkle_subcommand:
        print("Error: Missing merkle subcommand. Choose from: build, root, prove, verify-proof", file=sys.stderr)
        return 2

    if merkle_subcommand == "build":
        return _handle_merkle_build(args)
    elif merkle_subcommand == "root":
        return _handle_merkle_root(args)
    elif merkle_subcommand == "prove":
        return _handle_merkle_prove(args)
    elif merkle_subcommand == "verify-proof":
        return _handle_merkle_verify_proof(args)
    else:
        print(f"Error: Unknown merkle subcommand: {merkle_subcommand}", file=sys.stderr)
        return 2

def _handle_merkle_build(args) -> int:
    try:
        manifest = load_manifest(args.manifest)
        tree = build_merkle_tree_from_manifest(manifest)
        print("========================================")
        print("          MERKLE TREE BUILT             ")
        print("========================================")
        print(f"Manifest   : {args.manifest}")
        print(f"Algorithm  : {tree.algorithm.upper()}")
        print(f"Leaves     : {tree.leaf_count}")
        print(f"Merkle Root: {tree.root}")
        print("========================================")

        output_path = getattr(args, "output", None)
        if output_path:
            tree_data = {
                "manifest": str(args.manifest),
                "algorithm": tree.algorithm,
                "leaf_count": tree.leaf_count,
                "root": tree.root,
            }
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(json.dumps(tree_data, indent=2), encoding="utf-8")
            print(f"Saved tree summary -> {out_file}")
        return 0
    except FileAccessError as err:
        print(f"File Error: {err}", file=sys.stderr)
        return 3
    except (InvalidManifestError, UnsupportedAlgorithmError, MerkleError) as err:
        print(f"Merkle Build Error: {err}", file=sys.stderr)
        return 2

def _handle_merkle_root(args) -> int:
    try:
        manifest = load_manifest(args.manifest)
        tree = build_merkle_tree_from_manifest(manifest)
        print(f"Merkle Root: {tree.root}")
        print(f"Algorithm  : {tree.algorithm.upper()}")
        print(f"Leaf Count : {tree.leaf_count}")
        return 0
    except FileAccessError as err:
        print(f"File Error: {err}", file=sys.stderr)
        return 3
    except (InvalidManifestError, UnsupportedAlgorithmError, MerkleError) as err:
        print(f"Merkle Error: {err}", file=sys.stderr)
        return 2

def _handle_merkle_prove(args) -> int:
    try:
        manifest = load_manifest(args.manifest)
        proof = generate_manifest_inclusion_proof(manifest, args.relative_path)
        proof_json = serialize_proof_to_json(proof)

        out_file = Path(args.output)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(proof_json, encoding="utf-8")
        print(f"Generated inclusion proof for '{args.relative_path}' -> {out_file}")
        return 0
    except FileAccessError as err:
        print(f"File Error: {err}", file=sys.stderr)
        return 3
    except (InvalidManifestError, UnsupportedAlgorithmError, MerkleError, InvalidProofError) as err:
        print(f"Proof Generation Error: {err}", file=sys.stderr)
        return 2

def _handle_merkle_verify_proof(args) -> int:
    try:
        proof_path = Path(args.proof)
        if not proof_path.exists():
            print(f"File Error: Proof file not found: {args.proof}", file=sys.stderr)
            return 3

        proof_json = proof_path.read_text(encoding="utf-8")
        proof = deserialize_proof_from_json(proof_json)

        data_path = Path(args.data)
        if not data_path.exists():
            print(f"File Error: Data file not found: {args.data}", file=sys.stderr)
            return 3

        fp = fingerprint_file(data_path, algorithm=proof.algorithm)

        # Derive relative path from args if provided, else use file name
        rel_path = getattr(args, "relative_path", None)
        if not rel_path:
            rel_path = data_path.name

        entry = ManifestEntry(
            path=rel_path,
            size=fp.size,
            digest=fp.digest,
        )

        # Security requirement: expected_root comes strictly from CLI argument --root
        is_valid = verify_manifest_inclusion_proof(
            entry=entry,
            proof=proof,
            expected_root=args.root,
        )

        if is_valid:
            print("Proof Verification: SUCCESS (Valid proof against trusted root)")
            return 0
        else:
            print("Proof Verification: FAILED (Proof mismatch or untrusted root)", file=sys.stderr)
            return 1
    except FileAccessError as err:
        print(f"File Error: {err}", file=sys.stderr)
        return 3
    except (InvalidProofError, MerkleError, InvalidManifestError, UnsupportedAlgorithmError, ValueError) as err:
        print(f"Proof Verification Error: {err}", file=sys.stderr)
        return 2
