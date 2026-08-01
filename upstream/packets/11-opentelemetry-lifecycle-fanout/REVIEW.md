# Review — Unit 11: snapshot lifecycle targets before concurrent fanout

## Subject

- target: `open-telemetry/opentelemetry-js`;
- base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact source head: `59f83f889bed06a951d458556b2e7e1695cbea10`;
- branch: `upstream/unit-11-lifecycle-fanout`;
- relation: one commit ahead, zero behind;
- boundary: four production files and four tests;
- public upstream authority: none.

## Disposition

`HOLD — complete repair applied; final validation pending`

The prior metrics `REPAIR` is resolved. The deeper pass also found and repaired a second trace fanout in public `TracerProvider.forceFlush()`. No further product issue was found in the exact eight-file self-review. This is not independent final acceptance.

## Complete-diff findings

### `MultiSpanProcessor`

Accepted: opening snapshots, eager safe-call, original aggregate promise/error structure retained, throw/removal tests present.

### `TracerProvider.forceFlush`

Accepted repaired direction:

- provider bypasses `MultiSpanProcessor.forceFlush()` and therefore needs its own opening snapshot;
- per-processor timeout is still armed before invocation;
- synchronous invocation/then attachment failures are caught explicitly;
- caught failure clears the timeout and enters the existing per-processor result list;
- existing outer error-array rejection shape remains;
- focused tests assert later invocation, stable opening membership, exact one-error shape, and no timer leak.

### Logs

Accepted: public mutable processor array is snapshotted; direct calls are protected; timeout behavior remains.

### Metrics

Accepted: collector list is snapshotted; async collector methods are called directly; redundant helper and non-reversing throw tests are absent.

### Test isolation

Accepted: trace aggregate test restores `loggingErrorHandler()` correctly.

## Source cleanliness

- [x] one commit directly on current public main;
- [x] eight target-native source/test files only;
- [x] no workflows, publishers, lock/dependency files, generated output, or research vocabulary;
- [x] package-specific claims match actual async boundaries;
- [x] public provider trace force flush is included;
- [x] public main remained identical to the base during repair;
- [x] open duplicate/overlap searches found no replacement work;
- [ ] final exact-head workflow matrix complete;
- [ ] eligible independent reviewer accepts exact head;
- [ ] required changelog entries added with real public PR number.

## Exact-head workflows

Queued on `59f83f889bed06a951d458556b2e7e1695cbea10`:

- Unit `30694080939`;
- E2E `30694080935`;
- Lint `30694080925`;
- Bundler `30694080933`;
- W3C `30694080910`;
- API peer dependency `30694080929`;
- CodeQL `30694080926`;
- Zizmor `30694080955`.

Prior green heads are historical only.

## Compatibility review

- API/types unchanged;
- eager fanout retained;
- trace aggregate shutdown rejection and force-flush report/resolve behavior retained;
- trace provider error-array rejection retained;
- logs and metrics rejection retained;
- provider timeout behavior changes only by clearing a timer that no longer owns useful work after synchronous failure;
- future mutation remains visible;
- first-rejection/first-result policies remain.

## Independent reviewer guide

1. Verify the provider try/catch preserves the existing result-array contract and clears only its own timeout.
2. Verify provider and aggregate snapshots are both necessary because their force-flush paths are distinct.
3. Verify logs timeout wrapping is unchanged.
4. Verify metrics remains snapshot-only.
5. Verify all eight tests reverse a real source mechanism or protect compatibility/isolation.

## Remaining blockers

1. final-head workflows are queued;
2. independent exact-head acceptance is pending;
3. two changelog entries need the real upstream PR number;
4. current-main/duplicate/policy checks must be repeated immediately before filing;
5. public upstream contact remains unauthorized.

## Reviewer eligibility

Technical self-review only. It can find and require repair but cannot serve as independent final acceptance.
