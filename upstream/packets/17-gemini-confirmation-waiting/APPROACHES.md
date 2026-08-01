# Approaches — confirmation waiting ownership

## Chosen approach

Combine call-scoped guaranteed cleanup with scheduler-scoped counted aggregation.

1. Wrap the existing confirmation wait in `waitForConfirmationWithState`.
2. Attempt the clear callback on every settled path.
3. Preserve a primary wait error over a secondary cleanup error.
4. Add `ConfirmationWaitTracker` to the scheduler.
5. Emit the external boolean only on count transitions `0 -> 1` and `1 -> 0`.
6. Pass the tracker to both current `resolveConfirmation` call sites.

Why this approach:

- repairs the target-executed abort leak;
- covers ordinary wait failures and callback failures;
- preserves the public callback type;
- handles overlap without changing downstream consumers;
- keeps the source diff to three production files and three focused tests.

## Approach considered: bare `try/finally`

Sketch:

```ts
onWaitingForConfirmation?.(true);
try {
  return await waitForConfirmation(...);
} finally {
  onWaitingForConfirmation?.(false);
}
```

Useful property: balances one call when the wait rejects.

Reason rejected as the complete repair: two overlapping calls can still emit `true, true, false` while one wait remains active. The retained deterministic probe demonstrates this exact state.

## Approach considered: change the callback to a pending count

Sketch:

```ts
onWaitingForConfirmation?.(pendingCount);
```

Useful property: the callback itself carries complete aggregate state.

Reason deferred: it changes the public scheduler option contract and all consumers for a narrow lifecycle bug. The scheduler can preserve the existing boolean API and aggregate internally.

## Approach considered: make the callback call-scoped

Sketch:

```ts
onWaitingForConfirmation?.({ callId, waiting });
```

Useful property: downstream owners can aggregate by identity and diagnose unmatched transitions.

Reason deferred: it expands the callback contract and leaks scheduler call identity into consumers that only need global waiting state. A counted scheduler owner is sufficient for this unit.

## Approach considered: track active call IDs in a `Set`

Useful property: duplicate enter/leave events can be tied to a concrete call.

Reason deferred: `resolveConfirmation` currently receives a callback without call identity, and the scheduler already controls balanced invocation of the helper. A count gives the required global invariant with a smaller patch. A future need for per-call diagnostics could justify a set.

## Approach considered: swallow all clear-callback errors

Useful property: a monitoring callback cannot fail the confirmation operation.

Reason rejected: callback failures remain observable on the success path today. Silently swallowing them would change behavior and hide a broken deadline owner. The chosen precedence preserves the primary wait error only when two failures compete.

## Approach considered: let cleanup replace the primary wait error

Useful property: ordinary `finally` semantics are simple.

Reason rejected: an observer failure could replace the cancellation or confirmation failure that actually terminated the operation. The selected helper logs the cleanup failure and rethrows the original wait error.

## Approach considered: mutate one scheduler call site only

Reason rejected: current public head `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` has two `resolveConfirmation` call sites. The publication transform requires exactly two replacements and fails if current source drifts from that fence.

## Approach considered: publish the staged workflow diff

Reason rejected: PR [`gemini-cli#7`](https://github.com/teamleaderleo/gemini-cli/pull/7) stores the repair as an execution transform plus tests. Workflow files are evidence carriers, not product source. The clean branch contains only the six target files.

## Publication approaches and failures

### PR #8 first publication run

Carrier head: `ccd85e92c267109294e5596f9a8f16813c838bfd`  
Run: [`30594684917`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30594684917)  
Job: [`91044377734`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30594684917/job/91044377734)

The transform and Prettier completed. The file fence used `git diff --name-only "$UPSTREAM_HEAD"`, which listed only the two modified tracked files and omitted four new untracked files. Tests and publication were skipped.

Classification: carrier defect. The product transform had reached all six intended paths.

### Current publication repair

Carrier head: `893749cc087fec170956c4f439f36ee1c1888aff`  
Run: [`30674864738`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30674864738)

Changes to the carrier only:

- base pinned through immutable branch `fieldwork/upstream-f47-waiting-ownership-base`;
- current exact public base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`;
- stage all six files before comparing `git diff --cached --name-only`;
- publish to `fix/scheduler-confirmation-waiting-ownership`;
- run the 16 focused controls and core typecheck on the committed source tree.

## Rejected scope expansions

- changing confirmation policy behavior;
- terminating the bus wait when IDE confirmation rejects;
- solving confirmation modification call affinity from unit 16;
- changing scheduler queue concurrency;
- changing `DeadlineTimer` pause/resume behavior;
- adding UI state or telemetry;
- touching public upstream before authorization.
