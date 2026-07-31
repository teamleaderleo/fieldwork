#!/usr/bin/env python3
"""Retained transfer controls for the composed malformed-time repair.

The canonical behavior lives in ``reconcile.py`` and the native
``ObservedGenerationPilotTests`` matrix. These controls prove that the native
matrix remains present, the condition receipt retains the exact malformed input,
and the historical patch still reverses cleanly from the composed source.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATCH = HERE / "repairs" / "0001-fail-closed-malformed-authority-time.patch"
sys.path.insert(0, str(HERE))

import test_reconcile  # noqa: E402
from reconcile import reconcile  # noqa: E402


class MalformedAuthorityTimeCarrierRetirementTests(unittest.TestCase):
    def test_native_matrix_owns_the_transferred_controls(self) -> None:
        native = test_reconcile.ObservedGenerationPilotTests
        self.assertTrue(
            hasattr(
                native,
                "test_16_malformed_authority_time_is_action_local_and_composable",
            )
        )
        self.assertTrue(
            hasattr(
                native,
                "test_17_malformed_global_observation_boundary_still_aborts",
            )
        )

    def test_condition_receipt_retains_exact_malformed_expiry(self) -> None:
        invalid_values: tuple[object, ...] = (
            "not-a-time",
            "2026-08-01T02:30:00",
            123,
        )
        pilot = test_reconcile.ObservedGenerationPilotTests(
            methodName="test_16_malformed_authority_time_is_action_local_and_composable"
        )
        pilot.setUp()

        for invalid in invalid_values:
            with self.subTest(invalid=invalid):
                record = deepcopy(pilot.cross_repository)
                record["authority"] = {
                    "merge": test_reconcile.authorized(expires_at=invalid),
                    "deploy": test_reconcile.authorized(
                        expires_at="2026-08-01T02:30:00Z"
                    ),
                }
                facts = pilot.live_facts(record)
                projection = reconcile(record, facts, test_reconcile.OBSERVED_AT)
                condition = pilot.condition(
                    projection,
                    "AuthorityUsable",
                    action="merge",
                )

                self.assertEqual(invalid, condition["inputs"]["expires_at"])
                self.assertEqual(
                    ("Unknown", "InvalidAuthorityTime"),
                    (condition["status"], condition["reason"]),
                )

    def test_historical_patch_matches_composed_source(self) -> None:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "apply",
                "--reverse",
                "--check",
                str(PATCH),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
