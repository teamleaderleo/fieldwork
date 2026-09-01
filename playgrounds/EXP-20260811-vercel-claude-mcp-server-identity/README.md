# Vercel AI SDK Claude MCP server-name identity

## State

`COMPLETE — source-read + model-executed + target-test-prepared`

Owner: `chatgpt:gpt-5.6-sol`  
Created: `2026-08-11`  
Claim scope: interface  
Target: `target:vercel-ai`  
Target hub: #2  
Programme: #13  
Owned target carrier: `teamleaderleo/ai#72`  
Public upstream contact authorized: `no`

## In simple words

The new per-harness MCP API lets Claude callers configure external MCP servers by arbitrary server name.

Claude Code already uses an internal MCP server named `harness-tools` to carry host-defined AI SDK tools. That internal name is also baked into the stream translator: every native tool name beginning `mcp__harness-tools__` is assumed to belong to Vercel's internal host-tool transport and its native call/result events are suppressed.

The public MCP API does not reserve or reject the caller server name `harness-tools`.

That creates two deterministic behaviors from the same collision:

1. **No host AI SDK tools configured:** the caller's external `harness-tools` server remains configured and can execute, but its calls are mistaken for Vercel's internal transport and disappear from the normal dynamic tool stream.
2. **Host AI SDK tools configured:** Vercel creates its internal MCP server and assigns it to `mcpServers['harness-tools']`, replacing the caller's external server under the same key.

An ordinary external name such as `context7` does not have either problem.

Current answer: `harness-tools` is an undocumented reserved identity exposed through a public caller-controlled namespace.

## Exact subject

Public repository: https://github.com/vercel/ai  
Current public main at investigation: `cbdbeee90d9aa4fee399b5628073f9fc30165ca6`  
Feature commit: `a03ff6c8682501c151306b93f36ec4b654ae779a`  
Retrieval date: `2026-08-11`

Primary paths:

- `packages/harness-claude-code/src/bridge/index.ts`;
- `packages/harness-claude-code/src/bridge/create-emit-stream-event.ts`;
- `packages/harness-claude-code/src/bridge/create-emit-stream-event.test.ts`;
- `content/providers/02-ai-sdk-harnesses/01-claude-code.mdx`;
- `content/docs/03-ai-sdk-harnesses/03-tools.mdx`.

Owned carrier: `teamleaderleo/ai#72`, exact base `cbdbeee90d9aa4fee399b5628073f9fc30165ca6`.

## Source map

### Public configuration namespace

`createClaudeCode({ mcpServers })` accepts MCP server definitions keyed by server name. The reviewed docs do not name `harness-tools` as reserved.

The bridge starts each turn with:

```text
mcpServers = copy(caller mcpServers)
```

### Internal host-tool server

When host AI SDK tools are present, the bridge creates an in-process MCP server named `harness-tools` and then performs:

```text
mcpServers['harness-tools'] = internalServer
```

There is no collision check. A caller server under that key is replaced.

### Stream identity

The stream translator recognizes internal host-tool traffic solely through the native-name prefix:

```text
mcp__harness-tools__<tool>
```

Those ids are put in the internal `mcpToolUseIds` set. Their native `tool-call` and later `tool-result` events are suppressed because the internal host-tool MCP handler already emits a typed call/result pair with a separate synthetic id.

External MCP tools with other server names are marked `dynamic: true`, `providerExecuted: true` and emitted normally.

The translator has no information saying whether a particular `mcp__harness-tools__*` call came from the internal server or from a caller-owned external server using the same name.

## Competing explanations

### H1 — `harness-tools` is a documented reserved name

**Weakened.** The public adapter docs describe `mcpServers` as definitions keyed by server name and do not identify a reserved key in the reviewed material.

### H2 — external `harness-tools` is rejected before reaching the bridge

**Rejected by source.** Caller server records are copied without a reserved-name check.

### H3 — an external collision is harmless because internal host tools always exist

**Rejected.** The internal server is only created when host AI SDK tools are present. With no host tools, the caller external server survives but the translator still suppresses its native events by prefix.

### H4 — the problem affects every external MCP server

**Rejected by negative control.** Ordinary names such as `context7` are explicitly covered by the new translator tests and emit dynamic calls/results.

## Executable discriminator

Run:

```sh
python3 playgrounds/EXP-20260811-vercel-claude-mcp-server-identity/run.py
```

Observed:

```json
{
  "external_harness_tools_event_visible_as_dynamic": false,
  "external_harness_tools_server_preserved_when_host_tools_exist": false,
  "external_harness_tools_server_survives_when_no_host_tools": true,
  "merged_harness_tools_kind_with_host_tools": "internal-host-tools",
  "negative_control_context7_remains_external": true
}
```

Evidence class: `model-executed`.

## Target-native discriminator

Owned PR `teamleaderleo/ai#72` adds one focused translator test at exact current-main base.

It emits an MCP tool-use/result named `mcp__harness-tools__external-query` and requires the pair to appear as ordinary external dynamic provider-executed events.

Current code is expected to suppress both because the prefix is assumed internal.

That carrier proves the stream-classification manifestation. The configuration replacement manifestation is directly established by the current bridge merge assignment.

Evidence remains `target-test-prepared` until owned CI executes.

## Change thesis

Current behavior:

```text
public caller namespace contains key "harness-tools"
        ↓
internal implementation also owns "harness-tools"
        ↓
no host tools: caller server runs, stream identity suppressed
host tools:    caller server replaced by internal server
```

Consequence: adding host-defined tools or merely selecting one otherwise-valid MCP server name can change external MCP availability and stream observability without an explicit configuration error.

The repair needs one identity policy, not two local patches. Candidate directions:

1. reject/reserve the caller server name `harness-tools` at adapter configuration/start with a clear message; or
2. move the internal host-tool server to an identity outside the caller namespace and make stream suppression depend on explicit internal provenance rather than a public name prefix.

The second direction is cleaner long-term but wider. The first is smaller and makes the current hidden constraint explicit.

## Candidate tests

1. ordinary external MCP server names remain dynamic and visible;
2. caller `harness-tools` receives an explicit deterministic outcome;
3. the outcome is identical whether host AI SDK tools are present or absent;
4. host-defined AI SDK tools retain typed non-dynamic events;
5. external MCP tool calls retain dynamic provider-executed events;
6. no caller server is silently replaced;
7. no external MCP stream is suppressed solely by caller-chosen server name;
8. docs/types expose any reserved-name rule if reservation is selected;
9. current package tests/build/type-check remain green.

## Negative results and boundaries

- No claim is made that the collision lets an external MCP server impersonate a host tool in the host execution path; the reviewed manifestations are replacement and stream identity loss.
- The new external MCP permission semantics are ambiguous and are not folded into this finding.
- No matching open upstream issue or pull request surfaced under direct collision searches during the investigation.
- Third-party upstream remained read-only.

## Recommendation

Promote to a bounded campaign. The next decision is explicit:

> Is `harness-tools` a reserved public configuration name, or should internal host-tool identity move outside the caller MCP namespace?

Pick one policy and test both collision manifestations against it.
