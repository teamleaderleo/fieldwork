from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.audit_pr_evidence_identity import (
    IdentityError,
    build_receipt,
    classify_identity,
)


BASE = "1" * 40
HEAD = "2" * 40
MERGE = "3" * 40
OTHER = "4" * 40
PARENT = "5" * 40
NEW_BASE = "6" * 40
ZERO = "0" * 40
COMMANDS = [
    {"command": "node scripts/test_interaction_references.js", "outcome": "success"},
    {"command": "python3 scripts/check_fieldwork_integrity.py", "outcome": "success"},
    {
        "command": "python3 -m unittest -v scripts.test_pr_evidence_identity",
        "outcome": "success",
    },
]


class PullRequestEvidenceIdentityTest(unittest.TestCase):
    def receipt(self, **overrides: object) -> dict[str, object]:
        data: dict[str, object] = {
            "checkout_sha": HEAD,
            "head_sha": HEAD,
            "event_base_sha": BASE,
            "observed_base_sha": BASE,
            "event_before_sha": None,
            "push_forced": None,
            "event_sha": MERGE,
            "parents": [PARENT],
            "event_name": "pull_request",
            "ref": "refs/pull/42/merge",
            "head_ref": "feature/example",
            "base_ref": "main",
            "run_id": "100",
            "run_attempt": "1",
            "expected": "exact-head",
            "technical_gate_name": "fieldwork-integrity",
            "technical_gate_commands": [dict(command) for command in COMMANDS],
        }
        data.update(overrides)
        return data

    def push_receipt(self, **overrides: object) -> dict[str, object]:
        data = self.receipt(
            event_name="push",
            ref="refs/heads/main",
            checkout_sha=HEAD,
            event_sha=HEAD,
            event_base_sha=None,
            observed_base_sha=None,
            event_before_sha=BASE,
            push_forced=False,
            head_ref="",
            base_ref="",
            parents=[BASE],
        )
        data.update(overrides)
        return data

    def test_exact_head_checkout(self) -> None:
        receipt = build_receipt(self.receipt())
        self.assertEqual(receipt.classification, "exact-head")
        self.assertTrue(receipt.base_current)
        self.assertIsNone(receipt.current_integration_evidence)
        self.assertTrue(receipt.reusable_evidence)
        self.assertEqual(receipt.schema_version, 2)

    def test_synthetic_merge_ref_checkout(self) -> None:
        receipt = build_receipt(
            self.receipt(
                checkout_sha=MERGE,
                parents=[BASE, HEAD],
                expected="synthetic-merge-ref",
            )
        )
        self.assertEqual(receipt.classification, "synthetic-merge-ref")
        self.assertEqual(receipt.parents, (BASE, HEAD))
        self.assertTrue(receipt.base_current)
        self.assertTrue(receipt.current_integration_evidence)

    def test_moved_base_preserves_historical_merge_identity(self) -> None:
        receipt = build_receipt(
            self.receipt(
                checkout_sha=MERGE,
                observed_base_sha=NEW_BASE,
                parents=[BASE, HEAD],
                expected="synthetic-merge-ref",
            )
        )
        self.assertEqual(receipt.classification, "synthetic-merge-ref")
        self.assertEqual(receipt.event_base_sha, BASE)
        self.assertEqual(receipt.observed_base_sha, NEW_BASE)
        self.assertFalse(receipt.base_current)
        self.assertTrue(receipt.reusable_evidence)
        self.assertFalse(receipt.current_integration_evidence)

    def test_moved_base_keeps_literal_head_identity_without_current_integration(self) -> None:
        receipt = build_receipt(self.receipt(observed_base_sha=NEW_BASE))
        self.assertEqual(receipt.classification, "exact-head")
        self.assertFalse(receipt.base_current)
        self.assertTrue(receipt.reusable_evidence)

    def test_valid_identity_with_failed_gate_is_not_reusable(self) -> None:
        commands = [dict(command) for command in COMMANDS]
        commands[1]["outcome"] = "failure"
        commands[2]["outcome"] = "skipped"
        receipt = build_receipt(self.receipt(technical_gate_commands=commands))
        self.assertEqual(receipt.classification, "exact-head")
        self.assertEqual(receipt.technical_gate_outcome, "failure")
        self.assertFalse(receipt.reusable_evidence)
        self.assertEqual(
            [command.outcome for command in receipt.technical_gate_commands],
            ["success", "failure", "skipped"],
        )

    def test_unrelated_checkouts_remain_typed_other_and_nonreusable(self) -> None:
        cases = (
            self.receipt(
                checkout_sha=OTHER,
                parents=[PARENT],
                expected="other-checkout",
            ),
            self.receipt(
                checkout_sha=OTHER,
                parents=[BASE, PARENT],
                expected="other-checkout",
            ),
            self.receipt(
                checkout_sha=MERGE,
                parents=[HEAD, BASE],
                expected="other-checkout",
            ),
        )
        for data in cases:
            with self.subTest(data=data):
                receipt = build_receipt(data)
                self.assertEqual(receipt.classification, "other-checkout")
                self.assertFalse(receipt.reusable_evidence)

    def test_expected_classification_fails_on_identity_mismatch(self) -> None:
        with self.assertRaisesRegex(IdentityError, "expected exact-head"):
            build_receipt(
                self.receipt(
                    checkout_sha=MERGE,
                    parents=[BASE, HEAD],
                )
            )

    def test_malformed_types_shas_and_gate_fields_fail_closed(self) -> None:
        cases = (
            self.receipt(checkout_sha=True),
            self.receipt(head_sha="A" * 40),
            self.receipt(event_base_sha="1" * 39),
            self.receipt(observed_base_sha=True),
            self.receipt(parents=True),
            self.receipt(parents=[PARENT, PARENT]),
            self.receipt(event_name=True),
            self.receipt(run_id=True),
            self.receipt(run_attempt="0"),
            self.receipt(technical_gate_name=""),
            self.receipt(technical_gate_commands=[]),
            self.receipt(
                technical_gate_commands=[dict(COMMANDS[0]), dict(COMMANDS[0])]
            ),
            self.receipt(
                technical_gate_commands=[{"command": "x", "outcome": "green"}]
            ),
            self.receipt(
                technical_gate_commands=[
                    {"command": "x", "outcome": "success", "extra": 1}
                ]
            ),
        )
        for data in cases:
            with self.subTest(data=data):
                with self.assertRaises(IdentityError):
                    build_receipt(data)

    def test_unknown_and_missing_fields_fail_closed(self) -> None:
        unknown = self.receipt(extra=True)
        with self.assertRaisesRegex(IdentityError, "unknown field"):
            build_receipt(unknown)
        missing = self.receipt()
        del missing["event_base_sha"]
        with self.assertRaisesRegex(IdentityError, "missing field"):
            build_receipt(missing)

    def test_checkout_cannot_be_its_own_parent(self) -> None:
        with self.assertRaisesRegex(IdentityError, "own parent"):
            classify_identity(
                checkout_sha=MERGE,
                head_sha=HEAD,
                event_base_sha=BASE,
                event_sha=MERGE,
                parents=[BASE, MERGE],
            )

    def test_pull_request_event_metadata_fails_closed(self) -> None:
        cases = (
            self.receipt(event_name="workflow_dispatch"),
            self.receipt(ref="refs/heads/main"),
            self.receipt(ref="refs/pull/42/head"),
            self.receipt(ref="refs/pull/0/merge"),
            self.receipt(head_ref=""),
            self.receipt(base_ref=""),
            self.receipt(head_ref="feature with space"),
            self.receipt(base_ref="main\tbranch"),
            self.receipt(event_sha=HEAD),
            self.receipt(event_sha=BASE),
            self.receipt(head_sha=BASE),
            self.receipt(event_before_sha=BASE),
            self.receipt(push_forced=False),
        )
        for data in cases:
            with self.subTest(data=data):
                with self.assertRaises(IdentityError):
                    build_receipt(data)

    def test_push_event_metadata_and_update_state(self) -> None:
        ordinary = build_receipt(self.push_receipt())
        self.assertEqual(ordinary.classification, "exact-head")
        self.assertEqual(ordinary.event_before_sha, BASE)
        self.assertEqual(ordinary.push_update_kind, "ordinary-update")
        self.assertIsNone(ordinary.base_current)

        forced = build_receipt(self.push_receipt(push_forced=True))
        self.assertEqual(forced.push_update_kind, "forced-update")

        created = build_receipt(
            self.push_receipt(event_before_sha=ZERO, push_forced=False)
        )
        self.assertEqual(created.push_update_kind, "branch-created")

    def test_push_event_metadata_fails_closed(self) -> None:
        contradictions = (
            {"ref": "refs/pull/42/merge"},
            {"ref": "refs/tags/v1"},
            {"ref": "refs/heads/main branch"},
            {"head_ref": "feature/example"},
            {"base_ref": "main"},
            {"event_sha": OTHER},
            {"event_base_sha": BASE},
            {"observed_base_sha": BASE},
            {"push_forced": None},
            {"event_before_sha": ZERO, "push_forced": True},
        )
        for contradiction in contradictions:
            with self.subTest(data=contradiction):
                with self.assertRaises(IdentityError):
                    build_receipt(self.push_receipt(**contradiction))

    def test_cli_output_and_optimizer_status_match(self) -> None:
        root = Path(__file__).resolve().parents[1]
        tool = root / "scripts" / "audit_pr_evidence_identity.py"
        data = self.receipt(
            checkout_sha=MERGE,
            parents=[BASE, HEAD],
            expected="synthetic-merge-ref",
        )
        with tempfile.TemporaryDirectory() as temporary:
            input_path = Path(temporary) / "input.json"
            output_path = Path(temporary) / "output.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            runs = []
            for optimized in (False, True):
                command = [sys.executable]
                if optimized:
                    command.append("-O")
                command.extend(
                    [str(tool), str(input_path), "--output", str(output_path)]
                )
                runs.append(
                    subprocess.run(
                        command,
                        cwd=root,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                )

        ordinary, optimized = runs
        self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
        self.assertEqual(optimized.returncode, 0, optimized.stderr)
        self.assertEqual(json.loads(ordinary.stdout), json.loads(optimized.stdout))
        payload = json.loads(ordinary.stdout)
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["classification"], "synthetic-merge-ref")
        self.assertEqual(payload["parents"], [BASE, HEAD])
        self.assertEqual(payload["technical_gate_outcome"], "success")
        self.assertTrue(payload["reusable_evidence"])


if __name__ == "__main__":
    unittest.main()
