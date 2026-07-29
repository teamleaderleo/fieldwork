# Playwright fixture teardown — repository intent review

Date: 2026-07-30

Repository under study: `microsoft/playwright`

Fork experiments: `teamleaderleo/playwright`

Fieldwork issue: `teamleaderleo/fieldwork#26`

No upstream contact occurred.

## In simple words

Playwright is a robot doing a test and then cleaning up.

The robot has chores such as closing the browser, saving a trace, stopping a server, and deleting test data.

When one shared timer is already empty, the robot can cross a chore off its list without starting it. A later cleanup period then cannot find that chore.

The first prototype kept unfinished chores and retried them later. That recovered lost cleanup, but it happened too late: `afterAll` could enter while the failed test's resource was still open and reuse it.

The revised rule is:

> Give unfinished, related chores one bounded recovery turn before `afterAll` asks for its own fixtures. Keep the total cleanup budget fixed. Then write an internal receipt describing what finished and what did not.

This is bounded recovery, not a promise that every cleanup callback always finishes.

## What are we doing?

The campaign investigates one narrow runner invariant:

> A test fixture callback that never started teardown because its shared slot was already exhausted should not be silently forgotten.

The intended intervention has four parts:

1. retain only test fixture teardowns that never started;
2. retry them within one existing bounded cleanup budget;
3. allocate that budget by connected fixture dependency groups, preserving child-before-parent teardown order;
4. report incomplete recovery before `testEnd`.

The intervention is a safety net for fixtures sharing the test or hook timeout. It does not replace an explicit fixture timeout for cleanup needing its own allowance.

## Repository precedent

### Shared timeout exhaustion is intentional

