# Playwright cleanup recovery, outcome accounting, and artifacts

- Assignment: #26
- Programme: #15, `web-tooling-runtime-correctness`
- Target hub: #10, Playwright
- Central review candidates: #141 and #142
- Worker: `chatgpt:gpt-5.6-thinking`
- State: `ready-for-synthesis`
- Original target revision: `microsoft/playwright@0b2088e58e398106445c39fd3e5ec4cb85ef8bbb`
- Original target package version: `1.63.0-next`
- Exact executed revisions: retained by the owned-fork pull requests and workflow runs named below
- Retrieval and execution dates: 2026-07-29 through 2026-07-30
- Upstream contact authorized: `false`

## In simple words

Playwright is a robot with a cleanup checklist.

When the shared cleanup timer is already empty, the robot can erase a fixture cleanup from the checklist without running it. Later cleanup cannot try again because the fixture is no longer registered.

The reviewed recovery design does three things:

1. keep only fixture finalizers that never started;
2. give related fixtures one bounded recovery turn before `afterAll` enters;
3. write a private receipt describing what completed and what did not.

This is bounded recovery. It is not a promise that every stalled user callback will finish.

A separate result-model issue also emerged. A test marked with `test.fail()` can absorb an unrelated fixture cleanup exception because both use the public `failed` status. The run may then be counted as expected without retrying. That question is deliberately separated into candidate #142.

## What reviewers are being asked to decide

### Candidate #141 — bounded fixture recovery

Review whether Playwright should retain never-started shared-slot fixture finalizers, recover them by dependency group within one existing cleanup budget before `afterAll`, reuse the remaining budget for worker cleanup, and emit an internal receipt before `testEnd`.

### Candidate #142 — unexpected cleanup failure after `test.fail()`

Review how a cleanup, hook, fixture, or runner failure that is independent of an expected body failure should reach worker replacement, retry selection, and final outcome without casually changing the public status model.

These are different owning boundaries and should not be one patch.

## Evidence vocabulary

- **Executed target reproduction** — exact Playwright Test runner tests executed in the owned fork with retained workflow runs.
- **Source-confirmed** — pinned implementation and repository history directly support the mechanism.
- **Prepared target test** — a focused test exists in an owned fork but does not yet have a retained execution result.
- **Probe-reproduced model** — a controlled library-level or synthetic probe demonstrates part of the mechanism but is not the exact target runner path.
- **Candidate contract** — a desired invariant proposed for review; current code is not assumed to promise it.

The report does not upgrade prepared tests or source analysis into executed defects.

## Execution and ownership map

| Owner | Responsibility | Lifetime | Relevant completion boundary |
| --- | --- | --- | --- |
| Runner and dispatcher | scheduling, retries, final outcome, reporter dispatch | whole invocation or phase | worker result and `testEnd` |
| `WorkerMain` | hooks, fixture runner, active test, worker shutdown | worker process | After Hooks, `afterAll`, Worker Cleanup |
| Fixture runner | fixture graph, instances, setup and teardown order | test or worker scope | shared slot or custom fixture slot |
| Browser/context fixtures | browser process, contexts, pages, video source | worker or attempt | fixture teardown and context close |
| Artifact recorders | screenshot, trace, video, error context | attempt | context closure, trace packaging, attachment dispatch |
| Reporters | result events and durable reports | whole invocation | `onEnd` and `onExit` |

The strongest defect sits at the boundary between the fixture registry, shared teardown timing, `afterAll`, and reporter completion.

## Strongest confirmed mechanism

A test-scoped fixture without its own timeout uses the runnable's shared After Hooks slot.

When that slot is already exhausted before the fixture teardown body begins, the current fixture teardown path skips the body. Its cleanup path still removes dependency usage and deletes the fixture from `instanceForId`.

The later cleanup pass therefore cannot find the fixture and cannot give its finalizer another bounded opportunity.

Potential consequences include omitted custom finalizers, BrowserContext closure, local service shutdown, artifact finalization, and attachments that never reach the result.

## Causal experiment stack

The campaign did not jump directly from source reading to a preferred scheduler. Each design had a control that could reject it.

| Step | Experiment | Result | Decision |
| --- | --- | --- | --- |
| 1 | Retain never-started fixtures | Later finalizer becomes reachable | Retention is necessary |
| 2 | One shared fallback slot | First slow deferred callback consumes the slot; later receipt is absent before `testEnd` | One shared slot is insufficient |
| 3 | Equal per-fixture shares | Independent finalizers progress | Useful fairness property |
| 4 | Dependency safety control | Child callback times out but keeps running while parent resource closes | Equal per-fixture shares rejected |
| 5 | Connected dependency-group shares | Child and parent share one slot; parent does not begin while child remains active | Dependency-group scheduler retained |
| 6 | Retry only in later Worker Cleanup | `afterAll` reuses the failed test's retained fixture | Late placement rejected |
| 7 | Spend the same cleanup slot before `afterAll` | Fresh `afterAll` fixture restored; campaign remains green | Current lead placement |
| 8 | Internal receipt convention | Four states, stable identity, and source location retained | Reporting refinement accepted in fork |
| 9 | Expected body failure plus cleanup exception | No retry; run counted as expected | Separate outcome-accounting candidate opened |

