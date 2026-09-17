#!/usr/bin/env python3
"""Classify retained patch materialization and enforce repository policy.

Structural syntax and native Git parsing are necessary but not sufficient for
an implementation carrier. In particular, ``Binary files ... differ`` is a
parse-valid comparison summary that contains no replacement bytes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Iterable

if __package__:
    from .validate_patch_syntax import (
        HUNK_HEADER,
        PatchSyntaxError,
        discover_tracked_patches,
        validate_patch_text,
    )
    from .validate_patch_with_git import (
        NativePatchSyntaxError,
        validate_patch_with_git,
    )
else:
    from validate_patch_syntax import (
        HUNK_HEADER,
        PatchSyntaxError,
        discover_tracked_patches,
        validate_patch_text,
    )
    from validate_patch_with_git import (
        NativePatchSyntaxError,
        validate_patch_with_git,
    )

SCHEMA_VERSION = 1
BINARY_SUMMARY = "binary-summary-nonmaterializing"
EVIDENCE_ONLY_SUFFIX = ".diff-summary"
MATERIALIZABLE_KINDS = frozenset(
    {"textual-hunks", "git-binary-payload", "metadata-only"}
)


@dataclass(frozen=True)
class SectionReceipt:
    section: int
    start_line: int
    kind: str
    materializable: bool


@dataclass(frozen=True)
class PatchReceipt:
    path: str
    parse_state: str
    materialization_state: str
    section_kinds: tuple[str, ...]
    sections: tuple[SectionReceipt, ...]
    native_numstat: tuple[str, ...]


@dataclass
class _SectionState:
    start_line: int
    has_hunk: bool = False
    has_git_binary_payload: bool = False
    has_binary_summary: bool = False


def _is_file_header_boundary(lines: list[str], index: int) -> bool:
    return lines[index].startswith("--- ") and (
        index + 1 < len(lines) and lines[index + 1].startswith("+++ ")
    )


def _finish_section(
    sections: list[SectionReceipt], section: _SectionState | None
) -> None:
    if section is None:
        return
    if section.has_binary_summary:
        kind = BINARY_SUMMARY
    elif section.has_git_binary_payload:
        kind = "git-binary-payload"
    elif section.has_hunk:
        kind = "textual-hunks"
    else:
        # The structural validator already proved that a section without hunks
        # or binary content is a complete supported metadata-only change.
        kind = "metadata-only"
    sections.append(
        SectionReceipt(
            section=len(sections) + 1,
            start_line=section.start_line,
            kind=kind,
            materializable=kind in MATERIALIZABLE_KINDS,
        )
    )


def classify_patch_text(text: str, path: str = "<patch>") -> tuple[SectionReceipt, ...]:
    """Return section classifications after structural validation succeeds."""

    validate_patch_text(text, path)
    lines = text.splitlines()
    sections: list[SectionReceipt] = []
    current: _SectionState | None = None
    file_headers_seen = False

    for index, line in enumerate(lines):
        line_number = index + 1
        diff_boundary = line.startswith("diff --git ") or line.startswith("Index: ")
        file_header_boundary = _is_file_header_boundary(lines, index)

        if diff_boundary:
            _finish_section(sections, current)
            current = _SectionState(start_line=line_number)
            file_headers_seen = False
        elif file_header_boundary:
            if current is None:
                current = _SectionState(start_line=line_number)
            elif file_headers_seen:
                _finish_section(sections, current)
                current = _SectionState(start_line=line_number)
            file_headers_seen = True

        if HUNK_HEADER.match(line):
            if current is None:
                raise AssertionError("validated hunk has no section")
            current.has_hunk = True
        elif line == "GIT binary patch":
            if current is None:
                current = _SectionState(start_line=line_number)
            current.has_git_binary_payload = True
        elif line.startswith("Binary files "):
            if current is None:
                current = _SectionState(start_line=line_number)
            current.has_binary_summary = True

    _finish_section(sections, current)
    if not sections:
        raise AssertionError("validated patch produced no section classification")
    return tuple(sections)


def inspect_patch(path: Path) -> PatchReceipt:
    """Run both parser layers and return one machine-readable classification."""

    text = path.read_text(encoding="utf-8")
    sections = classify_patch_text(text, str(path))
    native_output = validate_patch_with_git(path)
    native_numstat = tuple(line for line in native_output.splitlines() if line.strip())
    materializable = all(section.materializable for section in sections)
    return PatchReceipt(
        path=str(path),
        parse_state="parse-valid",
        materialization_state=(
            "materializable" if materializable else "nonmaterializing"
        ),
        section_kinds=tuple(section.kind for section in sections),
        sections=sections,
        native_numstat=native_numstat,
    )


def policy_violation(path: Path, receipt: PatchReceipt) -> str | None:
    """Allow nonmaterializing summaries only under one explicit evidence suffix."""

    if receipt.materialization_state == "materializable":
        return None
    if path.suffix == EVIDENCE_ONLY_SUFFIX:
        return None
    return (
        f"{path}: {BINARY_SUMMARY} is allowed only under the explicit "
        f"evidence-only suffix {EVIDENCE_ONLY_SUFFIX}; retain replacement "
        "bytes for an implementation carrier"
    )


def build_receipt(paths: Iterable[Path]) -> tuple[dict[str, object], list[str]]:
    files: list[dict[str, object]] = []
    violations: list[str] = []

    for path in sorted(paths):
        try:
            receipt = inspect_patch(path)
        except (
            OSError,
            UnicodeDecodeError,
            PatchSyntaxError,
            NativePatchSyntaxError,
        ) as exc:
            violations.append(str(exc))
            continue

        files.append(asdict(receipt))
        violation = policy_violation(path, receipt)
        if violation is not None:
            violations.append(violation)

    document: dict[str, object] = {
        "schemaVersion": SCHEMA_VERSION,
        "evidenceClass": "parse-and-materialization-policy",
        "files": files,
        "policyViolations": violations,
    }
    return document, violations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="artifacts to inspect; defaults to every tracked *.patch file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional JSON receipt path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paths = args.paths or discover_tracked_patches()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"unable to discover tracked patches: {exc}", file=sys.stderr)
        return 1

    document, violations = build_receipt(paths)
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

    if violations:
        print("Retained patch policy violations:", file=sys.stderr)
        print("\n".join(violations), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
