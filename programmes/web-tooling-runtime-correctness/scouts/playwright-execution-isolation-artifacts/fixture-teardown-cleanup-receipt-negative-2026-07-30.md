# Playwright deferred cleanup receipt negative control — 2026-07-30

## Result

The dependency-group scheduler preserved teardown safety when its group allowance was exhausted, but the test result contained no machine-readable cleanup receipt.

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Receipt probe | PR `#12` |
| Execution PR | `#14` |
| Workflow run | `30481142677` |
| Job | `90675247334` |
| Scheduler | dependency-group budget prototype |
| Runner | Ubuntu 24.04.4, Node 22, one worker |
| Outcome | expected reporting failure |

No upstream contact occurred.

## Scenario

- project and Worker Cleanup timeout: 2 seconds;
- `afterEach`: 3 seconds, exhausting the original After Hooks slot;
- child fixture finalizer: 5 seconds;
- root fixture owns the dependency resource;
- child and root share one dependency-group recovery allowance.

## Observed behavior

Output contained only:

```text
child-finalizer-started
```

Output did not contain:

```text
child-finalizer-finished
root-closed
```

This confirms the group scheduler preserved ordering: the root callback did not start after the child exhausted the group allowance.

The nested runner reported:

```text
Tearing down "child" exceeded the test timeout of 133ms.
```

The outer receipt assertion observed:

```text
Expected: application/json
Received: undefined
```

No `fixture-cleanup` attachment was present.

## Required receipt

The test requires an attachment before `testEnd`:

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

The receipt may also include completed built-in or custom fixtures. Consumers must be able to identify at least:

- completed;
- timed out after starting;
- failed after starting;
- not started because the dependency-group budget was exhausted.

## Why an attachment is useful

A JSON attachment reaches:

- live reporter `onAttach` handling;
- the attempt result before `testEnd`;
- blob and JSON reports;
- merged reports;
- CI artifact processing.

It avoids overloading the test status with every cleanup detail and separates configured timeout failures from recovery scheduler outcomes.

## Diagnostic issue exposed by the run

The child error says the **test timeout was 133ms**, but 133ms is a recovery scheduler allocation derived from a 2-second project timeout. That wording can mislead users into believing they configured a 133ms test timeout.

A production design should label the distinction explicitly, for example:

```text
Worker Cleanup allocated 133ms to fixture dependency group "child → root"; child teardown did not complete within that recovery allowance.
```

## Next intervention

Add cleanup-state tracking to `FixtureRunner` without changing the validated dependency-group scheduler:

1. record whether each deferred teardown started;
2. classify completion, timeout, failure, and unstarted states;
3. attach one `fixture-cleanup` JSON document during Worker Cleanup before propagating the existing error;
4. preserve current step and timeout errors;
5. assert reporter and blob-report delivery;
6. replace scheduler-allocation timeout wording with a recovery-specific diagnostic.
