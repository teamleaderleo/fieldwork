# Captured MCP Call Candidate

Date: 2026-07-30  
Campaign: #84  
Public Codex recheck: `a5082373f18119dc5d3eb993267c97f37880935d`

## Source observation

`ToolInvocation` already carries:

```rust
pub session: Arc<Session>,
pub turn: Arc<TurnContext>,
pub(crate) step_context: Arc<StepContext>,
```

`StepContext` owns the request's exact `McpBinding` and `ToolRouter`.

The current MCP handler uses the handler's A-side `ToolInfo` for model and hook metadata, then calls `handle_mcp_tool_call`, which refreshes thread MCP state and resolves a prepared call from the current runtime B.

The captured binding is therefore available at the call site and does not require a new cross-thread lookup or persistence field.

## Smallest routing change

At MCP handler entry:

```rust
let captured_call = invocation
    .step_context
    .mcp
    .prepare_call(&self.tool.server_name, &self.tool.tool.name);
```

Pass `captured_call` into the call executor.

Call selection:

```text
captured_call is Some
→ execute the captured prepared call
→ do not wait for or route to a replacement client

captured_call is None
→ this may be a cached-startup advertisement
→ wait for the selected server
→ obtain live B
→ require advertised-A/live-B authority-fingerprint equality
→ execute B only when equality is verified
```

Unknown absence should fail closed. A missing captured call must not automatically imply that any current same-name tool is compatible.

## Why this preserves current useful behavior

### Ready request binding

A ready server already inserts prepared calls into the request binding. Those calls regain the rule from the [captured catalogue authority change](https://redirect.github.com/openai/codex/pull/34588).

### Cached optional server

A cached optional server can advertise tools before a client is ready and therefore has no captured prepared call. The live wait from the [cached-startup late-binding change](https://redirect.github.com/openai/codex/pull/35590) remains available as an explicit compatibility exception.

### Removed tool

If B lacks the advertised tool, retain the current typed unavailable outcome.

### Equal replacement

Different server process B may execute when its accepted authority fingerprint equals A. Record both identities and the verified late-rebind result.

## Current-policy tightening

Captured execution alone is insufficient when current policy tightened after sampling.

The call should evaluate two authorities:

- A: approval and permission state captured with the request;
- B: current approval and permission state at dispatch.

Effective decision:

```text
allow only when A and B both allow
prompt when A or B requires prompting
deny when A or B denies
apply the tighter sandbox/permission restrictions
```

B may tighten an in-flight call. B may not relax A.

This can be implemented as dual evaluation rather than inventing a total ordering across approval modes and permission profiles.

## Authority fingerprint for cached late binding

Minimum fields:

- configured connection identity;
- observed remote server identity;
- canonical server and tool name;
- input schema;
- output schema when part of the callable contract;
- visibility metadata;
- approval/safety/scheduling annotations;
- file-input declaration and rewrite metadata;
- plugin and connector provenance affecting approval or hooks;
- server origin and environment identity used by permission decisions;
- server and per-tool approval modes.

Description drift can be reported separately if excluded from the authority fingerprint. It still belongs in the receipt because the model planned from A's description.

## Suggested function boundary

Avoid passing only server/tool strings into the executor.

Candidate input:

```rust
struct McpCallAuthority {
    advertised_tool: ToolInfo,
    captured_call: Option<PreparedMcpCall>,
    captured_config_digest: Digest,
    advertised_catalogue_digest: Digest,
}
```

The call executor then chooses captured execution or verified late binding and returns a receipt containing the decision.

An incremental first patch can pass `Option<PreparedMcpCall>` plus `ToolInfo` without introducing the final receipt type, provided the tests prove the routing boundary.

## Required first tests

1. Ready captured call A; runtime replaced with same-name B; execution uses A.
2. Captured client A closes; B exists; call fails on A without rerouting.
3. A requires prompt; B becomes permissive; call still prompts.
4. A is permissive; B requires prompt; B tightens the call.
5. Cached A has no prepared call; equal B executes with verified late rebind.
6. Cached A schema differs from B; fail closed before B call.

## Relationship to generation work

This routing change and generation-bound publication are complementary.

- Generation tickets decide which runtime/catalogue may publish for future requests.
- Captured-call authority decides what governs work already emitted by an older request.

Fixing only publication still allows an in-flight A response to route through B. Fixing only captured calls still allows stale or out-of-order catalogues to publish for new requests.

## Current decision

Use captured prepared calls by default. Keep live late binding only for cached tools that lacked a captured call, and gate it on verified equality. Apply current policy as an added restriction, never as an in-flight relaxation.

This is a design handoff only. Public Codex remains read-only.
