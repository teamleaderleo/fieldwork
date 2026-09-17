# Playwright fixture teardown fairness negative control — 2026-07-30

## Result

The no-budget negative control failed exactly at the pre-`testEnd` attachment invariant.

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Execution PR | `#6` |
| Workflow run | `30477359223` |
| Job | `90662303102` |
| Merge ref | `7f82b9947e7705fe39d687f6ed8c586bcadbe1f5` |
| Base experiment | narrow retention PR #1 plus fairness test PR #3 |
| Allocator | none; all deferred fixtures share one fresh worker-cleanup slot |
| Runner | Ubuntu 24.04.4, Node 22, one worker |
| Outcome | expected failure |

No upstream contact occurred.

## Observed sequence

The nested test ran attempt 0 and retry 1. On each attempt:

1. `afterEach` exhausted the original test cleanup slot;
2. blocker and sentinel were retained;
3. blocker consumed the fresh Worker Cleanup slot;
4. the test result was sent without the sentinel attachment;
5. the sentinel callback ran later during process-level cleanup and printed its marker.

Observed stdout included:

```text
%%sentinel-0
%%sentinel-1
```

Observed sentinel attachment arrays were:

```text
[
  [],
  []
]
```

The required arrays were:

```text
[
  [sentinel-0],
  [sentinel-1]
]
```

## Causal conclusion

The passing budgeted prototype and failing no-budget control use the same retention mechanism and fairness invariant. The difference is recovery-slot allocation.

This establishes:

- retaining skipped fixtures alone is insufficient;
- a single shared retry slot lets the first slow deferred fixture starve later finalizers;
- stdout markers are not adequate evidence of test-result cleanup;
- callbacks can run after `testEnd`, while attachments and other report mutations are already lost;
- partitioning recovery budget is causally responsible for the recovered pre-`testEnd` attachments in the passing intervention.

## Additional signal

The negative run printed:

```text
Internal error: fixture integrity at playwright
```

This did not appear in the passing budgeted run. It indicates retained test-fixture usage reached later worker fixture cleanup while test cleanup debt remained unresolved. That is another reason to require the retained test-fixture recovery phase to finish or explicitly account for abandonment before worker fixtures are torn down.

## Confidence update

| Claim | Confidence |
|---|---|
| One shared fallback slot is unfair | high |
| Late process cleanup cannot repair test-result attachments | high |
| Budget partitioning causes the observed attachment recovery | high on Ubuntu/Node 22 |
| Narrow retention is sufficient as a final fix | rejected |
| Recovery requires scheduling plus explicit completion accounting | high |

## Next controls

- cross-platform execution of the passing budgeted prototype;
- dependency-safety control showing that equal per-fixture shares can start a root cleanup while a timed-out child callback still runs;
- dependency-group budget intervention preserving child-before-root ordering.
