# Playwright fixture teardown fairness prototype — 2026-07-30

## Decision

Continue the Playwright campaign with fixture teardown fairness as the lead finding.

The original source finding remains high confidence: a custom test-scoped fixture can have its teardown body skipped when the shared after-hooks slot is exhausted, then be deleted before the later worker-cleanup pass receives a fresh slot.

The deeper work now separates three questions:

1. Can never-started teardown bodies be retained safely?
2. Does one fresh shared retry slot provide fair cleanup?
3. Can fairness improve without extending the total worker-cleanup deadline?

No upstream contact occurred.

## Current fork stack

| Layer | Branch | Head | Draft PR | Purpose |
|---|---|---|---|---|
| Narrow retention | `fieldwork/fixture-teardown-resumption-probe` | `c15e66124e5af9d705ce10d95714c3e0a031198f` | `teamleaderleo/playwright#1` | Retain only never-started final-test fixture teardowns and retry them in existing worker cleanup. |
| Fairness invariant | `fieldwork/fixture-teardown-fairness-probe` | `eb3d58e61a8dac699ebd7c2f8c4f9622ecc2d6dd` | `teamleaderleo/playwright#3` | Demonstrate that a slow first deferred fixture can consume the fresh shared slot and starve a later finalizer. |
| Budgeted fairness | `fieldwork/fixture-teardown-budgeted-fairness` | `1f791156928090242d05d42daa420712c4f1f171` | `teamleaderleo/playwright#4` | Divide the existing worker-cleanup budget among fixtures deferred at the start of the pass. |

The stack is rebased cleanly:

- PR #3 is one commit ahead of PR #1 and adds only the fairness invariant.
- PR #4 is one commit ahead of PR #3 and changes only `fixtureRunner.ts` plus the expanded fairness test.

## Layer 1 — narrow retention

PR #1 preserves a fixture record only when all of the following hold:

- scope is test;
- cleanup is the final test cleanup path (`runnable.type === 'test'`);
- the fixture has no dedicated fixture timeout slot;
- the selected shared slot is already exhausted;
- the teardown body has not started.

The fixture remains in `instanceForId` with dependency edges intact. Existing worker cleanup already performs another test-scope teardown pass with a fresh project-timeout slot, so no new cleanup phase is added.

Fixtures whose teardown body starts are still removed in `finally`, preserving the historical duplicate-error rule. Fixtures with explicit or worker fixture slots keep their existing independent-slot behavior. Hook-local fixture scopes are not retained, preserving fresh instances for later `beforeAll` or `afterAll` hooks.

### Status-accounting correction

A cleanup-debt error cannot rely only on `TestInfo._isFailure()` after `test.fail()`:

- the body may fail as expected;
- an `afterEach` timeout or deferred teardown can add runner errors;
- status can remain `failed`, matching expected status `failed`;
- worker replacement would then be suppressed.

The prototype now:

1. avoids appending another cleanup-debt error when the test is already unexpectedly failing;
2. records cleanup debt when the test is not unexpectedly failing;
3. forces status to `timedOut` if expected-failure accounting still reports the test as expected;
4. verifies distinct worker indices and retained fixture finalization across retry.

This is useful for the experiment, but it exposes a broader runner limitation. `WorkerMain.unhandledError` already documents that Playwright lacks a distinct “failed unexpectedly after an expected body failure” status and sometimes stops the worker separately. A final implementation may need an explicit cleanup-debt signal to `WorkerMain` rather than status mutation.

## Layer 2 — fairness invariant

PR #3 creates this sequence:

1. `afterEach` exhausts the original after-hooks slot before fixture teardown starts.
2. Both `blocker` and `sentinel` are retained.
3. Worker cleanup starts with a fresh shared project-timeout slot.
4. `blocker` runs first and consumes that fresh slot.
5. `sentinel` reaches teardown with no shared time remaining.

The invariant requires more than a stdout marker. The sentinel adds an attachment, and the test requires that attachment in each attempt’s result. This proves the teardown body completed before `testEnd`.

That distinction is important because process-level graceful shutdown may attempt retained fixtures after the test result has already been sent. Such late cleanup can still release a browser or process, but attachments and other report mutations arrive too late for the original test result.

Source prediction:

- PR #1 should fail PR #3’s attachment invariant.
- The sentinel may run later during process shutdown, but the report should still lack the attachment.

