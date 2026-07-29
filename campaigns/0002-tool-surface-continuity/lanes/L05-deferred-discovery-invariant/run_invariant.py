#!/usr/bin/env python3
"""Audit planner-to-wire deferred-tool discovery invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

LOAD_EXISTING = "load_existing_deferred_tools"
DIRECT = {"direct", "direct_model_only"}
VALID_DELIVERY = {"direct", "inherited_verified"}


def classify(case: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    warning_codes: list[str] = []
    presence = case.get("presence")
    exposure = case.get("exposure")
    discovery = case.get("discovery", {})

    if presence == "absent":
        return "accept", reasons, warning_codes

    if exposure in DIRECT:
        return "accept", reasons, warning_codes

    if exposure != "deferred":
        reasons.append(f"unknown exposure {exposure!r}")
        return "reject", reasons, warning_codes

    if not case.get("search_metadata", False):
        reasons.append("deferred family has no searchable metadata")

    if discovery.get("tool") is None or discovery.get("execution") == "absent":
        reasons.append("discovery tool absent")
    else:
        if not discovery.get("advertised", False):
            reasons.append("discovery route is not advertised in the logical request")
        if not discovery.get("registered", False):
            reasons.append("discovery route has no registered runtime")
        if not discovery.get("executable", False):
            reasons.append("discovery route is not executable")
        if discovery.get("semantics") != LOAD_EXISTING:
            reasons.append("discovery semantics do not load existing deferred tools")

        delivery = discovery.get(
            "delivery", "direct" if discovery.get("advertised", False) else "absent"
        )
        if delivery not in VALID_DELIVERY:
            if delivery == "omitted_unverified":
                reasons.append(
                    "discovery route is present logically but omitted from the wire without verified inheritance"
                )
            elif delivery == "absent":
                reasons.append("discovery route is absent from the effective wire request")
            else:
                reasons.append(f"unknown discovery delivery state {delivery!r}")

    # An executed discovery call with zero matches is healthy. Route existence
    # and execution are separate from the number of returned tools.
    if discovery.get("execution") == "executed":
        result_count = discovery.get("result_count")
        if not isinstance(result_count, int) or result_count < 0:
            reasons.append("executed discovery has an invalid result_count")

    if discovery.get("catalogue_state") == "stale":
        warning_codes.append("stale_discovery_catalogue")

    if case.get("provenance_state") == "stale_saved":
        warning_codes.append("stale_saved_provenance")

    return ("reject" if reasons else "accept"), reasons, warning_codes


def audit(document: dict[str, Any]) -> dict[str, Any]:
    rows = []
    mismatches = []
    for case in document.get("cases", []):
        actual, reasons, warning_codes = classify(case)
        expected = case.get("expected")
        expected_warning_codes = sorted(case.get("expected_warning_codes", []))
        actual_warning_codes = sorted(warning_codes)
        row = {
            "id": case.get("id"),
            "family": case.get("family"),
            "expected": expected,
            "actual": actual,
            "reasons": reasons,
            "expected_warning_codes": expected_warning_codes,
            "warning_codes": actual_warning_codes,
            "discovery_execution": case.get("discovery", {}).get("execution"),
            "discovery_delivery": case.get("discovery", {}).get("delivery"),
            "result_count": case.get("discovery", {}).get("result_count"),
        }
        rows.append(row)
        if expected != actual or expected_warning_codes != actual_warning_codes:
            mismatches.append(row)

    return {
        "schema_version": 2,
        "source_revision": document.get("source_revision"),
        "case_count": len(rows),
        "accepted": [row["id"] for row in rows if row["actual"] == "accept"],
        "rejected": [row["id"] for row in rows if row["actual"] == "reject"],
        "warnings": [
            {"id": row["id"], "codes": row["warning_codes"]}
            for row in rows
            if row["warning_codes"]
        ],
        "mismatches": mismatches,
        "passed": not mismatches,
        "cases": rows,
        "command": document.get("command"),
        "run_date": document.get("run_date"),
        "environment": document.get("environment"),
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
