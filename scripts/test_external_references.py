#!/usr/bin/env python3
"""Regression tests for the tracked-file reference scanner."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import check_external_references as policy


class ExternalReferencePolicyTests(unittest.TestCase):
    def scan(self, text: str, owners: set[str] | None = None) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text(text, encoding="utf-8")
            return policy.scan_file(
                path,
                "teamleaderleo/fieldwork",
                owners or {"teamleaderleo"},
            )

    def test_owned_direct_issue_link_is_allowed(self) -> None:
        self.assertEqual(
            self.scan("https://github.com/teamleaderleo/stensibly/issues/490"),
            [],
        )

    def test_owned_shorthand_is_allowed(self) -> None:
        self.assertEqual(self.scan("See teamleaderleo/stensibly#490."), [])

    def test_third_party_direct_issue_link_is_rejected(self) -> None:
        failures = self.scan("https://github.com/openai/codex/issues/123")
        self.assertEqual(len(failures), 1)
        self.assertIn("direct third-party GitHub reference", failures[0])

    def test_third_party_shorthand_is_rejected(self) -> None:
        failures = self.scan("See openai/codex#123.")
        self.assertEqual(len(failures), 1)
        self.assertIn("third-party shorthand reference", failures[0])

    def test_intentional_marker_allows_third_party_link(self) -> None:
        self.assertEqual(
            self.scan(
                "<!-- fieldwork: intentional-upstream-reference -->\n"
                "https://github.com/openai/codex/issues/123"
            ),
            [],
        )

    def test_additional_controlled_owner_can_be_configured(self) -> None:
        self.assertEqual(
            self.scan(
                "https://github.com/example-owned/project/issues/1",
                {"teamleaderleo", "example-owned"},
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
