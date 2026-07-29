# Codex Rust MCP tool-timeout cancellation

Status: active implementation lane

Fieldwork issue: #134
Campaign: #133
Outcome-model follow-up: #162
Owned fork experiment: `teamleaderleo/codex#22`
Upstream contact authorized: false

## Exact pins

- Codex source: `openai/codex@5989dcc470695fc3f25a7eb3e90c014ef56d7d2a`
- Owned Codex experiment base: `teamleaderleo/codex:fieldwork/upstream-5989-base-clean`
- Owned Codex experiment head under test: `d637bf38108afedd52ac8d99efb80ceff797aa48`
- Rust SDK dependency: `rmcp = 3.0.0`
- Retrieval and experiment date: 2026-07-30

## Plain-language result so far

Codex currently stops waiting when its MCP tool timer expires, but the ordinary legacy request remains alive. The server is not told to cancel. A delayed tool can therefore finish after Codex has already reported a timeout.

The first real Codex `RmcpClient` regression confirmed all of the following together:

1. Codex returned `timed out awaiting tools/call`.
2. The server did not observe MCP cancellation.
3. The delayed synthetic mutation completed.
4. A later tool request on the same connection still succeeded.

This is a request-ownership defect, not immediate connection failure.

## Required invariant

When Codex reports an MCP tool timeout, the caller wait and the underlying request must not silently diverge.

A complete result must keep separate facts for:

1. caller deadline reached;
2. cancellation requested;
3. cancellation delivered or request stream closed;
4. remote cancellation observed;
5. remote operation terminally settled;
6. effect reconciled or still unknown.

Cancellation delivery is not proof that a mutation did not commit. A server can commit immediately before receiving cancellation or can ignore cancellation.

## Use cases

### Read-only lookup

Examples include search, list, read, and inspect.

Preferred behavior:

- cancel the timed-out request to release work;
- discard late output from the original request;
- permit retry only after connection health and request lineage are clear;
- do not let a late response satisfy a new request or pollute a cache.

The main cost of missing cancellation is wasted work and retained response ownership. A dishonest or incorrectly annotated server can still mutate during a nominal read, so automatic retry should not rely only on server hints.

### Potential mutation

Examples include sending a message, creating a ticket, deploying, charging, deleting, uploading, or changing account state.

Preferred behavior:

- attempt request-scoped cancellation promptly;
- report the result as outcome unknown unless a durable receipt proves otherwise;
- never automatically replay an accepted or possibly accepted request;
- reconcile using the original call ID, an idempotency key, an operation receipt, or a follow-up read.

A generic timeout followed by an automatic retry can duplicate the external effect.

### Tool paused for user elicitation

Examples include payment confirmation, deployment approval, account selection, and destructive-action review.

Preferred behavior:

- do not charge user decision time against active tool execution time;
- cancel the parent request when active tool time later expires;
- retire any associated elicitation request;
- reject a late user response instead of reviving a timed-out operation.

This use case rejects a simple wall-clock SDK timeout as the universal default.

### Concurrent tool calls

Preferred behavior:

- cancel only the timed-out request;
- keep unrelated requests and subscriptions alive;
- close the shared connection only when cancellation delivery itself proves the transport is unresponsive.

Closing the whole transport for every timeout converts one uncertain request into several uncertain requests.

### Broken or saturated transport

Preferred behavior:

- keep the caller-visible deadline bounded;
- give cancellation delivery a short grace period;
- if the cancellation write stalls, mark the connection unusable and trigger normal recovery;
- report the original operation as outcome unknown.

Awaiting `RequestHandle::cancel()` without a bound can turn a 40-second configured timeout into an unbounded wait.

### Modern 2026 lifecycle

Preferred behavior:

- distinguish legacy `notifications/cancelled` from per-request HTTP stream closure;
- preserve high-level MRTR / `input_required` handling;
- distinguish stateless terminal stream closure from stateful resumable disconnection;
- test modern stdio and modern Streamable HTTP separately.

Codex currently uses the Rust SDK's high-level modern `call_tool`, so a raw-request rewrite would lose lifecycle behavior. A complete modern solution likely requires a cancellable high-level SDK operation or handle.

## Implemented probes

The owned Codex fork contains four focused tests.

1. `tool_timeout_cancellation_probe.rs`
   - real Codex `RmcpClient::call_tool`;
   - records server cancellation and delayed effect completion;
   - verifies a follow-up request remains usable.
