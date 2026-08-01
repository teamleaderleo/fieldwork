# Review — Unit 11: stabilize lifecycle fanout targets

## Subject

- target: `open-telemetry/opentelemetry-js`;
- base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact source head: `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- validation carrier: owned draft PR #19;
- relation: six commits ahead, zero behind;
- boundary: three production files and three tests;
- public upstream authority: none.

## Disposition

`HOLD — complete successor repair applied; exact-head validation pending`

The metrics overclaim is removed, and the separate public `TracerProvider.forceFlush()` path is included. This self-review finds no additional product defect in the successor six-file diff. It is not independent final acceptance.

## Complete-diff findings

### `MultiSpanProcessor`

Accepted: opening snapshots, eager safe-call, original aggregate promise/error structure retained, and throw/removal tests present.

### `TracerProvider.forceFlush()`

Accepted repaired direction:

- public provider bypasses aggregate force flush and needs its own opening snapshot;
- per-processor timeout remains armed before invocation;
- eager safe-call converts a direct throw into a rejected processor result;
- the existing catch clears the timeout and records the error;
- existing outer error-array rejection remains;
- tests assert later invocation, opening membership, exact one-error shape, and zero timer leak.

### Logs

Accepted: the retained public processor array is snapshotted, direct calls are protected, and timeout behavior remains.

### Metrics

Accepted exclusion: no supported post-construction collector mutation path was found; the prior tests used private-state casts; async collector methods already normalize reader throws.

### Test isolation

Accepted: aggregate trace cleanup restores `loggingErrorHandler()`.

## Source cleanliness

- [x] direct child of current public main;
- [x] six target-native source/test files only;
- [x] no metrics, workflows, publishers, lock/dependency files, generated output, or research vocabulary;
- [x] public provider trace force flush included;
- [x] public main and duplicate searches refreshed during repair;
- [ ] exact successor workflow matrix complete;
- [ ] contents-API commits squashed;
- [ ] eligible independent reviewer accepts exact head;
- [ ] required changelog entries added with real public PR number.

## Exact-head workflows

Triggered on `a1e604526ea87fc22a91f6b2fe84b02f528e9f88`:

- Unit `30694086716`;
- CodeQL `30694086713`;
- W3C `30694086725`;
- Zizmor `30694086726`;
- API peer dependency `30694086723`;
- Bundler `30694086727`;
- E2E `30694086733`;
- Lint `30694086746`.

Prior green heads are historical only.

## Compatibility review

- API/types unchanged;
- eager fanout retained;
- aggregate trace shutdown rejection and force-flush report/resolve behavior retained;
- provider error-array rejection retained;
- logs rejection and timeout behavior retained;
- provider timeout changes only by clearing a timer after synchronous failure;
- future mutation remains visible.

## Independent reviewer guide

1. Verify provider safe-call preserves the current result-array contract and clears only its own timeout.
2. Verify provider and aggregate snapshots are both necessary because their force-flush paths are distinct.
3. Verify logs timeout wrapping is unchanged.
4. Verify metrics exclusion is justified by supported reachability.
5. Verify all ten focused assertions reverse a source mechanism or protect compatibility/isolation.

## Remaining blockers

1. successor workflows must settle;
2. independent exact-head acceptance is pending;
3. six source commits should be squashed;
4. two changelog entries need the real upstream PR number;
5. current-main, duplicate, and policy checks must be repeated immediately before filing;
6. public upstream contact remains unauthorized.

## Reviewer eligibility

Technical self-review only. It can require repair and record evidence but cannot serve as independent final acceptance.
