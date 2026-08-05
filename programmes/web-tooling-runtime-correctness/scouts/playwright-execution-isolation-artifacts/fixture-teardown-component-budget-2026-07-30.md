# Playwright dependency-group cleanup budget — 2026-07-30

## Decision

Promote dependency-group recovery scheduling as the lead fixture teardown intervention.

Equal per-fixture allocation remains a useful independent-fairness control, but is rejected as a general policy because a timed-out child finalizer can continue running while its resource-owning dependency begins teardown.

No upstream contact occurred.

## Exact comparison

### Equal per-fixture control

| Field | Value |
|---|---|
| Safety probe | `teamleaderleo/playwright#8` |
| Execution PR | `#9` |
| Workflow run | `30480460210` |
| Job | `90672968142` |
| Safety branch head | `f4498093f75cec22f75cc1ba2a8422ee493e8e4b` |
| Result | expected failure |

Observed order:

```text
child-finalizer-started
root-closed
```

Missing:

```text
child-finished-root-open
```

The nested test timed out at 2 seconds. The equal-share allocator started the child, its allocation expired, and the root callback ran before the child completed.

### Dependency-group intervention

| Field | Value |
|---|---|
| Intervention PR | `teamleaderleo/playwright#10` |
| Execution PR | `#11` |
| Workflow run | `30480496796` |
| Job | `90673090294` |
| Component branch head | `8197f236d0911401882eb9b8f624f39f42589324` |
| Result | 8 passed |
| Duration | 13.4 seconds |

Command:

```bash
npm run ttest -- \
  tests/playwright-test/fixture-teardown-resumption.spec.ts \
  tests/playwright-test/fixture-teardown-fairness.spec.ts \
  tests/playwright-test/fixture-teardown-dependency-safety.spec.ts \
  --workers=1
```

## Scheduler behaviour

The intervention:

1. finds fixtures that were deferred when Worker Cleanup begins;
2. builds connected components using `_deps` and `_usages` edges;
3. weights each component by fixture count;
4. allocates a bounded share of the remaining Worker Cleanup test-fixture slot to each component;
5. gives all fixtures in one component the same slot;
6. charges actual elapsed time back to the existing Worker Cleanup slot;
7. returns unused component reservation only after that component finishes.

## Why grouping fixes the safety failure

A teardown timeout rejects the runner's timeout race but does not cancel the fixture callback. Under individual shares:

1. child callback starts;
2. child share expires;
3. usage tracking is force-cleared;
4. root receives a different share and starts;
5. child and root cleanup overlap.

Under one component slot:

- if child finishes, remaining component time is available to root;
- if child exhausts the component slot, root sees the same exhausted slot and does not start;
- dependency teardown cannot begin concurrently with the timed-out child callback.

The exact eight-test pass includes the required safe child-before-root invariant in addition to all previous retention, retry, attachment, expected-failure, hook-isolation, and independent-fairness controls.

## Candidate ranking

| Candidate | Status |
|---|---|
| Retain skipped fixtures only | necessary but insufficient |
| One shared fallback slot | rejected: independent starvation before `testEnd` |
| Equal per-fixture allocation | rejected as general policy: dependency-order violation |
| Dependency-group weighted allocation | lead prototype |

## Remaining gap: completion receipts

Dependency grouping preserves ordering by refusing to start later fixtures after a component exhausts its allowance. That means a safe run can still end with:

- child: started, timed out, callback still running or abandoned at process exit;
- root: never started because the component budget was exhausted.

Those states remain implicit today.

Draft PR `teamleaderleo/playwright#12` requires a `fixture-cleanup` JSON attachment before `testEnd` with states such as:

```json
{
  "version": 1,
  "phase": "worker-cleanup",
  "fixtures": [
    { "name": "child", "state": "timed-out-after-start" },
    { "name": "root", "state": "not-started-budget-exhausted" }
  ]
}
```

The next intervention should add explicit cleanup receipts without changing the validated dependency-group scheduler.

## Remaining validation

- cross-platform run of the eight-test dependency-group suite;
- machine-readable cleanup receipts for exhausted components;
- diagnostic wording that distinguishes scheduler allocation from configured timeout;
- abrupt cancellation during recovery;
- actual BrowserContext and child-process ownership cases;
- a dedicated WorkerMain cleanup-debt signal instead of experimental status mutation.
