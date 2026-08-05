# Playwright fixture teardown deep dive — 2026-07-30

## Status

This is the strongest finding from the Playwright execution, isolation, teardown, and artifact scout.

Confidence is split deliberately:

- **source mechanism: high** — the skip-and-delete path is explicit in `Fixture.teardown`, and worker cleanup can only revisit fixtures still present in `instanceForId`;
- **campaign value: high** — the mechanism can suppress independent cleanup callbacks and attachments across retries;
- **prototype confidence: medium** — the narrow repair has a coherent source diff and a four-case test matrix, but exact JavaScript runner execution is still pending;
- **complete solution confidence: low** — a stacked fairness probe shows that one fresh shared cleanup slot can be exhausted again.

No upstream contact occurred.

## Revisions and retained work

| Item | Value |
|---|---|
| Fork | `teamleaderleo/playwright` |
| Fork base used for the prototype | `beaf223604b5c199b25287cd3c66bb8a9801a30c` |
| Narrow prototype branch | `fieldwork/fixture-teardown-resumption-probe` |
| Narrow prototype head | `12f673e214df7e2d774ae9f908ff501634aee8ba` |
| Narrow prototype PR | `teamleaderleo/playwright#1` |
| Fairness probe branch | `fieldwork/fixture-teardown-fairness-probe` |
| Fairness probe head | `2f9e182b797a355bec8c151916c255f23070a635` |
| Fairness probe PR | `teamleaderleo/playwright#3`, stacked on PR #1 |

Both PRs are drafts inside the fork. Neither is intended for upstream submission.

## Exact mechanism

### Normal ownership

1. Test-scoped fixtures are inserted into `FixtureRunner.instanceForId` during setup.
2. Fixtures without an explicit timeout use the runnable slot. During final test cleanup, that is the shared after-hooks slot.
3. `teardownScope('test')` collects fixtures in dependency-safe teardown order.
4. Each fixture calls `Fixture.teardown`.
5. Worker cleanup later creates a fresh project-timeout slot and calls `teardownScope('test')` again before worker fixtures are torn down.

### Loss path

1. A peer fixture or `afterEach` consumes the shared after-hooks slot.
2. A later test-scoped fixture reaches `Fixture.teardown` with no time remaining.
3. Its teardown body is not started. This avoids an immediate cascade of timeout errors.
4. The `finally` block still removes dependency links and deletes the fixture from `instanceForId`.
5. The test is already failing, so the worker enters its full cleanup pass with a fresh slot.
6. The skipped fixture is absent from `instanceForId`, so worker cleanup cannot collect or retry it.
7. Any user cleanup callback, manual context close, attachment, marker, or other finalizer in that fixture body never runs.

The important distinction is **never started** versus **started and failed**. Existing code treats both as permanently removed.

## Why the distinction is compatible with runner history

### Attempted teardown must still be removed

A 2022 runner fix made fixture removal unconditional after a teardown attempt to avoid reporting the same teardown error once during the test and again during worker cleanup. The narrow prototype preserves this: once `_runWithTimeout` starts the teardown, the fixture is removed even if the attempt times out or throws.

### Dedicated fixture slots must remain independent

A 2024 runner fix established that a fixture with its own timeout slot can still tear down after a test or `afterEach` timeout. The narrow prototype preserves this. A fixture whose dedicated slot is itself exhausted remains on the existing force-cleanup path because a fresh runnable slot cannot replenish that dedicated slot.

### Hook-local fixture scopes must not be retained

`beforeAll` and `afterAll` processing can continue to later hooks after one hook fails. Retaining a skipped test-scoped fixture from one hook would let the next hook reuse stale state. The prototype therefore retains fixtures only when `runnable.type === 'test'`, which covers final test cleanup and the immediate worker cleanup retry, not per-hook fixture scopes.

## Narrow prototype

PR #1 changes the following behaviour:

1. `Fixture.teardown` reports whether teardown completed or was deferred.
2. A fixture is deferred only when all of these are true:
   - it is in final test cleanup;
   - teardown never started;
   - it has no dedicated fixture slot;
   - the shared runnable slot is exhausted.
3. Deferred fixtures remain in `instanceForId` with dependency links intact.
4. `testScopeClean` reflects whether test-scoped fixtures actually remain.
5. If no earlier timeout error already failed the test, a `TimeoutManagerError` is recorded through `TestInfo._failWithError` so the worker is replaced and full cleanup runs.
6. Worker cleanup's existing fresh test teardown pass can collect the deferred fixtures.

### Expected cost

The narrow prototype does not add a new cleanup phase or a new timeout. It uses the existing worker-cleanup pass and its existing project-timeout slot. Retained fixture records live only until that immediate pass in the failure path.

## Test matrix in PR #1

### 1. Peer fixture consumes the shared slot

Setup order makes `blocker` tear down before `sentinel`. `blocker` starts and times out. `sentinel` is deferred and then retried during worker cleanup.

Assertions:

- sentinel marker appears on attempt 0 and retry 1;
- retries use distinct worker indices;
- sentinel attachments are present in both test result attempts, proving the callback ran before `testEnd`.

### 2. Timed-out dependent fixture

