#!/usr/bin/env python3
"""Parse retained patch files with Git without applying them.

The custom retained-patch validator provides focused diagnostics for hunk and
section errors. This companion gate delegates Git binary-patch decoding,
compression, declared-length, and extended-header parsing to Git's own parser.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
from typing import Iterable


class NativePatchSyntaxError(ValueError):
    """Raised when Git rejects a retained patch during parse-only inspection."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def discover_tracked_patches(root: Path | None = None) -> list[Path]:
    """Return repository-tracked patch files, excluding generated dependencies."""

    root = root or repository_root()
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.patch"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [
        root / raw.decode("utf-8")
        for raw in completed.stdout.split(b"\0")
        if raw
    ]


def validate_patch_with_git(path: Path) -> str:
    """Require Git to parse one patch through its non-applying numstat mode."""

    resolved = path.resolve()
    completed = subprocess.run(
        ["git", "apply", "--numstat", "--", str(resolved)],
        cwd=repository_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        raise NativePatchSyntaxError(
            f"{path}: git apply --numstat rejected retained patch: {detail}"
        )
    return completed.stdout


def validate_paths(paths: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in sorted(paths):
        try:
            output = validate_patch_with_git(path)
        except (OSError, UnicodeDecodeError, NativePatchSyntaxError) as exc:
            errors.append(str(exc))
        else:
            summary = output.strip().replace("\n", "; ") or "metadata-only patch"
            print(f"valid native Git patch parse: {path}: {summary}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="patch files to validate; defaults to every tracked *.patch file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = args.paths or discover_tracked_patches()
    errors = validate_paths(paths)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
