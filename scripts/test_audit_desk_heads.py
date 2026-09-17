#!/usr/bin/env python3
from __future__ import annotations

import unittest

from audit_desk_heads import (
    AuditInputError,
    DeskReference,
    PullRequestState,
    audit_references,
    parse_references,
)

REPO = "teamleaderleo/fieldwork"
HEAD_A = "a" * 40
HEAD_B = "b" * 40


def marker(*, pr: int = 231, head: str = HEAD_A, lane: str = "R3") -> str:
    return (
        "<!-- fieldwork:desk-ref "
        f"repo={REPO} pr={pr} head={head} lane={lane} -->"
    )


def reference(
    *, issue: int = 213, pr: int = 231, head: str = HEAD_A, lane: str = "R3"
) -> DeskReference:
    return DeskReference(
        issue_repository=REPO,
        issue_number=issue,
        repository=REPO,
        pr_number=pr,
        expected_head=head,
        lane=lane,
    )


def pull_request(
    *,
    pr: int = 231,
    head: str = HEAD_A,
    state: str = "open",
    merged: bool = False,
) -> PullRequestState:
    return PullRequestState(
        repository=REPO,
        number=pr,
        head_sha=head,
        state=state,
        merged=merged,
    )


class DeskHeadAuditTests(unittest.TestCase):
    def test_parses_valid_markers(self) -> None:
        refs = parse_references(
            f"State: ready\n{marker()}\n{marker(pr=238, lane='D0')}",
            issue_repository=REPO,
            issue_number=213,
        )
        self.assertEqual([item.pr_number for item in refs], [231, 238])
        self.assertEqual([item.lane for item in refs], ["R3", "D0"])

    def test_rejects_issue_without_markers(self) -> None:
        with self.assertRaisesRegex(AuditInputError, "contains no desk references"):
            parse_references(
                "State: ready",
                issue_repository=REPO,
                issue_number=213,
            )

    def test_rejects_malformed_marker(self) -> None:
        with self.assertRaisesRegex(AuditInputError, "is malformed"):
            parse_references(
                "<!-- fieldwork:desk-ref repo=teamleaderleo/fieldwork "
                "pr=231 head=short lane=R3 -->",
                issue_repository=REPO,
                issue_number=213,
            )

    def test_rejects_duplicate_marker_in_one_issue(self) -> None:
        with self.assertRaisesRegex(AuditInputError, "duplicates desk reference"):
            parse_references(
                f"{marker()}\n{marker(lane='D0')}",
                issue_repository=REPO,
                issue_number=213,
            )

    def test_reports_stale_head(self) -> None:
        findings = audit_references(
            [reference()],
            {f"{REPO}#231": pull_request(head=HEAD_B)},
        )
        self.assertEqual([item.code for item in findings], ["stale_head"])
        self.assertEqual(findings[0].actual_head, HEAD_B)

    def test_reports_missing_pull_request(self) -> None:
        findings = audit_references([reference()], {})
        self.assertEqual([item.code for item in findings], ["missing_pull_request"])

    def test_reports_closed_and_merged_active_entries(self) -> None:
        closed_findings = audit_references(
            [reference()],
            {f"{REPO}#231": pull_request(state="closed")},
        )
        self.assertEqual(
            [item.code for item in closed_findings],
            ["closed_active_entry"],
        )

        merged_findings = audit_references(
            [reference()],
            {f"{REPO}#231": pull_request(state="closed", merged=True)},
        )
        self.assertEqual(
            [item.code for item in merged_findings],
            ["merged_active_entry"],
        )

    def test_reports_conflicting_heads_across_issues(self) -> None:
        findings = audit_references(
            [
                reference(issue=213, head=HEAD_A, lane="R3"),
                reference(issue=160, head=HEAD_B, lane="D0"),
            ],
            {f"{REPO}#231": pull_request(head=HEAD_B)},
        )
        self.assertEqual(
            [item.code for item in findings],
            ["conflicting_expected_heads", "stale_head"],
        )

    def test_current_open_head_passes(self) -> None:
        findings = audit_references(
            [reference()],
            {f"{REPO}#231": pull_request()},
        )
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
