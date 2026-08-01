# Review — Unit 11: stabilize lifecycle fanout targets

## Subject

- target: `open-telemetry/opentelemetry-js`;
- base/current main: `2c931bf4eec18a234a28706567c6977f08139abd`;
- exact source head: `f4910b355d12895edf25372444f76d4def08901c`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- validation carrier: owned draft PR #19;
- relation: one commit ahead, zero behind;
- boundary: three production files and three tests;
- public upstream authority: none.

## Disposition

`HOLD — complete squashed repair applied; exact-head validation pending`

The metrics overclaim is removed, and the separate public `TracerProvider.forceFlush()` path is included. This self-review finds no additional product defect in the exact six-file diff. It is not independent final acceptance.

## Findings

### Aggregate trace

Accepted: opening snapshots, eager safe-call, original shutdown rejection and force-flush global-report/resolve structure, and direct-throw/removal tests.

### Public provider trace

Accepted:

- provider bypasses aggregate force flush and needs its own snapshot;
- safe-call routes synchronous failure into the existing catch;
- that catch clears the per-processor timeout and records the error;
- existing outer error-array rejection remains;
- tests assert later invocation, opening membership, one-error shape, and zero timer leak.

### Logs

Accepted: retained public processor array is snapshotted; direct calls are protected; timeout behavior remains.

### Metrics

Accepted exclusion: no supported post-construction collector mutation path was found; prior tests used private-state casts; async collector methods already normalize reader throws.

### Source cleanliness

- [x] one commit directly on current public main;
- [x] six target-native source/test files only;
- [x] no metrics or non-product residue;
- [x] public provider path included;
- [x] duplicate/current-main checks refreshed during repair;
- [ ] exact workflow matrix complete;
- [ ] eligible independent reviewer accepts exact head;
- [ ] changelog entries added with real public PR number.

## Exact-head workflows

- Unit `30694264703`;
- W3C `30694264710`;
- Bundler `30694264711`;
- API peer dependency `30694264708`;
- CodeQL `30694264717`;
- E2E `30694264735`;
- Zizmor `30694264748`;
- Lint `30694264729`.

## Independent reviewer guide

1. Verify provider safe-call preserves its result-array contract and clears only its own timeout.
2. Verify provider and aggregate snapshots are independently necessary.
3. Verify logs timeout wrapping is unchanged.
4. Verify metrics exclusion follows supported reachability.
5. Verify the ten focused tests reverse source mechanisms or protect compatibility/isolation.

## Remaining blockers

Exact workflows, independent acceptance, root/experimental changelog entries, final current-main/duplicate/policy refresh, and public-contact authority.

## Reviewer eligibility

Technical self-review only; not independent final acceptance.
