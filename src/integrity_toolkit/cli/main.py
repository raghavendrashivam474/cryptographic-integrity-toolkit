"""Cryptographic Integrity Toolkit CLI Main Entry Point."""

import argparse
import sys
from typing import List, Optional

from integrity_toolkit import __version__
from integrity_toolkit.crypto import (
    CryptoError,
    hash_stream,
    hash_text,
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="integrity",
        description="Cryptographic Integrity Toolkit — Cryptographic file integrity and Merkle proof CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"integrity {__version__}",
        help="Show program's version number and exit.",
    )

    subparsers = parser.add_subparsers(
        title="available commands",
        dest="command",
        metavar="COMMAND",
        help="Sub-command to execute",
    )

    # Sprint 01 Demonstration Command: integrity hash
    hash_parser = subparsers.add_parser(
        "hash",
        help="Calculate cryptographic hash digest of input text or stream.",
    )
    hash_parser.add_argument(
        "-t",
        "--text",
        type=str,
        help="Text string payload to hash.",
    )
    hash_parser.add_argument(
        "-a",
        "--algorithm",
        type=str,
        default="sha256",
        help="Cryptographic hash algorithm (sha256, sha512, blake2b). Default: sha256",
    )

    return parser


def handle_hash_command(args: argparse.Namespace) -> int:
    """Execute the 'hash' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    algorithm = args.algorithm

    try:
        if args.text is not None:
            digest = hash_text(args.text, algorithm=algorithm)
            input_desc = args.text
        elif not sys.stdin.isatty():
            # Reading from stdin stream (e.g. piped input)
            digest = hash_stream(sys.stdin.buffer, algorithm=algorithm)
            input_desc = "<stdin>"
        else:
            sys.stderr.write("Error: Either --text must be provided or data must be piped via stdin.\n")
            return 1

        algo_label = algorithm.upper()
        sys.stdout.write(f"Algorithm : {algo_label}\n")
        sys.stdout.write(f"Input     : {input_desc}\n")
        sys.stdout.write(f"Digest    : {digest}\n")
        return 0

    except CryptoError as err:
        sys.stderr.write(f"Error: {err}\n")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """CLI execution entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "hash":
        return handle_hash_command(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
