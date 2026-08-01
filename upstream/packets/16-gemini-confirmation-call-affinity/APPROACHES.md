# Approaches — Unit 16 confirmation modification call affinity

## In simple words

The selected direction keeps authority inside the confirmation loop: resolve the exact call ID, validate the current approval generation before and after asynchronous modification, rebuild from the revalidated call, and update that same ID. The current-main candidate also proves ordering through two real scheduler calls waiting simultaneously and responses delivered in reverse order.

Alternatives either preserve insertion-order ambiguity, widen the state API before evidence requires it, or weaken stale-authority protection.

## Decision criteria

1. One confirmation generation owns response, modifier input, rebuild tool, and state update.
2. Two simultaneous approvals remain isolated under reverse response order.
3. Authority loss during asynchronous work fails before publication.
4. Public APIs and existing confirmation behavior stay compatible.
5. The source diff remains narrow, reviewable, and platform-neutral.

## Selected approach

### Exact-ID lookup with pre/post-await generation fence

- Design: derive `callId` from the validating call; fetch a waiting call by that ID; pass it to the modifier; after await, fetch again and require `AwaitingApproval` plus object identity; rebuild from the revalidated call and update the same ID.
- Owning boundary: private confirmation modification helpers.
- Current source: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`, one commit over current base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`.
- Evidence: predecessor run `30595253180` passed 14/14; current-main real scheduler control is committed and run `30691280000` owns execution.
- Advantages: closes wrong-call and stale-generation paths without a public API or state-manager change.
- Costs and risks: introduces thrown stale-authority errors; uses state-object identity as the generation discriminator.
- Remaining controls: current-main focused/integration execution, core typecheck, full preflight, independent review.

## Viable alternatives

### Explicit approval-generation token

- Design: add a version/token to waiting state and compare it after modification.
- Why plausible: states the invariant directly and survives benign object reconstruction.
- Improvement: explicit compare-and-swap semantics.
- Widening: state types, transitions, publication, tests, and migration reasoning.
- Discriminator: evidence that same-generation waiting calls are legitimately reconstructed as new objects.
- Reopening trigger: scheduler refactor makes object identity unstable.

### State-manager guarded update

- Design: add `updateArgsIfAwaiting(callId, generation, ...)` and combine the final check with the update.
- Why plausible: centralizes race protection.
- Improvement: stronger atomicity if state mutation can interleave synchronously around `updateArgs`.
- Widening: state-manager API and additional caller contracts.
- Discriminator: a demonstrated interleave between the post-await read and synchronous update.
- Reopening trigger: scheduler state updates gain asynchronous hooks or multi-threaded ownership.

## Executed losing approaches

### `state.firstActiveCall` as authority

- Exact source/evidence: public base `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`; evidence PR #2 head `a7f5cc934446849e19a08cc8f4527473ada74401`.
- What ran: focused target-native inline affinity test and core typecheck.
- Result: modifier received `call-a` while response correlation owned `call-b`.
- Why it lost: insertion order carries no confirmation authority.
- Retained value: deterministic baseline failure.

### Exact-ID lookup only before the modifier

- Exact head: `0ffa264696cb7dd422ee0596518fd2f1194b529d`.
- What ran: focused controls; adjacent suite exposed a separate stale fixture.
- Result: initial mismatch closed, but cancellation/replacement during the modifier await could still publish stale arguments.
- Why it lost: authority was assumed to survive asynchronous work.
- Retained value: established the correct initial lookup boundary.

### Pre/post status check without generation identity

- Exact head family: `c707e267ae2053195646f00f495c159484fc6c15`.
- What ran: five focused controls, eight adjacent controls, build, typecheck, formatting, and lint.
- Result: green, then complete-diff review found same-ID approval replacement.
- Why it lost: a new `AwaitingApproval` object under the same ID could accept stale modifier output.
- Retained value: selected approach plus one identity fence.

### Transiently generate the integration test inside the publisher

