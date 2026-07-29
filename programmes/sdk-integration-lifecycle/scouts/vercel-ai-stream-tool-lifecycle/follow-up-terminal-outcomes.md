# Follow-up: cancellation intent and terminal outcomes

## Status

- Scout: #17
- Scout PR: #34
- Explicit-abort campaign: #76
- Truncated-stream campaign: #94
- Resumable Stop campaign: #95
- Explicit-abort target candidate: `teamleaderleo/ai#1` — ready for review
- Resumable sticky-state candidate: `teamleaderleo/ai#3` — ready for review
- Pinned target revision: `teamleaderleo/ai@2b872b0db3769decf69945830c66a897c1e37347`
- Explicit-abort implementation revision: `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`
- Explicit-abort branch head with Fieldwork tests: `a80622cbc1e86794ce55d913a050d649e39f6051`
- Upstream contact: none

## Corrected interpretation

The SDK intentionally separates consumer cancellation from operation abort.

- `reader.cancel()` or an early break means that one consumer has stopped receiving output.
- a caller-provided `AbortSignal`, including the signal owned by `Chat.stop()`, means that the operation should abort.
- a resumable client disconnect should preserve server work; deliberate Stop needs a separate server-visible cancellation channel.

The original scout treated continued tool execution after reader cancellation as a possible defect. Source tests make the intended distinction explicit: reader cancellation is recorded as `isAborted: false`. Stop that as an independent defect candidate unless cancellation corrupts another active consumer or leaves public state inconsistent.

## Explicit-abort invariant

An explicit abort should:

1. reach the provider request;
2. reach cooperative local tools;
3. settle every public aggregate promise exactly once with the abort reason;
4. emit one abort part;
5. invoke abort callbacks once;
6. avoid normal completion or a competing error outcome;
7. preserve partial UI state with an unambiguous aborted classification.

Ordinary reader cancellation should remain scoped to that consumer.

## Confirmed candidate

The pinned implementation checks `abortSignal.aborted` around `await reader.read()`. If the provider stream stays open and the read remains pending, the abort path may never execute and aggregate promises can remain pending.

The [maintainer-authored explicit-abort candidate](https://redirect.github.com/vercel/ai/pull/16852) listens to the abort signal independently of provider reads. It rejects result promises, invokes abort callbacks, emits an abort part, closes the outward stream, and cancels the pending reader. The implementation is staged in owned PR `teamleaderleo/ai#1`.

Fieldwork added target-native tests for:

- abort after partial provider output while the next read remains pending;
- abort during delayed local tool execution;
- all aggregate promises;
- provider cancellation and cooperative tool signal delivery;
- one abort part and one abort callback;
- no normal end callback and no later tool result.

PR #1 merges cleanly and is ready for review. The fork has no Actions runs or commit statuses, and this environment could not clone GitHub, so the added tests remain unexecuted here.

## Final branch dispositions

### Ordinary provider stream error

At the pinned revision, aggregate getters automatically consume the stream and `consumeStream()` rejects all pending result promises when the stream errors. Pinned tests cover this behavior. The older staged candidate was closed as redundant in `teamleaderleo/ai#2`.

Keep provider error as a regression baseline, not a new fix branch.

### Silent incomplete close

A provider stream that closes after partial output without an error or terminal chunk resolves partial text, records a step, derives finish reason `other`, and reaches UI end handling as not aborted. This classification and compatibility question is split to campaign #94.

### Delayed local tools

Tool abort cooperation is included in campaign #76 and candidate PR #1. SDK correctness owns signal delivery, result suppression, and truthful reporting. Applications still own idempotency, transaction boundaries, and compensation for committed side effects.

### Reader cancellation and tee consumers

`StreamTextResult` creates derived streams with `ReadableStream.tee()`. Cancelling one branch must not automatically abort work needed by another branch. Continue only if a deterministic case shows corruption or unresolved public state.

### Resumable Stop

The pinned Next example correctly uses a separate Stop route, but its chat-level `canceledAt` value persists into later runs. Candidate `teamleaderleo/ai#3` clears and awaits stale state before starting a new run. Campaign #95 covers the remaining need for run-scoped cancellation identity and delayed Stop races.

### ToolLoopAgent callback parity

The pinned agent API omits direct `onAbort`, `onError`, and `onChunk` parity with `streamText`. The [upstream ToolLoopAgent stream-callback candidate](https://redirect.github.com/vercel/ai/pull/15867) already covers that API surface with implementation, runtime and type tests, documentation, callback merging, and a changeset. Stop duplicate Fieldwork implementation work.

## Validation matrix

| Scenario | Provider | Tool | Aggregate promises | Callbacks and stream | Disposition |
| --- | --- | --- | --- | --- | --- |
| normal completion | completes | completes | resolve once | finish once | baseline |
| one reader cancels | may continue | may continue | other consumers remain valid | consumer partial, not aborted | intended |
| explicit abort during pending read | cancelled | receives signal | reject once with abort reason | abort once, no normal end | campaign #76 / PR #1 |
| explicit abort during delayed tool | already finished or cancelled | receives signal | reject once | no later success claim | campaign #76 / PR #1 |
| provider stream error | errors | settles consistently | reject once | stream error | pinned baseline |
| silent close after partial output | closes incompletely | depends on emitted calls | currently resolves partial result | currently looks non-aborted | campaign #94 |
| resumable disconnect | continues | continues | run remains active | reconnectable | intended architecture |
| explicit resumable Stop | cancelled through server channel | receives signal | settle aborted once | durable run-specific state | campaign #95 / PR #3 |

## Boundaries

This follow-up reports evidence and stages owned-fork candidates. It makes no upstream contact, acceptance claim, or modification outside owned repositories.
