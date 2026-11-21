"""Handler for the 'hash' CLI command."""
import sys
from pathlib import Path
from integrity_toolkit.crypto import (
    UnsupportedAlgorithmError,
    hash_stream,
    hash_text,
)

def handle_hash(args) -> int:
    """Process hash command for text, file, or stdin."""
    algorithm = getattr(args, "algorithm", "sha256")
    text_arg = getattr(args, "text", None)
    file_arg = getattr(args, "file", None)

    if file_arg and text_arg:
        print("Error: Specify either --text or --file, not both.", file=sys.stderr)
        return 2

    if file_arg:
        file_path = Path(file_arg)
        if not file_path.exists():
            print(f"Error: File not found: {file_arg}", file=sys.stderr)
            return 3
        if not file_path.is_file():
            print(f"Error: Target path is not a file: {file_arg}", file=sys.stderr)
            return 3
        try:
            with open(file_path, "rb") as f:
                digest = hash_stream(f, algorithm=algorithm)
            print(f"Algorithm : {algorithm.upper()}")
            print(f"File      : {file_path}")
            print(f"Digest    : {digest}")
            return 0
        except UnsupportedAlgorithmError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 2
        except Exception as err:
            print(f"File Error: {err}", file=sys.stderr)
            return 3

    if text_arg is not None:
        text_input = text_arg
    else:
        if sys.stdin.isatty():
            print(
                "Error: Either --text must be provided or data must be piped via stdin.",
                file=sys.stderr,
            )
            return 1
        text_input = sys.stdin.read()

    try:
        digest = hash_text(text_input, algorithm=algorithm)
        print(f"Algorithm : {algorithm.upper()}")
        print(f"Input     : {text_input}")
        print(f"Digest    : {digest}")
        return 0
    except UnsupportedAlgorithmError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
