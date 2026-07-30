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
INDEX_LINE = re.compile(
    r"^index (?P<old>[0-9a-fA-F]+)\.\.(?P<new>[0-9a-fA-F]+)"
    r"(?: [0-7]{6})?$"
)
BINARY_PAYLOAD_HEADER = re.compile(r"^(?:literal|delta) [0-9]+$")
NO_NEWLINE_MARKER = r"\ No newline at end of file"
EMPTY_BLOB_HASHES = (
    "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "473a0f4c3be8a93681a267e3b1e9a7dcda1185436fe141f7749120a303721813",
)
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
    has_binary_summary: bool = False
    has_git_binary_marker: bool = False
    has_binary_payload_header: bool = False
    has_binary_payload_data: bool = False
    file_headers_seen: bool = False
    metadata: set[str] = field(default_factory=set)
    index_old: str | None = None
    index_new: str | None = None
    similarity: int | None = None



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



def _is_zero_hash(value: str | None) -> bool:
    return bool(value) and set(value) == {"0"}



def _is_empty_blob_hash(value: str | None) -> bool:
    if not value or len(value) < 7:
        return False
    lowered = value.lower()
    return any(full_hash.startswith(lowered) for full_hash in EMPTY_BLOB_HASHES)



def _metadata_only_section_is_valid(section: FileSection) -> bool:
    metadata = section.metadata
    mode_only = {"old mode", "new mode"} <= metadata
    empty_creation = (
        "new file mode" in metadata
        and _is_zero_hash(section.index_old)
        and _is_empty_blob_hash(section.index_new)
    )
    empty_deletion = (
        "deleted file mode" in metadata
        and _is_empty_blob_hash(section.index_old)
        and _is_zero_hash(section.index_new)
    )
    rename_only = (
        {"rename from", "rename to"} <= metadata
        and section.similarity == 100
    )
    copy_only = (
        {"copy from", "copy to"} <= metadata
        and section.similarity == 100
    )
    return mode_only or empty_creation or empty_deletion or rename_only or copy_only



def _binary_section_is_valid(section: FileSection) -> bool:
    if section.has_binary_summary:
        return True
    return (
        section.has_git_binary_marker
        and section.has_binary_payload_header
        and section.has_binary_payload_data
    )



def _finish_section(path: str, section: FileSection) -> None:
    if (
        section.has_hunk
        or _binary_section_is_valid(section)
        or _metadata_only_section_is_valid(section)
    ):
        return
    raise PatchSyntaxError(
        f"{path}:{section.start_line}: file section contains no hunks, "
        "complete binary payload, or complete metadata-only change"
    )



def _metadata_name(line: str) -> str | None:
    for prefix in METADATA_PREFIXES:
        if line.startswith(prefix):
            return prefix.rstrip()
    return None



def _record_section_metadata(section: FileSection, line: str) -> bool:
    index_match = INDEX_LINE.match(line)
    if index_match is not None:
        section.index_old = index_match.group("old")
        section.index_new = index_match.group("new")
        return True

    metadata_name = _metadata_name(line)
    if metadata_name is None:
        return False

    section.metadata.add(metadata_name)
    if metadata_name == "similarity index":
        raw_value = line.removeprefix("similarity index ").removesuffix("%")
        if raw_value.isdigit():
            section.similarity = int(raw_value)
    return True



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

        if line.startswith("Binary files "):
            if section is None:
                section = FileSection(start_line=line_number)
                saw_section = True
            section.has_binary_summary = True
            continue

        if line == "GIT binary patch":
            if section is None:
                section = FileSection(start_line=line_number)
                saw_section = True
            section.has_git_binary_marker = True
            continue

        if section is not None and section.has_git_binary_marker:
            if BINARY_PAYLOAD_HEADER.match(line):
                section.has_binary_payload_header = True
                continue
            if section.has_binary_payload_header and line:
                section.has_binary_payload_data = True
                continue

        if section is not None:
            _record_section_metadata(section, line)
        elif _metadata_name(line) is not None or INDEX_LINE.match(line):
            raise PatchSyntaxError(
                f"{path}:{line_number}: metadata appears before a file section"
            )

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
