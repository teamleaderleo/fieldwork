# Playwright fixture teardown — repository intent review

Date: 2026-07-30

Repository under study: `microsoft/playwright`

Fork experiments: `teamleaderleo/playwright`

Fieldwork issue: `teamleaderleo/fieldwork#26`

No upstream contact occurred.

## Explain it like I am five

Playwright is a robot doing a test and then cleaning up.

The robot has chores such as closing the browser, saving a trace, stopping a server, and deleting test data.

The original bug is that, when one shared timer is already empty, the robot can cross a chore off its list without ever starting it. A later emergency-cleanup period then cannot find that chore.

The first prototype kept unfinished chores on the list and retried them later. That recovered lost cleanup, but the retry happened too late: `afterAll` could enter the room while the failed test's resource was still open and reuse it.

The revised rule is:

> Give unfinished, related chores one bounded recovery turn before `afterAll` asks for its own fixtures. Keep the total emergency-cleanup budget fixed. Then write an internal receipt describing what finished and what did not.

This is bounded recovery, not a promise that every cleanup callback will always finish.

## What are we doing?

The campaign is investigating one narrow runner invariant:

> A test fixture callback that never started teardown because its shared slot was already exhausted should not be silently forgotten.

The intended intervention has four parts:

1. retain only test fixture teardowns that never started;
2. retry them within one existing, bounded cleanup budget;
3. allocate that budget by connected fixture dependency groups, preserving child-before-parent teardown ordering;
4. report incomplete recovery before `testEnd`.

The intervention is a safety net for fixtures that share the test/hook timeout. It does not replace an explicit fixture timeout for cleanup that needs its own allowance.

## Repository precedent

### 1. Shared timeout exhaustion is intentional

In `microsoft/playwright#30175`, maintainers explained that a fixture sharing an exhausted timeout cannot simply receive unlimited extra teardown time. A stalled callback could otherwise hold the worker indefinitely. The discussion also identified `afterAll` ordering as a constraint: test fixtures should be gone before `afterAll` resolves fixtures.

Implication:

- do not frame this campaign as "always run every fixture teardown";
- preserve a hard upper bound;
- preserve fixture lifecycle ordering around `afterAll`.

### 2. Separate fixture slots should continue independently

Merged PR `microsoft/playwright#32157` established that a timeout in one fixture slot should not prevent teardown in another slot, and that an `afterEach` timeout should not block fixture teardown that has its own timeout.

The same PR added an important regression invariant: after an `afterEach` timeout, `afterAll` should receive a fresh test-scoped fixture instance.

Implication:

- custom fixture timeouts remain the primary mechanism for critical cleanup;
- recovery for shared-slot fixtures must occur before `afterAll` fixture resolution;
- the intervention must not consume or overwrite dedicated fixture timeout slots.

### 3. Artifact loss during teardown timeout is a known user problem

Issue `microsoft/playwright#31537` reported missing video and trace screenshots when an action timed out during fixture teardown. The eventual runner work improved independent timeout-slot progression.

Implication:

- artifact preservation is a real user-facing consequence, not an abstract scheduler concern;
- the campaign should test attachments and reporter delivery before `testEnd`, not rely on stdout or process-exit cleanup.

### 4. The repository prefers small internal conventions over broad public API

The contribution guide requires an approved issue before upstream implementation, small readable diffs, hermetic tests, all-three-platform compatibility, semantic commits, and no new dependencies.

Reporter history also contains an underscore attachment convention. Current terminal and HTML reporters hide attachments whose names begin with `_`, while custom reporters can still consume them.

Implication:

- keep all fork PRs draft and experimental;
- do not propose a new public reporter API before maintainer agreement;
- use an internal `_fixture-cleanup` attachment if the receipt remains attachment-based;
- keep scheduler, reporting, diagnostics, and outcome-accounting changes separable.

## Anti-patterns to avoid

### Unlimited cleanup extension

Do not keep waiting until every finalizer completes. A hung user callback must remain bounded.

### One full timeout per fixture

Do not multiply the project timeout by the number of fixtures. Recovery must share one fixed budget.

### Equal per-fixture timeout races

A timed-out child callback continues running after the timeout race rejects. Starting its parent cleanup immediately can close the parent resource underneath the child.

Use connected dependency groups rather than independent fixture slices.

### Retaining test fixtures across `afterAll`

This is now confirmed as an actual prototype defect, not merely a theoretical concern.

Execution PR `teamleaderleo/playwright#23`, run `30485904509`, job `90691366536`, observed:

```text
resource-setup-1
test-resource-1
afterAll-resource-1
afterAll-saw-test-resource-closed-false
resource-teardown-1
```

`afterAll` reused the failed test's still-live fixture and ran before its finalizer.

The prior lead ordering—retrying only in later Worker Cleanup—is rejected.

### Treating process-exit output as successful test reporting

A callback can print during late process cleanup after `testEnd`. That does not restore attachments, traces, or reporter state for the test result.

Require result attachments or equivalent events before `testEnd`.

### Ordinary visible attachment for internal scheduler data

A normal `fixture-cleanup` attachment can clutter built-in reports and accidentally appear public.

