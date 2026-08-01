# Review — Unit 11: stabilize lifecycle fanout targets

## Subject

- target: `open-telemetry/opentelemetry-js`;
- base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact source head: `f4910b355d12895edf25372444f76d4def08901c`;
- validation carrier: PR #19;
- relation: one commit ahead, zero behind;
- boundary: three production files and three tests;
- public upstream authority: none.

## Disposition

`HOLD — complete supported-path repair validating`

The prior metrics repair is superseded by a narrower conclusion: metrics did not have a supported public mutation path. The successor removes metrics and adds the public trace-provider force-flush path. No further product issue was found in the exact six-file self-review. Independent final acceptance remains required.

## Complete-diff findings

### `MultiSpanProcessor`

Accepted: snapshot retained caller-supplied array; eager safe-call; original aggregate error structure retained; throw/removal tests present.

### `TracerProvider.forceFlush()`

Accepted:

- provider bypasses aggregate force flush and needs its own snapshot;
- helper converts synchronous processor throws into rejected promises;
- existing `.catch()` clears the per-processor timeout and records the error;
- outer collected-error-array contract remains;
- tests assert later invocation, stable opening set, rejection shape, and no timer leak.

### `MultiLogRecordProcessor`

Accepted: public retained processor array is snapshotted; direct calls are protected; timeout behavior remains; throw/removal tests present.

### Metrics exclusion

Accepted:

- provider creates an internal collector list instead of retaining the readers array;
- prior tests spliced private state;
- collector lifecycle methods are async;
- no metrics source/test file belongs in the upstream contribution.

### Test isolation

Accepted: aggregate trace cleanup installs `loggingErrorHandler()` correctly.

## Source cleanliness

- [x] one commit directly on current public main;
- [x] six target-native source/test files only;
- [x] no metrics/private-state controls;
- [x] no workflows, publishers, lock/dependency files, generated output, or research vocabulary;
- [x] public provider force flush included;
- [x] public main matched the base during repair;
- [x] refreshed overlap searches found no equivalent open work;
- [ ] successor exact-head matrix complete;
- [ ] eligible independent reviewer accepts exact head;
- [ ] required changelog entries added with real PR number.

## Exact-head workflows

Queued on `f4910b355d12895edf25372444f76d4def08901c`:

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

## Compatibility review

- API/types unchanged;
- eager fanout retained;
- aggregate trace shutdown rejects;
- aggregate trace force flush reports globally and resolves;
- provider trace force flush retains error-array rejection;
- logs retain rejection/timeout behavior;
- future mutation remains visible;
- provider timer cleanup changes only a timer with no remaining owner after synchronous failure.

## Independent reviewer guide

1. Verify provider safe-call feeds the existing `.catch()` and preserves error-array output.
2. Verify aggregate and provider snapshots are separately necessary.
3. Verify logs timeout wrapping is unchanged.
4. Verify metrics removal is justified by ownership/public-path analysis.
5. Verify all ten focused tests reverse a supported mechanism or protect compatibility/isolation.

## Remaining blockers

1. successor workflows are queued;
2. independent exact-head acceptance is pending;
3. root and experimental changelog entries need the real upstream PR number;
4. current-main/duplicate/policy checks must be repeated at filing time;
5. public upstream contact remains unauthorized.

## Reviewer eligibility

Technical self-review only; not independent final acceptance.
