#!/usr/bin/env python3
"""Historical carrier receipt for the composed malformed-time repair.

The executable behavior now lives in ``reconcile.py`` and the native
``ObservedGenerationPilotTests`` matrix. This file deliberately retains only a
transfer assertion so the former patch carrier cannot keep an obsolete baseline
crash expectation alive.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_reconcile import ObservedGenerationPilotTests  # noqa: E402


class MalformedAuthorityTimeCarrierRetirementTests(unittest.TestCase):
    def test_native_matrix_owns_the_transferred_controls(self) -> None:
        self.assertTrue(
            hasattr(
                ObservedGenerationPilotTests,
                "test_16_malformed_authority_time_is_action_local_and_composable",
            )
        )
        self.assertTrue(
            hasattr(
                ObservedGenerationPilotTests,
                "test_17_malformed_global_observation_boundary_still_aborts",
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
