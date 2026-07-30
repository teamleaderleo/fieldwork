#!/usr/bin/env python3
"""Audit exact pull-request heads recorded in Fieldwork review and delivery desks.

The evaluator is read-only. It validates explicit HTML-comment markers in issue
bodies and compares them with live owned pull-request metadata, or with a
retained JSON snapshot for focused tests.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable
from urllib import error, request

MARKER_PREFIX = "fieldwork:desk-ref"
LANES = {"R1", "R2", "R3", "D0", "D1", "D2", "D3"}
REPOSITORY_PATTERN = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
REPOSITORY_RE = re.compile(rf"{REPOSITORY_PATTERN}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
MARKER_BLOCK_RE = re.compile(r"<!--\s*fieldwork:desk-ref\b.*?-->", re.DOTALL)
MARKER_RE = re.compile(
    rf"<!--\s*{re.escape(MARKER_PREFIX)}\s+"
    rf"repo=(?P<repository>{REPOSITORY_PATTERN})\s+"
    r"pr=(?P<pr>[1-9][0-9]*)\s+"
    r"head=(?P<head>[0-9a-f]{40})\s+"
    r"lane=(?P<lane>R1|R2|R3|D0|D1|D2|D3)\s*-->",
    re.DOTALL,
)


class AuditInputError(ValueError):
    """The issue markers or retained snapshot are malformed."""


class AuditTransportError(RuntimeError):
    """Live GitHub metadata could not be retrieved or decoded."""


class AuditNotFound(AuditTransportError):
    """A requested live GitHub object does not exist or is inaccessible."""


@dataclass(frozen=True)
class DeskReference:
    issue_repository: str
    issue_number: int
    repository: str
    pr_number: int
    expected_head: str
    lane: str

    @property
    def pr_key(self) -> str:
        return f"{self.repository}#{self.pr_number}"


@dataclass(frozen=True)
class PullRequestState:
    repository: str
    number: int
    head_sha: str
    state: str
    merged: bool
    draft: bool = False

    @property
    def key(self) -> str:
        return f"{self.repository}#{self.number}"


@dataclass(frozen=True)
class AuditFinding:
    code: str
    message: str
    issue_repository: str | None = None
    issue_number: int | None = None
    repository: str | None = None
    pr_number: int | None = None
    lane: str | None = None
    expected_head: str | None = None
    actual_head: str | None = None


def parse_references(
    body: str,
    *,
    issue_repository: str,
    issue_number: int,
) -> list[DeskReference]:
    if not isinstance(body, str):
        raise AuditInputError(
            f"{issue_repository}#{issue_number} body must be a string"
        )

    blocks = MARKER_BLOCK_RE.findall(body)
    if MARKER_PREFIX in body and not blocks:
        raise AuditInputError(
            f"{issue_repository}#{issue_number} contains an unterminated desk marker"
        )
    if not blocks:
        raise AuditInputError(
            f"{issue_repository}#{issue_number} contains no desk references"
        )

    references: list[DeskReference] = []
    seen: set[tuple[str, int]] = set()
    for index, block in enumerate(blocks):
        match = MARKER_RE.fullmatch(block)
        if match is None:
            compact = " ".join(block.split())
            raise AuditInputError(
                f"{issue_repository}#{issue_number} desk marker {index} is malformed: "
                f"{compact}"
            )
        repository = match.group("repository")
        pr_number = int(match.group("pr"))
        lane = match.group("lane")
        identity = (repository, pr_number)
        if identity in seen:
            raise AuditInputError(
                f"{issue_repository}#{issue_number} duplicates desk reference "
                f"{repository}#{pr_number}"
            )
        seen.add(identity)
        references.append(
            DeskReference(
                issue_repository=issue_repository,
                issue_number=issue_number,
                repository=repository,
                pr_number=pr_number,
                expected_head=match.group("head"),
                lane=lane,
            )
        )
    return references


def audit_references(
    references: Iterable[DeskReference],
    pull_requests: dict[str, PullRequestState],
) -> list[AuditFinding]:
    refs = list(references)
    findings: list[AuditFinding] = []

    expected_by_pr: dict[str, str] = {}
    for ref in refs:
        previous = expected_by_pr.get(ref.pr_key)
        if previous is not None and previous != ref.expected_head:
            findings.append(
                AuditFinding(
                    code="conflicting_expected_heads",
                    message=(
                        f"{ref.pr_key} is referenced with both {previous} and "
                        f"{ref.expected_head}"
                    ),
                    issue_repository=ref.issue_repository,
                    issue_number=ref.issue_number,
                    repository=ref.repository,
                    pr_number=ref.pr_number,
                    lane=ref.lane,
                    expected_head=ref.expected_head,
                    actual_head=previous,
                )
            )
        else:
            expected_by_pr[ref.pr_key] = ref.expected_head

    for ref in refs:
        pr = pull_requests.get(ref.pr_key)
        if pr is None:
            findings.append(
                AuditFinding(
                    code="missing_pull_request",
                    message=f"{ref.pr_key} could not be resolved",
                    issue_repository=ref.issue_repository,
                    issue_number=ref.issue_number,
                    repository=ref.repository,
                    pr_number=ref.pr_number,
                    lane=ref.lane,
                    expected_head=ref.expected_head,
                )
            )
            continue
        if pr.merged:
            findings.append(
                AuditFinding(
                    code="merged_active_entry",
                    message=f"{ref.pr_key} is merged but remains an active desk entry",
                    issue_repository=ref.issue_repository,
                    issue_number=ref.issue_number,
                    repository=ref.repository,
                    pr_number=ref.pr_number,
                    lane=ref.lane,
                    expected_head=ref.expected_head,
                    actual_head=pr.head_sha,
                )
            )
        elif pr.state != "open":
            findings.append(
                AuditFinding(
                    code="closed_active_entry",
                    message=(
                        f"{ref.pr_key} is {pr.state!r} but remains an active desk entry"
                    ),
                    issue_repository=ref.issue_repository,
                    issue_number=ref.issue_number,
                    repository=ref.repository,
                    pr_number=ref.pr_number,
                    lane=ref.lane,
                    expected_head=ref.expected_head,
                    actual_head=pr.head_sha,
                )
            )
        if pr.head_sha != ref.expected_head:
            findings.append(
                AuditFinding(
                    code="stale_head",
                    message=(
                        f"{ref.pr_key} desk head {ref.expected_head} differs from "
                        f"live head {pr.head_sha}"
                    ),
                    issue_repository=ref.issue_repository,
                    issue_number=ref.issue_number,
                    repository=ref.repository,
                    pr_number=ref.pr_number,
                    lane=ref.lane,
                    expected_head=ref.expected_head,
                    actual_head=pr.head_sha,
                )
            )

    findings.sort(
        key=lambda finding: (
            finding.code,
            finding.repository or "",
            finding.pr_number or 0,
            finding.issue_number or 0,
            finding.lane or "",
        )
    )
    return findings


class GitHubReader:
    def __init__(
        self,
        *,
        api_url: str = "https://api.github.com",
        token: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def get_json(self, path: str) -> dict[str, Any]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "fieldwork-desk-head-audit/1",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = f"{self.api_url}{path}"
        req = request.Request(url, headers=headers)
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                payload = json.load(response)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404:
                raise AuditNotFound(f"GitHub returned 404 for {url}") from exc
            raise AuditTransportError(
                f"GitHub request failed {exc.code} for {url}: {detail}"
            ) from exc
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise AuditTransportError(f"GitHub request failed for {url}: {exc}") from exc
        if not isinstance(payload, dict):
            raise AuditTransportError(f"GitHub returned a non-object payload for {url}")
        return payload


def load_live(
    *,
    issue_repository: str,
    issue_numbers: list[int],
    api_url: str,
    token: str | None,
) -> tuple[list[DeskReference], dict[str, PullRequestState]]:
    reader = GitHubReader(api_url=api_url, token=token)
    references: list[DeskReference] = []
    for issue_number in issue_numbers:
        issue = reader.get_json(
            f"/repos/{issue_repository}/issues/{issue_number}"
        )
        references.extend(
            parse_references(
                issue.get("body") or "",
                issue_repository=issue_repository,
                issue_number=issue_number,
            )
        )

    pull_requests: dict[str, PullRequestState] = {}
    for ref in references:
        if ref.pr_key in pull_requests:
            continue
        try:
            pr = reader.get_json(
                f"/repos/{ref.repository}/pulls/{ref.pr_number}"
            )
        except AuditNotFound:
            continue
        head = pr.get("head")
        if not isinstance(head, dict) or not isinstance(head.get("sha"), str):
            raise AuditTransportError(f"{ref.pr_key} response has no head SHA")
        pull_requests[ref.pr_key] = PullRequestState(
            repository=ref.repository,
            number=ref.pr_number,
            head_sha=head["sha"],
            state=str(pr.get("state") or "unknown"),
            merged=bool(pr.get("merged", False)),
            draft=bool(pr.get("draft", False)),
        )
    return references, pull_requests


def load_snapshot(
    path: Path,
) -> tuple[list[DeskReference], dict[str, PullRequestState]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditInputError(f"cannot read snapshot {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise AuditInputError("snapshot must be an object")

    raw_issues = raw.get("issues")
    raw_prs = raw.get("pull_requests")
    if not isinstance(raw_issues, list) or not isinstance(raw_prs, list):
        raise AuditInputError("snapshot issues and pull_requests must be arrays")

    references: list[DeskReference] = []
    for index, item in enumerate(raw_issues):
        if not isinstance(item, dict):
            raise AuditInputError(f"snapshot issues[{index}] must be an object")
        repository = item.get("repository")
        number = item.get("number")
        body = item.get("body")
        if not isinstance(repository, str) or REPOSITORY_RE.fullmatch(repository) is None:
            raise AuditInputError(f"snapshot issues[{index}].repository is invalid")
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            raise AuditInputError(f"snapshot issues[{index}].number is invalid")
        references.extend(
            parse_references(
                body,
                issue_repository=repository,
                issue_number=number,
            )
        )

    pull_requests: dict[str, PullRequestState] = {}
    for index, item in enumerate(raw_prs):
        if not isinstance(item, dict):
            raise AuditInputError(f"snapshot pull_requests[{index}] must be an object")
        repository = item.get("repository")
        number = item.get("number")
        head_sha = item.get("head_sha")
        state = item.get("state")
        merged = item.get("merged")
        draft = item.get("draft", False)
        if not isinstance(repository, str) or REPOSITORY_RE.fullmatch(repository) is None:
            raise AuditInputError(
                f"snapshot pull_requests[{index}].repository is invalid"
            )
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            raise AuditInputError(f"snapshot pull_requests[{index}].number is invalid")
        if not isinstance(head_sha, str) or SHA_RE.fullmatch(head_sha) is None:
            raise AuditInputError(f"snapshot pull_requests[{index}].head_sha is invalid")
        if state not in {"open", "closed"}:
            raise AuditInputError(f"snapshot pull_requests[{index}].state is invalid")
        if not isinstance(merged, bool) or not isinstance(draft, bool):
            raise AuditInputError(
                f"snapshot pull_requests[{index}] merged/draft must be boolean"
            )
        pr = PullRequestState(
            repository=repository,
            number=number,
            head_sha=head_sha,
            state=state,
            merged=merged,
            draft=draft,
        )
        if pr.key in pull_requests:
            raise AuditInputError(f"snapshot duplicates pull request {pr.key}")
        pull_requests[pr.key] = pr
    return references, pull_requests


def build_report(
    *,
    source: str,
    references: list[DeskReference],
    pull_requests: dict[str, PullRequestState],
    findings: list[AuditFinding],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": "pass" if not findings else "fail",
        "reference_count": len(references),
        "pull_request_count": len(pull_requests),
        "references": [asdict(item) for item in references],
        "pull_requests": [
            asdict(pull_requests[key]) for key in sorted(pull_requests)
        ],
        "findings": [asdict(item) for item in findings],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit exact-head references in Fieldwork review and delivery issues."
    )
    parser.add_argument("--repository", default="teamleaderleo/fieldwork")
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--api-url", default="https://api.github.com")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.snapshot is not None:
            references, pull_requests = load_snapshot(args.snapshot)
            source = f"snapshot:{args.snapshot}"
        else:
            issue_numbers = args.issue or [213, 160]
            if any(number <= 0 for number in issue_numbers):
                raise AuditInputError("issue numbers must be positive")
            references, pull_requests = load_live(
                issue_repository=args.repository,
                issue_numbers=issue_numbers,
                api_url=args.api_url,
                token=os.environ.get("GITHUB_TOKEN"),
            )
            source = f"live:{args.repository}#{','.join(map(str, issue_numbers))}"
        findings = audit_references(references, pull_requests)
        report = build_report(
            source=source,
            references=references,
            pull_requests=pull_requests,
            findings=findings,
        )
    except AuditInputError as exc:
        report = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "input",
            "status": "invalid",
            "findings": [{"code": "invalid_input", "message": str(exc)}],
        }
        exit_code = 2
    except AuditTransportError as exc:
        report = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "live",
            "status": "blocked",
            "findings": [{"code": "transport_error", "message": str(exc)}],
        }
        exit_code = 3
    else:
        exit_code = 0 if not findings else 1

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