2. `tool_timeout_elicitation_probe.rs`
   - user response delay exceeds the configured tool timeout;
   - distinguishes Codex active-time accounting from SDK wall-clock timeout.
3. `tool_timeout_modern_http_probe.rs`
   - real stateless modern HTTP server;
   - returns a never-ending request SSE body;
   - records whether timeout closes that individual stream.
4. `tool_timeout_cancel_delivery_probe.rs`
   - raw legacy server stops reading after `tools/call`;
   - forces the cancellation notification write to stall;
   - checks whether the caller deadline remains bounded and whether the connection is retired.

## Candidate implementations

### A. Current Codex outer timeout

Mechanism: run the whole operation under the elicitation-aware `active_time_timeout` and drop the future when the deadline expires.

Good:

- preserves active execution time;
- user elicitation pauses the deadline;
- caller return remains bounded even on a stuck transport.

Bad:

- dropping the legacy request wait sends no MCP cancellation;
- the remote tool can finish after timeout;
- pending response ownership remains until late response, explicit cancellation, or transport teardown.

Disposition: insufficient.

### B. SDK-native request timeout

Mechanism: move the legacy deadline into `PeerRequestOptions.timeout`.

Good:

- small code change;
- uses the Rust SDK's existing request cancellation path;
- keeps timeout and SDK responder cleanup together.

Bad:

- charges user elicitation time against the deadline;
- request cancellation delivery can itself block;
- requested-modern sessions that fall back to legacy can acquire competing outer and inner deadlines.

Disposition: useful control; poor universal Codex policy.

### C. Codex pause-aware explicit cancellation

Mechanism: retain the legacy `RequestHandle`, wait on its response under `active_time_timeout`, then explicitly call `handle.cancel()`.

Good:

- preserves elicitation pause semantics;
- sends request-scoped cancellation;
- does not disturb unrelated calls when cancellation delivery works.

Bad:

- awaiting cancellation can exceed the configured timeout on a wedged transport;
- manually awaiting `handle.rx` bypasses some private SDK cleanup helpers;
- modern high-level lifecycle still needs a separate solution.

Disposition: strongest simple legacy implementation, but cancellation delivery needs a bound.

### D. Codex pause-aware bounded cancellation with transport escalation

Mechanism:

1. return the caller timeout immediately;
2. move the owned request handle into a background cancellation task;
3. give cancellation delivery a short grace period;
4. if delivery fails or stalls, cancel the shared `RunningService` so pending ownership is retired through transport teardown.

Good:

- preserves active-time accounting;
- keeps normal timeout request-scoped;
- keeps caller return bounded;
- escalates connection closure only after direct evidence that cancellation delivery is stuck.

Bad:

- cancellation can arrive after the caller sees the timeout;
- connection escalation still interrupts unrelated work;
- runtime shutdown can race the background task;
- timeout remains outcome unknown for mutations even when cancellation is delivered.

Disposition: leading owned-fork candidate pending behavior matrix.

## Tool metadata and retry policy

Codex retains MCP `ToolAnnotations`, including read-only and idempotency hints. The MCP SDK explicitly defines these as hints and warns clients not to make decisions from untrusted server annotations alone.

Recommended use:

- use hints for wording, telemetry, approval defaults, and conservative scheduling;
- do not automatically replay a timed-out mutation based only on `readOnlyHint` or `idempotentHint`;
- permit stronger retry policy only for explicitly trusted connectors, host-configured policy, or a durable operation receipt;
- preserve the original model call ID and thread metadata for reconciliation.

## Outcome-model boundary

The public Codex MCP tool-call item currently has only `inProgress`, `completed`, and `failed`, with an error containing only a message. It cannot distinguish cancellation requested, cancellation unconfirmed, transport closed, or outcome unknown.

Fieldwork candidate #162 owns that broader event-model decision. This lane keeps the request cancellation mechanism focused.

## Verification state

- Baseline legacy cancellation/effect/follow-up probe: passed on the real Codex crate.
- Full four-variant matrix: running through the owned fork and the Fieldwork single-job runner.
- Modern stream-close result: pending.
- Cancellation-send-stall result: pending.
- No upstream contact occurred.

## Decision gate

Promote a production direction only when one candidate demonstrates:

1. legacy cancellation observed;
2. delayed synthetic mutation stopped;
3. elicitation pause preserved;
4. caller return bounded when cancellation delivery stalls;
5. stalled delivery retires the unhealthy connection;
6. a later request succeeds when cancellation delivery succeeds;
7. modern behavior is explicitly classified rather than assumed;
8. no automatic replay of a potentially mutating request.
