# L04 — MCP timeout outcome model

State: `complete — durable model retained; clean Codex application unowned`

Programme: `sdk-integration-lifecycle`

Campaign: #133

Parent candidate: #134

Fieldwork issue: #162

Closed Codex evidence carriers: `teamleaderleo/codex#28`, `teamleaderleo/codex#29`

Inspected owned Codex base: `f7265553ea1510304f3091833dcbce65ef21f10c`

Upstream contact authorized: `false`

## In simple words

An MCP timeout says Codex stopped waiting. It leaves the remote outcome open: the request may still be running, may have committed an effect, or may have failed before the server produced a result.

This lane preserves the caller-side facts needed before receipt, compaction, recovery, refresh, fallback, or retry policy consumes the result. The accepted output is this behavior-neutral model and case matrix. There is no active canonical Codex implementation.

## Exact question

What is the smallest internal representation that distinguishes a local `tools/call` deadline, a known pre-dispatch exit, a received remote result, and another unclassified local or transport failure while existing model-visible output remains unchanged?

## Inspected information-loss path

```text
codex-rmcp-client::RmcpClient::call_tool
  -> run_service_operation("tools/call", timeout, ...)
  -> private ClientOperationError::Timeout
  -> anyhow::Error

codex-mcp::PreparedMcpCall::call_with_preparation
  -> local preparation and catalog-generation gates
  -> adds context while retaining typed causes

codex-core::handle_approved_mcp_tool_call
  -> formats failures into existing output
  -> returns McpToolOutput

registry boundary
  -> boxes concrete output as dyn ToolOutput
  -> existing generic result envelope exposes no execution-certainty field
```

There are two loss boundaries:

1. typed preparation, execution, and timeout facts can be flattened into one formatted failure;
2. a fact retained only on concrete `McpToolOutput` disappears when the value crosses the generic `ToolOutput` boundary.

A useful implementation must survive both boundaries without changing direct or Code Mode public output.

## Confirmed evidence

The parent #134 probe established this combination:

```text
caller deadline reached
cancellation observed by server = false
delayed effect completed = true
follow-up request remained usable = true
```

Therefore:

- a local caller deadline is not a remote terminal receipt;
- a persisted failed tool output is not proof of non-execution;
- application-level `isError` is compatible with a request that executed and returned a result;
- cancellation requested, delivered, observed, and remotely settled are separate facts;
- error-string matching is unsuitable for authority or replay decisions.

## Durable internal model

```rust
NotDispatched
RemoteResultReceived
LocalFailureUnclassified
LocalTimeoutOutcomeUnknown
```

### `NotDispatched`

Use this state only when the local owner knows execution did not begin. Accepted cases include invalid local arguments, unavailable or blocked policy, approval exit before execution, a catalog-generation mismatch before `client.call_tool`, and a typed local preparation failure before that call.

The implementation must preserve preparation phase identity below the point where preparation and execution failures become one `anyhow::Error`. Generic preparation failures remain unclassified unless that lower layer proves the request was never dispatched.

### `RemoteResultReceived`

`PreparedMcpCall` returned a remote `CallToolResult`. This proves response receipt. It does not turn application-level `isError` into proof of non-execution, rollback, or replay safety.

### `LocalFailureUnclassified`

Conservative fail-closed state for another local or transport failure whose dispatch and settlement facts are absent. It can include a connection loss after request bytes were written, so policy must treat the remote effect as unknown.

### `LocalTimeoutOutcomeUnknown`

The retained cause chain contains a typed `ClientOperationError::Timeout` for `tools/call`.

It means:

```text
Codex stopped waiting after the local caller deadline.
Remote execution may still be running or may already have committed an effect.
```

A context-wrapped timeout for another operation, such as handshake or `tools/list`, remains `LocalFailureUnclassified`.

## Case matrix

The retained `artifacts/outcome-cases.json` records:

