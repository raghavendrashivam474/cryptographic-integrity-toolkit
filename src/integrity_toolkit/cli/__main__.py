"""Executable module entry point for python -m integrity_toolkit.cli."""
import sys
from integrity_toolkit.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
