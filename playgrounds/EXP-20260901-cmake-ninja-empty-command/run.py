#!/usr/bin/env python3
"""Probe the generated Ninja rule for a custom command that evaluates empty."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import tempfile


def first_line(command: list[str]) -> str:
    result = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout.splitlines()[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmake", default="cmake")
    parser.add_argument("--ninja", default="ninja")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="cmake-empty-command-") as temporary:
        root = pathlib.Path(temporary)
        source = root / "src"
        build = root / "build"
        source.mkdir()
        (source / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.20)\n"
            "project(empty NONE)\n"
            "add_custom_command(\n"
            "  OUTPUT empty\n"
            "  COMMAND \"$<$<BOOL:0>:${CMAKE_COMMAND}>\"\n"
            "  VERBATIM\n"
            ")\n"
            "add_custom_target(gen ALL DEPENDS empty)\n",
            encoding="utf-8",
        )
        subprocess.run(
            [args.cmake, "-S", str(source), "-B", str(build), "-G", "Ninja"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        build_ninja = (build / "build.ninja").read_text(encoding="utf-8")
        lines = build_ninja.splitlines()
        rule_index, rule = next(
            (index, line)
            for index, line in enumerate(lines)
            if line.startswith("build empty ")
        )
        command = next(
            (
                line.strip()
                for line in lines[rule_index + 1 : rule_index + 6]
                if line.startswith("  COMMAND = ")
            ),
            None,
        )

        result = {
            "schema_version": 1,
            "cmake": first_line([args.cmake, "--version"]),
            "ninja": first_line([args.ninja, "--version"]),
            "rule": rule,
            "command": command,
            "is_phony": rule.endswith(": phony") or ": phony " in rule,
            "has_working_directory_only_command": bool(
                command and re.match(r"^COMMAND = cd(?: /D)? ", command)
            ),
        }
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
