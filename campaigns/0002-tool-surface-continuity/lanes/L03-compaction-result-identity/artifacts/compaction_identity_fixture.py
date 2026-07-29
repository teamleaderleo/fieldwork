#!/usr/bin/env python3
"""Deterministic synthetic fixtures for Codex compaction/result identity.

This models the relevant behavior at source revision
3725f02cf38d856bc82bb46dd68ab61bb96ec6fc without executing real tools.
It deliberately uses a benign synthetic mutation named ``set_marker``.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

SOURCE_REVISION = "3725f02cf38d856bc82bb46dd68ab61bb96ec6fc"
FIXTURE_VERSION = 1
SYNTHETIC_OUTPUT_ID_NAMESPACE = uuid.UUID("90d38d3e-6a5b-4d52-bfe2-2f1e634bfac4")

Item = dict[str, Any]


def user(text: str) -> Item:
    return {"kind": "message", "role": "user", "text": text, "id": f"msg_{hash8(text)}"}


def call(call_id: str = "call_marker_1", item_id: str = "fc_marker_1") -> Item:
    return {
        "kind": "function_call",
        "name": "set_marker",
        "arguments": {"value": "green"},
        "call_id": call_id,
        "id": item_id,
        "mutation": True,
    }


def result(
    text: str = "marker=green",
    *,
    call_id: str = "call_marker_1",
    item_id: str = "fco_marker_1",
    synthetic: bool = False,
) -> Item:
    return {
        "kind": "function_call_output",
        "call_id": call_id,
        "id": item_id,
        "output": text,
        "success": text != "aborted",
        "synthetic": synthetic,
    }


def hash8(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]


def digest(items: list[Item]) -> str:
    encoded = json.dumps(items, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def synthetic_output_id(prefix: str, source_item_id: str | None) -> str | None:
    if not source_item_id:
        return None
    derived = uuid.uuid5(SYNTHETIC_OUTPUT_ID_NAMESPACE, f"{prefix}:{source_item_id}")
    return f"{prefix}_{derived}"


def normalize_for_prompt(raw_items: list[Item]) -> list[Item]:
    """Model ContextManager::for_prompt identity behavior for function calls."""
    items = copy.deepcopy(raw_items)
    output_call_ids = {
        item["call_id"]
        for item in items
        if item.get("kind") == "function_call_output" and item.get("call_id")
    }

    insertions: list[tuple[int, Item]] = []
    for index, item in enumerate(items):
        if item.get("kind") != "function_call":
            continue
        call_id = item.get("call_id")
        if call_id not in output_call_ids:
            insertions.append(
                (
                    index,
                    result(
                        "aborted",
                        call_id=call_id,
                        item_id=synthetic_output_id("fco", item.get("id")),
                        synthetic=True,
                    ),
                )
            )

    for index, output in reversed(insertions):
        items.insert(index + 1, output)

    call_ids = {
        item["call_id"]
        for item in items
        if item.get("kind") == "function_call" and item.get("call_id")
    }
    return [
        item
        for item in items
        if item.get("kind") != "function_call_output" or item.get("call_id") in call_ids
    ]


def compact_install(prompt_items: list[Item], implementation: str) -> list[Item]:
    """Model the installed replacement histories for the three implementations."""
    retained_users = [
        copy.deepcopy(item)
        for item in prompt_items
        if item.get("kind") == "message" and item.get("role") == "user"
    ]
    if implementation == "local":
        checkpoint = {
            "kind": "message",
            "role": "user",
            "id": "msg_compaction_summary",
            "text": "[compaction summary: synthetic marker fixture]",
            "checkpoint": "summary",
        }
    elif implementation == "remote_v1":
        checkpoint = {
            "kind": "compaction",
            "id": "cmp_remote_v1",
            "encrypted_content": "fixture-remote-v1",
            "checkpoint": "remote_v1",
        }
    elif implementation == "remote_v2":
        checkpoint = {
            "kind": "compaction",
            "id": "cmp_remote_v2",
            "encrypted_content": "fixture-remote-v2",
            "checkpoint": "remote_v2",
        }
    else:
        raise ValueError(f"unknown implementation: {implementation}")
    return retained_users + [checkpoint]


def identity_census(items: list[Item]) -> dict[str, Any]:
    calls = [item for item in items if item.get("kind") == "function_call"]
    outputs = [item for item in items if item.get("kind") == "function_call_output"]
    positions = {
        "calls": [index for index, item in enumerate(items) if item.get("kind") == "function_call"],
        "outputs": [
            index for index, item in enumerate(items) if item.get("kind") == "function_call_output"
        ],
    }
    return {
        "call_count": len(calls),
        "output_count": len(outputs),
        "synthetic_output_count": sum(bool(item.get("synthetic")) for item in outputs),
        "positions": positions,
        "digest": digest(items),
    }


def fail_closed_check(raw_items: list[Item]) -> dict[str, Any]:
    calls = [(index, item) for index, item in enumerate(raw_items) if item.get("kind") == "function_call"]
    outputs = [
        (index, item)
        for index, item in enumerate(raw_items)
        if item.get("kind") == "function_call_output"
    ]
    reasons: list[str] = []
    by_call: dict[str, list[tuple[int, Item]]] = {}
    for index, output in outputs:
        by_call.setdefault(str(output.get("call_id")), []).append((index, output))

    seen_call_ids: set[str] = set()
    for call_index, call_item in calls:
        call_id = call_item.get("call_id")
        if not call_id:
            reasons.append("call_id_missing")
            continue
        if call_id in seen_call_ids:
            reasons.append(f"duplicate_call_id:{call_id}")
        seen_call_ids.add(call_id)
        if not call_item.get("id"):
            reasons.append(f"call_item_id_missing:{call_id}")
        matching = by_call.get(str(call_id), [])
        if len(matching) == 0:
            reasons.append(f"result_missing:{call_id}")
        elif len(matching) > 1:
            reasons.append(f"result_duplicated:{call_id}")
        else:
            output_index, output_item = matching[0]
            if not output_item.get("id"):
                reasons.append(f"result_item_id_missing:{call_id}")
            if output_index < call_index:
                reasons.append(f"result_precedes_call:{call_id}")

    known_call_ids = {str(item.get("call_id")) for _, item in calls if item.get("call_id")}
    for _, output in outputs:
        output_call_id = str(output.get("call_id"))
        if output_call_id not in known_call_ids:
            reasons.append(f"orphan_result:{output_call_id}")

    return {"allowed": not reasons, "reasons": sorted(set(reasons))}


def base_scenarios() -> dict[str, list[Item]]:
    prompt = user("Set the synthetic marker to green.")
    return {
        "complete": [prompt, call(), result()],
        "missing": [prompt, call()],
        "duplicated": [prompt, call(), result(), result("marker=green (duplicate)", item_id="fco_marker_2")],
        "reordered": [prompt, result(), call()],
        "late": [prompt, call()],
    }


def evaluate_case(name: str, raw_items: list[Item], implementation: str) -> dict[str, Any]:
    normalized_before = normalize_for_prompt(raw_items)
    installed = compact_install(normalized_before, implementation)
    resumed = copy.deepcopy(installed)

    raw_after_late = copy.deepcopy(installed)
    if name == "late":
        raw_after_late.append(result(item_id="fco_marker_late"))
    normalized_after_late = normalize_for_prompt(raw_after_late)

    return {
        "implementation": implementation,
        "scenario": name,
        "provider_compaction_completed": True,
        "raw_before": identity_census(raw_items),
        "prompt_before": identity_census(normalized_before),
        "fail_closed_at_boundary": fail_closed_check(raw_items),
        "installed_after_compaction": identity_census(installed),
        "resumed_or_forked": identity_census(resumed),
        "raw_after_late_delivery": identity_census(raw_after_late),
        "prompt_after_late_delivery": identity_census(normalized_after_late),
        "current_behavior": classify_current_behavior(name, normalized_before, normalized_after_late),
    }


def classify_current_behavior(
    name: str, normalized_before: list[Item], normalized_after_late: list[Item]
) -> str:
    if name == "complete":
        return "completed pair reaches compactor, then raw call/result identity is replaced by checkpoint"
    if name == "missing":
        return "missing result becomes prompt-only synthetic aborted output, then identity is replaced"
    if name == "duplicated":
        return "both results reach the compactor; no deduplication or fail-closed gate"
    if name == "reordered":
        return "existing result remains before its call; no causal reordering or fail-closed gate"
    if name == "late":
        after = identity_census(normalized_after_late)
        assert after["output_count"] == 0
        return "late result appended after checkpoint becomes orphan and disappears from the next prompt"
    raise AssertionError(name)


def assert_expected(report: dict[str, Any]) -> None:
    rows = {(row["implementation"], row["scenario"]): row for row in report["cases"]}
    for implementation in ("local", "remote_v1", "remote_v2"):
        complete = rows[(implementation, "complete")]
        assert complete["prompt_before"]["call_count"] == 1
        assert complete["prompt_before"]["output_count"] == 1
        assert complete["fail_closed_at_boundary"]["allowed"] is True
        assert complete["installed_after_compaction"]["call_count"] == 0
        assert complete["installed_after_compaction"]["output_count"] == 0

        missing = rows[(implementation, "missing")]
        assert missing["prompt_before"]["synthetic_output_count"] == 1
        assert missing["fail_closed_at_boundary"]["allowed"] is False

        duplicated = rows[(implementation, "duplicated")]
        assert duplicated["prompt_before"]["output_count"] == 2
        assert duplicated["fail_closed_at_boundary"]["allowed"] is False

        reordered = rows[(implementation, "reordered")]
        assert reordered["prompt_before"]["positions"]["outputs"][0] < reordered["prompt_before"]["positions"]["calls"][0]
        assert reordered["fail_closed_at_boundary"]["allowed"] is False

        late = rows[(implementation, "late")]
        assert late["raw_after_late_delivery"]["output_count"] == 1
        assert late["prompt_after_late_delivery"]["output_count"] == 0
        assert late["fail_closed_at_boundary"]["allowed"] is False


def build_report() -> dict[str, Any]:
    scenarios = base_scenarios()
    cases = [
        evaluate_case(name, items, implementation)
        for implementation in ("local", "remote_v1", "remote_v2")
        for name, items in scenarios.items()
    ]
    report = {
        "fixture_version": FIXTURE_VERSION,
        "source_revision": SOURCE_REVISION,
        "mutation": "synthetic set_marker(value=green)",
        "implementations": ["local", "remote_v1", "remote_v2"],
        "cases": cases,
        "summary": {
            "complete_pair_preserved_as_raw_items_after_compaction": False,
            "missing_result_synthesized_as_aborted_for_prompt": True,
            "duplicate_results_rejected": False,
            "reordered_result_rejected": False,
            "late_orphan_result_visible_to_next_prompt": False,
            "recommended_policy": "fail closed before compaction for mutation calls with incomplete or ambiguous identity",
        },
    }
    assert_expected(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