## Layer 3 — budgeted fairness

PR #4 detects fixtures that were already deferred when worker cleanup begins. It partitions the existing test-fixture cleanup slot dynamically:

```text
allowance = floor(remaining worker-cleanup test budget / deferred fixtures remaining)
```

For each deferred fixture:

1. create a temporary runnable slot using that allowance;
2. run the fixture teardown under the temporary slot;
3. charge actual elapsed time back to the original worker-cleanup slot;
4. carry unused time forward to later fixtures.

The total configured worker-cleanup test-fixture budget is not multiplied by fixture count.

### Example

With 120 ms and three deferred fixtures:

- `blocker` receives 40 ms and times out;
- if it consumes 40 ms, 80 ms remain for two fixtures;
- `sentinelB` receives 40 ms and completes quickly;
- unused time remains available;
- `sentinelA` receives the remaining share and completes.

The expanded test requires both sentinel attachments in teardown order for attempt 0 and retry 1.

## Phase ownership after worker failure

Worker cleanup currently runs:

1. retained test-scoped fixtures under a project-timeout `teardownSlot`;
2. remaining `afterAll` hooks;
3. worker fixtures;
4. trace finalization under a separate project-timeout slot;
5. `testEnd`.

The budgeted prototype partitions the retained test-fixture phase. Trace finalization has a separate slot. Worker fixtures also have fixture-owned slots initialized from the project timeout, so the test-fixture partition does not directly consume their fixture timeout allowance.

The main reporting requirement is therefore to finish useful custom test fixture finalizers before `testEnd`.

## Remaining risks

### 1. Diagnostic meaning

Temporary runnable allowances change the timeout amount shown for a deferred fixture. The number is a scheduler allocation, not a user-configured fixture timeout. Diagnostics should distinguish:

- configured timeout;
- inherited test cleanup timeout;
- fairness allocation during recovery.

### 2. Equal allocation is policy, not truth

Equal sharing is simple but may under-allocate a legitimate expensive finalizer. Alternatives include:

- weighted dependency groups;
- a minimum start allowance plus a shared completion pool;
- fixture metadata indicating cleanup cost or criticality;
- reservation for known artifact finalizers.

### 3. Tiny remaining budgets

`TimeoutManager.isTimeExhaustedFor` treats a 1 ms slot as exhausted because of timer compensation. The prototype only creates a separate allowance when at least 2 ms remain per deferred fixture. With less time, a fixture may still receive no meaningful start opportunity.

### 4. Dependency fairness

Teardown order must remain dependency-safe. Equal fixture shares treat a dependent and its dependency as separate finalizers. A dependency group may deserve one combined reservation so a slow child cannot leave its resource-owning parent without enough cleanup time.

### 5. Status model

Expected-failure tests expose the difference between body expectedness and runner cleanup correctness. A final design should decide whether cleanup debt:

- changes test status;
- adds a separate unexpected-cleanup result bit;
- forces worker replacement without changing pass/fail;
- appears as a report-level error.

### 6. Exact execution remains pending

Fork CI still has not started automatically, and the current environment does not contain an installable JavaScript Playwright Test checkout. All three layers remain source-backed draft experiments rather than executed patches.

## Required execution matrix

Run all three branches with:

```bash
npm ci
npm run ttest -- tests/playwright-test/fixture-teardown-resumption.spec.ts
npm run ttest -- tests/playwright-test/fixture-teardown-fairness.spec.ts
```

Record:

- attempt and worker indices;
- fixture setup and teardown order;
- first teardown start time;
- allocated and consumed cleanup time;
- attachment list at `testEnd`;
- process-level cleanup output after `testEnd`;
- browser/context/process survivors;
- total worker replacement latency;
- timeout messages shown to the user.

Run on Linux, macOS, and Windows.

## Current recommendation

Keep PR #1 as the minimal mechanism repair and PR #3 as its required negative control. Treat PR #4 as the leading scheduler prototype.

Do not promote PR #4 as a final patch until exact execution answers these questions:

1. Do all intended attachments arrive before `testEnd`?
2. Does total worker-cleanup duration remain bounded by the existing slot?
3. Are timeout diagnostics understandable?
4. Do dependency chains finalize in safe order?
5. Does expected-failure reporting remain correct?

The campaign has moved from a speculative retry idea to a concrete fairness experiment with a bounded intervention and explicit reporting invariants.
