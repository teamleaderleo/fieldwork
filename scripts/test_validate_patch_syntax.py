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
            r"""diff --git a/a b/a
--- a/a
+++ b/a
@@ -1 +1 @@
-old
\ No newline at end of file
+new
\ No newline at end of file
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

    def test_accepts_git_mode_only_patch(self) -> None:
        validate_patch_text(
            """diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
"""
        )

    def test_accepts_rename_only_patch_at_full_similarity(self) -> None:
        validate_patch_text(
            """diff --git a/old.txt b/new.txt
similarity index 100%
rename from old.txt
rename to new.txt
"""
        )

    def test_accepts_copy_only_patch_at_full_similarity(self) -> None:
        validate_patch_text(
            """diff --git a/source.txt b/copy.txt
similarity index 100%
copy from source.txt
copy to copy.txt
"""
        )

    def test_rejects_changed_rename_without_hunk(self) -> None:
        self.assert_invalid(
            """diff --git a/old.txt b/new.txt
similarity index 92%
rename from old.txt
rename to new.txt
""",
            "complete metadata-only change",
        )

    def test_accepts_empty_file_creation(self) -> None:
        validate_patch_text(
            """diff --git a/empty.txt b/empty.txt
new file mode 100644
index 0000000..e69de29
"""
        )

    def test_accepts_empty_file_deletion(self) -> None:
        validate_patch_text(
            """diff --git a/empty.txt b/empty.txt
deleted file mode 100644
index e69de29..0000000
"""
        )

    def test_accepts_sha256_empty_file_creation(self) -> None:
        validate_patch_text(
            """diff --git a/empty.txt b/empty.txt
new file mode 100644
index 0000000..473a0f4c
"""
        )

    def test_rejects_nonempty_new_file_without_hunk(self) -> None:
        self.assert_invalid(
            """diff --git a/data.txt b/data.txt
new file mode 100644
index 0000000..1234567
""",
            "complete metadata-only change",
        )

    def test_rejects_nonempty_deleted_file_without_hunk(self) -> None:
        self.assert_invalid(
            """diff --git a/data.txt b/data.txt
deleted file mode 100644
index 1234567..0000000
""",
            "complete metadata-only change",
        )

    def test_accepts_binary_patch_payload(self) -> None:
        validate_patch_text(
            """diff --git a/image.png b/image.png
new file mode 100644
index 0000000..1234567
GIT binary patch
literal 0
HcmV?d00001
"""
        )

    def test_accepts_two_binary_payload_blocks(self) -> None:
        validate_patch_text(
            """diff --git a/image.png b/image.png
index 1111111..2222222 100644
GIT binary patch
literal 1
Ic${Nk000310RR91

literal 0
HcmV?d00001
"""
        )

    def test_rejects_truncated_second_binary_payload_block(self) -> None:
        self.assert_invalid(
            """diff --git a/image.png b/image.png
index 1111111..2222222 100644
GIT binary patch
literal 1
Ic${Nk000310RR91

literal 1
""",
            "binary payload block contains no encoded data",
        )

    def test_accepts_binary_files_summary(self) -> None:
        validate_patch_text(
            """diff --git a/image.png b/image.png
index 1111111..2222222 100644
Binary files a/image.png and b/image.png differ
"""
        )

    def test_rejects_bare_git_binary_marker(self) -> None:
        self.assert_invalid(
            """diff --git a/image.png b/image.png
GIT binary patch
""",
            "GIT binary patch marker has no payload header",
        )

    def test_rejects_binary_header_without_payload_data(self) -> None:
        self.assert_invalid(
            """diff --git a/image.png b/image.png
GIT binary patch
literal 10
""",
            "binary payload block contains no encoded data",
        )

    def test_rejects_bare_diff_header(self) -> None:
        self.assert_invalid(
            "diff --git a/a.txt b/a.txt\n",
            "file section contains no hunks",
        )

    def test_rejects_file_headers_without_hunk(self) -> None:
        self.assert_invalid(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
""",
            "file section contains no hunks",
        )

    def test_rejects_valid_first_file_and_header_only_second_file(self) -> None:
        self.assert_invalid(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
diff --git a/b.txt b/b.txt
--- a/b.txt
+++ b/b.txt
""",
            "file section contains no hunks",
        )

    def test_rejects_non_patch_text(self) -> None:
        self.assert_invalid("not a patch\n", "contains no patch file sections")


if __name__ == "__main__":
    unittest.main()
