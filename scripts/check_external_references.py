#!/usr/bin/env python3
"""Reject accidental direct cross-links to external GitHub work."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

MARKER = "fieldwork: intentional-upstream-reference"
SCANNED_SUFFIXES = {
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".json",
    ".jsonl",
    ".toml",
    ".yaml",
    ".yml",
}

DIRECT_URL = re.compile(
    r"https?://github\.com/"
    r"(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)/"
    r"(?P<kind>issues|pull|discussions|commit)/"
    r"(?P<identifier>[A-Za-z0-9_.-]+)"
)

SHORTHAND = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"(?P<owner>[A-Za-z0-9_.-]+)/"
    r"(?P<repo>[A-Za-z0-9_.-]+)#"
    r"(?P<number>[0-9]+)\b"
)


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def current_repository() -> str | None:
    value = os.environ.get("GITHUB_REPOSITORY")
    if value:
        return value.lower()

    try:
        remote = run_git("config", "--get", "remote.origin.url")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    if remote.startswith("git@github.com:"):
        path = remote.removeprefix("git@github.com:")
    else:
        parsed = urlparse(remote)
        if parsed.hostname != "github.com":
            return None
        path = parsed.path.lstrip("/")

    return path.removesuffix(".git").lower() or None


def tracked_files() -> list[Path]:
    try:
        names = run_git("ls-files", "-z").split("\0")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError("unable to list tracked files") from exc

    return [
        Path(name)
        for name in names
        if name and Path(name).suffix.lower() in SCANNED_SUFFIXES
    ]


def has_intentional_marker(lines: list[str], index: int) -> bool:
    start = max(0, index - 2)
    return any(MARKER in lines[position] for position in range(start, index + 1))


def is_same_repository(owner: str, repo: str, current: str | None) -> bool:
    return current == f"{owner}/{repo}".lower()


def scan_file(path: Path, current: str | None) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []

    errors: list[str] = []
    for index, line in enumerate(lines):
        intentional = has_intentional_marker(lines, index)

        for match in DIRECT_URL.finditer(line):
            owner = match.group("owner")
            repo = match.group("repo")
            if is_same_repository(owner, repo, current) or intentional:
                continue

            original = match.group(0)
            wrapped = original.replace(
                "https://github.com/", "https://redirect.github.com/", 1
            ).replace("http://github.com/", "https://redirect.github.com/", 1)
            errors.append(
                f"{path}:{index + 1}: direct external GitHub reference: {original}\n"
                f"  use {wrapped} or add an intentional-reference marker"
            )

        for match in SHORTHAND.finditer(line):
            owner = match.group("owner")
            repo = match.group("repo")
            if is_same_repository(owner, repo, current) or intentional:
                continue

            errors.append(
                f"{path}:{index + 1}: external shorthand reference: "
                f"{match.group(0)}\n"
                "  replace it with a descriptive redirect.github.com link"
            )

    return errors


def main() -> int:
    current = current_repository()
    failures: list[str] = []

    for path in tracked_files():
        failures.extend(scan_file(path, current))

    if failures:
        print("External reference policy violations:\n", file=sys.stderr)
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    print("External reference policy check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
