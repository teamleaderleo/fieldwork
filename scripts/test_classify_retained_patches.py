#!/usr/bin/env python3
"""Reversing controls for retained-patch materialization and blob identity."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.classify_retained_patches import (
    BINARY_SUMMARY,
    EVIDENCE_ONLY_SUFFIX,
    EVIDENCE_ROLE,
    IMPLEMENTATION_ROLE,
    build_receipt,
    classify_patch_text,
    discover_tracked_materialization_artifacts,
)


TEXT_PATCH = """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
"""


class SectionClassificationTests(unittest.TestCase):
    def test_classifies_textual_hunks(self) -> None:
        sections = classify_patch_text(TEXT_PATCH)
        self.assertEqual([section.kind for section in sections], ["textual-hunks"])
        self.assertTrue(sections[0].materializable)

    def test_hunk_content_that_looks_like_file_headers_stays_in_one_section(self) -> None:
        sections = classify_patch_text(
            """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
--- deleted content beginning with two dashes
+++ added content beginning with two pluses
"""
        )
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].kind, "textual-hunks")
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


class GitRepositoryMixin:
    def run_git(self, repo: Path, *args: str, check: bool = True) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout

    def init_repo(self, repository: Path) -> None:
        self.run_git(repository, "init", "-q")
        self.run_git(repository, "config", "user.name", "Fieldwork Test")
        self.run_git(
            repository,
            "config",
            "user.email",
            "fieldwork@example.invalid",
        )

    def make_binary_summary(self, root: Path) -> str:
        repo = root / "source"
        repo.mkdir()
        self.init_repo(repo)
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


class ExactBinaryPairPolicyTests(GitRepositoryMixin, unittest.TestCase):
    def inspect_summary(
        self, root: Path, name: str
    ) -> tuple[dict[str, object], list[str]]:
        summary = self.make_binary_summary(root)
        path = root / name
        path.write_text(summary, encoding="utf-8")
        return build_receipt([path])

    def assert_nonmaterializing(self, document: dict[str, object]) -> None:
        self.assertEqual(len(document["files"]), 1)
        file_receipt = document["files"][0]
        self.assertEqual(file_receipt["parse_state"], "parse-valid")
        self.assertEqual(file_receipt["materialization_state"], "nonmaterializing")
        self.assertEqual(file_receipt["section_kinds"], (BINARY_SUMMARY,))

    def test_parse_valid_summary_cannot_be_retained_as_candidate_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document, violations = self.inspect_summary(Path(tmp), "candidate.patch")

        self.assert_nonmaterializing(document)
        self.assertEqual(len(violations), 1)
        self.assertIn(EVIDENCE_ONLY_SUFFIX, violations[0])
        self.assertEqual(
            document["files"][0]["repository_state"], "explicit-untracked"
        )
        self.assertFalse(document["files"][0]["repository_policy_eligible"])

    def test_generic_diff_name_is_not_an_evidence_only_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document, violations = self.inspect_summary(Path(tmp), "candidate.diff")

        self.assert_nonmaterializing(document)
        self.assertEqual(len(violations), 1)
        self.assertIn(EVIDENCE_ONLY_SUFFIX, violations[0])

    def test_explicit_evidence_suffix_keeps_nonmaterializing_classification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            document, violations = self.inspect_summary(
                Path(tmp), f"comparison{EVIDENCE_ONLY_SUFFIX}"
            )

        self.assertEqual(violations, [])
        self.assert_nonmaterializing(document)
        self.assertEqual(
            document["artifactRoleCounts"],
            {IMPLEMENTATION_ROLE: 0, EVIDENCE_ROLE: 1},
        )

    def test_materializable_content_cannot_hide_under_evidence_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"candidate{EVIDENCE_ONLY_SUFFIX}"
            path.write_text(TEXT_PATCH, encoding="utf-8")
            document, violations = build_receipt([path])

        self.assertEqual(document["files"][0]["materialization_state"], "materializable")
        self.assertEqual(len(violations), 1)
        self.assertIn("evidence-only", violations[0])

    def test_no_argument_discovery_covers_all_policy_suffixes_and_blob_identity(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp)
            self.init_repo(repository)

            source_root = repository / "fixture"
            source_root.mkdir()
            summary = self.make_binary_summary(source_root)
            names = [
                "candidate.patch",
                "candidate.diff",
                f"comparison{EVIDENCE_ONLY_SUFFIX}",
            ]
            for name in names:
                (repository / name).write_text(summary, encoding="utf-8")
            self.run_git(repository, "add", "--", *names)

            discovered = discover_tracked_materialization_artifacts(repository)
            self.assertEqual([path.name for path in discovered], sorted(names))
            document, violations = build_receipt(discovered)

            expected_oids = {
                name: self.run_git(repository, "rev-parse", f":{name}").strip()
                for name in names
            }

        self.assertEqual(
            sorted(Path(file_receipt["path"]).name for file_receipt in document["files"]),
            sorted(names),
        )
        for file_receipt in document["files"]:
            name = Path(file_receipt["path"]).name
            self.assertEqual(file_receipt["repository_state"], "tracked-clean")
            self.assertTrue(file_receipt["repository_policy_eligible"])
            self.assertEqual(file_receipt["git_mode"], "100644")
            self.assertEqual(file_receipt["git_blob_oid"], expected_oids[name])
            self.assertEqual(file_receipt["byte_length"], len(summary.encode()))
            self.assertEqual(
                file_receipt["raw_sha256"],
                hashlib.sha256(summary.encode()).hexdigest(),
            )
        self.assertEqual(
            document["artifactRoleCounts"],
            {IMPLEMENTATION_ROLE: 2, EVIDENCE_ROLE: 1},
        )
        self.assertEqual(document["repositoryStateCounts"], {"tracked-clean": 3})
        self.assertEqual(len(violations), 2)
        self.assertTrue(any("candidate.patch" in violation for violation in violations))
        self.assertTrue(any("candidate.diff" in violation for violation in violations))
        self.assertFalse(
            any(f"comparison{EVIDENCE_ONLY_SUFFIX}" in violation for violation in violations)
        )


class RepositoryIdentityFailureTests(GitRepositoryMixin, unittest.TestCase):
    def test_tracked_symlink_is_retained_as_typed_identity_failure(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp)
            self.init_repo(repository)
            target = repository / "target.txt"
            target.write_text(TEXT_PATCH, encoding="utf-8")
            link = repository / "candidate.patch"
            link.symlink_to(target.name)
            self.run_git(repository, "add", "candidate.patch")

            document, violations = build_receipt([link])

        self.assertEqual(len(document["files"]), 1)
        entry = document["files"][0]
        self.assertEqual(entry["parse_state"], "not-inspected")
        self.assertEqual(entry["repository_state"], "tracked-invalid")
        self.assertEqual(entry["git_mode"], "120000")
        self.assertEqual(entry["error_code"], "symlink-not-allowed")
        self.assertEqual(len(violations), 1)

    def test_dirty_tracked_file_cannot_borrow_index_blob_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp)
            self.init_repo(repository)
            path = repository / "candidate.patch"
            path.write_text(TEXT_PATCH, encoding="utf-8")
            self.run_git(repository, "add", "candidate.patch")
            tracked_oid = self.run_git(
                repository, "rev-parse", ":candidate.patch"
            ).strip()
            path.write_text(TEXT_PATCH.replace("+new", "+newer"), encoding="utf-8")

            document, violations = build_receipt([path])

        entry = document["files"][0]
        self.assertEqual(entry["parse_state"], "not-inspected")
        self.assertEqual(entry["error_code"], "working-tree-blob-mismatch")
        self.assertEqual(entry["git_blob_oid"], tracked_oid)
        self.assertEqual(entry["repository_state"], "tracked-dirty")
        self.assertIn(tracked_oid, entry["error_message"])
        self.assertEqual(len(violations), 1)

    def test_tracked_parse_failure_remains_a_typed_file_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp)
            self.init_repo(repository)
            path = repository / f"malformed{EVIDENCE_ONLY_SUFFIX}"
            malformed = "diff --git a/a b/a\n@@ malformed\n"
            path.write_text(malformed, encoding="utf-8")
            self.run_git(repository, "add", path.name)
            oid = self.run_git(repository, "rev-parse", f":{path.name}").strip()

            document, violations = build_receipt([path])

        entry = document["files"][0]
        self.assertEqual(entry["parse_state"], "parse-invalid")
        self.assertEqual(entry["repository_state"], "tracked-clean")
        self.assertEqual(entry["git_blob_oid"], oid)
        self.assertEqual(entry["error_type"], "PatchSyntaxError")
        self.assertEqual(len(violations), 1)


if __name__ == "__main__":
    unittest.main()
