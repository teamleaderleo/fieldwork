#!/usr/bin/env python3
"""Reversing controls for retained-patch materialization classification."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.classify_retained_patches import (
    BINARY_SUMMARY,
    build_receipt,
    classify_patch_text,
)


class SectionClassificationTests(unittest.TestCase):
    def test_classifies_textual_hunks(self) -> None:
        sections = classify_patch_text(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
"""
        )
        self.assertEqual([section.kind for section in sections], ["textual-hunks"])
        self.assertTrue(sections[0].materializable)

    def test_classifies_git_binary_payload(self) -> None:
        sections = classify_patch_text(
            """diff --git a/image.png b/image.png
new file mode 100644
index 0000000..1234567
GIT binary patch
literal 0
HcmV?d00001
"""
        )
        self.assertEqual(
            [section.kind for section in sections], ["git-binary-payload"]
        )
        self.assertTrue(sections[0].materializable)

    def test_classifies_metadata_only(self) -> None:
        sections = classify_patch_text(
            """diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
"""
        )
        self.assertEqual([section.kind for section in sections], ["metadata-only"])
        self.assertTrue(sections[0].materializable)

    def test_classifies_binary_summary_as_nonmaterializing(self) -> None:
        sections = classify_patch_text(
            """diff --git a/old.bin b/new.bin
index 1111111..2222222 100644
Binary files a/old.bin and b/new.bin differ
"""
        )
        self.assertEqual([section.kind for section in sections], [BINARY_SUMMARY])
        self.assertFalse(sections[0].materializable)


class ExactBinaryPairPolicyTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout

    def make_binary_summary(self, root: Path) -> str:
        repo = root / "source"
        repo.mkdir()
        self.run_git(repo, "init", "-q")
        self.run_git(repo, "config", "user.name", "Fieldwork Test")
        self.run_git(repo, "config", "user.email", "fieldwork@example.invalid")
        binary = repo / "image.bin"
        old_bytes = b"\x00old binary bytes\xff"
        new_bytes = b"\x00new binary bytes\xfe"
        binary.write_bytes(old_bytes)
        self.run_git(repo, "add", "image.bin")
        self.run_git(repo, "commit", "-qm", "base binary")
        binary.write_bytes(new_bytes)

        summary = self.run_git(repo, "diff", "HEAD", "--", "image.bin")
        self.assertIn("Binary files ", summary)
        self.assertNotIn("GIT binary patch", summary)
        self.assertNotIn("literal ", summary)
        self.assertNotIn(new_bytes.hex(), summary)
        return summary

    def test_parse_valid_summary_cannot_be_retained_as_candidate_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self.make_binary_summary(root)
            candidate = root / "candidate.patch"
            candidate.write_text(summary, encoding="utf-8")

            document, violations = build_receipt([candidate])

        self.assertEqual(len(document["files"]), 1)
        file_receipt = document["files"][0]
        self.assertEqual(file_receipt["parse_state"], "parse-valid")
        self.assertEqual(file_receipt["materialization_state"], "nonmaterializing")
        self.assertEqual(file_receipt["section_kinds"], (BINARY_SUMMARY,))
        self.assertEqual(len(violations), 1)
        self.assertIn("retained *.patch contains", violations[0])

    def test_evidence_only_nonpatch_extension_keeps_explicit_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = self.make_binary_summary(root)
            evidence = root / "comparison.diff-summary"
            evidence.write_text(summary, encoding="utf-8")

            document, violations = build_receipt([evidence])

        self.assertEqual(violations, [])
        file_receipt = document["files"][0]
        self.assertEqual(file_receipt["parse_state"], "parse-valid")
        self.assertEqual(file_receipt["materialization_state"], "nonmaterializing")
        self.assertEqual(file_receipt["section_kinds"], (BINARY_SUMMARY,))


if __name__ == "__main__":
    unittest.main()
