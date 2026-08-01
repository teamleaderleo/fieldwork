# Deep dive — confirmation waiting ownership

## Contract under review

`Scheduler` accepts an optional `onWaitingForConfirmation(waiting: boolean)` callback. The callback was introduced by upstream PR [`#18415`](https://github.com/google-gemini/gemini-cli/pull/18415) so `LocalAgentExecutor` can pause and resume a deadline timer while a subagent waits for human approval.

That callback is an ownership signal. Every successful transition to waiting needs one later transition out, and a global boolean needs to stay true while any owned wait remains active.

## Current source behavior

At public head `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`, `resolveConfirmation` performs this sequence:

1. call `onWaitingForConfirmation?.(true)`;
2. await the bus/IDE confirmation race;
3. call `onWaitingForConfirmation?.(false)`.

The final callback sits after the rejecting `await`. Abort, iterator failure, state lookup failure, or another thrown wait error skips it.

Exact current file:

- [`confirmation.ts@f47d6c6f`](https://github.com/google-gemini/gemini-cli/blob/f47d6c6f7a1308d81f9f57acf7d279f0928c5249/packages/core/src/scheduler/confirmation.ts)

The current scheduler passes the same callback directly at two `resolveConfirmation` call sites:

- [`scheduler.ts@f47d6c6f`](https://github.com/google-gemini/gemini-cli/blob/f47d6c6f7a1308d81f9f57acf7d279f0928c5249/packages/core/src/scheduler/scheduler.ts)

## Failure 1: rejected waits leak waiting ownership

The retained negative case starts a real confirmation wait, observes the `true` callback, aborts the wait, and expects balanced transitions.

Current result:

```text
expected [ true ] to deeply equal [ true, false ]
```

The assertion ran in target-native Vitest at exact candidate head `974f6e288bf3e86af0c06cb445b9626bd5d2280f`. The carrier required this predicted failure and then passed core typecheck.

Consequence: the deadline owner can remain paused after the confirmation operation has already terminated.

## Failure 2: direct per-call booleans lose overlapping ownership

A bare `try/finally` repairs the single rejected wait, yet direct per-call boolean callbacks still produce this legal overlap sequence:

```text
wait A enters  -> true
wait B enters  -> true
wait A leaves  -> false
```

At that point wait B remains active while the consumer sees `false`.

The retained deterministic prior-art probe records:

```json
{
  "transitions": [true, true, false],
  "pendingApprovalsAfterFirstResolution": 1,
  "reportedWaiting": false
}
```

Artifacts:

- [`expanded_lifecycle_probe.mjs`](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/expanded_lifecycle_probe.mjs)
- [`expanded_lifecycle_probe-output.json`](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/artifacts/expanded_lifecycle_probe-output.json)

## Selected repair

### Call-scoped cleanup helper

`waitForConfirmationWithState` owns one enter/leave pair around the existing confirmation wait.

Required behavior:

- call `true` before waiting;
- capture the primary wait result or error;
- always attempt `false` after the wait settles;
- after a failed wait, preserve the primary wait error if cleanup also throws and log the cleanup error;
- after a successful wait, let a cleanup callback error remain observable;
- return the original confirmation result after successful cleanup.

This keeps cancellation and wait failures authoritative while avoiding silent callback failures.

### Scheduler-level counted owner

`ConfirmationWaitTracker` maintains an active-wait count and exposes `update(waiting)`.

Transitions:

- `true` at count zero: emit external `true`, then record the first active wait;
- additional `true`: increment without another external transition;
- `false`: reject an unmatched clear, decrement, and emit external `false` only when the count reaches zero;
- if the initial external `true` callback throws, leave the count at zero;
- if the final external `false` callback throws, the completed wait remains removed, so internal ownership stays accurate.

The scheduler owns one tracker instance and passes `tracker.update` at both current confirmation call sites.

## IDE confirmation semantics on the current head

`waitForConfirmation` races bus confirmation with an optional IDE confirmation promise. At `f47d6c6f…`, IDE rejection is logged and the bus remains the surviving owner. The current-head repair test therefore verifies that IDE rejection alone does not leave the waiting state; the bus response later completes the call and produces the final clear.

This differs from an earlier staged assumption that IDE rejection should terminate the whole wait. The exact-head workflow corrected the test to match current source semantics before publication.

## Error precedence

| Wait result | Clear callback result | Observable result |
| --- | --- | --- |
| success | success | original confirmation result |
| failure | success | original wait error |
| failure | failure | original wait error; cleanup error logged |
| success | failure | cleanup error |

This avoids replacing an abort or bus failure with a secondary observer failure.

## Exact source fence

Production:

1. `confirmation-wait-tracker.ts`
2. `confirmation.ts`
3. `scheduler.ts`

Tests:

1. `confirmation-wait-tracker.test.ts`
2. `confirmation.waiting-state.repair.test.ts`
3. `confirmation.waiting-state.test.ts`

The clean candidate has no Fieldwork workflow files.

## Current-head reconciliation

The original test-only and staged work used base `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`.

Current public head `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` is five commits ahead. One intervening source change touches `scheduler.ts` and leaves two confirmation call sites. `confirmation.ts` still contains the leak-prone callback sequence. The materialization workflow changed the scheduler replacement fence from one call site to two and updated the IDE-rejection test semantics.

## Prior-art classification

- [`#18415`](https://github.com/google-gemini/gemini-cli/pull/18415): merged origin of the callback and deadline-timer use. Its scheduler test verifies callback plumbing, not rejected-wait cleanup or overlap aggregation.
- [`gemini-cli#3`](https://github.com/teamleaderleo/gemini-cli/pull/3): canonical test-only negative case.
- [`gemini-cli#5`](https://github.com/teamleaderleo/gemini-cli/pull/5): completed exact-head negative execution carrier.
- [`gemini-cli#7`](https://github.com/teamleaderleo/gemini-cli/pull/7): staged repair, controls, and typed 16/16 receipt.
- [`gemini-cli#8`](https://github.com/teamleaderleo/gemini-cli/pull/8): source publication carrier and current-head test receipt.
- Public issue/PR search on 2026-08-01 found adjacent confirmation, IDE, and parallel-tool reports, but no exact published repair for balanced callback cleanup plus counted overlap ownership.

## Scope boundary

This unit changes waiting-state ownership only. It does not change:

- confirmation policy decisions;
- correlation or modification call affinity;
- message-bus request/response formats;
- IDE fallback policy;
- deadline timer implementation;
- scheduler queue ordering;
- UI rendering;
- public callback type.
