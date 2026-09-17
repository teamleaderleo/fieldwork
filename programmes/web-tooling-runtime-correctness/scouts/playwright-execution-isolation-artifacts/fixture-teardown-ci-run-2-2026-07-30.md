# Playwright fixture teardown CI run 2 — 2026-07-30

## Result

The corrected budgeted-fairness stack passed the exact targeted Playwright Test runner suite.

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Execution PR | `#5` |
| Workflow run | `30477170427` |
| Job | `90661670642` |
| Merge ref | `6107dc0b195a6c01c7e42041b09f552ed986db1e` |
| Prototype base | `fieldwork/fixture-teardown-budgeted-fairness@424b81b4352cfaca14f1ded145dab53f1fdf6b82` |
| Runner | GitHub-hosted Ubuntu 24.04.4 |
| Node | 22 |
| Workers | 1 |
| Tests | 7 |
| Outcome | 7 passed |
| Test duration | 13.6 seconds |

No upstream contact occurred.

## Command

```bash
npm run ttest -- \
  tests/playwright-test/fixture-teardown-resumption.spec.ts \
  tests/playwright-test/fixture-teardown-fairness.spec.ts \
  --workers=1
```

The repository's standard `run-test` action performed `npm ci`, the repository build, Chromium installation, and the targeted runner invocation.

## Passed invariants

### Narrow retention

- a peer fixture can consume the original shared teardown slot;
- a never-started independent fixture remains registered;
- Worker Cleanup retries it with the fresh project-timeout slot;
- its marker and attachment appear for attempt 0 and retry 1;
- attempts use distinct worker indices.

### Dependency cleanup

- a timed-out dependent fixture does not erase its retained dependency cleanup;
- the dependency and an independent fixture both finalize in teardown order.

### `afterEach` exhaustion

- `afterEach` can exhaust the original after-hooks slot before fixture teardown begins;
- the retained fixture still finalizes during Worker Cleanup on both attempts.

### Expected-failure accounting

- an expected body failure plus cleanup debt still replaces the worker;
- the retained fixture finalizes on attempt 0 and retry 1.

### Hook isolation

- a fixture used by a timed-out `afterAll` hook is not retained for the next `afterAll` hook;
- the later hook receives a fresh fixture instance.

### Budgeted fairness

- when all test fixtures are deferred, a slow first deferred fixture cannot consume the full recovery budget and starve a later sentinel;
- sentinel attachments are present in each attempt result before `testEnd`;
- with one slow deferred fixture followed by two quick finalizers, both later finalizers run in teardown order on both attempts;
- unused per-fixture allocation is carried forward.

## Confidence update

| Claim | Confidence after run 2 |
|---|---|
| Original skip-and-delete mechanism is campaign-worthy | high |
| Narrow retention works on Ubuntu/Node 22 | high |
| Expected-failure worker replacement works in tested case | high |
| Equal-share budget prototype works in tested cases | high |
| Attachments arrive before `testEnd` | high |
| Dependency and hook isolation controls remain intact in tested cases | high |
| macOS and Windows behaviour | pending |
| Diagnostic wording and final status model | unresolved |
| Equal allocation is the right production policy | unresolved |

## Causal control

A matching no-budget execution PR, `teamleaderleo/playwright#6`, runs the same suite against the narrow retention branch plus the fairness invariant. Its expected failure is the missing pre-`testEnd` sentinel attachment after a slow deferred fixture consumes the single fresh shared slot.

A passing intervention plus a failing no-budget control would establish that budget partitioning, rather than unrelated test timing, causes the recovered finalizers.

## Next work

1. complete the no-budget negative control;
2. run the passing stack on macOS and Windows;
3. inspect timeout diagnostics produced by the temporary allocations;
4. add dependency-group cases in which a slow dependent and its resource-owning parent are both deferred;
5. compare equal allocation against a minimum-start reservation plus shared completion pool.
