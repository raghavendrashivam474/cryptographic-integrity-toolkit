"""Command-line interface entry point for the Cryptographic Integrity Toolkit."""

import argparse
import sys
from pathlib import Path

import integrity_toolkit
from integrity_toolkit.crypto import (
    UnsupportedAlgorithmError,
    get_supported_algorithms,
    hash_text,
)
from integrity_toolkit.integrity import (
    DEFAULT_ALGORITHM,
    FileAccessError,
    IntegrityError,
    InvalidManifestError,
    UnsafePathError,
    create_manifest,
    fingerprint_file,
    save_manifest,
    verify_manifest,
)


def _format_fingerprint_output(fp) -> str:
    """Format single file fingerprint output for display."""
    return f"""========================================
       FILE FINGERPRINT
========================================

File       : {fp.path}
Size       : {fp.size} bytes
Algorithm  : {fp.algorithm.upper()}

Fingerprint:
{fp.digest}

Status     : SUCCESS
========================================="""


def _format_verification_output(report) -> str:
    """Format verification report output for display."""
    status_str = "SUCCESS" if report.is_success else "FAILED"
    lines = [
        "========================================",
        "        INTEGRITY VERIFICATION",
        "========================================",
        "",
        f"Manifest : {report.manifest_path}",
        f"Algorithm: {report.algorithm.upper()}",
        "",
        f"Total files : {report.total}",
        "",
        f"MATCH       : {report.matched}",
        f"MODIFIED    : {report.modified}",
        f"MISSING     : {report.missing}",
        f"UNEXPECTED  : {report.unexpected}",
        f"ERROR       : {report.error}",
        "",
        f"Overall Status: {status_str}",
        "",
        "========================================",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Construct and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="integrity",
        description="Cryptographic File Integrity and Merkle Proof Toolkit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"integrity {integrity_toolkit.__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: hash (Sprint 01 baseline)
    hash_parser = subparsers.add_parser("hash", help="Compute hash of text or file input")
    hash_parser.add_argument(
        "--text",
        type=str,
        help="Text string to compute hash for",
    )
    hash_parser.add_argument(
        "--algorithm",
        type=str,
        default=DEFAULT_ALGORITHM,
        choices=get_supported_algorithms(),
        help="Hash algorithm to use (default: sha256)",
    )

    # Command: fingerprint (Sprint 02)
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

    # Command: verify (Sprint 02)
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

    return parser


def main(args: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code integer."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if parsed_args.command == "hash":
        if not parsed_args.text:
            print("Error: --text argument is required for 'hash' command.", file=sys.stderr)
            return 2
        digest = hash_text(parsed_args.text, algorithm=parsed_args.algorithm)
        print(f"Algorithm : {parsed_args.algorithm.upper()}")
        print(f"Input     : {parsed_args.text}")
        print(f"Digest    : {digest}")
        return 0

    if parsed_args.command == "fingerprint":
        target_path = Path(parsed_args.target)
        if not target_path.exists():
            print(f"Error: Target path not found: {parsed_args.target}", file=sys.stderr)
            return 3

        try:
            if target_path.is_file():
                fp = fingerprint_file(target_path, algorithm=parsed_args.algorithm)
                print(_format_fingerprint_output(fp))
                return 0
            elif target_path.is_dir():
                if not parsed_args.output:
                    print(
                        "Error: --output manifest path is required when target is a directory.",
                        file=sys.stderr,
                    )
                    return 2
                manifest = create_manifest(
                    target_path,
                    algorithm=parsed_args.algorithm,
                    exclude_paths=[parsed_args.output],
                )
                save_path = save_manifest(manifest, parsed_args.output)
                print(f"Generated integrity manifest ({len(manifest.entries)} entries) -> {save_path}")
                return 0
            else:
                print(f"Error: Target is neither a regular file nor directory: {target_path}", file=sys.stderr)
                return 3
        except UnsupportedAlgorithmError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 2
        except FileAccessError as err:
            print(f"File Error: {err}", file=sys.stderr)
            return 3
        except IntegrityError as err:
            print(f"Integrity Error: {err}", file=sys.stderr)
            return 2

    if parsed_args.command == "verify":
        try:
            report = verify_manifest(
                root=parsed_args.root,
                manifest=parsed_args.manifest,
                ignore_unexpected=parsed_args.ignore_unexpected,
            )
            print(_format_verification_output(report))
            return 0 if report.is_success else 1
        except (InvalidManifestError, UnsafePathError, UnsupportedAlgorithmError) as err:
            print(f"Manifest Error: {err}", file=sys.stderr)
            return 2
        except FileAccessError as err:
            print(f"File Error: {err}", file=sys.stderr)
            return 3
        except IntegrityError as err:
            print(f"Verification Error: {err}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
