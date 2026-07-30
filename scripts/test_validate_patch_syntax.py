#!/usr/bin/env python3
"""Focused tests for retained unified-diff syntax validation."""

from __future__ import annotations

import unittest

from scripts.validate_patch_syntax import PatchSyntaxError, validate_patch_text


class PatchSyntaxTests(unittest.TestCase):
    def assert_invalid(self, patch: str, pattern: str) -> None:
        with self.assertRaisesRegex(PatchSyntaxError, pattern):
            validate_patch_text(patch, "candidate.patch")

    def test_accepts_valid_single_hunk(self) -> None:
        validate_patch_text(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1,2 +1,3 @@
 first
-second
+second changed
+third
"""
        )

    def test_accepts_multiple_files_and_hunks(self) -> None:
        validate_patch_text(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
@@ -4,2 +4,2 @@ context
 keep
-remove
+replace
diff --git a/b.txt b/b.txt
--- a/b.txt
+++ b/b.txt
@@ -0,0 +1,2 @@
+one
+two
"""
        )

    def test_accepts_plain_unified_file_boundaries(self) -> None:
        validate_patch_text(
            """--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
--- a/b.txt
+++ b/b.txt
@@ -1 +1 @@
-before
+after
"""
        )

    def test_accepts_deleted_lines_that_resemble_file_headers(self) -> None:
        validate_patch_text(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
--- old heading
+++ new heading
"""
        )

    def test_rejects_wrong_old_count(self) -> None:
        self.assert_invalid(
            """diff --git a/a b/a
--- a/a
+++ b/a
@@ -1,2 +1 @@
-old
+new
""",
            "old expected 2, saw 1",
        )

    def test_rejects_wrong_new_count(self) -> None:
        self.assert_invalid(
            """diff --git a/a b/a
--- a/a
+++ b/a
@@ -1 +1,2 @@
-old
+new
""",
            "new expected 2, saw 1",
        )

    def test_rejects_truncated_hunk_before_next_file(self) -> None:
        self.assert_invalid(
            """diff --git a/a b/a
--- a/a
+++ b/a
@@ -1,2 +1,2 @@
 keep
diff --git a/b b/b
--- a/b
+++ b/b
""",
            "hunk count mismatch",
        )

    def test_rejects_extra_prefixed_content(self) -> None:
        self.assert_invalid(
            """diff --git a/a b/a
--- a/a
+++ b/a
@@ -1 +1 @@
-old
+new
+extra
""",
            "extra content after completed hunk",
        )

    def test_accepts_no_newline_marker(self) -> None:
        validate_patch_text(
            """diff --git a/a b/a
--- a/a
+++ b/a
@@ -1 +1 @@
-old
\\ No newline at end of file
+new
\\ No newline at end of file
"""
        )

    def test_rejects_malformed_hunk_header(self) -> None:
        self.assert_invalid(
            """diff --git a/a b/a
--- a/a
+++ b/a
@@ -1,one +1,1 @@
-old
+new
""",
            "malformed hunk header",
        )

    def test_accepts_git_metadata_only_patch(self) -> None:
        validate_patch_text(
            """diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
"""
        )

    def test_accepts_binary_patch_policy(self) -> None:
        validate_patch_text(
            """diff --git a/image.png b/image.png
new file mode 100644
index 0000000..1234567
GIT binary patch
literal 0
HcmV?d00001
"""
        )

    def test_rejects_non_patch_text(self) -> None:
        self.assert_invalid("not a patch\n", "contains no unified-diff hunks")


if __name__ == "__main__":
    unittest.main()
