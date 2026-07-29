# Captured MCP call authority follow-up

Review date: 2026-07-30  
Current public source: `openai/codex@85c082ccccf6b5ac4d6c31d14f960057348b78f4`  
Related implementation campaign: #84  
Public upstream contact authorized: `false`

## Exact question

After one model sampling request captures MCP catalogue A, which connection, schema, metadata, approval policy, permission profile, and tool revision govern a tool call emitted by that response if thread MCP state changes to B before dispatch?

## Stated contracts

The relevant source comments and change descriptions state a strong request boundary:

- `StepContext.mcp` is the exact MCP connections and catalogue for one step;
- `StepContext.tool_router` is the plan advertised and executed for that sampling request;
- PR #34588 says a call from one model step must not reroute to a replacement client or run against a catalogue revision the model did not see;
- `McpConfig` says each prepared call owns immutable connection, approval, and sandbox authority.

## Current execution path

The current path has two revisions:

### A — request-captured planning state

`McpHandler` is created from the request's `ToolInfo` and retains:

- the model-facing tool schema and description;
- tool-search metadata;
- MCP namespace and hook name;
- file-input declarations visible to the model;
- tool scheduling metadata exposed through the request router.

### B — call-time live state

Before handler execution, the tool runtime refreshes dirty MCP state and waits for the selected server. `handle_mcp_tool_call` then calls `current_binding_for_call`, captures the latest binding, and obtains a new `PreparedMcpCall`.

B supplies:

- the live client and connection set;
- current server metadata and origin;
- current tool annotations and connector metadata;
- current approval policy, permission profile, reviewer, and config layers;
- current file-input rewrite metadata;
- execution and result behavior.

The call therefore can be planned and hooked as A while approved and executed as B.

## Change history

### PR #34588 — captured catalogue authority

`Bind MCP calls to captured catalog revisions` introduced request-scoped bindings because calls must not reroute to replacement clients or unseen catalogues.

Before runtime centralization, the core handler consistently used the step-owned `McpRuntimeSnapshot` for metadata, approval lookup, argument preparation, and `tools/call`.

### PR #34930 — current runtime lookup

`Centralize thread MCP state in McpRuntime` moved approval and execution to the thread's latest binding. The same change added a test proving that a newly refreshed binding captures current approval settings. That is correct for a newly captured step, but the test does not exercise a call emitted by an older already-sampled step.

### PR #35590 — explicit cached-startup rebind

`Expose cached MCP tools before server startup` intentionally advertises cached catalogue A, waits for startup, and prepares the call against live B.

Its integration test proves:

- inference sees process A's cached tool description;
- the same tool name executes on process B;
- a tool absent from B fails closed.

It does not test same-name schema, approval, annotation, visibility, hook, file-input, or semantic changes.

### PRs #35937 and #36011 — wider startup reuse

Later changes moved the selected-server wait before the parallel execution gate and shared the optional startup deadline across connection sets. They preserve the A-to-B rebind while making cached advertisement available earlier and across more connection sets.

## Approval-relaxation case

The current approval helper auto-approves an MCP prompt when:

- the current approval policy is `Never`; and
- the current permission profile is disabled, external, or otherwise has full disk write authority.

Source-derived race:

```text
step captures A with prompt-required approval
→ model sampling begins with A
→ thread settings change to B: approval Never + disabled permission profile
→ MCP runtime is marked dirty
→ model emits an MCP call from the A response
→ call path refreshes and captures B
→ B auto-approves and executes
```

A config relaxation can therefore take effect inside a request that was sampled under stricter authority. A tightening can also replace A, but tightening is conservative; relaxation is the critical direction.

## Candidate authority contract

### 1. Captured-first execution

When `step_context.mcp.prepare_call(server, tool)` exists, execute that exact prepared call. A runtime refresh must not replace its client, schema, metadata, or approval authority.

The binding already retains the old connection set and client lifetime. If the captured client closes, fail on that client rather than rerouting.

### 2. Current policy as an additional restriction

A newer policy may tighten an in-flight call but must not relax it.

A simple safe rule is dual authorization:

```text
call is allowed only when captured authority A and current authority B both allow it
```

Operationally:

- prompt when either A or B requires a prompt;
- deny or fail closed when either authority disallows the call;
- apply current sandbox or permission restrictions when they are tighter;
- defer a relaxation until the next sampling step.

This avoids requiring a fragile total ordering across all approval and permission-profile variants.

### 3. Bounded cached-startup exception

A cached tool has no captured prepared call. After startup, live B may be used only when an authority fingerprint proves compatibility with advertised A.

The fingerprint should cover at least:

- server identity or accepted connection identity;
- canonical tool name;
- input and output schemas;
- visibility and relevant tool metadata;
- annotations used for approval and scheduling;
- file-input declarations and rewrite metadata;
- plugin/connector provenance that affects approval or hooks;
- configured approval mode and server-level execution metadata.

Descriptions may be classified separately if they are considered non-authoritative, but the receipt should still report description drift.

Outcome:

```text
fingerprint A == fingerprint B → execute B and record verified late rebind
fingerprint A != fingerprint B → fail closed and require a new sampling step
```

### 4. Revision receipt

Every MCP call receipt should include bounded values for:

- sampling-step catalogue revision/digest;
- captured prepared-call revision when present;
- live binding revision/digest at dispatch;
- late-rebind reason;
- equality result and differing field classes;
- captured and current approval-policy digests;
- effective dual-authorization result;
- execution client/server identity.

## Compiled test matrix

### Ready captured call

1. Capture A with a ready client and tool `write`.
2. Replace runtime with B before dispatch.
3. Assert the call still uses A's client, schema, metadata, and authority.
4. Close A's client and assert fail closed without routing to B.

### Approval relaxation

1. A requires prompting.
2. While sampling is pending, update B to `Never` with disabled permissions.
3. Emit the A tool call.
4. Assert the call still prompts or fails; it must not silently auto-approve under B.

Reverse the policies and verify B may tighten the call.

### Cached same-name schema change

1. Cache A with `tool(x: string)`.
2. Start B behind the same configured identity with `tool(count: integer)` and hold initialization.
3. Let inference receive A and emit `{x: "value"}`.
4. Release B.
5. Assert typed revision mismatch before B execution.

### Cached same-name authority change

Repeat with unchanged schema but changed:

- destructive/open-world annotations;
- visibility;
- approval mode;
- file-input metadata;
- plugin or connector provenance.

Assert fail closed unless the accepted authority fingerprint is equal.

### Verified equal late rebind

Use different server processes with equal authority fingerprints. Assert the call may execute on B and the receipt records both server identities and verified equality.

## Decision

The existing generic late-binding optimization should remain available only as a verified compatibility exception. It should not replace the default captured-call rule.

The smallest candidate change is:

1. use the step's prepared call when present;
2. wait for live B only when the step advertised a cached tool without a prepared call;
3. compare an A/B authority fingerprint before executing B;
4. apply current policy only as an additional restriction, never as an in-flight relaxation.

Public Codex remained read-only. No upstream issue, comment, reaction, pull request, or code write occurred.