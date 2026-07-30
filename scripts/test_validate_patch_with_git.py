#!/usr/bin/env python3
"""Focused tests for the native Git retained-patch parser gate."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.validate_patch_syntax import validate_patch_text
from scripts.validate_patch_with_git import (
    NativePatchSyntaxError,
    validate_patch_with_git,
)


class NativePatchSyntaxTests(unittest.TestCase):
    def test_rejects_nonempty_malformed_binary_payload(self) -> None:
        patch_text = """diff --git a/image.bin b/image.bin
index 1111111..2222222 100644
GIT binary patch
literal 10
garbage

"""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "malformed.patch"
            path.write_text(patch_text, encoding="utf-8")
            with self.assertRaisesRegex(
                NativePatchSyntaxError,
                "git apply --numstat rejected retained patch",
            ):
                validate_patch_with_git(path)

    def test_accepts_real_git_generated_binary_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "source"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.name", "Fieldwork Test"],
                cwd=repo,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "fieldwork@example.invalid"],
                cwd=repo,
                check=True,
            )

            binary = repo / "image.bin"
            binary.write_bytes(b"\x00old binary payload\n")
            subprocess.run(["git", "add", "image.bin"], cwd=repo, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "base binary"],
                cwd=repo,
                check=True,
            )

            binary.write_bytes(b"\x00new binary payload with more bytes\n")
            generated = subprocess.run(
                ["git", "diff", "--binary", "HEAD", "--", "image.bin"],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
            self.assertIn("GIT binary patch", generated)

            patch = Path(temp_dir) / "generated.patch"
            patch.write_text(generated, encoding="utf-8")

            # Both diagnostic layers must accept a real Git-produced patch.
            validate_patch_text(generated, str(patch))
            numstat = validate_patch_with_git(patch)
            self.assertIn("image.bin", numstat)


if __name__ == "__main__":
    unittest.main()