- Exact carrier: PR #6 head `12e096c7672c86fd45d45f87c6a3324347559d11`; run `30690542009`.
- What ran: dependency install, source restore, test generation, Prettier, pre-commit lint.
- Result: ESLint rejected two unused declarations before product tests.
- Why it lost: transient generation created an avoidable harness surface and obscured the immutable candidate.
- Retained value: exact lint classification and corrected test requirements.

### Keep source generation inside execution carriers

- Exact fallback: PR #22 head `e41dd92ab680f5eb05370bf7d5263a70f6897e34`.
- Result: runner queue only; superseded before execution.
- Why it lost: the source can be materialized and reviewed directly.
- Retained value: immutable corrected integration-test head `6804d0b87c196b265c42276f2939573edaf6d89c`.

## Source composition approach

The corrected test branch accumulated the exact four-file diff over current base. Internal PR #23 then squash-merged those four commits onto `repair/16-confirmation-call-affinity-current-main`, producing one source commit `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`. The canonical branch and clean review PR #24 now point to that commit. Execution carrier #6 checks out the immutable source directly.

This separates:

- source identity;
- execution machinery;
- packet documentation;
- eventual public issue/PR authority.

## Rejected easy answers

### Build from the original validating call

- Temptation: keep `toolCall.tool.build` after selecting the current waiting call.
- Problem: the current waiting generation is the authority after the await.
- Control: candidate rebuilds from the revalidated waiting call.

### Fall back to another active call when the target disappears

- Temptation: preserve progress.
- Problem: recreates cross-call mutation.
- Control: missing target and status-loss cases require zero publication.

### Relax the waiting-status requirement

- Temptation: allow updates after scheduler advancement.
- Problem: modified arguments belong to an approval decision and lose authority after cancellation/execution.
- Control: editor status-loss case rejects.

### Merge the change into the owned fork's main branch before validation

- Temptation: obtain a single commit quickly.
- Problem: obscures the clean public-base relationship.
- Decision: maintain a dedicated current-main repair branch and canonical source branch.

## Prior work

| Link | Approach | Status | Relationship |
| --- | --- | --- | --- |
| [Fieldwork PR #45](https://github.com/teamleaderleo/fieldwork/pull/45) | source survey and repair sketch | merged research | origin of exact-ID direction |
| [Evidence PR #2](https://github.com/teamleaderleo/gemini-cli/pull/2) | baseline target-native reproduction | closed | proves inline mechanism |
| [Carrier PR #6](https://github.com/teamleaderleo/gemini-cli/pull/6) | execution and publication history | open draft | active immutable-source validation |
| [Source composition PR #23](https://github.com/teamleaderleo/gemini-cli/pull/23) | squash four-file current-main candidate | merged owned-fork PR | creates exact source head |
| [Clean source PR #24](https://github.com/teamleaderleo/gemini-cli/pull/24) | workflow-free review surface | open draft | canonical exact-head review |
| [Fallback PR #22](https://github.com/teamleaderleo/gemini-cli/pull/22) | corrected transient publisher | closed superseded | retains queue/provenance record |
| [Portfolio PR #269](https://github.com/teamleaderleo/fieldwork/pull/269) | current-owner map | open draft | records generation gap and adjacent editor work |
| Public searches, 2026-08-01 | no equivalent issue/PR/commit found | read-only | no replacement found |

## Deferred adjacent work

- external-editor lifetime versus edit-session completion
- waiting-indicator aggregation
- generic compare-and-swap state APIs
- durable approval receipts across resume
- end-to-end UI presentation

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | base `3499c84...`, PR #2 | reject `firstActiveCall` authority | exact wrong-call failure | upstream replacement |
| 2026-07-30 | head `0ffa264...` | require post-await revalidation | modifier awaits can outlive authority | modifier becomes synchronous |
| 2026-07-31 | head `c707e267...` | require generation identity | same-ID replacement remained | explicit token added |
| 2026-07-31 | head `b359ece8...`, run `30595253180` | retain exact-ID plus identity fence | 14/14 green | integration contradicts it |
| 2026-08-01 | run `30690542009` | stop transient test generation | pre-test lint failure | none; corrected test committed |
| 2026-08-01 | source `0c3a86b...` | select immutable four-file candidate | one clean commit on current main with real scheduler test | current execution or review rejects it |
