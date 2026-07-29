# Follow-up: cancellation intent and terminal outcomes

## Status

- Scout: #17
- Scout PR: #34
- Follow-up campaign: #76
- Owned target candidate: `teamleaderleo/ai#1`
- Pinned target revision: `teamleaderleo/ai@2b872b0db3769decf69945830c66a897c1e37347`
- Candidate patch revision: `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`
- Upstream contact: none

## Corrected interpretation

The SDK intentionally separates consumer cancellation from operation abort.

- `reader.cancel()` or an early break means that one consumer has stopped receiving output.
- a caller-provided `AbortSignal`, including the signal owned by `Chat.stop()`, means that the operation should abort.
- a resumable client disconnect should preserve server work; deliberate Stop needs a separate server-visible cancellation channel.

The original scout treated continued tool execution after reader cancellation as a possible defect. Source tests make the intended distinction explicit: reader cancellation is recorded as `isAborted: false`. The branch should therefore stop as a defect candidate unless cancellation corrupts another active consumer or leaves public state inconsistent.

## Enforceable invariant

For each run, every terminal path should converge exactly once on one outcome:

- completed;
- aborted by an explicit operation signal;
- errored;
- timed out;
- incomplete provider close;
- consumer-disconnected or consumer-cancelled where the underlying run remains owned elsewhere.

An explicit abort should:

1. reach the provider request;
2. reach cooperative local tools;
3. settle all public aggregate promises exactly once;
4. emit at most one abort part;
5. invoke abort callbacks at most once;
6. avoid normal completion callbacks after abort;
7. preserve partial output with an unambiguous aborted state where the UI layer supports it.

Ordinary reader cancellation should remain scoped to that consumer.

## Confirmed target-native candidate

The pinned implementation checks `abortSignal.aborted` around `reader.read()`. If the provider stream stays open and the read remains pending, the abort path may never execute and aggregate promises may remain pending.

A maintainer-authored upstream candidate listens to the abort signal independently of provider reads. It rejects result promises, invokes abort callbacks, emits an abort part, closes the outward stream, and cancels the pending reader. The exact candidate has been staged without modification in the owned fork as draft PR `teamleaderleo/ai#1`.

This staging preserves provenance. Fieldwork did not contact upstream and did not represent the patch as accepted.

## Surrounding cases

### Provider stream error before finish

A provider body can error after semantic output but before a terminal chunk. The public stream may error while aggregate promises depend on a graceful transform flush. This is a separate terminal-settlement case from explicit abort and should receive the same all-promises conformance checks.

### Silent incomplete close

At the pinned revision, an incomplete stream with partial output can resolve as a partial step with finish reason `other`. This may be useful recovery behavior, but persistence and callers need an explicit way to distinguish provider completion from incomplete closure.

### Delayed local tools

Tools receive the operation abort signal. Tests should verify signal delivery, callback order, tool result suppression, and settlement when a delayed tool is active. An abort cannot undo a side effect already committed, so tool safety also requires application-level idempotency or transaction design.

### Reader cancellation and tee consumers

`StreamTextResult` creates derived streams with `ReadableStream.tee()`. Cancelling one branch must not automatically abort work needed by another branch. The test matrix should verify that the remaining branch continues consistently and that cancelled-branch callbacks report partial consumer state without claiming operation abort.

### Resumable Stop

A request disconnect cannot communicate whether the user deliberately stopped, navigated away, closed a tab, or lost connectivity. A resumable application needs a run ID, a dedicated stop endpoint or equivalent channel, durable cancellation state, and a server-owned abort controller. Navigation and reconnection should preserve the run; deliberate Stop should abort it.

## Campaign decision

Promote the shared terminal-outcome question to campaign #76.

Active first candidate: explicit abort while the provider read remains pending.

Additional conformance cases: provider error before finish, incomplete close, active delayed tool, pre-aborted signal, abort/error race, multiple result consumers, and resumable Stop routing.

Stop reader cancellation as an independent SDK defect hypothesis unless deterministic evidence shows corruption, indefinite public state, or violation of another active consumer's contract.

## Validation matrix

| Scenario | Provider | Tool | Aggregate promises | Callbacks and stream | Expected disposition |
| --- | --- | --- | --- | --- | --- |
| normal completion | completes | completes | resolve once | finish once | baseline |
| one reader cancels | may continue | may continue | other consumers remain valid | consumer partial, not aborted | intended |
| explicit abort during pending read | abort signal | abort signal | reject or settle aborted once | abort once, no normal end | candidate fix |
| explicit abort during delayed tool | already completed model step or aborted provider | abort signal | settle aborted once | no later success claim | conformance case |
| provider error before finish | errors | stop or settle consistently | reject once | error once | conformance case |
| silent close without terminal chunk | closes incompletely | depends on emitted calls | typed incomplete outcome | no false completion | design case |
| resumable client disconnect | continues | continues | run remains active | reconnectable | application architecture |
| explicit resumable Stop | aborts through server channel | abort signal | settle aborted once | durable aborted state | application architecture |

## Boundaries

This follow-up reports evidence and stages an owned-fork candidate. It makes no upstream contact, acceptance claim, or implementation recommendation beyond the owned evaluation campaign.
