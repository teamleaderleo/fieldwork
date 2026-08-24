# Approaches — Unit 16 confirmation modification call affinity

## In simple words

The selected direction keeps authority inside the confirmation loop: resolve the exact call ID, validate the current approval generation before and after asynchronous modification, rebuild from the revalidated call, and update that same ID. The final candidate also proves ordering through two real scheduler calls waiting simultaneously and responses delivered in reverse order.

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
- Final source: `b6d8e8bb6160aec16555647d81d46a694e44b58b`, one commit over base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`.
- Evidence: final run `30692554758` passed 15/15, posttest build, core typecheck, changed-file lint, exact fence, clean tree, and publication.
- Advantages: closes wrong-call and stale-generation paths without a public API or state-manager change.
- Costs and risks: introduces thrown stale-authority errors and uses state-object identity as the generation discriminator.
- Remaining controls: eligible independent review and maintainer feedback through issue-first discussion.

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
- Improvement: stronger atomicity if state mutation can interleave around `updateArgs`.
- Widening: state-manager API and additional caller contracts.
- Discriminator: a demonstrated interleave between the post-await read and synchronous update.
- Reopening trigger: state updates gain asynchronous hooks or multi-threaded ownership.

## Executed losing approaches

### `state.firstActiveCall` as authority

- Evidence: PR #2, head `a7f5cc934446849e19a08cc8f4527473ada74401`, run `30505534210`.
- Result: modifier received `call-a` while response correlation owned `call-b`.
- Why it lost: insertion order carries no response authority.

### Exact-ID lookup only before the modifier

- Head: `0ffa264696cb7dd422ee0596518fd2f1194b529d`.
- Result: initial mismatch closed, while authority could still change during the modifier await.
- Why it lost: asynchronous work can outlive approval ownership.

### Pre/post status check without generation identity

- Head family: `c707e267ae2053195646f00f495c159484fc6c15`.
- Result: focused and adjacent controls passed; complete-diff review found same-ID approval replacement.
- Why it lost: a new waiting generation under the same ID could accept stale output.

### Transiently generate the integration test inside the publisher

- Carrier/run: PR #6, `30690542009`.
- Result: unused declarations failed pre-commit lint before product tests.
- Why it lost: transient generation created avoidable harness drift.
- Retained value: corrected integration-test requirements.

### Initial current-main source `0c3a86b...`

- Result history: reverse-order behavior passed after formatting normalization; posttest exposed incomplete response fixture fields.
- Why it lost: test fixture typing was incomplete.
- Retained value: final source adds explicit `resultDisplay`, `error`, and `errorType` fields.

## Final source composition

The execution carrier corrected the scheduler fixture, normalized all four files, reset to the exact public base, and created one clean commit. Final source:

- head: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- parent: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- branch: `fix/scheduler-confirmation-call-affinity`
- clean PR: #24
- exact fence: four scheduler source/test files

This separates source identity, execution machinery, packet documentation, and eventual public authority.

## Rejected easy answers

### Build from the original validating call

The current waiting generation is the authority after the await. The final candidate rebuilds from the revalidated waiting call.

### Fall back to another active call when the target disappears

Fallback recreates cross-call mutation. Missing target and status-loss cases require zero publication.

### Relax the waiting-status requirement

Modified arguments belong to an approval decision and lose authority after cancellation or execution.

### Fold the unrelated workflow lint fix into unit 16

The unchanged base reproduces `.github/workflows/pr-size-labeler-batch-run.yml` shellcheck `SC2031`. Adding that repair would widen the unit beyond its assigned scope.

## Prior work

| Link | Approach | Status | Relationship |
| --- | --- | --- | --- |
| [Fieldwork PR #45](https://github.com/teamleaderleo/fieldwork/pull/45) | source survey and repair sketch | merged | origin of exact-ID direction |
| [Evidence PR #2](https://github.com/teamleaderleo/gemini-cli/pull/2) | baseline reproduction | closed | proves inline mechanism |
| [Carrier PR #6](https://github.com/teamleaderleo/gemini-cli/pull/6) | execution and publication history | closed complete | owns final receipts |
| [Source PR #24](https://github.com/teamleaderleo/gemini-cli/pull/24) | workflow-free review surface | open draft | canonical review head |
| [Fallback PR #22](https://github.com/teamleaderleo/gemini-cli/pull/22) | corrected transient publisher | closed superseded | provenance only |
| Public searches, 2026-08-01 | no equivalent issue/PR/commit found | read-only | repeat before filing |

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
| 2026-07-31 | head `b359ece8...` | retain exact-ID plus identity fence | 14/14 green | integration contradiction |
| 2026-08-01 | runs `30690542009`–`30692147133` | correct harness, formatting, and fixture typing | classified failures isolated each issue | none |
| 2026-08-01 | head `b6d8e8bb...`, run `30692554758` | select final candidate and issue-first route | 15/15 and all candidate gates green; baseline preflight blocker confirmed | independent review or maintainer preference |
