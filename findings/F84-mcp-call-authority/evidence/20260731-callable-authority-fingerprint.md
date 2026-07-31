# MCP cached-call authority fingerprint

Date: 2026-07-31  
Worker: lane L  
Fieldwork issues: #84, #239, #254  
Public Codex source: `4642370542739d5dd080b0c87a9de06a6435d3db`  
Public upstream interaction: none

## Question

When a model step advertised a cached MCP tool before its server became ready, which live fields must still match before Codex may approve, rewrite, or dispatch the call?

## Current source boundary

The current handler stores the advertised `ToolInfo`, but `handle_mcp_tool_call` passes only server and raw tool name. It refreshes the session runtime and prepares the call from a newly captured live binding. Ordinary calls therefore also leave the step-captured `McpBinding`, even though `StepContext` retains that exact binding and `PreparedMcpCall` retains its exact client and catalogue revision.

Relevant current files:

- `codex-rs/core/src/tools/handlers/mcp.rs`;
- `codex-rs/core/src/mcp_tool_call.rs`;
- `codex-rs/core/src/session/step_context.rs`;
- `codex-rs/codex-mcp/src/binding.rs`;
- `codex-rs/codex-mcp/src/tools.rs`;
- `codex-rs/core/tests/suite/mcp_tool_cache.rs`.

## Governing precedents

### Captured ordinary authority

Merged openai/codex PR #34588 introduced `McpBinding` and `PreparedMcpCall` so calls from one model step keep the exact ready client and catalogue revision captured for that step. This is the default path whenever `step_context.mcp.prepare_call(server, tool)` exists.

### Cached-only startup fallback

Merged openai/codex PR #35590 permits cached tool definitions to reach inference before startup. A cached-only binding has the visible `ToolInfo` but no `PreparedMcpCall`; execution waits for startup and may prepare a live call afterward.

### Deliberate descriptive drift

`regular_mcp_definition_cache_preserves_live_session_state` advertises the first process's dynamic tool and namespace descriptions, then expects the second live process to execute after startup. The schema and operation remain the same while descriptions differ. Descriptions therefore are not part of the fail-closed callable-authority fingerprint.

### Deliberate read-only weakening

Cached definitions clear `annotations.read_only_hint` before advertisement because that cached scheduling claim may be stale. The equivalent live definition may restore `read_only_hint: true`. Exact serialized `ToolInfo` equality would therefore reject a deliberately compatible live call.

## Selected two-path rule

1. **Captured path.** If the step binding has a `PreparedMcpCall`, execute that exact prepared call. Do not refresh and reroute the call to the session's newest client.
2. **Cached-only path.** Only when the step binding has no prepared call may Codex wait for startup and prepare a live call.
3. **Authority gate.** Before approval metadata, permission hooks, file rewriting, memory pollution marking, request metadata, or dispatch, compare the advertised cached authority with the live prepared-call authority.
4. **Mismatch.** Return a model-visible unavailable/stale-authority result and perform none of those irreversible or externally visible preparation steps.

## Proposed fingerprint

The fingerprint should use canonical structured values rather than hashing whole serialized `ToolInfo`.

### Included

| Field | Reason |
| --- | --- |
| raw MCP server name | Routing authority |
| raw MCP tool name | Protocol operation identity |
| canonical callable namespace and name | Identity selected by the model |
| input schema | Defines accepted arguments and mutation surface |
| output schema | Defines the result contract exposed to the model |
| `destructive_hint` | Approval and mutation authority |
| `idempotent_hint` | Retry/certainty semantics |
| `open_world_hint` | Approval and external-effect authority |
| connector ID | App policy, remembered approval, auth elicitation, and account authority |
| optional OpenAI file-input map | Controls argument rewriting and file upload authority |
| execution-relevant tool metadata | `link_id`, connected-account identity, plugin identity where present, app resource/output-template identity, and Codex Apps request metadata used during approval or dispatch |

### Excluded or normalized

| Field | Treatment | Reason |
| --- | --- | --- |
| tool description | exclude | Current cache regression deliberately permits process-specific descriptive drift |
| tool title | exclude from dispatch equality; retain for display | Presentation can change without changing callable operation authority |
| namespace/connector description | exclude | Presentation only in the current cache precedent |
| connector display name | exclude from identity equality; connector ID remains included | Human-facing label may change while connector authority remains stable |
| plugin display names | exclude | Presentation and discovery label, not a stable execution identity |
| server origin | exclude | Telemetry/transport label; exact client ownership is carried separately |
| `supports_parallel_tool_calls` | exclude from call-time equality | Scheduling occurred before dispatch and cached startup deliberately weakens parallel assumptions |
| `read_only_hint` | normalize away for cached fallback | Cached advertisement intentionally clears it; destructive/open-world/idempotent fields remain authoritative |

## Rejected alternatives

### Whole serialized `ToolInfo` equality

Rejected as the final policy. It is conservative but incompatible with the repository's deliberate description drift and read-only weakening. It remains useful as a negative experiment only.

### Schema-only equality

Rejected. It would permit connector, destructive/open-world, file-rewrite, account, and app metadata drift before approval and dispatch.

### Always use the newest live binding

Rejected. It defeats the captured-client invariant for ordinary calls and lets a same-name replacement silently inherit a model step's earlier authority.

### Never permit cached execution

Rejected. It removes the startup-latency behavior intentionally added by #35590 instead of preserving it with a bounded authority gate.

## Discriminating controls required

1. A non-cached ordinary call keeps the original `PreparedMcpCall` client after runtime replacement.
2. A cached-only advertisement with different description and restored read-only hint, but the same fingerprint, executes the live client.
3. Cached-only input-schema drift fails before approval, hook execution, file rewriting, and server dispatch.
4. Cached-only connector/destructive/open-world/file-parameter drift fails before those same boundaries.
5. A same-name replacement cannot inherit remembered approval from a different connector identity.
6. Ordinary unchanged runtime refresh retains ready-client reuse.
7. Explicit reload publishes one replacement and stale captured authority fails closed according to its own catalogue revision.

## Evidence classes and limits

- `source-read`: current handler, binding, metadata, approval, file rewrite, cache, and test-server paths.
- `historical-precedent`: merged public PRs #34588 and #35590.
- `target-executed`: publication 5/5 and reconnect 3/3 are separate lifecycle receipts; they do not execute this authority fingerprint.
- `unknown`: no current-head source candidate has yet passed the six authority-specific behavior controls above.

## Next transition

Create one current-source authority carrier over `4642370542739d5dd080b0c87a9de06a6435d3db` that implements captured-first selection plus the structured cached-only fingerprint. The carrier must publish no source branch until exact ordinary-capture, equivalent-cache, schema-drift, and pre-side-effect negative controls pass. A later integration control should use the existing `mcp_tool_cache` process fixture so descriptive drift remains demonstrably compatible.
