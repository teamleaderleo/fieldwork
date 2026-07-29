#!/usr/bin/env python3
"""Patch public Codex tests to reproduce cached-A/live-B schema drift.

The patch is applied only in an ephemeral CI checkout. It does not write to the
public Codex repository.
"""

from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one exact match, found {count}")
    return text.replace(old, new, 1)


def patch_server(root: Path) -> None:
    path = root / "codex-rs/rmcp-client/src/bin/test_stdio_server.rs"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''const APP_ONLY_CWD_MARKER_FILE_ENV: &str = "MCP_TEST_APP_ONLY_CWD_MARKER_FILE";
const DYNAMIC_SERVER_METADATA_ENV: &str = "MCP_TEST_DYNAMIC_SERVER_METADATA";
const INITIALIZE_BARRIER_FILE_ENV: &str = "MCP_TEST_INITIALIZE_BARRIER_FILE";
''',
        '''const APP_ONLY_CWD_MARKER_FILE_ENV: &str = "MCP_TEST_APP_ONLY_CWD_MARKER_FILE";
const DYNAMIC_SERVER_METADATA_ENV: &str = "MCP_TEST_DYNAMIC_SERVER_METADATA";
const ECHO_SCHEMA_V2_MARKER_FILE_ENV: &str = "MCP_TEST_ECHO_SCHEMA_V2_MARKER_FILE";
const INITIALIZE_BARRIER_FILE_ENV: &str = "MCP_TEST_INITIALIZE_BARRIER_FILE";
''',
        "server constants",
    )

    text = replace_once(
        text,
        '''fn dynamic_server_process_label() -> Option<String> {
    std::env::var_os(DYNAMIC_SERVER_METADATA_ENV)
        .is_some()
        .then(|| format!("rmcp-test-process-{}", std::process::id()))
}
''',
        '''fn dynamic_server_process_label() -> Option<String> {
    std::env::var_os(DYNAMIC_SERVER_METADATA_ENV)
        .is_some()
        .then(|| format!("rmcp-test-process-{}", std::process::id()))
}

fn echo_schema_v2() -> bool {
    std::env::var_os(ECHO_SCHEMA_V2_MARKER_FILE_ENV)
        .is_some_and(|path| std::path::Path::new(&path).exists())
}
''',
        "schema marker helper",
    )

    text = replace_once(
        text,
        '''        #[expect(clippy::expect_used)]
        let schema: JsonObject = serde_json::from_value(json!({
            "type": "object",
            "properties": {
                "message": { "type": "string" },
                "env_var": { "type": "string" }
            },
            "required": ["message"],
            "additionalProperties": false
        }))
        .expect("echo tool schema should deserialize");
''',
        '''        let schema_value = if echo_schema_v2() {
            json!({
                "type": "object",
                "properties": {
                    "count": { "type": "integer" }
                },
                "required": ["count"],
                "additionalProperties": false
            })
        } else {
            json!({
                "type": "object",
                "properties": {
                    "message": { "type": "string" },
                    "env_var": { "type": "string" }
                },
                "required": ["message"],
                "additionalProperties": false
            })
        };
        #[expect(clippy::expect_used)]
        let schema: JsonObject = serde_json::from_value(schema_value)
            .expect("echo tool schema should deserialize");