Prefer `_fixture-cleanup` while the schema remains internal and experimental.

### Fixture name as the only identity

Playwright registrations have an internal id specifically because fixture names can be overridden or repeated. A receipt should carry an opaque registration id plus the human name and source location. Name alone is ambiguous.

### Mutating reporter data after dispatch

Do not rewrite attachment arrays after reporters may have consumed them. Emit the receipt through the normal attachment event before `testEnd`.

### Changing status merely to restart a worker

The prototype currently uses `timedOut` for one expected-failure cleanup-debt path. This is acceptable as a temporary experiment when the lifecycle truly timed out, but it is not a complete outcome model.

Playwright's retry and final-outcome logic compare `status` with `expectedStatus`. A worker-stop flag alone restarts the process but does not necessarily make an expected-failure test unexpected. A final design needs an internal unexpected-cleanup dimension that influences retries and final outcome without inventing a misleading public status.

### Large combined patch

Do not combine scheduling, lifecycle ordering, receipt schema, HTML presentation, diagnostics, and outcome semantics into one prospective upstream PR. The repository explicitly prefers small readable changes.

## Revised architecture

### Phase 1: ordinary After Hooks

Use the current shared After Hooks slot for callbacks and test fixture teardown.

If the slot is exhausted before a test fixture finalizer starts, retain that fixture as cleanup debt.

### Phase 2: bounded deferred test-fixture recovery

Before `afterAll` resolves fixtures:

1. create one full-cleanup slot using the existing project timeout;
2. build connected components among retained fixtures through dependency and usage edges;
3. allocate bounded component shares from that one slot;
4. preserve child-before-parent ordering within each component;
5. charge actual elapsed time to the one full-cleanup slot;
6. force-clear registry entries after each attempted or unstartable finalizer so `afterAll` cannot reuse the failed test's fixture.

### Phase 3: `afterAll`

Run `afterAll` only after the failed test's fixture registry has been cleared. Hook fixture resolution should create fresh test-scoped instances.

### Phase 4: remaining Worker Cleanup

Reuse the remaining time in the same full-cleanup slot for residual test fixtures and worker fixtures. Do not create a second recovery budget.

### Phase 5: receipt and diagnostics

Before `testEnd`, emit an internal `_fixture-cleanup` JSON attachment for deferred recovery.

Provisional schema:

```json
{
  "version": 1,
  "phase": "deferred-test-fixture-recovery",
  "budget": {
    "timeout": 2000,
    "elapsed": 134
  },
  "fixtures": [
    {
      "id": "opaque-registration-id",
      "name": "child",
      "location": {
        "file": "a.spec.ts",
        "line": 12,
        "column": 7
      },
      "state": "timed-out-after-start"
    },
    {
      "id": "opaque-registration-id",
      "name": "root",
      "location": {
        "file": "a.spec.ts",
        "line": 6,
        "column": 7
      },
      "state": "not-started-budget-exhausted"
    }
  ]
}
```

Current state vocabulary:

- `completed`
- `failed-after-start`
- `timed-out-after-start`
- `not-started-budget-exhausted`

Human diagnostics should call temporary shares "fixture recovery allocations", not user-configured test timeouts.

## Wording guidance for issues and PRs

### Preferred one-sentence problem statement

> When the shared After Hooks timeout is already exhausted, Playwright can skip a test fixture finalizer and remove the fixture from the registry, preventing bounded recovery and suppressing artifacts or resource cleanup.

### Preferred one-sentence intervention

> Retain only never-started finalizers, recover them by dependency group within one existing cleanup budget before `afterAll`, and emit an internal cleanup receipt before `testEnd`.

### Preferred promise level

Use:

- bounded recovery;
- gives each independent dependency group an opportunity;
- preserves child-before-parent teardown order;
- records incomplete cleanup;
- does not extend the total cleanup deadline.

Avoid:

- guarantees cleanup;
- always runs teardown;
- prevents resource leaks;
- gives every fixture its own timeout;
- transparent or behavior-free change.

### Suggested ELI5 block

> Playwright is a robot with a cleanup checklist. Today, when the shared timer is empty, it can cross off a chore without doing it. The change keeps that chore on the list, gives related chores one bounded cleanup turn before `afterAll` enters the room, and writes a private receipt saying which chores finished.

## Current fork stack after review

- `teamleaderleo/playwright#22`: negative `afterAll` isolation invariant.
- `teamleaderleo/playwright#23`: exact execution showing the failed test fixture was reused by `afterAll` before teardown.
- `teamleaderleo/playwright#24`: revised source intervention that spends the existing full-cleanup budget before `afterAll` and reuses the remainder later.
- `teamleaderleo/playwright#25`: regression harness for the full campaign plus the repository's existing fresh-`afterAll`-fixture timeout test.

All remain drafts. No upstream submission or contact occurred.

## Decision

The original source finding remains strong.

The dependency-group scheduler remains the strongest scheduling policy tested.

The previous placement in later Worker Cleanup is rejected because it violates `afterAll` fixture isolation.

The lead candidate is now:

> dependency-group bounded recovery before `afterAll`, using one existing full-cleanup budget, followed by an internal cleanup receipt before `testEnd`.
