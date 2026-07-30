#!/usr/bin/env python3
"""Validate structural syntax of retained unified-diff patch files.

This checker verifies hunk metadata and line counts. It does not prove that a
patch applies to its claimed source revision; target workflows must still run
``git apply --check`` against an exact checkout.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
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
METADATA_PREFIXES = (
    "old mode ",
    "new mode ",
    "new file mode ",
    "deleted file mode ",
    "similarity index ",
    "dissimilarity index ",
    "rename from ",
    "rename to ",
    "copy from ",
    "copy to ",
)


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


@dataclass
class FileSection:
    start_line: int
    has_hunk: bool = False
    has_binary: bool = False
    file_headers_seen: bool = False
    metadata: set[str] = field(default_factory=set)


def _count(raw: str | None) -> int:
    return 1 if raw is None else int(raw)


def _is_hard_boundary(line: str) -> bool:
    return (
        line.startswith("diff --git ")
        or line.startswith("Index: ")
        or line.startswith("Binary files ")
        or line.startswith("Only in ")
    )


def _is_file_header_boundary(line: str, next_line: str | None) -> bool:
    return line.startswith("--- ") and bool(
        next_line is not None and next_line.startswith("+++ ")
    )


def _finish_hunk(path: str, hunk: HunkState) -> None:
    if hunk.old_seen != hunk.old_expected or hunk.new_seen != hunk.new_expected:
        raise PatchSyntaxError(
            f"{path}:{hunk.header_line}: hunk count mismatch: "
            f"old expected {hunk.old_expected}, saw {hunk.old_seen}; "
            f"new expected {hunk.new_expected}, saw {hunk.new_seen}"
        )


def _metadata_only_section_is_valid(section: FileSection) -> bool:
    metadata = section.metadata
    return (
        {"old mode", "new mode"} <= metadata
        or "new file mode" in metadata
        or "deleted file mode" in metadata
        or {"rename from", "rename to"} <= metadata
        or {"copy from", "copy to"} <= metadata
    )


def _finish_section(path: str, section: FileSection) -> None:
    if (
        section.has_hunk
        or section.has_binary
        or _metadata_only_section_is_valid(section)
    ):
        return
    raise PatchSyntaxError(
        f"{path}:{section.start_line}: file section contains no hunks, "
        "binary payload, or complete metadata-only change"
    )


def _metadata_name(line: str) -> str | None:
    for prefix in METADATA_PREFIXES:
        if line.startswith(prefix):
            return prefix.rstrip()
    return None


def validate_patch_text(text: str, path: str = "<patch>") -> None:
    """Validate one patch file's structural unified-diff syntax."""

    lines = text.splitlines()
    hunk: HunkState | None = None
    section: FileSection | None = None
    saw_section = False

    for index, line in enumerate(lines):
        line_number = index + 1
        next_line = lines[index + 1] if index + 1 < len(lines) else None
        header = HUNK_HEADER.match(line)
        diff_boundary = line.startswith("diff --git ") or line.startswith("Index: ")
        hard_boundary = _is_hard_boundary(line)
        file_header_boundary = _is_file_header_boundary(line, next_line)

        if hunk is not None:
            if line == NO_NEWLINE_MARKER:
                continue

            if hunk.complete:
                if header is not None or hard_boundary or file_header_boundary:
                    _finish_hunk(path, hunk)
                    hunk = None
                else:
                    raise PatchSyntaxError(
                        f"{path}:{line_number}: extra content after completed hunk "
                        f"from line {hunk.header_line}"
                    )
            elif header is not None or hard_boundary:
                _finish_hunk(path, hunk)
                hunk = None
            else:
                # While a hunk is incomplete, every prefixed line is content.
                # A deleted source line beginning "-- " appears as "--- " in
                # the patch and must not be mistaken for a file header.
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

        if diff_boundary:
            if section is not None:
                _finish_section(path, section)
            section = FileSection(start_line=line_number)
            saw_section = True
        elif file_header_boundary:
            if section is None:
                section = FileSection(start_line=line_number)
                saw_section = True
            elif section.file_headers_seen:
                _finish_section(path, section)
                section = FileSection(start_line=line_number)
            section.file_headers_seen = True

        if header is not None:
            if section is None:
                raise PatchSyntaxError(
                    f"{path}:{line_number}: hunk appears before a file section"
                )
            section.has_hunk = True
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

        if line == "GIT binary patch" or line.startswith("Binary files "):
            if section is None:
                section = FileSection(start_line=line_number)
                saw_section = True
            section.has_binary = True

        metadata_name = _metadata_name(line)
        if metadata_name is not None:
            if section is None:
                raise PatchSyntaxError(
                    f"{path}:{line_number}: metadata appears before a file section"
                )
            section.metadata.add(metadata_name)

    if hunk is not None:
        _finish_hunk(path, hunk)
    if section is not None:
        _finish_section(path, section)
    if not saw_section:
        raise PatchSyntaxError(f"{path}: contains no patch file sections")


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
