# Follow-up: cancellation intent and terminal outcomes

## Status

- Scout: #17
- Scout PR: #34
- Explicit-abort campaign: #76
- Truncated-stream campaign: #94
- Resumable Stop campaign: #95
- Explicit-abort candidate: [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) — draft
- Resumable sticky-state mitigation: [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3) — draft
- Pinned target revision: [`vercel/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://redirect.github.com/vercel/ai/commit/2b872b0db3769decf69945830c66a897c1e37347)
- Explicit-abort implementation provenance: [`0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`](https://redirect.github.com/vercel/ai/commit/0ef2ae9a7f143d90972b4ff217046e0b04ea67f1)
- Current owned explicit-abort branch head: `a8019871b9b45def4bc3e78055d6411751d1ab73`
- Upstream contact: none

## Corrected interpretation

The SDK intentionally separates consumer cancellation from operation abort.

- `reader.cancel()` or an early break means that one consumer stopped receiving output.
- A caller-provided `AbortSignal`, including the signal owned by `Chat.stop()`, means that the operation should abort.
- A resumable client disconnect should preserve server work; deliberate Stop needs a separate server-visible cancellation channel.

The original scout treated continued tool execution after reader cancellation as a possible defect. The pinned UI conversion path records `isAborted` only after an explicit abort chunk, and its cancellation callback can persist partial state without claiming operation abort. See [`handleUIMessageStreamFinish`](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/ui-message-stream/handle-ui-message-stream-finish.ts#L69-L138).

Stop “reader cancellation should automatically abort tools” as an independent defect claim unless a deterministic case shows corruption of another consumer or unresolved public state.

## Explicit-abort invariant

An explicit abort should:

1. reach the provider request;
2. reach cooperative local tools;
3. reject each root result promise once with the abort reason;
4. make derived result getters reject through those roots rather than hang;
5. emit at most one abort part;
6. invoke abort callbacks at most once;
7. avoid normal completion or a competing error outcome;
8. preserve partial UI state with an unambiguous aborted classification.

Ordinary reader cancellation should remain scoped to that consumer.

## Confirmed pending-read gap

The pinned resilient stream awaits `reader.read()` and checks `abortSignal.aborted` only after the read returns. If the provider remains open, the pull can stay pending after the operation signal has fired. See the [pinned implementation](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.ts#L1432-L1493).

The [maintainer-authored explicit-abort candidate](https://redirect.github.com/vercel/ai/pull/16852) adds an abort listener independent of provider reads, rejects result state, reports one abort, closes the outward stream, and cancels the pending reader. The implementation is staged in owned PR #1.

## Result-settlement model

The public result exposes many getters, but they are not independent settlement roots. At the owned candidate revision, `rejectResultPromises()` directly rejects:

- finish reason;
- raw finish reason;
- usage;
- steps;
- initial response messages.

Text, content, final step, output, tool call/result collections, request/response metadata, and accumulated response messages derive from those roots. See the [getter and rejection implementation](https://github.com/teamleaderleo/ai/blob/fieldwork/explicit-abort-terminal-settlement/packages/ai/src/generate-text/stream-text.ts#L2425-L2673).

## Added target-native coverage

[`stream-text-explicit-abort.test.ts`](https://github.com/teamleaderleo/ai/blob/fieldwork/explicit-abort-terminal-settlement/packages/ai/src/generate-text/stream-text-explicit-abort.test.ts) covers:

- abort after partial provider output while the next read remains pending;
- root promises and representative derived getters;
- provider-reader cancellation;
- a signal already aborted before `streamText` begins;
- abort during delayed local-tool execution;
- one abort part and one abort callback;
- no normal end callback and no later tool result.

The branch merges cleanly. The fork has no Actions runs or commit statuses, and the available execution environment could not clone GitHub. The tests are therefore written and statically reviewed but unexecuted.

## Open callback-ordering gate

The candidate currently awaits `onAbort` and telemetry callbacks before it emits the abort part, closes the outward stream, and calls `reader.cancel()`. [`notify()` waits for callback promises](https://github.com/teamleaderleo/ai/blob/fieldwork/explicit-abort-terminal-settlement/packages/ai/src/util/notify.ts#L6-L20), while the `onAbort` option does not state that it pauses stream processing.

A slow or never-settling callback can therefore delay cancellation. Campaign #76 must select and test one contract:

- callback completion is part of abort completion and has an explicit bound; or
- result settlement and provider cancellation occur first, while notification cannot block them.

## Final branch dispositions

### Ordinary provider stream error

At the pinned revision, aggregate getters automatically consume the stream and `consumeStream()` rejects the root result promises when the stream errors. The [pinned provider-error test](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.test.ts#L2725-L2785) verifies representative public getters. The older owned candidate was closed as redundant in [`teamleaderleo/ai#2`](https://github.com/teamleaderleo/ai/pull/2).

Keep provider error as a regression baseline, not a new fix branch.

### Silent incomplete close

A provider stream that closes after partial output without an error or terminal chunk resolves partial text, records a step, derives finish reason `other`, and does not call `onError`. See the [pinned incomplete-close tests](https://redirect.github.com/vercel/ai/blob/2b872b0db3769decf69945830c66a897c1e37347/packages/ai/src/generate-text/stream-text.test.ts#L2644-L2724).

This classification and compatibility question belongs to campaign #94.

### Delayed local tools

Tool abort cooperation is included in campaign #76 and candidate PR #1. SDK correctness owns signal delivery, result suppression, and truthful terminal reporting. Applications still own idempotency, transaction boundaries, and compensation for committed side effects.

### Reader cancellation and tee consumers

`StreamTextResult` creates derived streams with `ReadableStream.tee()`. Cancelling one branch must not automatically abort work required by another branch. Continue only if a deterministic case shows corruption or unresolved public state.

### Resumable Stop

The pinned Next example correctly uses a separate Stop route, but its chat-level `canceledAt` value persists into later runs. Candidate PR #3 clears stale state for the sequential case. It remains a draft mitigation because cancellation is not run-scoped and the file store has no transactional ownership checks. Campaign #95 owns delayed Stop, older-finish, reconnect, and concurrent-write cases.

### ToolLoopAgent callback parity

The pinned agent API omits direct `onAbort`, `onError`, and `onChunk` parity with `streamText`. The [existing upstream ToolLoopAgent callback candidate](https://redirect.github.com/vercel/ai/pull/15867) already contains implementation, runtime/type tests, documentation, callback merging, and a changeset. Stop duplicate Fieldwork implementation work.

## Validation matrix

| Scenario | Provider | Tool | Root results | Callbacks and stream | Disposition |
| --- | --- | --- | --- | --- | --- |
| normal completion | completes | completes | resolve once | finish once | baseline |
| one reader cancels | may continue | may continue | other consumers remain valid | consumer partial, not aborted | intended |
| explicit abort during pending read | cancelled | receives signal | reject once with abort reason | abort once, no normal end | campaign #76 / draft PR #1 |
| explicit abort during delayed tool | already finished or cancelled | receives signal | reject once | no later success claim | campaign #76 / draft PR #1 |
| provider stream error | errors | settles consistently | reject once | stream error | pinned baseline |
| silent close after partial output | closes incompletely | depends on emitted calls | currently resolves partial result | currently looks non-aborted | campaign #94 |
| resumable disconnect | continues | continues | run remains active | reconnectable | intended architecture |
| explicit resumable Stop | cancelled through server channel | receives signal | settle aborted once | durable run-specific state | campaign #95; PR #3 is partial only |

## Boundaries

This follow-up reports evidence and stages owned-fork candidates. It makes no upstream contact, acceptance claim, or modification outside owned repositories.