A `blocker` depends on `root`, and an independent `sentinel` is also present. The blocker times out first. Both `root` and `sentinel` must be retained and finalized in worker cleanup.

This checks dependency-link preservation and independent cleanup.

### 3. `afterEach` consumes the slot

The test body passes, but `afterEach` times out before fixture teardown begins. A quick sentinel fixture must still finalize on both attempts after worker replacement.

This covers the case where no fixture teardown consumed the original slot.

### 4. Consecutive `afterAll` hooks

The first `afterAll` times out while using a test-scoped fixture. The second `afterAll` must receive a new fixture instance rather than a retained stale one.

This guards the prototype boundary around hook-local fixture scopes.

## Residual fairness failure

PR #3 adds a stacked invariant that the narrow prototype does not satisfy:

1. `afterEach` exhausts the original shared slot before any fixture teardown starts.
2. Both `blocker` and `sentinel` are deferred.
3. Worker cleanup begins with one fresh shared slot.
4. The first deferred fixture, `blocker`, starts and consumes that fresh slot.
5. `sentinel` reaches teardown with no time remaining again.

The source-level prediction is that the sentinel still never gets a cleanup opportunity.

This means the complete finding is broader than “retry once.” It is a **cleanup fairness and accounting problem**: a serial list of independent finalizers shares one budget, and an earlier finalizer can prevent later finalizers from starting in both normal and fallback cleanup.

## Artifact and browser implications

The fixture runner does not know what a user fixture owns. A skipped callback may contain:

- `BrowserContext.close()`, which is needed to finalize context-owned videos;
- manual trace stop/export;
- screenshot or diagnostic collection;
- temporary profile or server cleanup;
- `testInfo.attach()` calls;
- user marker files used by CI orchestration;
- shutdown of a child process or local service.

Built-in fixtures often have dedicated slots or other runner integration, so this finding is strongest for custom test-scoped fixtures and wrappers that place finalization in fixture code.

## Solution policies to compare

### Policy A — one existing worker-cleanup retry

This is PR #1.

Advantages:

- minimal code change;
- no extra timeout phase;
- preserves attempted-fixture removal and hook isolation;
- recovers common cases where the original blocker has already been removed.

Limit:

- another slow deferred fixture can starve later fixtures again.

### Policy B — dedicated bounded allowance per deferred fixture

Each deferred fixture receives a fresh small slot during worker cleanup.

Advantages:

- every fixture gets a real execution opportunity;
- simple completion accounting.

Risks:

- worst-case cleanup time grows with fixture count;
- choosing a fixed cap is arbitrary;
- dependency chains may need different treatment from independent fixtures.

### Policy C — shared deadline with reserved starts

Reserve enough of the worker-cleanup budget to start every deferred fixture, then spend the remainder according to dependency order.

Advantages:

- bounded total cleanup duration;
- better fairness than first-come, first-served.

Risks:

- substantially more scheduler logic;
- a started finalizer may receive too little time to complete;
- difficult error and trace attribution.

### Policy D — trigger finalizers and report receipts

After the main cleanup deadline, trigger remaining independent teardown callbacks without claiming completion, then emit explicit states such as:

- `completed`;
- `timed-out-after-start`;
- `not-started-budget-exhausted`;
- `triggered-without-completion`.

Advantages:

- users and reporters can distinguish missing cleanup from completed cleanup;
- bounded runner shutdown remains possible.

Risks:

- fire-and-forget teardown can race trace/report finalization and process exit;
- user code may assume teardown completion ordering.

## Recommended next experiment

Treat PR #1 as a narrow mechanism probe, not a final patch. Run PR #1 and PR #3 together, then compare two bounded interventions:

1. one fresh shared retry pass;
2. a per-deferred-fixture allowance capped by a total worker-cleanup deadline.

Record for every fixture:

- setup order and dependency edges;
- first teardown start time;
- whether the body started;
- completion or timeout;
- cleanup pass number;
- attachment delivery before `testEnd`;
- worker PID and browser/context survivors;
- total added shutdown time.

The decision criterion should be: **maximize the number of cleanup bodies that receive a meaningful opportunity while retaining a hard upper bound on worker shutdown.**

## Exact execution commands

From a checkout of `teamleaderleo/playwright`:

```bash
node --version
npm ci
npm run ttest -- tests/playwright-test/fixture-teardown-resumption.spec.ts

git checkout fieldwork/fixture-teardown-fairness-probe
npm run ttest -- tests/playwright-test/fixture-teardown-fairness.spec.ts
```

Run the same tests on Linux, macOS, and Windows because timer scheduling, process shutdown, and file attachment behaviour can differ.

## Current conclusion

This is a strong finding, but it is not yet a complete upstream-ready fix.

The strongest proven statement is:

> Playwright can permanently suppress a custom test-scoped fixture's teardown callback when a shared cleanup slot is exhausted, even though a later worker-cleanup pass has a fresh slot.

The narrow prototype recovers a meaningful subset without violating known historical constraints. The stacked fairness probe demonstrates that the final design needs explicit cleanup-debt scheduling or explicit abandoned-finalizer reporting rather than a single blind retry.