- five known pre-dispatch cases;
- remote success and remote application-error results;
- the typed local `tools/call` deadline;
- a non-`tools/call` timeout negative control;
- connection loss after possible request write;
- generic fail-closed local or transport failure;
- cancellation delivery without a terminal receipt.

Every case keeps automatic retry unauthorized.

## Behavior-neutral first slice

A clean first implementation must preserve:

- model-visible function-call output;
- Code Mode result JSON;
- public `McpToolCallItem` status and error schema;
- app-server and generated SDK schemas;
- retry and compaction behavior;
- session-expiry recovery;
- MCP refresh, rebinding, and fallback behavior.

Any exported Rust workspace type is still an internal API boundary and deserves deliberate review even when no wire schema changes.

## Required handoff regression

```text
typed tools/call timeout
→ MCP handler
→ registry result envelope
→ receipt or lifecycle observer reads outcome unknown
→ direct and Code Mode public output unchanged
```

A classifier that stores the fact only on concrete `McpToolOutput` is incomplete because the generic registry owner cannot consume it.

## Implementation history

Owned Codex PRs #28 and #29 staged the design and useful tests. Both are closed evidence carriers with patch scripts and workflow history. Neither produced an accepted clean source-only, target-tested head.

A future implementation should branch from current owned Codex `main`, apply direct Rust source and tests, and publish one independently reviewed exact head. Carrier workflow history should stay retired.

## Relationship to adjacent work

### #134 — cancellation and transport facts

#134 owns cancellation request, bounded delivery, server observation, connection-generation retirement, reconnect, late result, and transport settlement. Delivery remains evidence, not remote terminal certainty.

### #83 — receipt and compaction policy

#83 may map this typed caller fact into an ambiguous or may-still-run receipt. It must consume the fact through the generic lifecycle boundary and retain its source identity.

### #86 — fallback and replay authority

#86 decides whether a fallback or replay is authorized after identity, capability, authority, and settlement evidence are considered. This lane grants no replay authority.

## Clean application gate

1. Branch from current owned Codex `main`.
2. Apply direct source and tests without carrier scripts or temporary workflows in the canonical diff.
3. Preserve typed preparation phase before failure flattening.
4. Prove catalog mismatch and local preparation failure are `NotDispatched` only when they occur before `client.call_tool`.
5. Prove a context-wrapped `tools/call` timeout becomes `LocalTimeoutOutcomeUnknown`.
6. Prove non-`tools/call` timeout and connection loss after write remain fail-closed and unclassified.
7. Carry the fact across the `ToolOutput` trait-object boundary to the receipt or lifecycle owner.
8. Run one real `RmcpClient -> PreparedMcpCall -> core -> registry observer` timeout control.
9. Prove direct and Code Mode model-visible output remains unchanged.
10. Keep every automatic retry flag false.
11. Review any exported Rust API deliberately.
12. Publish and independently review a source-only exact head.

## Negative results

- No public schema extension is justified by this first model.
- No distinct public `timedOut` status is proposed.
- Cancellation delivery is not a terminal state.
- Typed failure classification alone does not authorize retry.
- `readOnlyHint` or `idempotentHint` from an arbitrary server is not sufficient replay authority.
- No active Codex implementation or upstream interaction exists.

## Evidence boundary

Accepted:

- source-read information-loss map;
- parent timeout probe;
- behavior-neutral four-state model;
- reviewed case matrix and implementation gates.

Pending:

- clean source application;
- compiled owned-Codex tests;
- trait-object-crossing receipt handoff;
- connection-loss-after-write fixture;
- real timeout-through-core execution;
- direct and Code Mode compatibility receipts.

## Disposition

**ACCEPT durable model; EXECUTE before implementation acceptance.**

## Stop condition

Stop when a clean exact Codex head proves that the typed caller outcome survives preparation, core mapping, generic registry ownership, and receipt observation while public output stays compatible and replay remains unauthorized without stronger evidence.
