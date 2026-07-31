#!/usr/bin/env python3
"""Reversing controls for retained-patch index identity movement."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import scripts.classify_retained_patches as classifier


TEXT_PATCH = """diff --git a/a.txt b/a.txt
--- a/a.txt
+++ b/a.txt
@@ -1 +1 @@
-old
+new
"""
REPLACEMENT_PATCH = TEXT_PATCH.replace("+new", "+replacement")


class RetainedPatchIndexMovementTests(unittest.TestCase):
    def run_git(
        self,
        repository: Path,
        *args: str,
        input_bytes: bytes | None = None,
    ) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repository,
            input=input_bytes,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout.decode("utf-8", errors="strict")

    def init_repo(self, repository: Path) -> None:
        self.run_git(repository, "init", "-q")
        self.run_git(repository, "config", "user.name", "Fieldwork Test")
        self.run_git(
            repository,
            "config",
            "user.email",
            "fieldwork@example.invalid",
        )

    def test_unchanged_index_remains_tracked_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            self.init_repo(repository)
            path = repository / "candidate.patch"
            path.write_text(TEXT_PATCH, encoding="utf-8")
            self.run_git(repository, "add", path.name)
            original_oid = self.run_git(
                repository,
                "rev-parse",
                f":{path.name}",
            ).strip()

            document, violations = classifier.build_receipt([path])

        self.assertEqual(violations, [])
        self.assertEqual(len(document["files"]), 1)
        entry = document["files"][0]
        self.assertEqual(entry["repository_state"], "tracked-clean")
        self.assertTrue(entry["repository_policy_eligible"])
        self.assertEqual(entry["git_blob_oid"], original_oid)
        self.assertEqual(entry["parse_state"], "parse-valid")
        self.assertEqual(entry["section_kinds"], ("textual-hunks",))

    def test_index_movement_between_observations_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            self.init_repo(repository)
            path = repository / "candidate.patch"
            path.write_text(TEXT_PATCH, encoding="utf-8")
            self.run_git(repository, "add", path.name)
            original_oid = self.run_git(
                repository,
                "rev-parse",
                f":{path.name}",
            ).strip()
            replacement_oid = self.run_git(
                repository,
                "hash-object",
                "-w",
                "--stdin",
                input_bytes=REPLACEMENT_PATCH.encode("utf-8"),
            ).strip()

            original_stage_entry = classifier._stage_entry
            observations = 0

            def stage_entry_with_one_index_flip(
                root: Path,
                relative: Path,
            ) -> tuple[str, str, str] | None:
                nonlocal observations
                observed = original_stage_entry(root, relative)
                observations += 1
                if observations == 1:
                    self.run_git(
                        root,
                        "update-index",
                        "--cacheinfo",
                        "100644",
                        replacement_oid,
                        relative.as_posix(),
                    )
                return observed

            with mock.patch.object(
                classifier,
                "_stage_entry",
                side_effect=stage_entry_with_one_index_flip,
            ):
                document, violations = classifier.build_receipt([path])

            current_oid = self.run_git(
                repository,
                "rev-parse",
                f":{path.name}",
            ).strip()

        self.assertEqual(observations, 2)
        self.assertEqual(current_oid, replacement_oid)
        self.assertNotEqual(original_oid, replacement_oid)
        self.assertEqual(len(document["files"]), 1)
        entry = document["files"][0]
        self.assertEqual(entry["error_code"], "index-changed-during-inspection")
        self.assertEqual(entry["error_type"], "ArtifactIdentityError")
        self.assertEqual(entry["parse_state"], "not-inspected")
        self.assertEqual(entry["materialization_state"], "unknown")
        self.assertEqual(entry["section_kinds"], [])
        self.assertEqual(entry["native_numstat"], [])
        self.assertEqual(entry["repository_state"], "tracked-invalid")
        self.assertFalse(entry["repository_policy_eligible"])
        self.assertEqual(entry["git_blob_oid"], original_oid)
        self.assertEqual(entry["raw_sha256"], hashlib.sha256(TEXT_PATCH.encode()).hexdigest())
        self.assertEqual(entry["byte_length"], len(TEXT_PATCH.encode()))
        self.assertEqual(document["repositoryStateCounts"], {"tracked-invalid": 1})
        self.assertEqual(len(violations), 1)
        self.assertIn("index-changed-during-inspection", violations[0])


if __name__ == "__main__":
    unittest.main()
