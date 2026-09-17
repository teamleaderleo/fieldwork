#!/usr/bin/env python3

"""Model Claude harness MCP server-name identity at cbdbeee9."""

import json


def merge_servers(external, host_tools_present):
    merged = dict(external)
    if host_tools_present:
        merged["harness-tools"] = {"kind": "internal-host-tools"}
    return merged


def stream_classification(native_tool_name):
    if native_tool_name.startswith("mcp__harness-tools__"):
        return {"kind": "internal-host-tool", "emit_dynamic": False}
    if native_tool_name.startswith("mcp__"):
        return {"kind": "external-mcp", "emit_dynamic": True}
    return {"kind": "native", "emit_dynamic": False}


def main():
    external = {
        "harness-tools": {"kind": "external-caller-server"},
        "context7": {"kind": "external-caller-server"},
    }
    no_host_tools = merge_servers(external, False)
    with_host_tools = merge_servers(external, True)

    result = {
        "negative_control_context7_remains_external": (
            stream_classification("mcp__context7__query")["emit_dynamic"] is True
        ),
        "external_harness_tools_server_survives_when_no_host_tools": (
            no_host_tools["harness-tools"]["kind"] == "external-caller-server"
        ),
        "external_harness_tools_event_visible_as_dynamic": (
            stream_classification("mcp__harness-tools__external-query")["emit_dynamic"]
            is True
        ),
        "external_harness_tools_server_preserved_when_host_tools_exist": (
            with_host_tools["harness-tools"]["kind"] == "external-caller-server"
        ),
        "merged_harness_tools_kind_with_host_tools": with_host_tools["harness-tools"]["kind"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