''',
        "echo schema",
    )

    text = replace_once(
        text,
        '''            "echo" | "echo-tool" => {
                let args: EchoArgs = match request.arguments {
''',
        '''            "echo" | "echo-tool" => {
                if echo_schema_v2() {
                    let count = request
                        .arguments
                        .as_ref()
                        .and_then(|arguments| arguments.get("count"))
                        .and_then(serde_json::Value::as_i64)
                        .ok_or_else(|| {
                            McpError::invalid_params(
                                "echo schema v2 requires integer count".to_string(),
                                None,
                            )
                        })?;
                    let process = dynamic_server_process_label()
                        .unwrap_or_else(|| "echo-schema-v2".to_string());
                    return Ok(Self::structured_result(json!({
                        "echo": format!("{process}-count-{count}"),
                        "env": null,
                    })));
                }

                let args: EchoArgs = match request.arguments {
''',
        "echo call handler",
    )

    path.write_text(text, encoding="utf-8")


def patch_test(root: Path) -> None:
    path = root / "codex-rs/core/tests/suite/mcp_tool_cache.rs"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''            let app_only_cwd_marker_file = config.cwd.join("cwd-app-only");
            let barrier_file = config.cwd.join("allow-initialize");
            let pid_file = config.cwd.join("mcp.pid");
''',
        '''            let app_only_cwd_marker_file = config.cwd.join("cwd-app-only");
            let barrier_file = config.cwd.join("allow-initialize");
            let echo_schema_v2_marker_file = config.cwd.join("echo-schema-v2");
            let pid_file = config.cwd.join("mcp.pid");
''',
        "test marker path",
    )

    text = replace_once(
        text,
        '''                        "MCP_TEST_DYNAMIC_SERVER_METADATA": "1",
                        "MCP_TEST_PID_FILE": pid_file,
''',
        '''                        "MCP_TEST_DYNAMIC_SERVER_METADATA": "1",
                        "MCP_TEST_ECHO_SCHEMA_V2_MARKER_FILE": echo_schema_v2_marker_file,
                        "MCP_TEST_PID_FILE": pid_file,
''',
        "test marker environment",
    )

    text = replace_once(
        text,
        '''    let barrier_file = PathUri::from_host_native_path(fixture.config.cwd.join("allow-initialize"))?;
    let pid_file = PathUri::from_host_native_path(fixture.config.cwd.join("mcp.pid"))?;
''',
        '''    let barrier_file = PathUri::from_host_native_path(fixture.config.cwd.join("allow-initialize"))?;
    let echo_schema_v2_marker_file =
        PathUri::from_host_native_path(fixture.config.cwd.join("echo-schema-v2"))?;
    let pid_file = PathUri::from_host_native_path(fixture.config.cwd.join("mcp.pid"))?;
''',
        "test marker URI",
    )

    text = replace_once(
        text,
        '''    fs.write_file(
        &app_only_cwd_marker_file,
        b"app-only".to_vec(),
        /*sandbox*/ None,
    )
    .await?;
    let NewThread {
''',
        '''    fs.write_file(
        &app_only_cwd_marker_file,
        b"app-only".to_vec(),
        /*sandbox*/ None,
    )
    .await?;
    fs.write_file(
        &echo_schema_v2_marker_file,
        b"count-schema".to_vec(),
        /*sandbox*/ None,
    )
    .await?;
    let NewThread {
''',
        "enable second schema",
    )

    text = replace_once(
        text,
        '''        let called_process = end
            .result
            .expect("echo call should succeed")
            .structured_content
            .and_then(|content| content.get("echo").cloned())
            .and_then(|echo| echo.as_str().map(ToString::to_string))
            .expect("echo result should identify its live server process");
''',
        '''        let schema_error = end
            .result
            .expect_err("A-shaped echo arguments should fail against B's count schema")
            .to_string();
''',
        "capture schema mismatch",
    )

    text = replace_once(
        text,
        '''        anyhow::Ok(called_process)
''',
        '''        anyhow::Ok(schema_error)
''',
        "return schema mismatch",
    )

    text = replace_once(
        text,
        '''    assert_definition(
        &cached_response,
        &format!("Tools in the {NAMESPACE} namespace."),
        &format!("Echo from {first_process}."),
    );
''',
        '''    assert_definition(
        &cached_response,
        &format!("Tools in the {NAMESPACE} namespace."),
        &format!("Echo from {first_process}."),
    );
    let cached_body = cached_response.single_request().body_json();
    let cached_echo = responses::namespace_child_tool(&cached_body, NAMESPACE, "echo")
        .expect("cached request should advertise echo");
    assert_eq!(cached_echo["parameters"]["required"], json!(["message"]));
    assert!(cached_echo["parameters"]["properties"].get("count").is_none());
''',
        "assert advertised A schema",
    )

    text = replace_once(
        text,
        '''    assert_eq!(cached_turn.await??, second_process);
''',
        '''    let schema_error = cached_turn.await??;
    assert!(
        schema_error.contains("echo schema v2 requires integer count"),
        "live B should reject the A-shaped arguments: {schema_error}"
    );
''',
        "assert live B rejection",
    )

    text = replace_once(
        text,
        '''    let output = cached_done_response
        .single_request()
        .function_call_output_text("cached-call")
        .expect("successful tool output should be returned to the model");
    assert!(
        output.contains(&second_process),
        "model-visible tool output should come from the live server: {output}"
    );
''',
        '''    let output = cached_done_response
        .single_request()
        .function_call_output_text("cached-call")
        .expect("schema mismatch should be returned to the model");
    assert!(
        output.contains("echo schema v2 requires integer count"),
        "model-visible output should report the live B schema rejection: {output}"
    );
''',
        "assert model-visible mismatch",
    )

    path.write_text(text, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch.py /path/to/codex")
    root = Path(sys.argv[1]).resolve()
    patch_server(root)
    patch_test(root)


if __name__ == "__main__":
    main()
