#!/usr/bin/env python3
"""Adversarial controls for Git binary marker completeness."""

from __future__ import annotations

import unittest

from scripts.validate_patch_syntax import PatchSyntaxError, validate_patch_text


class BinaryMarkerCompletenessTests(unittest.TestCase):
    def assert_missing_payload(self, patch: str) -> None:
        with self.assertRaisesRegex(
            PatchSyntaxError,
            "GIT binary patch marker has no payload header",
        ):
            validate_patch_text(patch, "candidate.patch")

    def test_mode_change_cannot_hide_bare_binary_marker(self) -> None:
        self.assert_missing_payload(
            """diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
GIT binary patch
"""
        )

    def test_text_hunk_cannot_hide_bare_binary_marker(self) -> None:
        # A completed text hunk rejects later non-boundary content before the
        # marker reaches section finalization. The safety requirement is that
        # the mixed form cannot be accepted; the earlier error path is valid.
        with self.assertRaises(PatchSyntaxError):
            validate_patch_text(
                """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
GIT binary patch
""",
                "candidate.patch",
            )

    def test_binary_summary_cannot_hide_bare_binary_marker(self) -> None:
        self.assert_missing_payload(
            """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
GIT binary patch
"""
        )


if __name__ == "__main__":
    unittest.main()
