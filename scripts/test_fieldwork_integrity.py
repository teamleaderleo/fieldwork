#!/usr/bin/env python3
"""Regression tests for Fieldwork integrity helpers."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from check_fieldwork_integrity import validate_candidate_patch


class CandidatePatchValidationTests(unittest.TestCase):
    def validate(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "candidate.patch")
            path.write_text(content, encoding="utf-8")
            return validate_candidate_patch(path)

    def test_accepts_valid_multifile_patch(self) -> None:
        errors = self.validate(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,2 +1,2 @@
-old
 context
+new
diff --git a/b.txt b/b.txt
--- a/b.txt
+++ b/b.txt
@@ -3 +3,2 @@
 keep
+added
"""
        )
        self.assertEqual(errors, [])

    def test_rejects_stale_hunk_counts(self) -> None:
        errors = self.validate(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,2 +1,2 @@
-old
+new
"""
        )
        self.assertTrue(any("declares old/new 2/2 but contains 1/1" in error for error in errors))

    def test_rejects_malformed_hunk_header(self) -> None:
        errors = self.validate(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ broken @@
-old
+new
"""
        )
        self.assertTrue(any("malformed unified-diff hunk header" in error for error in errors))

    def test_rejects_patch_without_hunks(self) -> None:
        errors = self.validate(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
"""
        )
        self.assertTrue(any("contains no unified-diff hunks" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
