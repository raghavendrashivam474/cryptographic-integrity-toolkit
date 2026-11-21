"""Handler for the 'fingerprint' CLI command."""
import sys
from pathlib import Path
from integrity_toolkit.crypto import UnsupportedAlgorithmError
from integrity_toolkit.integrity import (
    FileAccessError,
    IntegrityError,
    create_manifest,
    fingerprint_file,
    save_manifest,
)

def _format_fingerprint_output(fp) -> str:
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

def handle_fingerprint(args) -> int:
    """Process fingerprint command for file or directory."""
    target_path = Path(args.target)
    algorithm = getattr(args, "algorithm", "sha256")
    output_arg = getattr(args, "output", None)

    if not target_path.exists():
        print(f"Error: Target path not found: {args.target}", file=sys.stderr)
        return 3

    try:
        if target_path.is_file():
            fp = fingerprint_file(target_path, algorithm=algorithm)
            print(_format_fingerprint_output(fp))
            return 0
        elif target_path.is_dir():
            if not output_arg:
                print(
                    "Error: --output manifest path is required when target is a directory.",
                    file=sys.stderr,
                )
                return 2
            manifest = create_manifest(
                target_path,
                algorithm=algorithm,
                exclude_paths=[output_arg],
            )
            save_path = save_manifest(manifest, output_arg)
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
