#!/usr/bin/env python3
"""Classify retained patch materialization and bind repository artifacts to Git blobs.

Structural syntax and native Git parsing are necessary but not sufficient for
an implementation carrier. In particular, ``Binary files ... differ`` is a
parse-valid comparison summary that contains no replacement bytes.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from typing import Any, Iterable

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

SCHEMA_VERSION = 2
BINARY_SUMMARY = "binary-summary-nonmaterializing"
EVIDENCE_ONLY_SUFFIX = ".diff-summary"
TRACKED_ARTIFACT_PATTERNS = ("*.patch", "*.diff", "*.diff-summary")
MATERIALIZABLE_KINDS = frozenset(
    {"textual-hunks", "git-binary-payload", "metadata-only"}
)
IMPLEMENTATION_ROLE = "implementation-carrier"
EVIDENCE_ROLE = "evidence-summary"


class ArtifactIdentityError(ValueError):
    """Raised when filesystem or tracked-blob identity is unsafe or inconsistent."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        identity_fields: dict[str, object] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.identity_fields = identity_fields or {}


@dataclass(frozen=True)
class SectionReceipt:
    section: int
    start_line: int
    kind: str
    materializable: bool


@dataclass(frozen=True)
class ArtifactIdentity:
    repository_state: str
    repository_policy_eligible: bool
    git_path: str | None
    git_mode: str | None
    git_blob_oid: str | None
    raw_sha256: str
    byte_length: int


@dataclass(frozen=True)
class PatchReceipt:
    path: str
    artifact_role: str
    repository_state: str
    repository_policy_eligible: bool
    git_path: str | None
    git_mode: str | None
    git_blob_oid: str | None
    raw_sha256: str
    byte_length: int
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


def artifact_role(path: Path) -> str:
    if path.name.endswith(EVIDENCE_ONLY_SUFFIX):
        return EVIDENCE_ROLE
    return IMPLEMENTATION_ROLE


def discover_tracked_materialization_artifacts(root: Path = Path(".")) -> list[Path]:
    """Return every tracked artifact governed by materialization policy."""

    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", *TRACKED_ARTIFACT_PATTERNS],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    names = completed.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return sorted(root / name for name in names if name)


