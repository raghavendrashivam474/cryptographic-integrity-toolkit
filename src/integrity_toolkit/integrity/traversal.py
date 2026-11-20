"""Directory traversal and file discovery service.

Provides safe, deterministic, recursive file discovery within a target directory root.
Applies path normalization (POSIX forward slashes), excludes specified files
(e.g. output manifest), and implements symbolic link policies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence, Union

from integrity_toolkit.integrity.exceptions import FileAccessError, UnsafePathError


def normalize_posix_path(path: Union[str, Path]) -> str:
    """Convert a path object or string to a normalized relative POSIX string (using '/').

    Windows backslashes ('\\') are converted to forward slashes ('/').
    """
    p_str = str(path).replace("\\", "/")
    # Strip leading ./ if present
    if p_str.startswith("./"):
        p_str = p_str[2:]
    return p_str


def discover_files(
    root: Union[str, Path],
    exclude_paths: Iterable[Union[str, Path]] | None = None,
    follow_symlinks: bool = False,
) -> list[str]:
    """Recursively discover eligible regular files under root directory.

    Args:
        root: Target directory path to scan.
        exclude_paths: Optional paths (relative or absolute) to exclude from discovery.
        follow_symlinks: Whether to follow symbolic links during traversal (default: False).

    Returns:
        Deterministically sorted list of normalized relative POSIX path strings.

    Raises:
        FileAccessError: If root directory does not exist or is not a directory.
        UnsafePathError: If path containment check fails during discovery.
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        raise FileAccessError(f"Directory not found: {root}")

    if not root_path.is_dir():
        raise FileAccessError(f"Path is not a directory: {root}")

    # Resolve normalized exclude list
    normalized_excludes = set()
    if exclude_paths:
        for exc in exclude_paths:
            exc_path = Path(exc)
            if exc_path.is_absolute():
                try:
                    rel_exc = exc_path.resolve().relative_to(root_path)
                    normalized_excludes.add(normalize_posix_path(rel_exc))
                except ValueError:
                    pass
            else:
                normalized_excludes.add(normalize_posix_path(exc_path))

    discovered_rel_paths: list[str] = []

    try:
        # Recursive traversal using os.walk / rglob
        for current_path in root_path.rglob("*"):
            # Check for symlink policy
            if current_path.is_symlink() and not follow_symlinks:
                continue

            if not current_path.is_file():
                continue

            # Containment check to prevent escaping root via symlinks
            resolved = current_path.resolve()
            try:
                resolved.relative_to(root_path)
            except ValueError:
                # Symlink targets outside root directory
                continue

            rel_path = current_path.relative_to(root_path)
            posix_rel = normalize_posix_path(rel_path)

            if posix_rel in normalized_excludes:
                continue

            discovered_rel_paths.append(posix_rel)

    except OSError as err:
        raise FileAccessError(f"Error accessing directory during traversal: {err}") from err

    # Return deterministically sorted relative path list
    discovered_rel_paths.sort()
    return discovered_rel_paths
