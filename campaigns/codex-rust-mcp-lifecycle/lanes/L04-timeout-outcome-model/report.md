# L04 — MCP timeout outcome model

State: `ready — durable model retained; clean Codex application unowned`

Programme: `sdk-integration-lifecycle`

Campaign: #133

Parent candidate: #134

Fieldwork issue: #162

Closed Codex evidence carriers: `teamleaderleo/codex#28`, `teamleaderleo/codex#29`

Inspected owned Codex base: `f7265553ea1510304f3091833dcbce65ef21f10c`

Public upstream contact authorized: `false`

## In simple words

An MCP timeout says Codex stopped waiting. It does not prove that the request stopped, cancellation reached the server, or a remote mutation did not commit.

This lane preserves the internal execution-certainty model needed before retry, compaction, refresh, recovery, or fallback policy consumes such a result. The durable result is this report and its case matrix. There is no active owned Codex implementation.

## Exact question

What is the smallest internal representation that lets Codex distinguish a local `tools/call` deadline from a settled remote result without changing the public tool-call schema or model-visible output?

## Source path

The inspected owned Codex source establishes this information-loss path:

```text
codex-rmcp-client::RmcpClient::call_tool
  -> run_service_operation("tools/call", timeout, ...)
  -> private ClientOperationError::Timeout
  -> anyhow::Error

codex-mcp::PreparedMcpCall::call_with_preparation
  -> adds tool/server context while retaining the cause chain

codex-core::handle_approved_mcp_tool_call
  -> converts the error to a string
  -> emits a failed McpToolCallItem
  -> converts it into CallToolResult

codex-core::McpHandler
  -> returns Ok(McpToolOutput)
  -> registry lifecycle can observe a normal returned output
```

The typed cause is lost before core retains execution certainty. Public MCP items then expose only their existing status and error message.

## Confirmed evidence

The parent #134 legacy probe records:

```text
caller deadline reached
cancellation observed by server = false
delayed effect completed = true
follow-up request remained usable = true
```

Therefore:

- a local timeout is not a remote terminal receipt;
- a persisted failed tool output is not proof of non-execution;
- a returned failed `CallToolResult` can still look lifecycle-completed;
- display-string matching is not a safe authority boundary.

## Durable internal model

```rust
NotDispatched
RemoteResultReceived
LocalFailureUnclassified
LocalTimeoutOutcomeUnknown
```

### `NotDispatched`

Core knows the remote call did not start, such as invalid local arguments, an unavailable prepared binding, disabled policy, or approval exit before execution.

### `RemoteResultReceived`

`PreparedMcpCall` returned a remote `CallToolResult`. This records response receipt and does not reinterpret the tool's application-level `isError` field.

### `LocalFailureUnclassified`

Conservative state for another local or transport failure whose dispatch and settlement facts are not yet typed.

### `LocalTimeoutOutcomeUnknown`

The retained `anyhow` cause chain contains `ClientOperationError::Timeout { label: "tools/call" }`.

It means:

```text
Codex stopped waiting after the local caller deadline.
Remote execution may still be running or may already have committed an effect.
```

## Why classification belongs below string conversion

`PreparedMcpCall` adds `anyhow::Context`, while the original typed timeout remains in the cause chain. A clean implementation should classify that cause before `handle_approved_mcp_tool_call` formats the error for existing output.

This avoids:

- parsing localized or reformatted messages;
- coupling receipt safety to telemetry text;
- treating every failure containing “timeout” as a dispatched MCP tool deadline;
- confusing handshake or `tools/list` timeouts with `tools/call`.

## Behavior-neutral first slice

A clean first implementation must not change:

- model-visible function-call output;
- Code Mode result JSON;
- public `McpToolCallItem` status or error schema;
- app-server or generated SDK schemas;
- retry or compaction behavior;
- session-expiry recovery;
- MCP refresh, rebinding, or fallback behavior.

It should require identical model-visible direct and Code Mode output for an ordinary local failure and a timeout marked outcome-unknown.

## Implementation history

Codex PRs #28 and #29 staged this design and useful focused tests. Both are closed evidence carriers. Neither produced an accepted source-only, target-tested head, and neither is an active canonical implementation.

Do not reopen or promote those carrier histories. A future application should branch cleanly from current owned Codex `main`, apply direct Rust source and tests, and publish a source-only exact head.

## Relationship to adjacent work

### #134 — cancellation mechanics

#134 owns cancellation request, bounded delivery, server observation, and transport settlement. Cancellation delivery remains a fact, not proof that a mutation did not commit.

### #83 — mutation identity and compaction

#83 may later map `LocalTimeoutOutcomeUnknown` to an ambiguous or may-still-run receipt. It must consume typed execution evidence, not error strings.

### Generic terminal semantics

The closed generic receipt experiment from Codex PR #25 remains useful evidence for pre-execution failure versus handler-executed uncertainty. It cannot identify an MCP timeout returned as an ordinary failed output.

## Retry and authority rules

This lane authorizes no retry.

Future policy must:

1. preserve original call and authority identity;
2. not trust arbitrary-server `readOnlyHint` or `idempotentHint` as proof;
3. require host policy, durable idempotency, or reconciliation before replaying a potential mutation;
4. treat cancellation requested, delivered, observed, and settled as separate facts;
5. require a new sampled step after runtime or authority changes.

## Negative results

- No public schema extension is justified by this first slice.
- No distinct public `timedOut` status is proposed.
- No cancellation-delivered terminal state is claimed before #134 completes its transport matrix.
- No automatic retry is safe merely because the local failure is typed.
- No upstream interaction occurred.

## Clean application gate

1. Branch from current owned Codex `main`.
2. Apply direct source and tests without temporary carrier history in the final diff.
3. Prove typed `tools/call` deadline classification survives outer `anyhow::Context`.
4. Prove other operation timeouts and generic failures remain unclassified.
5. Add one real `RmcpClient -> PreparedMcpCall -> core output` timeout control.
6. Prove direct and Code Mode model-visible output remains unchanged.
7. State that any exported Rust workspace type is an internal API boundary even without a wire-schema change.
8. Publish and independently review a source-only exact head.

## Next bounded steps

1. Complete #134 cancellation and transport evidence.
2. Apply this behavior-neutral internal type cleanly on current owned Codex `main`.
3. Map typed execution evidence into #83 receipt terminal certainty.
4. Only then evaluate whether public consumers need structured error detail or another status.

## Stop condition

Stop when compiled owned-fork tests prove that local MCP tool-call deadlines remain outcome-unknown internally while existing public and model output stays compatible, and receipt logic can consume that state without string parsing or unsafe replay.
