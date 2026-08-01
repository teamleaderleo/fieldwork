# Approaches — Unit 16 confirmation modification call affinity

## In simple words

The leading direction keeps authority inside the confirmation loop: resolve the exact call ID, validate the current approval generation before and after asynchronous modification, then rebuild and update that same call. Alternatives either preserve insertion-order ambiguity, widen the scheduler state API before evidence requires it, or weaken stale-authority protection.

## Decision criteria

1. One confirmation generation owns response, modifier input, rebuild tool, and state update.
2. The change preserves public APIs and existing confirmation behavior.
3. Authority loss during asynchronous work fails before publishing arguments.
4. The diff remains narrow and reviewable.
5. The design adds negligible runtime cost and stays platform-neutral.

## Selected approach

### Exact-ID lookup with pre/post-await generation fence

- Design: derive `callId` from the validating call; fetch a waiting call by that ID; pass it to the modifier; after await, fetch again and require `AwaitingApproval` plus object identity; rebuild from the revalidated call and update the same ID.
- Owning boundary: private confirmation modification helpers.
- Evidence: clean head `b359ece8a2bd059aef870a084ab9494eff16fa8f`, run `30595253180`, 14/14 tests.
- Advantages: closes both wrong-call and stale-generation paths without a public API change.
- Costs and risks: introduces thrown stale-authority errors; relies on state-object replacement as the generation discriminator.
- Remaining controls: real two-call out-of-order scheduler test, current-main rebase, full preflight.

## Viable alternatives

### Explicit approval generation token

- Design: add a generation/version token to waiting state and compare it after modification.
- Why it remains plausible: expresses the invariant directly and survives benign object replacement.
- What it would improve: clearer compare-and-swap semantics.
- What it would widen or complicate: state types, transitions, serialization/publication, tests, and migration reasoning.
- Exact discriminator: evidence that same-generation waiting calls are legitimately reconstructed as new objects.
- Reopening trigger: a current or planned scheduler refactor makes object identity unstable.

### State-manager guarded update

- Design: add an `updateArgsIfAwaiting(callId, generation, ...)` method that performs the final check and update atomically.
- Why it remains plausible: centralizes race protection.
- What it would improve: stronger atomicity if state mutation can interleave synchronously around `updateArgs`.
- What it would widen or complicate: public/internal state-manager API and callers outside confirmation.
- Exact discriminator: a demonstrated synchronous interleaving between the post-await read and update.
- Reopening trigger: scheduler execution becomes multi-threaded or state updates gain asynchronous hooks.

## Executed losing approaches

### Use `state.firstActiveCall`

- Exact branch, patch, or commit: public base `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`; evidence PR #2 head `a7f5cc934446849e19a08cc8f4527473ada74401`.
- What ran: focused target-native inline affinity test and core typecheck.
- Result: modifier received `call-a` while confirmation correlation owned `call-b`.
- Why it lost: insertion order carries no confirmation authority.
- Useful evidence retained: exact baseline failure and deterministic harness.

### Exact-ID lookup only before the modifier

- Exact branch, patch, or commit: carrier review head `0ffa264696cb7dd422ee0596518fd2f1194b529d`.
- What ran: focused controls; adjacent suite exposed a separate stale fixture.
- Result: first authority mismatch closed, but review found that cancellation/replacement during the modifier await could still publish stale arguments.
- Why it lost: authority was validated before asynchronous work and assumed afterward.
- Useful evidence retained: established the correct initial lookup boundary.

### Exact-ID pre/post status check without generation identity

- Exact branch, patch, or commit: clean publication before final replacement control, including `c707e267ae2053195646f00f495c159484fc6c15`.
- What ran: five focused controls plus eight adjacent controls, build, typecheck, formatting, and lint.
- Result: green, then complete-diff review identified same-ID waiting-generation replacement.
- Why it lost: a new `AwaitingApproval` object under the same ID could accept stale modifier output.
- Useful evidence retained: current selected approach plus one additional identity fence.

## Rejected easy answers

### Build from the original validating call

- Temptation: keep `toolCall.tool.build` after selecting the correct call for the modifier.
- Why it is incomplete or unsafe: the current waiting generation is the authority after the await; rebuilding from a captured object weakens that ownership chain.
- Negative control or source fact: the candidate's post-await check deliberately rebuilds from the revalidated waiting call.

### Fall back to another active call when the target disappears

- Temptation: preserve workflow continuity.
- Why it is incomplete or unsafe: it recreates the original cross-call mutation defect.
- Negative control or source fact: missing target and status-loss tests require zero modifier/update activity or zero `updateArgs`.

### Relax the status requirement

- Temptation: allow updates after the scheduler advances the call.
- Why it is incomplete or unsafe: modified arguments belong to an approval decision; publishing them after cancellation/execution changes authority.
- Negative control or source fact: editor status-loss control rejects and records zero updates.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [Fieldwork PR #45](https://github.com/teamleaderleo/fieldwork/pull/45) | source survey and repair sketch | merged research | origin of narrow exact-ID direction |
| [Evidence PR #2](https://github.com/teamleaderleo/gemini-cli/pull/2) | target-native baseline reproduction | closed | proves inline mechanism |
| [Production carrier PR #6](https://github.com/teamleaderleo/gemini-cli/pull/6) | repair, execution, clean publisher | open draft | owns full history and temporary workflow |
| [Portfolio PR #269](https://github.com/teamleaderleo/fieldwork/pull/269) | comparison and current-owner map | open draft | records replacement-generation gap and routes editor lifetime as integration work |
| Public upstream searches on 2026-08-01 | no equivalent issue/PR/commit found | current read-only search | no replacement found |

## Deferred adjacent work

- Two simultaneous real scheduler approval loops — required as an acceptance gate, kept out of the narrow source implementation.
- External-editor lifetime versus edit-session completion — may expose further lifecycle policy, separate from call identity.
- Waiting indicator aggregation — owned by the waiting-state unit.
- Generic compare-and-swap state APIs — deferred until another caller needs them.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | base `3499c84...`, PR #2 evidence | reject `firstActiveCall` authority | target-native mismatch | upstream replacement |
| 2026-07-30 | review head `0ffa264...` | require post-await revalidation | modifier awaits can outlive authority | modifier becomes synchronous |
| 2026-07-31 | clean head `c707e267...` | require generation identity | same-ID waiting replacement remained | explicit generation token added |
| 2026-07-31 | head `b359ece8...`, run `30595253180` | retain exact-ID plus object-identity fence | six focused and eight adjacent tests green | real integration or current-main evidence contradicts it |
| 2026-08-01 | public head `f47d6c6...` | disposition `REPAIR` | base drift, parallel test, and preflight remain | all three gates clear on one head |
