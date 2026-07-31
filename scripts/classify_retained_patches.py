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
        validate_patch_text,
    )
    from validate_patch_with_git import (
        NativePatchSyntaxError,
        validate_patch_with_git,
    )

SCHEMA_VERSION = 1
BINARY_SUMMARY = "binary-summary-nonmaterializing"
EVIDENCE_ONLY_SUFFIX = ".diff-summary"
TRACKED_ARTIFACT_PATTERNS = ("*.patch", "*.diff", "*.diff-summary")
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


@dataclass
class _HunkRemainder:
    old: int
    new: int

    @property
    def complete(self) -> bool:
        return self.old == 0 and self.new == 0


def discover_tracked_materialization_artifacts(root: Path = Path(".")) -> list[Path]:
    """Return every tracked artifact governed by materialization policy.

    Structural and native patch validators may deliberately retain their
    narrower ``*.patch`` contract. Materialization policy owns a wider naming
    boundary because ``*.diff`` must fail closed and ``*.diff-summary`` must
    remain explicitly visible as evidence-only.
    """

    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", *TRACKED_ARTIFACT_PATTERNS],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    names = completed.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return sorted(root / name for name in names if name)


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


def _consume_hunk_line(remainder: _HunkRemainder, line: str) -> None:
    if line.startswith(" "):
        remainder.old -= 1
        remainder.new -= 1
    elif line.startswith("-"):
        remainder.old -= 1
    elif line.startswith("+"):
        remainder.new -= 1
    elif line == r"\ No newline at end of file":
        return
    else:
        raise AssertionError("validated hunk contains an unsupported body line")

    if remainder.old < 0 or remainder.new < 0:
        raise AssertionError("validated hunk exceeded its declared line counts")


def classify_patch_text(text: str, path: str = "<patch>") -> tuple[SectionReceipt, ...]:
    """Return section classifications after structural validation succeeds."""

    validate_patch_text(text, path)
    lines = text.splitlines()
    sections: list[SectionReceipt] = []
    current: _SectionState | None = None
    file_headers_seen = False
    hunk: _HunkRemainder | None = None

    for index, line in enumerate(lines):
        line_number = index + 1

        # Hunk body content is data, even when a deleted line starts ``-- ``
        # and the next added line starts ``++ ``. In raw unified-diff text those
        # lines look like ``--- `` / ``+++ `` file headers, so they must be
        # consumed under the declared hunk counts before boundary detection.
        if hunk is not None:
            _consume_hunk_line(hunk, line)
            if hunk.complete:
                hunk = None
            continue

        hunk_match = HUNK_HEADER.match(line)
        if hunk_match:
            if current is None:
                raise AssertionError("validated hunk has no section")
            current.has_hunk = True
            hunk = _HunkRemainder(
                old=int(hunk_match.group("old_count") or "1"),
                new=int(hunk_match.group("new_count") or "1"),
            )
            if hunk.complete:
                hunk = None
            continue

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

        if line == "GIT binary patch":
            if current is None:
                current = _SectionState(start_line=line_number)
            current.has_git_binary_payload = True
        elif line.startswith("Binary files "):
            if current is None:
                current = _SectionState(start_line=line_number)
            current.has_binary_summary = True

    if hunk is not None:
        raise AssertionError("validated patch ended inside a hunk")
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
        help=(
            "artifacts to inspect; defaults to every tracked *.patch, *.diff, "
            "and *.diff-summary file"
        ),
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
        paths = args.paths or discover_tracked_materialization_artifacts()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"unable to discover tracked retained artifacts: {exc}", file=sys.stderr)
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