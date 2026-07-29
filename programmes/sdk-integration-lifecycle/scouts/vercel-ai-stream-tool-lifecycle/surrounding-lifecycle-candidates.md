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

Applications may need to consume and classify stream parts themselves, rely on telemetry, accept lower-level default error logging, or maintain different instrumentation when moving from `streamText` to `ToolLoopAgent`.

### External overlap

Upstream PR `vercel/ai#15867` already adds `onError`, `onChunk`, and `onAbort` to agent settings and per-call parameters, merges constructor and call callbacks, preserves the default error handler, and includes runtime tests, type tests, API documentation, and a changeset.

### Disposition

**Stop duplicate implementation work.** Retain as a pinned-revision API finding. Reopen only if the existing proposal omits a demonstrated ordering or compatibility case that matters to an owned application.

## Candidate 2: provider-body error before terminal chunk

### Source evidence

The pinned result getters automatically consume the stream. `consumeStream()` catches a stream error and rejects all pending result promises. Pinned tests exercise a provider stream error after metadata and verify rejection of text, steps, finish reason, and usage.

An older external candidate directly rejected promises from the resilient-stream catch path. It was staged as `teamleaderleo/ai#2`, then reviewed against the pinned revision.

### Consequence

A real provider stream error is already observable through the public aggregate-result path at the pin. It remains a useful baseline for the terminal matrix, but not a new implementation branch.

### Disposition

**Stop as a new fix.** `teamleaderleo/ai#2` was closed as superseded/redundant. Keep provider error in regression comparisons with explicit abort and silent close.

## Candidate 3: silent close with partial output

### Source evidence

The pinned implementation distinguishes an empty incomplete stream from a partial incomplete stream:

- empty incomplete streams reject with `No output generated. The model stream ended without a finish chunk.`;
- partial text without `text-end` or a finish chunk resolves the partial text, records one step, and derives finish reason `other`;
- the public `FinishReason` union has no `incomplete` or `truncated` member;
- the UI finish handler marks only explicit abort parts as aborted, so the partial silent close reaches its end callback as `isAborted: false`.

### Consequence

Partial recovery is useful, but persistence, billing, continuation, and UI state can treat provider truncation as ordinary completion. Partial tool input, completed tool calls without a terminal model event, and incomplete continuation steps may be more consequential than partial plain text.

### Disposition

**Promoted to campaign #94.** Build a target-native outcome matrix and choose a compatibility-safe representation before proposing a change.

## Candidate 4: local tool abort cooperation

### Source evidence

The operation abort signal is forwarded into local tool execution. Existing tests cover abort during tool execution. Fieldwork candidate `teamleaderleo/ai#1` now adds a delayed local-tool case alongside the pending-provider-read case.

A tool still controls whether its implementation observes the signal and whether an already committed side effect can be reversed.

### Consequence

The run can truthfully be aborted while a non-cooperative or already committed side effect still completes. A terminal state must avoid implying rollback.

### Disposition

**Included in campaign #76 and candidate PR #1.** SDK correctness owns signal delivery, result suppression, and truthful terminal reporting. Application design owns idempotency, transactions, and compensation.

## Candidate 5: resumable Stop routing and stale state

### Source evidence

The pinned Next example correctly separates disconnect from deliberate Stop:

- GET resumes `activeStreamId`;
- DELETE writes `canceledAt: Date.now()`;
- the streaming POST owns an `AbortController` and polls `canceledAt` from `onChunk`.

A concrete state bug remains:

- `saveChat` changes only fields supplied by the caller;
- the new-run POST previously omitted `canceledAt`, leaving the old timestamp durable;
- the new-run save was not awaited before streaming began;
- any truthy `canceledAt` aborts the current run.

One stopped run can therefore make a later run abort on its first chunk.

### Candidate

`teamleaderleo/ai#3` clears and awaits `canceledAt` before starting a new generation and awaits related state writes. It is the minimal sticky-state repair.

### Remaining boundary

Cancellation is still chat-scoped. A delayed or duplicated Stop for run A can race with run B. A stronger design needs an explicit run identity and must abort only when the cancelled identity matches the active generation.

### Disposition

**Promoted to campaign #95.** Validate the minimal repair, then test whether run-scoped cancellation is required. Keep cross-request and distributed ownership outside the core abort patch.

## Candidate 6: UI callback outcome agreement

### Source evidence

The chat layer records separate `isAbort`, `isDisconnect`, and `isError` flags and invokes its finish callback from `finally`. UI stream conversion separately reports partial state and distinguishes reader cancellation from explicit abort. Silent partial closure, however, reaches normal finish handling with finish reason `other`.

### Consequence

The same run crosses core stream parts, UI message conversion, transport errors, chat status, persistence callbacks, and resumable storage. A mismatch can save a partial message as complete or route a Stop to the wrong run.

### Disposition

Split by owner:

- explicit-abort agreement remains in campaign #76;
- incomplete-close agreement belongs to campaign #94;
- reconnect and Stop identity belong to campaign #95.

Promote only a specific disagreement reproduced at the pinned revision.

## Ranked recommendations

1. Execute and review `teamleaderleo/ai#1` for explicit abort, all aggregate promises, delayed tools, and race cases.
2. Validate the sticky resumable-state repair in `teamleaderleo/ai#3`, then test run-scoped Stop identity under campaign #95.
3. Build campaign #94's truncated-stream matrix before selecting a public representation or candidate fix.
4. Keep ordinary provider errors as a regression baseline, not a new fix branch.
5. Stop duplicate ToolLoopAgent callback work while `vercel/ai#15867` covers the same API surface.
6. Stop generic claims that all stream cancellation should abort all underlying work.
