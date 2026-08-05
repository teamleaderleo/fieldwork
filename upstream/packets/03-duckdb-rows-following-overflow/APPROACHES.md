# Approaches — unit 03 ROWS FOLLOWING overflow

## In simple words

The selected product repair changes one overflow fallback from the partition beginning to the partition end. It follows the meaning of a following frame that has moved beyond every row and matches the existing frame-end overflow treatment. Broader arithmetic refactors widen the review without evidence of a second defect.

The test-gate work also produced two useful losing approaches: a bare directory filter and a full wildcard that included unchanged slow tests. The current gate follows DuckDB's pull-request policy for a regular `.test` change.

## Decision criteria

1. A frame start beyond a partition produces an empty frame.
2. Ordinary bounded following frames and partition isolation stay unchanged.
3. The repair lives where `ROWS` frame starts are computed.
4. The source diff contains only the production line and target-native regression.
5. The ordinary gate matches DuckDB's current pull-request test selection.
6. No extra allocation, public API change, or broad window refactor.

## Selected product approach

### Saturate the overflowing FOLLOWING start at the current partition end

- Design: in `FrameBegin`, change the `TryAddOperator` failure fallback for `EXPR_FOLLOWING_ROWS` from `partition_begin_data[chunk_idx]` to `partition_end_data[chunk_idx]`.
- Owning boundary: `WindowBoundariesState::FrameBegin`.
- Evidence: historical native repair run `30595242656`; current-main focused pass in `30689967043`.
- Advantages: one-line product change, per-partition correctness, direct symmetry with frame-end overflow, easy review and revert.
- Cost: relies on partition end as the internal empty-frame sentinel; target-native tests cover that contract.

## Selected regression

Add `test/sql/window/test_rows_following_overflow.test` with:

1. `INT64_MAX FOLLOWING` for both frame bounds, expecting empty frames;
2. ordinary `1 FOLLOWING`, preserving next-row behavior;
3. two partitions, verifying row-local partition-end saturation.

## Selected current-main gate

Run:

- an exact two-file materialization fence that includes tracked and untracked paths;
- Ubuntu 24.04 Debug native `unittest` build;
- the exact focused regression;
- every regular `test/sql/window/*.test`;
- `make format-check`;
- clean two-file publication only after every gate succeeds.

DuckDB's current Main workflow enables slow tests on pull requests when `.test_slow` files change. Unit 03 adds a regular `.test`. The carrier records the excluded slow paths separately.

## Viable product alternatives

### Shared saturating row-boundary helper

Centralize signed add/subtract conversion and saturation for all `ROWS` frame boundaries.

Advantages:

- one arithmetic policy;
- potential future consistency.

Costs:

- expands scope into PRECEDING and other branches without a reproduced defect;
- raises regression and review cost;
- hides the one-line causal correction.

Reopening trigger: a native regression demonstrates another arithmetic fallback is wrong.

### Wider intermediate arithmetic

Compute in a wider integer type and clamp afterward.

Advantages:

- represents the mathematical sum before clamping;
- may reduce explicit overflow branches.

Costs:

- widens type and conversion review;
- adds compiler/platform considerations;
- offers little benefit over the existing checked-add contract.

Reopening trigger: maintainers request a general boundary-arithmetic model.

### Clamp through a synthetic maximum

Assign the largest `idx_t` on overflow and rely on common clamping.

Advantages:

- reuses the clamp path.

Costs:

- weakens the direct row-local partition invariant;
- adds conversion concerns;
- reads less clearly than assigning partition end.

## Executed losing gate approaches

### Bare directory filter

```text
./build/fieldwork/test/run 'test/sql/window'
```

Run `30674257475` failed without a retained exact failure. The accepted explicit wildcard in run `30689967043` classified the bare directory as an unsuitable filter.

Useful evidence retained: materialization, Debug build, and focused regression passed.

### Full wildcard inside a bounded Debug job

```text
./build/fieldwork/test/run 'test/sql/window/*'
```

Run `30689967043` passed the focused candidate test in three seconds, then selected unchanged `.test_slow` cases. Three slow tests exceeded the wrapper's 600-second timeout, and the job reached its 60-minute limit.

Artifact `8815977625`, digest `sha256:69ceb3c4720921b31b7b6c3ee03c61df4319fadc19538120cf0b1f5be6bd7642`, retains the exact partial output.

Useful evidence retained:

- wildcard selection works;
- candidate test passes on current main;
- exact slow-test capacity limits are known;
- always-run artifact retention works.

Reason superseded: DuckDB's ordinary pull-request path for a regular `.test` change excludes unchanged `.test_slow` files.

### Synthetic Main carrier merge

Historical Main run `30595243144` contained the regression but lacked the production patch in the synthetic merge. The regression failed with the baseline result while 252 smoke tests passed.

Useful evidence retained: baseline reversal and proof that the test catches the defect.

Reason superseded: it did not evaluate the repaired source.

## Rejected product approaches

### Saturate at partition beginning

This is the defective behavior. It converts a frame beyond the partition into the whole partition.

### Saturate at global input end

A global sentinel can cross partition boundaries. The required invariant is row-local partition containment.

### Change SQL frame semantics or parser validation

The offset is a valid signed 64-bit value. The defect is execution arithmetic, so parser rejection would alter valid SQL behavior and avoid the causal correction.

### File a second public issue

Public issue `duckdb/duckdb#24307` already records the reproduction.

### Submit the generated research branch

DuckDB's current contribution guide asks contributors to avoid LLM-generated pull requests. A human must independently derive, author or reimplement, and review the change.

## Prior work

| Link | Approach | Status | Relationship |
| --- | --- | --- | --- |
| `duckdb/duckdb#24307` | exact public reproduction | open | public problem record |
| `teamleaderleo/duckdb#8` | test plus execution-applied patch | historical carrier | evidence source |
| `teamleaderleo/fieldwork#253` | immutable reproduction report | retained | exact receipt |
| `teamleaderleo/duckdb#17` | current-main materialization and gates | active | current execution carrier |

## Deferred work

- full `make unit` and `make allunit`;
- release and relassert complete suites;
- macOS and Windows execution;
- broader arithmetic-helper cleanup;
- production prevalence measurement;
- public issue comment or pull request.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | `de477da...`, run `30580996108` | accept defect | exact native baseline result and ordinary control | baseline no longer reproduces |
| 2026-07-31 | carrier `2cfe22d...`, run `30595242656` | select partition-end fallback | focused repair passed with one-line change | current-main candidate failure or maintainer contract conflict |
| 2026-08-01 | run `30674257475` | reject bare directory filter | unusable suite selection and no retained failure | explicit test specification |
| 2026-08-01 | run `30689967043`, artifact `8815977625` | retain wildcard diagnostic, supersede as ordinary gate | focused pass plus unrelated slow-test timeouts | `.test_slow` source change or dedicated slow-suite run |
| 2026-08-01 | carrier `243ff392...`, run `30692119355` | select regular window PR-equivalent gate | aligns with target workflow for regular `.test` changes | target policy change or successor failure |

Public work remains behind independent human authorship/reimplementation, review, and explicit contact authority.