def _run_git(
    root: Path,
    *args: str,
    input_bytes: bytes | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        detail = os.fsdecode(completed.stderr).strip() or "unknown Git error"
        raise ArtifactIdentityError("git-command-failed", detail)
    return completed


def _find_repository_root(path: Path) -> Path | None:
    completed = _run_git(path.parent, "rev-parse", "--show-toplevel")
    if completed.returncode != 0:
        return None
    return Path(os.fsdecode(completed.stdout).strip()).absolute()


def _stage_entry(root: Path, relative: Path) -> tuple[str, str, str] | None:
    completed = _run_git(
        root,
        "ls-files",
        "--stage",
        "-z",
        "--error-unmatch",
        "--",
        os.fspath(relative),
    )
    if completed.returncode != 0:
        return None
    records = [record for record in completed.stdout.split(b"\0") if record]
    if len(records) != 1:
        raise ArtifactIdentityError(
            "ambiguous-index-entry",
            f"{relative}: expected one stage-0 index entry, found {len(records)}",
        )
    try:
        metadata, raw_name = records[0].split(b"\t", 1)
        raw_mode, raw_oid, raw_stage = metadata.split()
    except ValueError as exc:
        raise ArtifactIdentityError(
            "malformed-index-entry",
            f"{relative}: malformed git ls-files --stage output",
        ) from exc
    mode = raw_mode.decode("ascii")
    oid = raw_oid.decode("ascii")
    stage = raw_stage.decode("ascii")
    recorded_name = os.fsdecode(raw_name)
    if stage != "0":
        raise ArtifactIdentityError(
            "nonzero-index-stage",
            f"{relative}: index stage must be 0, observed {stage}",
        )
    if recorded_name != os.fspath(relative):
        raise ArtifactIdentityError(
            "index-path-mismatch",
            f"{relative}: index recorded unexpected path {recorded_name!r}",
        )
    return mode, oid, stage


def _identity_fields(
    *,
    repository_state: str,
    repository_policy_eligible: bool,
    git_path: str | None,
    git_mode: str | None,
    git_blob_oid: str | None,
    raw_sha256: str | None,
    byte_length: int | None,
) -> dict[str, object]:
    return {
        "repository_state": repository_state,
        "repository_policy_eligible": repository_policy_eligible,
        "git_path": git_path,
        "git_mode": git_mode,
        "git_blob_oid": git_blob_oid,
        "raw_sha256": raw_sha256,
        "byte_length": byte_length,
    }


def _read_regular_file_no_follow(path: Path) -> bytes:
    try:
        before = path.lstat()
    except OSError as exc:
        raise ArtifactIdentityError("filesystem-read-failed", f"{path}: {exc}") from exc
    if stat.S_ISLNK(before.st_mode):
        raise ArtifactIdentityError(
            "symlink-not-allowed",
            f"{path}: retained artifacts must not be symlinks",
        )
    if not stat.S_ISREG(before.st_mode):
        raise ArtifactIdentityError(
            "non-regular-file",
            f"{path}: retained artifacts must be regular files",
        )

    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ArtifactIdentityError("filesystem-open-failed", f"{path}: {exc}") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ArtifactIdentityError(
                "non-regular-file",
                f"{path}: opened retained artifact is not a regular file",
            )
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ArtifactIdentityError(
                "path-changed-during-open",
                f"{path}: pathname identity changed while opening retained artifact",
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)

    try:
        after = path.lstat()
    except OSError as exc:
        raise ArtifactIdentityError(
            "path-changed-during-read", f"{path}: {exc}"
        ) from exc
    if (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino):
        raise ArtifactIdentityError(
            "path-changed-during-read",
            f"{path}: pathname identity changed while reading retained artifact",
        )
    return b"".join(chunks)


def inspect_artifact_identity(path: Path) -> tuple[ArtifactIdentity, bytes]:
    """Return exact filesystem/Git identity and the bytes safe to classify."""

    absolute = path.absolute()
    root = _find_repository_root(absolute)
    relative: Path | None = None
    stage: tuple[str, str, str] | None = None
    if root is not None:
        try:
            relative = absolute.relative_to(root)
        except ValueError:
            relative = None
        if relative is not None:
            stage = _stage_entry(root, relative)

    stage_fields = {
        "git_path": os.fspath(relative) if relative is not None else None,
        "git_mode": stage[0] if stage is not None else None,
        "git_blob_oid": stage[1] if stage is not None else None,
    }

    try:
        raw = _read_regular_file_no_follow(absolute)
    except ArtifactIdentityError as exc:
        state = "tracked-invalid" if stage is not None else "identity-error"
        fields = _identity_fields(
            repository_state=state,
            repository_policy_eligible=False,
            raw_sha256=None,
            byte_length=None,
            **stage_fields,
        )
        raise ArtifactIdentityError(
            exc.code,
            str(exc),
            identity_fields=fields,
        ) from exc

    digest = hashlib.sha256(raw).hexdigest()
    if root is None or relative is None or stage is None:
        return (
            ArtifactIdentity(
                repository_state="explicit-untracked",
                repository_policy_eligible=False,
                git_path=os.fspath(relative) if relative is not None else None,
                git_mode=None,
                git_blob_oid=None,
                raw_sha256=digest,
                byte_length=len(raw),
            ),
            raw,
        )

    mode, oid, _ = stage
    tracked_fields = _identity_fields(
        repository_state="tracked-invalid",
        repository_policy_eligible=False,
        git_path=os.fspath(relative),
        git_mode=mode,
        git_blob_oid=oid,
        raw_sha256=digest,
        byte_length=len(raw),
    )
    if mode not in {"100644", "100755"}:
        raise ArtifactIdentityError(
            "unsupported-git-mode",
            f"{path}: tracked retained artifact has unsupported Git mode {mode}",
            identity_fields=tracked_fields,
        )
    try:
        blob = _run_git(root, "cat-file", "blob", oid, check=True).stdout
    except ArtifactIdentityError as exc:
        raise ArtifactIdentityError(
            exc.code,
            f"{path}: unable to read tracked blob {oid}: {exc}",
            identity_fields=tracked_fields,
        ) from exc
    if blob != raw:
        dirty_fields = dict(tracked_fields)
        dirty_fields["repository_state"] = "tracked-dirty"
        raise ArtifactIdentityError(
            "working-tree-blob-mismatch",
            f"{path}: working-tree bytes do not match tracked blob {oid}",
            identity_fields=dirty_fields,
        )
    if _stage_entry(root, relative) != stage:
        raise ArtifactIdentityError(
            "index-changed-during-inspection",
            f"{path}: tracked index identity changed during inspection",
            identity_fields=tracked_fields,
        )

    return (
        ArtifactIdentity(
            repository_state="tracked-clean",
            repository_policy_eligible=True,
            git_path=os.fspath(relative),
            git_mode=mode,
            git_blob_oid=oid,
            raw_sha256=digest,
            byte_length=len(raw),
        ),
        raw,
    )


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


def _validate_raw_with_git(raw: bytes, path: Path) -> str:
    """Run Git's parser on the exact bytes already bound to the receipt."""

    suffix = "".join(path.suffixes) or ".patch"
    with tempfile.TemporaryDirectory() as temporary:
        candidate = Path(temporary) / f"candidate{suffix}"
        candidate.write_bytes(raw)
        return validate_patch_with_git(candidate)


def _inspect_bound_patch(
    path: Path,
    identity: ArtifactIdentity,
    raw: bytes,
) -> PatchReceipt:
    text = raw.decode("utf-8")
    sections = classify_patch_text(text, str(path))
    native_output = _validate_raw_with_git(raw, path)
    native_numstat = tuple(line for line in native_output.splitlines() if line.strip())
    materializable = all(section.materializable for section in sections)
    return PatchReceipt(
        path=str(path),
        artifact_role=artifact_role(path),
        repository_state=identity.repository_state,
        repository_policy_eligible=identity.repository_policy_eligible,
        git_path=identity.git_path,
        git_mode=identity.git_mode,
        git_blob_oid=identity.git_blob_oid,
        raw_sha256=identity.raw_sha256,
        byte_length=identity.byte_length,
        parse_state="parse-valid",
        materialization_state=(
            "materializable" if materializable else "nonmaterializing"
        ),
        section_kinds=tuple(section.kind for section in sections),
        sections=sections,
        native_numstat=native_numstat,
    )


def inspect_patch(path: Path) -> PatchReceipt:
    """Bind exact bytes to repository identity, then run both parser layers."""

    identity, raw = inspect_artifact_identity(path)
    return _inspect_bound_patch(path, identity, raw)


def policy_violation(path: Path, receipt: PatchReceipt) -> str | None:
    """Keep evidence summaries nonmaterializing and carriers materializable."""

    if receipt.artifact_role == EVIDENCE_ROLE:
        if receipt.materialization_state == "nonmaterializing":
            return None
        return (
            f"{path}: {EVIDENCE_ONLY_SUFFIX} is evidence-only and must not contain "
            "a materializable implementation carrier"
        )
    if receipt.materialization_state == "materializable":
        return None
    return (
        f"{path}: {BINARY_SUMMARY} is allowed only under the explicit "
        f"evidence-only suffix {EVIDENCE_ONLY_SUFFIX}; retain replacement "
        "bytes for an implementation carrier"
    )


def _failure_entry(
    path: Path,
    exc: BaseException,
    identity: ArtifactIdentity | None,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "path": str(path),
        "artifact_role": artifact_role(path),
        "parse_state": "not-inspected"
        if isinstance(exc, ArtifactIdentityError)
        else "parse-invalid",
        "materialization_state": "unknown",
        "section_kinds": [],
        "sections": [],
        "native_numstat": [],
        "error_type": type(exc).__name__,
        "error_code": (
            getattr(exc, "code", None)
            or (
                "internal-classifier-error"
                if isinstance(exc, AssertionError)
                else type(exc).__name__
            )
        ),
        "error_message": str(exc),
    }
    if identity is not None:
        entry.update(asdict(identity))
    elif isinstance(exc, ArtifactIdentityError) and exc.identity_fields:
        entry.update(exc.identity_fields)
    else:
        entry.update(
            _identity_fields(
                repository_state="identity-error",
                repository_policy_eligible=False,
                git_path=None,
                git_mode=None,
                git_blob_oid=None,
                raw_sha256=None,
                byte_length=None,
            )
        )
    return entry


def build_receipt(paths: Iterable[Path]) -> tuple[dict[str, object], list[str]]:
    files: list[dict[str, object]] = []
    violations: list[str] = []
    role_counts = {IMPLEMENTATION_ROLE: 0, EVIDENCE_ROLE: 0}
    state_counts: dict[str, int] = {}

    for path in sorted(paths):
        role_counts[artifact_role(path)] += 1
        identity: ArtifactIdentity | None = None
        try:
            identity, raw = inspect_artifact_identity(path)
            receipt = _inspect_bound_patch(path, identity, raw)
        except (
            ArtifactIdentityError,
            OSError,
            UnicodeDecodeError,
            PatchSyntaxError,
            NativePatchSyntaxError,
            AssertionError,
        ) as exc:
            entry = _failure_entry(path, exc, identity)
            files.append(entry)
            violations.append(f"{path}: {entry['error_code']}: {exc}")
            state = str(entry["repository_state"])
            state_counts[state] = state_counts.get(state, 0) + 1
            continue

        files.append(asdict(receipt))
        state_counts[receipt.repository_state] = (
            state_counts.get(receipt.repository_state, 0) + 1
        )
        violation = policy_violation(path, receipt)
        if violation is not None:
            violations.append(violation)

    document: dict[str, object] = {
        "schemaVersion": SCHEMA_VERSION,
        "evidenceClass": "parse-materialization-and-blob-identity-policy",
        "artifactRoleCounts": role_counts,
        "repositoryStateCounts": state_counts,
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