## Dependency-group scheduler

The scheduler builds connected components using fixture dependency and usage relationships. Fixtures in one component share one recovery slot, preserving teardown order. Independent components receive bounded shares weighted by fixture count. Unused reservation returns to the remaining pool.

The scheduler passed eight exact runner tests with Node 22 and one worker:

| Platform | Result |
| --- | --- |
| Ubuntu 24.04 | 8 passed in 16.1s |
| macOS 26.4 arm64 | 8 passed in 14.8s |
| Windows Server 2025 | 8 passed in 19.8s |

This validates the scheduler cases across the repository's three required platform families. It does not yet validate the final combined pre-`afterAll` ordering and internal-receipt stack on all three platforms.

## Rejected late recovery placement

Owned probe PR `teamleaderleo/playwright#22` and execution PR `#23` tested whether retrying retained test fixtures only in later Worker Cleanup preserves hook isolation.

Workflow run `30485904509`, job `90691366536`, observed:

```text
resource-setup-1
test-resource-1
afterAll-resource-1
afterAll-saw-test-resource-closed-false
resource-teardown-1
```

`afterAll` received the failed test's still-live fixture. A fresh second fixture was never created.

Repository history already required a new fixture instance for `afterAll` after an `afterEach` timeout. The negative control therefore rejected late Worker Cleanup as the primary recovery point.

## Corrected pre-`afterAll` recovery

Owned source PR `teamleaderleo/playwright#24` moves the test-fixture recovery pass before `afterAll` fixture resolution.

It creates one bounded full-cleanup slot using the existing project timeout, spends the test-fixture portion before `afterAll` when cleanup debt exists, and reuses the same slot during later Worker Cleanup. It does not add another cleanup deadline.

Execution PR `teamleaderleo/playwright#25`, workflow run `30486881047`, job `90694673635`, produced:

```text
11 passed (22.9s)
```

The repository's existing regression `should run fixture teardown with custom timeout after afterEach timeout` also passed separately:

```text
1 passed (4.5s)
```

The source diff is limited to `workerMain.ts`: 17 additions and 5 deletions. The change moves recovery; it does not alter the dependency-group algorithm.

## Cleanup receipt

Deferred recovery can end in more states than pass or fail. The tested internal receipt records:

- `completed`
- `failed-after-start`
- `timed-out-after-start`
- `not-started-budget-exhausted`

Owned source PR `teamleaderleo/playwright#26` aligns the receipt with existing repository conventions:

- attachment name `_fixture-cleanup`, following the internal underscore convention;
- phase `deferred-test-fixture-recovery`;
- opaque fixture registration id;
- human fixture name;
- source location;
- recovery budget fields;
- one of the four cleanup states.

Execution PR `teamleaderleo/playwright#27`, workflow run `30487474207`, job `90696663923`, passed the complete eleven-test stack in 22.8 seconds on Ubuntu 24.04, Node 22, and one worker.

The receipt is emitted before `testEnd`. Output or callbacks that occur only after result dispatch cannot repair the already-delivered result.

## Current lead invariant

> When a shared-slot test fixture finalizer has not started because the normal slot is exhausted, retain only that fixture instance, recover retained fixtures by connected dependency group within one existing cleanup budget before `afterAll`, reuse the remaining budget for worker cleanup, and emit an internal receipt before `testEnd`.

The promise level is intentionally narrow:

- provide a bounded recovery opportunity;
- preserve dependency order;
- prevent failed-test fixtures from crossing into `afterAll`;
- make incomplete cleanup explicit;
- do not wait indefinitely;
- do not grant every fixture a complete extra timeout.

Cleanup that must have an independent allowance should continue to use an explicit fixture timeout.

## Expected-failure outcome accounting

Owned probe PR `teamleaderleo/playwright#28` tests a separate case:

- the body is marked with `test.fail()` and fails as expected;
- fixture teardown throws `cleanup exploded`;
- retries are set to one.

Execution PR `teamleaderleo/playwright#29`, workflow run `30487755057`, job `90697590797`, printed:

```text
cleanup-0-worker-0
1 passed
```

Only attempt zero ran. No fresh worker appeared. The nested exit code was zero.

The dispatcher selects failures by comparing result `status` with `expectedStatus`; final test outcome uses the same public comparison. A worker-stop flag alone can protect later tests but cannot make this result retryable or unexpected.

Candidate #142 therefore asks for a separate internal unexpected-cleanup dimension that can reach:

- worker replacement;
- retry selection;
- retained errors;
- final outcome.

No implementation has been selected. Blindly rewriting public status strings is explicitly out of scope.

