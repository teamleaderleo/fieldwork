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


def run_git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def initialize_repo(repo: Path) -> None:
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.name", "Fieldwork Test")
    run_git(repo, "config", "user.email", "fieldwork@example.invalid")


def retain_patch(directory: Path, name: str, patch_text: str) -> Path:
    patch = directory / name
    patch.write_text(patch_text, encoding="utf-8")
    validate_patch_text(patch_text, str(patch))
    validate_patch_with_git(patch)
    return patch


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

            # The custom layer intentionally checks structure, not base85/zlib.
            validate_patch_text(patch_text, str(path))
            with self.assertRaisesRegex(
                NativePatchSyntaxError,
                "git apply --numstat rejected retained patch",
            ):
                validate_patch_with_git(path)

    def test_accepts_real_git_generated_binary_patch_without_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "source"
            initialize_repo(repo)

            binary = repo / "image.bin"
            binary.write_bytes(b"\x00old binary payload\n")
            run_git(repo, "add", "image.bin")
            run_git(repo, "commit", "-qm", "base binary")

            binary.write_bytes(b"\x00new binary payload with more bytes\n")
            generated = run_git(repo, "diff", "--binary", "HEAD", "--", "image.bin")
            self.assertIn("GIT binary patch", generated)

            # Parse-only validation must not depend on target applicability.
            binary.unlink()
            patch = retain_patch(root, "generated.patch", generated)
            numstat = validate_patch_with_git(patch)
            self.assertIn("image.bin", numstat)

    def test_accepts_mode_only_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "source"
            initialize_repo(repo)
            script = repo / "script.sh"
            script.write_text("echo ok\n", encoding="utf-8")
            run_git(repo, "add", "script.sh")
            run_git(repo, "commit", "-qm", "base mode")

            script.chmod(0o755)
            generated = run_git(repo, "diff", "HEAD", "--", "script.sh")
            self.assertIn("old mode", generated)
            retain_patch(root, "mode.patch", generated)

    def test_accepts_full_similarity_rename_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "source"
            initialize_repo(repo)
            original = repo / "before.txt"
            original.write_text("same contents\n", encoding="utf-8")
            run_git(repo, "add", "before.txt")
            run_git(repo, "commit", "-qm", "base rename")

            run_git(repo, "mv", "before.txt", "after.txt")
            generated = run_git(repo, "diff", "--cached", "HEAD", "--")
            self.assertIn("similarity index 100%", generated)
            retain_patch(root, "rename.patch", generated)

    def test_accepts_binary_summary_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "source"
            initialize_repo(repo)
            binary = repo / "image.bin"
            binary.write_bytes(b"\x00old\n")
            run_git(repo, "add", "image.bin")
            run_git(repo, "commit", "-qm", "base summary")

            binary.write_bytes(b"\x00new\n")
            generated = run_git(repo, "diff", "HEAD", "--", "image.bin")
            self.assertIn("Binary files", generated)
            retain_patch(root, "binary-summary.patch", generated)

    def test_accepts_empty_file_creation_patch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = root / "source"
            initialize_repo(repo)
            run_git(repo, "commit", "--allow-empty", "-qm", "empty base")

            (repo / "empty.txt").touch()
            run_git(repo, "add", "empty.txt")
            generated = run_git(repo, "diff", "--cached", "HEAD", "--", "empty.txt")
            self.assertIn("new file mode", generated)
            retain_patch(root, "empty-file.patch", generated)


if __name__ == "__main__":
    unittest.main()
