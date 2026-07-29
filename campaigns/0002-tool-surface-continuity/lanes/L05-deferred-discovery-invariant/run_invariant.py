#!/usr/bin/env python3
"""Audit request-level deferred-tool discovery invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

LOAD_EXISTING = "load_existing_deferred_tools"
DIRECT = {"direct", "direct_model_only"}


def classify(case: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    presence = case.get("presence")
    exposure = case.get("exposure")
    discovery = case.get("discovery", {})

    if presence == "absent":
        return "accept", reasons

    if exposure in DIRECT:
        return "accept", reasons

    if exposure != "deferred":
        reasons.append(f"unknown exposure {exposure!r}")
        return "reject", reasons

    if not case.get("search_metadata", False):
        reasons.append("deferred family has no searchable metadata")

    if discovery.get("tool") is None or discovery.get("execution") == "absent":
        reasons.append("discovery tool absent")
    else:
        if not discovery.get("advertised", False):
            reasons.append("discovery route is not advertised in the request")
        if not discovery.get("registered", False):
            reasons.append("discovery route has no registered runtime")
        if not discovery.get("executable", False):
            reasons.append("discovery route is not executable")
        if discovery.get("semantics") != LOAD_EXISTING:
            reasons.append("discovery semantics do not load existing deferred tools")

    # An executed discovery call with zero matches is healthy. Route existence
    # and execution are separate from the number of returned tools.
    if discovery.get("execution") == "executed":
        result_count = discovery.get("result_count")
        if not isinstance(result_count, int) or result_count < 0:
            reasons.append("executed discovery has an invalid result_count")

    return ("reject" if reasons else "accept"), reasons


def audit(document: dict[str, Any]) -> dict[str, Any]:
    rows = []
    mismatches = []
    for case in document.get("cases", []):
        actual, reasons = classify(case)
        expected = case.get("expected")
        row = {
            "id": case.get("id"),
            "family": case.get("family"),
            "expected": expected,
            "actual": actual,
            "reasons": reasons,
            "discovery_execution": case.get("discovery", {}).get("execution"),
            "result_count": case.get("discovery", {}).get("result_count"),
        }
        rows.append(row)
        if expected != actual:
            mismatches.append(row)

    return {
        "schema_version": 1,
        "source_revision": document.get("source_revision"),
        "case_count": len(rows),
        "accepted": [row["id"] for row in rows if row["actual"] == "accept"],
        "rejected": [row["id"] for row in rows if row["actual"] == "reject"],
        "mismatches": mismatches,
        "passed": not mismatches,
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    document = json.loads(args.fixture.read_text(encoding="utf-8"))
    result = audit(document)
    rendered = json.dumps(result, indent=2) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