## Repository precedent and intentions

The history review found these constraints:

- timeout bounds are deliberate;
- custom-timeout fixtures own independent slots and should continue after another slot expires;
- attempted teardown must not be repeated merely because it failed;
- test fixtures should be gone before `afterAll` resolves its own fixtures;
- worker fixtures remain after `afterAll`;
- test-runner changes require focused hermetic tests;
- tests should work on Linux, macOS, and Windows;
- prospective changes should remain small, issue-led, and reviewed before upstream work.

Durable detail is in `fixture-teardown-repository-intent-review-2026-07-30.md`.

## Anti-patterns rejected

- extending teardown without a hard bound;
- multiplying project timeout by fixture count;
- giving dependent fixtures independent timeout races;
- retrying callbacks that already began and failed;
- retaining every fixture rather than only never-started finalizers;
- retrying retained test fixtures only after `afterAll`;
- treating process-exit stdout as successful reporter evidence;
- emitting internal scheduling data as an ordinary visible attachment;
- identifying receipt entries only by fixture name;
- changing public status strings solely to force retries;
- combining scheduler, diagnostics, receipt schema, and outcome accounting in one patch.

## Other retained findings

### Playwright MCP and CLI video receipts

**Evidence class:** source-confirmed mechanism plus prepared target tests.

The video flow can record a derived filename before screencast startup succeeds. Page-created startup failures are suppressed, so a stop response can advertise a recording whose screencast never started.

Owned fork tests exist in `teamleaderleo/playwright-mcp#1` and `teamleaderleo/playwright-cli#1`. They still need exact execution before promotion.

### Python async stop retriability

**Evidence class:** source-confirmed mechanism plus prepared target test.

`PlaywrightContextManager.__aexit__` marks exit before awaiting asynchronous transport shutdown. If the first `playwright.stop()` is cancelled, a retry can return immediately while connection cleanup remains incomplete.

Owned fork test `teamleaderleo/playwright-python#1` blocks transport shutdown, cancels the first stop, releases transport completion, retries stop, and requires final cleanup. It has not yet produced a retained target execution result.

### Crash-resilient blob reporting

**Evidence class:** source-confirmed candidate.

Blob report events are accumulated in memory and the durable ZIP is created during `onEnd`. A hard exit before or during `onEnd` can leave no replayable blob even when attempt artifacts already exist.

A journal prototype exists in the owned fork, but the next useful evidence is a deterministic phase-interruption matrix, not another implementation variant.

### Worker heartbeat hard kill

**Evidence class:** bounded open probe with counterevidence.

The worker force-kill path and browser process groups use different ownership boundaries. A library-level SIGKILL probe found no surviving observed Playwright driver or Chromium processes. The exact Playwright Test heartbeat-loss path remains worth one bounded process-tree probe, but no defect is claimed.

## Review packet

### Review candidate #141

Check:

1. skip-and-delete source mechanism;
2. no-budget starvation control;
3. equal-share dependency race;
4. connected-component safety;
5. late-placement `afterAll` failure;
6. same-budget pre-`afterAll` correction;
7. internal receipt naming, identity, and timing;
8. final cross-platform execution need.

Return one disposition: **accept**, **revise**, **execute**, **hold**, or **reject/stop**.

### Review candidate #142

Check:

1. expected body failure is distinct from cleanup exception;
2. only attempt zero runs despite one retry;
3. current result model's status comparison;
4. adjacent unhandled-error and hook-error precedent;
5. reporter, serial-suite, max-failure, and retry consequences of a new internal signal.

Return one disposition: **accept as separate candidate**, **revise**, or **hold for result-model design**.

## Durable evidence index

- `fixture-teardown-deep-dive-2026-07-30.md`
- `fixture-teardown-negative-control-2026-07-30.md`
- `fixture-teardown-dependency-safety-run-1-2026-07-30.md`
- `fixture-teardown-dependency-safety-run-2-2026-07-30.md`
- `fixture-teardown-component-budget-2026-07-30.md`
- `fixture-teardown-component-cross-platform-2026-07-30.md`
- `fixture-teardown-cleanup-receipt-negative-2026-07-30.md`
- `fixture-teardown-cleanup-receipt-run-2026-07-30.md`
- `fixture-teardown-recovery-diagnostics-state-matrix-2026-07-30.md`
- `fixture-teardown-repository-intent-review-2026-07-30.md`
- `fixture-teardown-repository-alignment-run-2026-07-30.md`
- `follow-up-2026-07-30.md`
- retained probes under `probe/`

## Handoff

- Parent scout: #26
- Central recovery candidate: #141
- Central outcome-accounting candidate: #142
- Fieldwork review PR: #49
- Primary owned source PRs: `teamleaderleo/playwright#24` and `#26`
- Primary negative outcome probe: `teamleaderleo/playwright#28`
- Upstream contact: unauthorized

No upstream contact occurred.