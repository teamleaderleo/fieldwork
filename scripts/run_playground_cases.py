#!/usr/bin/env python3
"""Run reusable Fieldwork case packs against a small stdin/stdout adapter."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Any

SCHEMA_VERSION = 1
DEFAULT_CASE_DIR = Path("playgrounds/cases")


class PackError(ValueError):
    pass


def _is_valid_timeout(value: Any) -> bool:
    if type(value) is int:
        if value <= 0:
            return False
        try:
            return math.isfinite(float(value))
        except OverflowError:
            return False
    if type(value) is float:
        return math.isfinite(value) and value > 0
    return False


def _json_values_equal(left: Any, right: Any) -> bool:
    """Compare decoded JSON without conflating booleans and numbers."""
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, dict) or isinstance(right, dict):
        if not isinstance(left, dict) or not isinstance(right, dict):
            return False
        return left.keys() == right.keys() and all(
            _json_values_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list) or isinstance(right, list):
        if not isinstance(left, list) or not isinstance(right, list):
            return False
        return len(left) == len(right) and all(
            _json_values_equal(left_value, right_value)
            for left_value, right_value in zip(left, right)
        )
    return left == right


def load_pack(path: Path) -> dict[str, Any]:
    try:
        pack = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackError(f"{path}: unable to load JSON: {exc}") from exc

    if not isinstance(pack, dict):
        raise PackError(f"{path}: pack must be a JSON object")
    schema_version = pack.get("schema_version")
    if type(schema_version) is not int or schema_version != SCHEMA_VERSION:
        raise PackError(
            f"{path}: schema_version must be integer {SCHEMA_VERSION}, "
            f"got {schema_version!r}"
        )
    if not isinstance(pack.get("name"), str) or not pack["name"].strip():
        raise PackError(f"{path}: name must be a non-empty string")
    if "timeout_seconds" in pack and not _is_valid_timeout(pack["timeout_seconds"]):
        raise PackError(
            f"{path}: timeout_seconds must be a finite positive number"
        )

    cases = pack.get("cases")
    if not isinstance(cases, list) or not cases:
        raise PackError(f"{path}: cases must be a non-empty array")

    seen: set[str] = set()
    for index, case in enumerate(cases):
        location = f"{path}: cases[{index}]"
        if not isinstance(case, dict):
            raise PackError(f"{location}: case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise PackError(f"{location}: id must be a non-empty string")
        if case_id in seen:
            raise PackError(f"{location}: duplicate id {case_id!r}")
        seen.add(case_id)

        has_json = "stdin_json" in case
        has_text = "stdin_text" in case
        if has_json == has_text:
            raise PackError(
                f"{location}: provide exactly one of stdin_json or stdin_text"
            )

        if "timeout_seconds" in case and not _is_valid_timeout(case["timeout_seconds"]):
            raise PackError(
                f"{location}: timeout_seconds must be a finite positive number"
            )
        timeout = case.get("timeout_seconds", pack.get("timeout_seconds", 5))
        if not _is_valid_timeout(timeout):
            raise PackError(
                f"{location}: timeout_seconds must be a finite positive number"
            )

        expect = case.get("expect", {})
        if not isinstance(expect, dict):
            raise PackError(f"{location}: expect must be an object")
        allowed = {
            "exit_code",
            "stdout_json",
            "stdout_contains",
            "stderr_contains",
            "timed_out",
        }
        unknown = set(expect) - allowed
        if unknown:
            raise PackError(f"{location}: unknown expectation keys: {sorted(unknown)}")

        if "exit_code" in expect:
            expected_exit_code = expect["exit_code"]
            if expected_exit_code is not None and type(expected_exit_code) is not int:
                raise PackError(f"{location}: expect.exit_code must be an integer or null")
        if "timed_out" in expect and type(expect["timed_out"]) is not bool:
            raise PackError(f"{location}: expect.timed_out must be boolean")

    return pack


def discover_packs(case_dir: Path) -> list[Path]:
    return sorted(path for path in case_dir.glob("*.json") if path.is_file())


def stdin_for(case: dict[str, Any]) -> str:
    if "stdin_json" in case:
        return json.dumps(case["stdin_json"], ensure_ascii=False) + "\n"
    return str(case["stdin_text"])


def check_expectations(
    case: dict[str, Any],
    *,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    timed_out: bool,
) -> list[str]:
    expect = case.get("expect", {})
    failures: list[str] = []

    if "timed_out" in expect and expect["timed_out"] != timed_out:
        failures.append(
            f"timed_out expected {expect['timed_out']}, got {timed_out}"
        )
    if "exit_code" in expect and expect["exit_code"] != exit_code:
        failures.append(f"exit_code expected {expect['exit_code']}, got {exit_code}")
    if "stdout_contains" in expect and str(expect["stdout_contains"]) not in stdout:
        failures.append(f"stdout did not contain {expect['stdout_contains']!r}")
    if "stderr_contains" in expect and str(expect["stderr_contains"]) not in stderr:
        failures.append(f"stderr did not contain {expect['stderr_contains']!r}")
    if "stdout_json" in expect:
        try:
            actual_json = json.loads(stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"stdout was not valid JSON: {exc}")
        else:
            if not _json_values_equal(actual_json, expect["stdout_json"]):
                failures.append(
                    f"stdout_json expected {expect['stdout_json']!r}, "
                    f"got {actual_json!r}"
                )

    return failures


def run_case(command: list[str], pack: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    timeout = float(case.get("timeout_seconds", pack.get("timeout_seconds", 5)))
    started = time.monotonic()
    timed_out = False
    exit_code: int | None
    stdout = ""
    stderr = ""

    try:
        completed = subprocess.run(
            command,
            input=stdin_for(case),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""

    duration_ms = round((time.monotonic() - started) * 1000, 3)
    failures = check_expectations(
        case,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
    )

    return {
        "id": case["id"],
        "tags": case.get("tags", []),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "stdout": stdout,
        "stderr": stderr,
        "status": "failed" if failures else ("passed" if case.get("expect") else "observed"),
        "failures": failures,
    }


def validate_all(case_dir: Path) -> int:
    paths = discover_packs(case_dir)
    if not paths:
        print(f"No case packs found under {case_dir}", file=sys.stderr)
        return 1

    failed = False
    for path in paths:
        try:
            pack = load_pack(path)
        except PackError as exc:
            failed = True
            print(exc, file=sys.stderr)
        else:
            print(f"valid: {path} ({len(pack['cases'])} cases)")
    return 1 if failed else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="list bundled case packs")
    mode.add_argument("--validate", action="store_true", help="validate bundled case packs")
    mode.add_argument("--pack", type=Path, help="case-pack JSON file to execute")
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--adapter", help="adapter command, parsed without a shell")
    parser.add_argument("--output", type=Path, help="write the full result JSON here")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list:
        for path in discover_packs(args.case_dir):
            try:
                pack = load_pack(path)
                description = pack.get("description", "")
                print(f"{path}: {pack['name']} — {description}")
            except PackError as exc:
                print(exc, file=sys.stderr)
                return 1
        return 0

    if args.validate:
        return validate_all(args.case_dir)

    if not args.adapter:
        print("--adapter is required with --pack", file=sys.stderr)
        return 2

    try:
        pack = load_pack(args.pack)
    except PackError as exc:
        print(exc, file=sys.stderr)
        return 1

    command = shlex.split(args.adapter)
    if not command:
        print("adapter command is empty", file=sys.stderr)
        return 2

    results = [run_case(command, pack, case) for case in pack["cases"]]
    summary = {
        "schema_version": 1,
        "pack": pack["name"],
        "adapter": command,
        "case_count": len(results),
        "passed": sum(result["status"] == "passed" for result in results),
        "observed": sum(result["status"] == "observed" for result in results),
        "failed": sum(result["status"] == "failed" for result in results),
        "results": results,
    }

    rendered = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    for result in results:
        print(f"{result['status']:>8}  {result['id']}", file=sys.stderr)
        for failure in result["failures"]:
            print(f"          {failure}", file=sys.stderr)

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
