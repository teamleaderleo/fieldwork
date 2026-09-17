# T3 OpenCode lifecycle CI run 01

Date: 2026-07-30

Fieldwork workflow run: `30492870269`

Target branch at first execution: `teamleaderleo/t3code:fieldwork/opencode-completion-reconciliation`

## Execution route

The owned T3 fork did not create a check suite for either branch pushes or its draft pull request, even after a focused workflow declared both triggers. The campaign therefore runs T3 tests from the Fieldwork repository, whose GitHub Actions are active, by checking out the public owned T3 branch and executing one test file per matrix job.

This is a CI routing workaround, not evidence that GitHub Actions are definitively disabled on the T3 fork.

## First-run results

### Observed product failures

- Steering prompt requests did not carry caller-generated OpenCode `messageID` values. Initial input and two steering prompts all reached the SDK fake, but none supplied the durable provider-message identity required for exact history recovery.
- An interrupt request naming a stale turn ID succeeded and called OpenCode abort instead of rejecting the mismatched affinity.
- When OpenCode idle arrived during abort, the adapter emitted ordinary `turn.completed: completed` for the interrupted turn.
- A delayed duplicate idle after a new turn started emitted completion for that newer turn and cleared it.
- Status and history reconciliation are not invoked during resumed-session startup; injected status/history failures therefore did not fail recovery.
- A busy status snapshot did not restore the persisted exact active turn.

### Test-harness failures

- Restart tests that waited for absent events used `Effect.timeout` under `@effect/vitest`'s virtual clock and reached Vitest's 60-second wall-clock timeout.
- The duplicate-interrupt test used the same invalid timeout pattern.
- The first integrated reaper test waited for a stale snapshot that was never considered stale under the virtual clock.

These timeout results are not production evidence.

### Existing behavior that passed

- An OpenCode abort transport failure preserved the active local turn and emitted no terminal completion.

## Test review changes after run 01

Target head after harness repair: `54acd60d1506c878911202697652eae8826e1907`

- Replaced virtual-clock absence waits with deterministic event collectors and finite scheduler draining.
- Changed the interrupt contract to accept canonical `turn.aborted` or `turn.completed: interrupted`, while still requiring one exact terminal result and local ready-state cleanup.
- Reduced the reaper test to the check-then-stop interleaving: an idle projection snapshot is materialized, a provider turn becomes active, and the stale stop decision must not kill it.
- Kept the fast observed product failures unchanged.

## Recent precedent incorporated

- T3 issue 4561 and proposed PR 4562 show durable provider status can diverge from projected session state after restart; the proposed repair uses optimistic concurrency through an expected session timestamp.
- T3 issues 4710 and 4795 show unrendered OpenCode skill permissions can survive abort and leave pending approval state that permanently blocks settlement.
- T3 PR 2360 proposes shared orchestration handling for successful interrupt and `turn.aborted`, supporting a split between adapter-local race classification and shared projected-state cleanup.

No upstream contact occurred.
