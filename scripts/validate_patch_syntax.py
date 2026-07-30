#!/usr/bin/env python3
"""Validate structural syntax of retained unified-diff patch files.

This checker verifies hunk metadata and line counts. It does not prove that a
patch applies to its claimed source revision; target workflows must still run
``git apply --check`` against an exact checkout.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

HUNK_HEADER = re.compile(
    r"^@@ -(?P<old_start>[0-9]+)(?:,(?P<old_count>[0-9]+))? "
    r"\+(?P<new_start>[0-9]+)(?:,(?P<new_count>[0-9]+))? @@(?: .*)?$"
)
NO_NEWLINE_MARKER = r"\ No newline at end of file"


class PatchSyntaxError(ValueError):
    """Raised when a retained patch is structurally malformed."""


@dataclass
class HunkState:
    header_line: int
    old_expected: int
    new_expected: int
    old_seen: int = 0
    new_seen: int = 0

    @property
    def complete(self) -> bool:
        return (
            self.old_seen == self.old_expected
            and self.new_seen == self.new_expected
        )


def _count(raw: str | None) -> int:
    return 1 if raw is None else int(raw)


def _is_patch_boundary(line: str) -> bool:
    return (
        line.startswith("diff --git ")
        or line.startswith("Index: ")
        or line.startswith("--- ")
        or line.startswith("Binary files ")
        or line.startswith("Only in ")
    )


def _finish_hunk(path: str, hunk: HunkState) -> None:
    if hunk.old_seen != hunk.old_expected or hunk.new_seen != hunk.new_expected:
        raise PatchSyntaxError(
            f"{path}:{hunk.header_line}: hunk count mismatch: "
            f"old expected {hunk.old_expected}, saw {hunk.old_seen}; "
            f"new expected {hunk.new_expected}, saw {hunk.new_seen}"
        )


def validate_patch_text(text: str, path: str = "<patch>") -> None:
    """Validate one patch file's structural unified-diff syntax."""

    lines = text.splitlines()
    hunk: HunkState | None = None
    saw_diff_header = False
    saw_hunk = False
    saw_binary_payload = False

    for line_number, line in enumerate(lines, start=1):
        header = HUNK_HEADER.match(line)

        if hunk is not None:
            if line == NO_NEWLINE_MARKER:
                continue

            if hunk.complete:
                if header is not None or _is_patch_boundary(line):
                    _finish_hunk(path, hunk)
                    hunk = None
                else:
                    raise PatchSyntaxError(
                        f"{path}:{line_number}: extra content after completed hunk "
                        f"from line {hunk.header_line}"
                    )
            elif header is not None or _is_patch_boundary(line):
                _finish_hunk(path, hunk)
                hunk = None
            else:
                if line.startswith(" "):
                    hunk.old_seen += 1
                    hunk.new_seen += 1
                elif line.startswith("-"):
                    hunk.old_seen += 1
                elif line.startswith("+"):
                    hunk.new_seen += 1
                elif line.startswith("@@"):
                    raise PatchSyntaxError(
                        f"{path}:{line_number}: malformed hunk header {line!r}"
                    )
                else:
                    raise PatchSyntaxError(
                        f"{path}:{line_number}: unexpected or truncated hunk content"
                    )

                if (
                    hunk.old_seen > hunk.old_expected
                    or hunk.new_seen > hunk.new_expected
                ):
                    raise PatchSyntaxError(
                        f"{path}:{line_number}: hunk from line {hunk.header_line} "
                        "contains more lines than declared"
                    )
                continue

        if header is not None:
            saw_hunk = True
            hunk = HunkState(
                header_line=line_number,
                old_expected=_count(header.group("old_count")),
                new_expected=_count(header.group("new_count")),
            )
            continue

        if line.startswith("@@"):
            raise PatchSyntaxError(
                f"{path}:{line_number}: malformed hunk header {line!r}"
            )
        if line.startswith("diff --git "):
            saw_diff_header = True
        if line == "GIT binary patch" or line.startswith("Binary files "):
            saw_binary_payload = True

    if hunk is not None:
        _finish_hunk(path, hunk)

    if not saw_hunk and not saw_binary_payload and not saw_diff_header:
        raise PatchSyntaxError(
            f"{path}: contains no unified-diff hunks, binary payload, or git metadata"
        )


def discover_tracked_patches() -> list[Path]:
    """Return tracked patch files so generated dependency trees are excluded."""

    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.patch"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [
        Path(raw.decode("utf-8"))
        for raw in completed.stdout.split(b"\0")
        if raw
    ]


def validate_paths(paths: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    for path in sorted(paths):
        try:
            text = path.read_text(encoding="utf-8")
            validate_patch_text(text, str(path))
        except (OSError, UnicodeDecodeError, PatchSyntaxError) as exc:
            errors.append(str(exc))
        else:
            print(f"valid patch syntax: {path}")
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
    try:
        paths = args.paths or discover_tracked_patches()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"unable to discover tracked patches: {exc}", file=sys.stderr)
        return 1

    errors = validate_paths(paths)
    if errors:
        print("Retained patch syntax violations:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"Validated {len(paths)} retained patch file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
