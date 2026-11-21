"""Handler for the 'verify' CLI command."""
import sys
from integrity_toolkit.crypto import UnsupportedAlgorithmError
from integrity_toolkit.integrity import (
    FileAccessError,
    IntegrityError,
    InvalidManifestError,
    UnsafePathError,
    verify_manifest,
)

def _format_verification_output(report) -> str:
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

def handle_verify(args) -> int:
    """Process manifest verification command."""
    try:
        report = verify_manifest(
            root=args.root,
            manifest=args.manifest,
            ignore_unexpected=getattr(args, "ignore_unexpected", False),
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
