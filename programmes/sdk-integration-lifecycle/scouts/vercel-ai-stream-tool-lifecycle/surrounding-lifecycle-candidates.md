# Surrounding lifecycle candidates

## Scope

This note extends scout #17 after the explicit-abort contract was clarified. It separates related cases by owning boundary so the terminal-settlement campaign does not become an undifferentiated cancellation bucket.

Pinned target revision: `teamleaderleo/ai@2b872b0db3769decf69945830c66a897c1e37347`

Upstream contact: none.

## Candidate 1: ToolLoopAgent callback-surface mismatch

### Source evidence

At the pinned revision:

- `AgentCallParameters` exposes `abortSignal`, start callbacks, step callbacks, tool-execution callbacks, and end callbacks.
- `AgentStreamParameters` only adds `experimental_transform`.
- `ToolLoopAgentSettings` exposes the same start, step, tool-execution, and end callbacks.
- `ToolLoopAgent.stream()` forwards `abortSignal` and the callbacks represented by those types into `streamText`.
- the agent types and settings do not expose `streamText` lifecycle callbacks `onAbort`, `onError`, or `onChunk`.

The operation can therefore be aborted, but an application using `ToolLoopAgent.stream()` cannot configure the same direct abort, error, and chunk observation hooks available through `streamText`.

### Consequence

Applications may need to:

- consume and classify stream parts themselves;
- rely on telemetry for abort and error observation;
- lose the ability to replace lower-level default error logging through the agent API;
- maintain different lifecycle instrumentation when moving from `streamText` to `ToolLoopAgent`.

This does not prove terminal settlement is incorrect. It is an API consistency and observability candidate.

### Next deterministic question

Build a type/runtime conformance test that configures equivalent lifecycle observation through `streamText` and `ToolLoopAgent.stream()` and records which events can be observed without custom stream parsing or telemetry.

### Disposition

**Additional scout or narrow API experiment.** Keep separate from campaign #76's first fix because it changes public API surface rather than repairing the same internal terminal path.

Promotion condition: demonstrate a realistic application requirement that cannot be met through the returned stream/result without duplicated lifecycle code, and identify a bounded callback-forwarding design with stable callback ordering.

## Candidate 2: provider-body error before terminal chunk

### Source evidence

Aggregate result promises are primarily finalized by the event processor's graceful `flush`. A provider stream that errors before a terminal chunk can bypass that flush path. A public report and candidate patch describe aggregate promises remaining pending or requiring explicit rejection when the provider body errors after output begins.

### Consequence

A caller can observe a stream error while separate result promises remain unresolved, producing two incompatible views of the same run.

### Next deterministic question

Inject a provider stream error after semantic output and before `model-call-end`; assert the outcome of every aggregate promise, stream consumer, callback, and tool-loop step.

### Disposition

**Campaign #76 conformance case.** It shares the terminal-settlement invariant, while retaining a distinct cause from explicit abort.

## Candidate 3: silent close with partial output

### Source evidence

The pinned implementation distinguishes an empty incomplete stream from a partial incomplete stream. Empty incomplete streams produce a no-output error. Partial incomplete streams can retain a partial step and derive finish reason `other` when no explicit finish reason was recorded.

### Consequence

Partial recovery is useful, but callers and persistence layers can confuse incomplete provider closure with a normal provider terminal event unless they inspect enough internal state.

### Next deterministic question

Compare the externally visible result and persistence state for:

- provider finish with raw reason absent;
- provider close after partial text without terminal chunk;
- provider error after partial text;
- explicit abort after partial text.

### Disposition

**Campaign #76 design case.** Seek a stable typed distinction before considering implementation changes.

## Candidate 4: local tool abort cooperation

### Source evidence

The operation abort signal is forwarded into local tool execution. Existing tests cover abort during tool execution and the outer abort part/callback. A tool still controls whether its implementation observes the signal and whether an already committed side effect can be reversed.

### Consequence

The run can truthfully be aborted while a non-cooperative or already committed side effect still completes. A terminal state must avoid implying rollback.

### Next deterministic question

Run three delayed tools under explicit abort:

1. cooperative read-only tool;
2. non-cooperative read-only tool;
3. side-effecting tool with an idempotency key and a commit boundary.

Record signal delivery, callback order, result suppression, side-effect state, and aggregate settlement.

### Disposition

**Campaign #76 conformance case plus application guidance.** SDK correctness can guarantee signal delivery and truthful reporting; application design owns idempotency and compensation.

## Candidate 5: resumable Stop routing

### Source evidence

A network disconnect does not communicate whether the user clicked Stop, navigated, closed a tab, or lost connectivity. The SDK's resumable pattern therefore uses continued server work for disconnects and an explicit server-visible cancellation route for deliberate Stop.

### Consequence

Using request disconnection as Stop either kills resumability or leaves deliberate Stop unable to reach the original server run.

### Next deterministic question

Build an owned application test with a run ID, durable cancellation flag, dedicated stop endpoint, and server-owned abort controller. Exercise navigation, reconnect, deliberate Stop, duplicate Stop, and Stop routed to a different process.

### Disposition

**Application integration case.** Keep outside the core SDK candidate unless a reusable SDK abstraction can be proven across distributed runtimes.

## Candidate 6: UI callback outcome agreement

### Source evidence

The chat layer records separate `isAbort`, `isDisconnect`, and `isError` flags and invokes its finish callback from `finally`. UI stream conversion separately reports partial state and distinguishes reader cancellation from explicit abort.

### Consequence

The same run crosses core stream parts, UI message conversion, transport errors, chat status, and persistence callbacks. A mismatch can save a partial message as complete or report an intentional Stop as a network error.

### Next deterministic question

Create one outcome table across core `streamText`, `toUIMessageStream`, HTTP transport, and `AbstractChat` for normal completion, Stop, reader cancellation, disconnect, provider error, and incomplete close.

### Disposition

**Campaign #76 cross-layer test.** Promote only specific disagreements that reproduce at the pinned revision.

## Ranked recommendations

1. Continue campaign #76 with explicit-abort and provider-error settlement first.
2. Add the delayed-tool and UI cross-layer matrices before accepting the candidate fix.
3. Open a separate narrow experiment for ToolLoopAgent lifecycle callbacks after a target-native type/runtime reproduction.
4. Treat resumable Stop as an owned-application architecture trial.
5. Stop generic claims that all stream cancellation should abort all underlying work.
