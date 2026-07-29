#!/usr/bin/env python3
"""Model Codex's source-defined HTTP/WebSocket prewarm reuse boundary.

This is a protocol fixture, not an OpenAI service emulator. It preserves the
request-building and incremental-reuse properties needed to distinguish:
- full HTTP transmission,
- fresh/full WebSocket transmission,
- prewarm -> first-turn incremental WebSocket transmission,
- changed tool manifests,
- reconnect and restart state reset.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

Json = dict[str, Any]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()[:16]


def additional_tools_item(tools: list[Json]) -> Json:
    return {"type": "additional_tools", "role": "developer", "tools": copy.deepcopy(tools)}


def developer_message(text: str) -> Json:
    return {"type": "message", "role": "developer", "content": text}


def build_request(
    fixture: Json,
    *,
    use_responses_lite: bool,
    request_kind: str,
    history: list[Json],
    tools: list[Json],
) -> Json:
    input_items = copy.deepcopy(history)
    if use_responses_lite:
        prefix = [additional_tools_item(tools)]
        if fixture["base_instructions"]:
            prefix.append(developer_message(fixture["base_instructions"]))
        input_items = prefix + input_items
        instructions = ""
        top_level_tools = None
    else:
        instructions = fixture["base_instructions"]
        top_level_tools = copy.deepcopy(tools)

    return {
        "model": fixture["model"],
        "instructions": instructions,
        "input": input_items,
        "tools": top_level_tools,
        "tool_choice": "auto",
        "parallel_tool_calls": not use_responses_lite,
        "reasoning": {"effort": "medium", "context": "all_turns" if use_responses_lite else None},
        "store": False,
        "stream": True,
        "stream_options": None,
        "include": ["reasoning.encrypted_content"],
        "service_tier": None,
        "prompt_cache_key": "thread-37",
        "text": None,
        "client_metadata": {
            "session_id": "session-37",
            "thread_id": "thread-37",
            "request_kind": request_kind,
        },
    }


def properties_match(previous: Json, current: Json) -> bool:
    # Mirrors responses_request_properties_match: input and client_metadata are
    # compared elsewhere/ignored; stream_options is deliberately ignored.
    compared = (
        "model",
        "instructions",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
        "reasoning",
        "store",
        "stream",
        "include",
        "service_tier",
        "prompt_cache_key",
        "text",
    )
    return all(previous.get(key) == current.get(key) for key in compared)


def incremental_items(previous: Json, current: Json) -> list[Json] | None:
    if not properties_match(previous, current):
        return None
    baseline = previous["input"]
    if len(current["input"]) < len(baseline):
        return None
    if current["input"][: len(baseline)] != baseline:
        return None
    return copy.deepcopy(current["input"][len(baseline) :])


def http_wire(request: Json) -> Json:
    return copy.deepcopy(request)


def websocket_wire(
    request: Json,
    *,
    previous_request: Json | None,
    previous_response_id: str | None,
    connection_alive: bool,
) -> Json:
    reuse = None
    if connection_alive and previous_request is not None and previous_response_id:
        reuse = incremental_items(previous_request, request)
    wire = copy.deepcopy(request)
    wire["type"] = "response.create"
    if reuse is None:
        wire.pop("previous_response_id", None)
    else:
        wire["previous_response_id"] = previous_response_id
        wire["input"] = reuse
    return wire


def direct_wire_tools(wire: Json) -> list[Json]:
    if isinstance(wire.get("tools"), list):
        return copy.deepcopy(wire["tools"])
    for item in wire.get("input", []):
        if item.get("type") == "additional_tools":
            return copy.deepcopy(item.get("tools", []))
    return []


def logical_tools(request: Json) -> list[Json]:
    return direct_wire_tools(request)


def tool_names(tools: list[Json]) -> list[str]:
    return [str(tool.get("name", "")) for tool in tools]


def benign_exec(tools: list[Json]) -> str:
    return "TOOL_OK" if "exec" in tool_names(tools) else "TOOL_UNAVAILABLE"


def summarize_case(name: str, logical: Json, wire: Json, inherited: list[Json] | None = None) -> Json:
    direct = direct_wire_tools(wire)
    effective = direct or copy.deepcopy(inherited or [])
    return {
        "case": name,
        "previous_response_id": wire.get("previous_response_id"),
        "wire_input_types": [item.get("type") for item in wire.get("input", [])],
        "logical_tool_names": tool_names(logical_tools(logical)),
        "direct_wire_tool_names": tool_names(direct),
        "effective_tool_names_if_inheritance_holds": tool_names(effective),
        "logical_tool_digest": digest(logical_tools(logical)),
        "direct_wire_tool_digest": digest(direct),
        "benign_exec_if_inheritance_holds": benign_exec(effective),
    }


def run(fixture: Json) -> Json:
    history = fixture["history"]
    startup_tools = fixture["startup_tools"]
    turn_tools = fixture["turn_tools"]
    changed_tools = fixture["changed_turn_tools"]

    lite_prewarm = build_request(
        fixture,
        use_responses_lite=True,
        request_kind="prewarm",
        history=[],
        tools=startup_tools,
    )
    lite_turn = build_request(
        fixture,
        use_responses_lite=True,
        request_kind="turn",
        history=history,
        tools=turn_tools,
    )
    lite_changed_turn = build_request(
        fixture,
        use_responses_lite=True,
        request_kind="turn",
        history=history,
        tools=changed_tools,
    )
    non_lite_prewarm = build_request(
        fixture,
        use_responses_lite=False,
        request_kind="prewarm",
        history=[],
        tools=startup_tools,
    )
    non_lite_turn = build_request(
        fixture,
        use_responses_lite=False,
        request_kind="turn",
        history=history,
        tools=turn_tools,
    )

    lite_incremental = websocket_wire(
        lite_turn,
        previous_request=lite_prewarm,
        previous_response_id="warm-lite",
        connection_alive=True,
    )
    lite_changed = websocket_wire(
        lite_changed_turn,
        previous_request=lite_prewarm,
        previous_response_id="warm-lite",
        connection_alive=True,
    )
    non_lite_incremental = websocket_wire(
        non_lite_turn,
        previous_request=non_lite_prewarm,
        previous_response_id="warm-non-lite",
        connection_alive=True,
    )
    fresh_lite = websocket_wire(
        lite_turn,
        previous_request=None,
        previous_response_id=None,
        connection_alive=True,
    )
    reconnect_lite = websocket_wire(
        lite_turn,
        previous_request=lite_prewarm,
        previous_response_id="warm-lite",
        connection_alive=False,
    )
    restart_lite = websocket_wire(
        lite_turn,
        previous_request=None,
        previous_response_id=None,
        connection_alive=False,
    )
    http_lite = http_wire(lite_turn)

    cases = [
        summarize_case("http_same_history_lite", lite_turn, http_lite),
        summarize_case("fresh_thread_websocket_lite", lite_turn, fresh_lite),
        summarize_case(
            "clean_prewarm_websocket_lite",
            lite_turn,
            lite_incremental,
            inherited=logical_tools(lite_prewarm),
        ),
        summarize_case("changed_tools_websocket_lite", lite_changed_turn, lite_changed),
        summarize_case("reconnect_websocket_lite", lite_turn, reconnect_lite),
        summarize_case("restart_websocket_lite", lite_turn, restart_lite),
        summarize_case(
            "clean_prewarm_websocket_non_lite",
            non_lite_turn,
            non_lite_incremental,
            inherited=logical_tools(non_lite_prewarm),
        ),
    ]

    by_name = {case["case"]: case for case in cases}
    assert by_name["http_same_history_lite"]["direct_wire_tool_names"] == ["exec", "file_edit"]
    assert by_name["fresh_thread_websocket_lite"]["direct_wire_tool_names"] == ["exec", "file_edit"]
    assert by_name["clean_prewarm_websocket_lite"]["previous_response_id"] == "warm-lite"
    assert by_name["clean_prewarm_websocket_lite"]["direct_wire_tool_names"] == []
    assert by_name["clean_prewarm_websocket_lite"]["effective_tool_names_if_inheritance_holds"] == [
        "exec",
        "file_edit",
    ]
    assert by_name["changed_tools_websocket_lite"]["previous_response_id"] is None
    assert by_name["changed_tools_websocket_lite"]["direct_wire_tool_names"] == [
        "exec",
        "file_edit",
        "view_image",
    ]
    assert by_name["reconnect_websocket_lite"]["previous_response_id"] is None
    assert by_name["restart_websocket_lite"]["previous_response_id"] is None
    assert by_name["clean_prewarm_websocket_non_lite"]["direct_wire_tool_names"] == [
        "exec",
        "file_edit",
    ]

    return {
        "fixture_version": 1,
        "claim_scope": "interface model of pinned public client source",
        "source_properties": {
            "shared_logical_request_builder": True,
            "reuse_ignores_client_metadata": True,
            "responses_lite_tools_are_input_items": True,
            "reconnect_clears_reuse_state": True,
        },
        "cases": cases,
        "earliest_deterministic_wire_divergence": {
            "case": "clean_prewarm_websocket_lite",
            "point": "incremental WebSocket request preparation",
            "observation": (
                "The first real turn carries previous_response_id and omits the already-sent "
                "AdditionalTools prefix. HTTP and fresh/reconnected WebSocket requests transmit "
                "AdditionalTools directly."
            ),
        },
        "negative_findings": [
            "A changed Responses Lite tool manifest rejects incremental reuse and sends the full input.",
            "Non-Lite WebSocket incremental requests repeat top-level tools.",
            "Reconnect and restart controls send full requests without previous_response_id.",
            "Top-level tools_count=0 alone cannot diagnose a missing Responses Lite tool surface.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    result = run(fixture)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