The [shared-timeout teardown discussion](https://redirect.github.com/microsoft/playwright/issues/30175) explains why a fixture sharing an exhausted timeout cannot simply receive unlimited extra teardown time: a stalled callback could hold the worker indefinitely. It also identifies `afterAll` ordering as a constraint; failed-test fixtures should be gone before the hook resolves its own fixtures.

Implications:

- do not promise that every teardown always runs;
- preserve a hard upper bound;
- preserve fixture ordering around `afterAll`.

### Separate fixture slots continue independently

The merged [independent fixture timeout-slot change](https://redirect.github.com/microsoft/playwright/pull/32157) established that a timeout in one slot should not prevent another slot from tearing down. It also added a regression requiring `afterAll` to receive a fresh test-scoped fixture after an `afterEach` timeout.

Implications:

- custom fixture timeouts remain the primary mechanism for critical cleanup;
- shared-slot recovery must occur before `afterAll` fixture resolution;
- recovery must not consume or overwrite dedicated fixture slots.

### Artifact loss during teardown timeout is a real user problem

The [fixture-cleanup artifact-loss report](https://redirect.github.com/microsoft/playwright/issues/31537) describes missing video and trace screenshots when an action timed out during fixture teardown.

Implications:

- artifact preservation is a user-facing consequence, not only a scheduler concern;
- tests should verify reporter delivery before `testEnd`, not rely on stdout or process-exit cleanup.

### The repository prefers small internal changes

The contribution guide requires an approved issue before implementation, small readable diffs, hermetic tests, all-three-platform compatibility, semantic commits, and no new dependencies.

Current terminal and HTML reporters also hide attachments beginning with `_`, while custom reporters can still consume them.

Implications:

- keep fork PRs draft and experimental;
- do not propose a broad public reporter API before maintainer agreement;
- use `_fixture-cleanup` while the receipt remains internal;
- keep scheduling, reporting, diagnostics, and outcome accounting separable.

## Anti-patterns to avoid

### Unlimited cleanup extension

Do not wait until every finalizer completes. A hung callback must remain bounded.

### One full timeout per fixture

Do not multiply the project timeout by fixture count. Recovery must share one fixed budget.

### Equal per-fixture timeout races

A timed-out child callback continues running after the timeout race rejects. Starting its parent cleanup immediately can close the resource underneath the child.

Use connected dependency groups rather than independent fixture slices.

### Retaining test fixtures across `afterAll`

This is an executed prototype defect.

Owned execution PR `teamleaderleo/playwright#23`, run `30485904509`, job `90691366536`, observed:

```text
resource-setup-1
test-resource-1
afterAll-resource-1
afterAll-saw-test-resource-closed-false
resource-teardown-1
```

`afterAll` reused the failed test's still-live fixture before its finalizer. Retrying only during later Worker Cleanup is rejected.

### Treating process-exit output as successful reporting

A callback can print after `testEnd`. That does not restore attachments, traces, or reporter state for the test result.

Require a normal result event before `testEnd`.

### Ordinary visible attachments for internal scheduler data

A normal `fixture-cleanup` attachment can clutter built-in reports and look like public output.

Prefer `_fixture-cleanup` while the schema remains internal.

### Fixture name as the only identity

Fixture registrations have an internal id because names can be overridden or repeated. A receipt should carry an opaque registration id plus the human name and source location.

### Mutating reporter data after dispatch

Do not rewrite attachment arrays after reporters may have consumed them. Emit the receipt through the normal attachment event before `testEnd`.

### Changing status only to restart a worker

Retry and final-outcome logic compare `status` with `expectedStatus`. A worker-stop bit can replace the process but does not necessarily make an expected-failure result unexpected.

A final design needs an internal unexpected-cleanup dimension rather than a misleading public status rewrite.

### Large combined patch

Do not combine scheduling, lifecycle ordering, receipt schema, presentation, diagnostics, and outcome semantics into one prospective patch.

## Revised lifecycle

### Ordinary After Hooks

Use the current shared slot for callbacks and test fixture teardown. If that slot is exhausted before a finalizer starts, retain the fixture as cleanup debt.

### Bounded deferred test-fixture recovery

Before `afterAll` resolves fixtures:

1. create one cleanup slot using the existing project timeout;
2. build connected fixture components through dependency and usage edges;
3. allocate bounded component shares from that one slot;
4. preserve child-before-parent ordering within each component;
5. charge actual elapsed time to the one slot;
6. clear registry entries after every attempted or unstartable finalizer so `afterAll` cannot reuse a failed-test fixture.

### `afterAll`

Run the hook only after the failed test's fixture registry is clear. Hook fixture resolution should create fresh test-scoped instances.

### Remaining Worker Cleanup

Reuse the remaining time in the same cleanup slot for residual test fixtures and worker fixtures. Do not create a second recovery budget.

### Receipt and diagnostics

Before `testEnd`, emit an internal `_fixture-cleanup` JSON attachment for deferred recovery.

Provisional fields:

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

Human diagnostics should call temporary shares fixture recovery allocations, not configured test timeouts.

## Wording guidance

### Problem

> When the shared After Hooks timeout is already exhausted, Playwright can skip a test fixture finalizer and remove the fixture from the registry, preventing bounded recovery and suppressing artifacts or resource cleanup.

### Intervention

> Retain only never-started finalizers, recover them by dependency group within one existing cleanup budget before `afterAll`, and emit an internal cleanup receipt before `testEnd`.

### Promise level

Use:

- bounded recovery;
- gives independent dependency groups an opportunity;
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

## Current owned-fork stack

- `teamleaderleo/playwright#22`: negative `afterAll` isolation invariant.
- `teamleaderleo/playwright#23`: execution showing fixture reuse before teardown.
- `teamleaderleo/playwright#24`: corrected source ordering using one cleanup budget.
- `teamleaderleo/playwright#25`: full regression execution plus the repository's existing fresh-fixture test.
- `teamleaderleo/playwright#26`: internal receipt convention.
- `teamleaderleo/playwright#27`: receipt regression execution.

All remain drafts. No upstream submission or contact occurred.

## Decision

The source finding remains strong. The dependency-group scheduler is the strongest tested policy. Recovery after `afterAll` is rejected. The current lead candidate is:

> dependency-group bounded recovery before `afterAll`, using one existing cleanup budget, followed by an internal cleanup receipt before `testEnd`.
