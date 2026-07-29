# Surrounding lifecycle candidates

## Scope

This note extends scout #17 after the explicit-abort contract was clarified. It separates related cases by owning boundary so campaign #76 does not become an undifferentiated cancellation bucket.

Pinned target revision: [`vercel/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://redirect.github.com/vercel/ai/commit/2b872b0db3769decf69945830c66a897c1e37347).

Upstream contact: none.

## Candidate 1: ToolLoopAgent callback-surface mismatch

### Source evidence

At the pinned revision:

- `AgentCallParameters` exposes the operation abort signal plus start, step, tool-execution, and end callbacks;
- `AgentStreamParameters` adds stream transforms but not direct `onAbort`, `onError`, or `onChunk` callbacks;
- `ToolLoopAgent.stream()` forwards the operation abort signal and the callbacks represented by its public types into `streamText`.

The operation can therefore be aborted, but an application using `ToolLoopAgent.stream()` cannot configure the same direct abort, error, and chunk observation hooks available through `streamText`.

### Consequence

Applications may need to consume and classify stream parts themselves, rely on telemetry, accept lower-level default error logging, or maintain different instrumentation when moving from `streamText` to `ToolLoopAgent`.

### External overlap

The [existing upstream ToolLoopAgent callback candidate](https://redirect.github.com/vercel/ai/pull/15867) adds `onError`, `onChunk`, and `onAbort` to agent settings and per-call parameters, merges constructor and call callbacks, preserves the default error handler, and includes runtime tests, type tests, API documentation, and a changeset.

### Disposition

**Stop duplicate implementation work.** Retain the pinned-revision API mismatch as a finding. Reopen only if the existing proposal omits a demonstrated ordering or compatibility case that matters to an owned application.

## Candidate 2: provider stream error before terminal chunk

### Source evidence

The result getters automatically consume the stream. `consumeStream()` catches a real stream error and rejects the root result promises. The [pinned provider-error test](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.test.ts#L2725-L2785) verifies representative public getters after a provider error.

An older external candidate directly rejected promises from the resilient-stream catch path. It was staged as [`teamleaderleo/ai#2`](https://github.com/teamleaderleo/ai/pull/2), then reviewed against the pinned revision and closed as redundant.

### Consequence

A real provider stream error is already observable through the public result path at the pin. It remains a useful comparison case for terminal conformance, but not a new implementation branch.

### Disposition

**Stop as a new fix.** Keep provider error in regression comparisons with explicit abort and silent close.

## Candidate 3: silent close with partial output

### Source evidence

The [pinned incomplete-close tests](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.test.ts#L2644-L2724) distinguish an empty incomplete stream from a partial incomplete stream:

- empty incomplete streams reject with `No output generated. The model stream ended without a finish chunk.`;
- partial text without a terminal finish chunk resolves the partial text, records one step, derives finish reason `other`, and does not call `onError`.

The public [finish-reason union](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/types/language-model.ts#L67-L83) has no `incomplete` or `truncated` member. The [UI finish handler](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/ui-message-stream/handle-ui-message-stream-finish.ts#L69-L138) marks only an explicit abort chunk as aborted.

### Consequence

Partial recovery is useful, but persistence, continuation, billing, and UI state can treat provider truncation as ordinary completion. Partial tool input, completed tool calls without a terminal model event, and incomplete continuation steps may be more consequential than partial plain text.

### Disposition

**Promoted to campaign #94.** Build a target-native outcome matrix and choose a compatibility-safe representation only after core, UI, and persistence traces agree.

## Candidate 4: local tool abort cooperation

### Source evidence

The operation abort signal is forwarded into local tool execution. Existing pinned tests cover abort during tool execution. Draft candidate [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) adds a delayed local-tool case alongside the pending-provider-read case.

A tool still controls whether its implementation observes the signal and whether an already committed side effect can be reversed.

### Consequence

The run can truthfully be aborted while a non-cooperative or already committed side effect still completes. A terminal state must not imply rollback.

### Review finding

PR #1 currently awaits abort callbacks before cancelling the provider reader and closing the outward stream. Because [`notify()` waits for callback promises](https://github.com/teamleaderleo/ai/blob/fieldwork/explicit-abort-terminal-settlement/packages/ai/src/util/notify.ts#L6-L20), callback ordering is part of the remaining campaign work.

### Disposition

**Included in campaign #76 and draft candidate PR #1.** SDK correctness owns signal delivery, result suppression, and truthful terminal reporting. Application design owns idempotency, transactions, and compensation.

## Candidate 5: resumable Stop routing and stale state

### Source evidence

The pinned Next example correctly separates disconnect from deliberate Stop:

- [GET resumes `activeStreamId`](https://github.com/teamleaderleo/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/examples/next/app/api/chat/%5Bid%5D/stream/route.ts#L8-L29);
- [DELETE writes `canceledAt: Date.now()`](https://github.com/teamleaderleo/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/examples/next/app/api/chat/%5Bid%5D/stream/route.ts#L31-L44);
- the [streaming POST owns an `AbortController` and polls `canceledAt`](https://github.com/teamleaderleo/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/examples/next/app/api/chat/route.ts#L64-L107).

A concrete sequential-state defect remains:

- [`saveChat`](https://github.com/teamleaderleo/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/examples/next/util/chat-store.ts#L22-L48) changes only fields supplied by the caller;
- the new-run POST omitted `canceledAt`, leaving the old timestamp durable;
- any truthy `canceledAt` aborts the current run.

One stopped run can therefore make a later run abort on its first chunk.

### Draft mitigation

[`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3) clears and awaits `canceledAt` before starting a new generation. It mitigates the ordered “Stop A, then start B” case.

### Remaining boundary

PR #3 is not a complete ownership fix:

- cancellation is still chat-scoped;
- a delayed or duplicated Stop A can race with run B;
- an older finish can overwrite a newer run's state;
- the file store has no compare-and-set or per-chat transaction;
- [`createUIMessageStreamResponse`](https://github.com/teamleaderleo/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/ui-message-stream/create-ui-message-stream-response.ts#L30-L39) starts the resumable consumer without awaiting it.

### Disposition

**Promoted to campaign #95.** Keep PR #3 as a draft mitigation until the sequential case is executed. Test run-scoped cancellation and conditional state ownership before promoting a complete candidate.

## Candidate 6: UI callback outcome agreement

### Source evidence

The chat layer records separate abort, disconnect, and error state and invokes its finish callback from a finalization path. UI stream conversion separately reports partial state and distinguishes reader cancellation from explicit abort. Silent partial closure, however, reaches end handling with finish reason `other` and no explicit abort marker.

### Consequence

The same run crosses core stream parts, UI conversion, transport errors, chat status, persistence callbacks, and resumable storage. A mismatch can save a partial message as complete or route a Stop to the wrong run.

### Disposition

Split by owner:

- explicit-abort agreement remains in campaign #76;
- incomplete-close agreement belongs to campaign #94;
- reconnect and Stop identity belong to campaign #95.

Promote only a specific disagreement reproduced at the pinned revision.

## Ranked recommendations

1. Execute and review draft PR #1 for pending reads, root and derived result settlement, pre-aborted signals, delayed tools, callback ordering, and race cases.
2. Validate draft PR #3 only as the sequential stale-state mitigation, then test run-scoped Stop identity under campaign #95.
3. Build campaign #94's truncated-stream matrix before selecting a public representation or candidate fix.
4. Keep ordinary provider errors as a regression baseline, not a new fix branch.
5. Stop duplicate `ToolLoopAgent` callback work while the [existing upstream candidate](https://redirect.github.com/vercel/ai/pull/15867) covers the same API surface.
6. Stop generic claims that all stream cancellation should abort all underlying work.