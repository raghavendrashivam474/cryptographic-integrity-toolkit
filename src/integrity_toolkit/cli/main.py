"""Unified command-line interface entry point for Cryptographic Integrity Toolkit."""

import argparse
import sys
from pathlib import Path

import integrity_toolkit
from integrity_toolkit.cli.handlers.fingerprint_cmd import handle_fingerprint
from integrity_toolkit.cli.handlers.hash_cmd import handle_hash
from integrity_toolkit.cli.handlers.merkle_cmd import handle_merkle
from integrity_toolkit.cli.handlers.verify_cmd import handle_verify
from integrity_toolkit.integrity import DEFAULT_ALGORITHM


def build_parser(prog: str = "integrity") -> argparse.ArgumentParser:
    """Construct and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Cryptographic Integrity Toolkit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {integrity_toolkit.__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: hash
    hash_parser = subparsers.add_parser("hash", help="Compute hash of text, file, or stdin input")
    hash_parser.add_argument(
        "--text",
        type=str,
        help="Text string to compute hash for",
    )
    hash_parser.add_argument(
        "--file",
        type=str,
        help="Path to file to compute stream hash for",
    )
    hash_parser.add_argument(
        "--algorithm",
        type=str,
        default=DEFAULT_ALGORITHM,
        help=f"Hash algorithm to use (default: {DEFAULT_ALGORITHM})",
    )

    # Command: fingerprint
    fp_parser = subparsers.add_parser(
        "fingerprint",
        help="Fingerprint a file or generate an integrity manifest for a directory",
    )
    fp_parser.add_argument(
        "target",
        type=str,
        help="Target file or directory path to fingerprint",
    )
    fp_parser.add_argument(
        "--algorithm",
        type=str,
        default=DEFAULT_ALGORITHM,
        help=f"Hash algorithm to use (default: {DEFAULT_ALGORITHM})",
    )
    fp_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output manifest destination path (required when target is a directory)",
    )

    # Command: verify
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify files against an integrity manifest",
    )
    verify_parser.add_argument(
        "root",
        type=str,
        help="Root directory containing files to verify",
    )
    verify_parser.add_argument(
        "-m",
        "--manifest",
        type=str,
        required=True,
        help="Path to the manifest JSON file",
    )
    verify_parser.add_argument(
        "--ignore-unexpected",
        action="store_true",
        help="Ignore files present on disk that are not in the manifest",
    )

    # Command group: merkle
    merkle_parser = subparsers.add_parser(
        "merkle",
        help="Merkle tree construction, root computation, proof generation and verification",
    )
    merkle_subparsers = merkle_parser.add_subparsers(dest="merkle_command", help="Merkle operations")

    # Subcommand: merkle build
    mb_parser = merkle_subparsers.add_parser("build", help="Build a Merkle tree from an integrity manifest")
    mb_parser.add_argument("manifest", type=str, help="Path to manifest JSON file")
    mb_parser.add_argument("-o", "--output", type=str, help="Optional output path for tree summary JSON")

    # Subcommand: merkle root
    mr_parser = merkle_subparsers.add_parser("root", help="Compute and display Merkle root hash from manifest")
    mr_parser.add_argument("manifest", type=str, help="Path to manifest JSON file")

    # Subcommand: merkle prove
    mp_parser = merkle_subparsers.add_parser("prove", help="Generate an inclusion proof for a file entry")
    mp_parser.add_argument("manifest", type=str, help="Path to manifest JSON file")
    mp_parser.add_argument("relative_path", type=str, help="Relative path of file in manifest")
    mp_parser.add_argument("-o", "--output", type=str, required=True, help="Output destination for proof JSON")

    # Subcommand: merkle verify-proof
    mvp_parser = merkle_subparsers.add_parser("verify-proof", help="Verify an inclusion proof against a trusted root")
    mvp_parser.add_argument("proof", type=str, help="Path to proof JSON file")
    mvp_parser.add_argument("--data", type=str, required=True, help="Path to actual target file on disk")
    mvp_parser.add_argument("--root", type=str, required=True, help="Trusted Merkle root hash")
    mvp_parser.add_argument(
        "--relative-path",
        "--relpath",
        type=str,
        default=None,
        help="Explicit manifest relative path of target file (defaults to target filename)",
    )

    return parser


create_parser = build_parser


def main(args: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code integer."""
    prog = "cit" if (sys.argv and Path(sys.argv[0]).stem in ("cit", "cit.exe")) else "integrity"
    parser = build_parser(prog=prog)
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if parsed_args.command == "hash":
        return handle_hash(parsed_args)
    elif parsed_args.command == "fingerprint":
        return handle_fingerprint(parsed_args)
    elif parsed_args.command == "verify":
        return handle_verify(parsed_args)
    elif parsed_args.command == "merkle":
        return handle_merkle(parsed_args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
