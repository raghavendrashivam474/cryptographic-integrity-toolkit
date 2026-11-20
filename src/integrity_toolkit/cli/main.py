"""Cryptographic Integrity Toolkit CLI Main Entry Point."""

import argparse
import sys
from typing import List, Optional

from integrity_toolkit import __version__


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

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI execution entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())