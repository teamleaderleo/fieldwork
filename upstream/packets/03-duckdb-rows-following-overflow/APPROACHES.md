# Approaches — unit 03 ROWS FOLLOWING overflow

## In simple words

The selected repair changes one overflow fallback from the partition beginning to the partition end. It follows the meaning of a following frame that has moved beyond all rows and matches the existing frame-end overflow treatment. Broader arithmetic refactors offer little value for this bounded defect. The technical direction leads; upstream submission remains paused for independent human authorship under DuckDB's contribution policy.

## Decision criteria

1. A frame start beyond a partition must produce an empty frame.
2. Ordinary bounded following frames and partition isolation must stay unchanged.
3. The repair should live where `ROWS` frame starts are computed.
4. The upstream diff should contain only the production line and target-native regression.
5. No extra allocation, public API change, or broad window refactor.

## Selected approach

### Saturate the overflowing FOLLOWING start at the current partition end

- Design: in `FrameBegin`, change the `TryAddOperator` failure fallback for `EXPR_FOLLOWING_ROWS` from `partition_begin_data[chunk_idx]` to `partition_end_data[chunk_idx]`.
- Owning boundary: `WindowBoundariesState::FrameBegin`.
- Evidence: historical native repair run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656); current-main clean run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475).
- Advantages: one-line product change, per-partition correctness, direct symmetry with frame-end overflow, easy review and revert.
- Costs and risks: relies on partition end as the internal empty-frame sentinel; target-native tests cover that contract.
- Remaining controls: current-main affected-suite and formatting completion; independent human authorship before any upstream submission.

## Viable alternatives

### Introduce a shared saturating row-boundary helper

- Design: centralize signed add/subtract conversion and saturation for all `ROWS` frame boundaries.
- Why it remains plausible: several branches perform related arithmetic.
- What it would improve: consistency and a single place for overflow policy.
- What it would widen or complicate: PRECEDING start/end semantics, current-row `+1` handling, and unrelated branches would enter the same review.
- Exact discriminator: evidence of a second incorrect branch that requires the same atomic contract.
- Reopening trigger: a new native regression demonstrates another arithmetic fallback is wrong.

### Compute in a wider integer type before clamping

- Design: use a wider signed or unsigned intermediate and clamp after conversion.
- Why it remains plausible: it can represent `row_idx + INT64_MAX` for practical relation sizes.
- What it would improve: fewer explicit overflow branches.
- What it would widen or complicate: type conversion rules, negative boundary validation, platform/compiler support, and all row-boundary paths.
- Exact discriminator: maintainers prefer a general arithmetic model over a local correction.
- Reopening trigger: project direction or existing wide-integer utility makes the change smaller than the local fix.

## Executed losing approaches

### Keep the patch as an execution-only carrier

- Exact branch, patch, or commit: `fieldwork/window-rows-following-overflow@2cfe22d250f5501a097b5f994ca01498513b939c`.
- What ran: a workflow applied the patch at execution time and ran the focused repair test.
- Result: candidate behavior passed, while the PR diff still lacked production source.
- Why it lost: the branch was unsuitable as a clean review or continuation surface.
- Useful evidence retained: focused native success, baseline red result from the synthetic merge, and exact historical test.

### Treat the generic Main workflow failure as a product failure

- Exact branch, patch, or commit: synthetic merge `914d14b862136fab1b7b4fc8c6d68bf3e55789ab` for owned PR `#8`.
- What ran: DuckDB smoke CI with the regression file but without applying the retained source patch.
- Result: 252 tests passed and the intended regression failed with the exact baseline whole-partition result.
- Why it lost: the execution topology tested the baseline carrier, not the repaired product source.
- Useful evidence retained: a reversing baseline control on DuckDB's ordinary CI runner.

## Rejected easy answers

### Clamp overflow to zero or the global input end

- Temptation: use a generic numeric sentinel.
- Why it is incomplete or unsafe: frames are partition-local; global values can cross partition boundaries or depend on later clamping in opaque ways.
- Negative control or source fact: the state already supplies each row's exact `partition_end_data`.

### Remove only the regression test from the carrier

- Temptation: treat the historical custom workflow success as sufficient.
- Why it is incomplete or unsafe: reviewers need the target-native test and production source together on one clean head.
- Negative control or source fact: owned PR `#8` changed only a workflow, patch artifact, and test.

### File a second public issue

- Temptation: satisfy an issue-first expectation before code review.
- Why it is incomplete or unsafe: public issue [`duckdb/duckdb#24307`](https://github.com/duckdb/duckdb/issues/24307) already contains the exact reproduction and remains open.
- Negative control or source fact: duplicate searches found no separate implementation PR.

### Submit the generated branch upstream

- Temptation: the diff is small and technically supported.
- Why it is incomplete or unsafe: DuckDB's current `CONTRIBUTING.md` asks contributors to avoid LLM-generated pull requests. A human must independently author or reimplement and review the change.
- Negative control or source fact: current policy at upstream commit `63094a6f...`.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`duckdb/duckdb#24307`](https://github.com/duckdb/duckdb/issues/24307) | exact public reproduction | open, reproduced | public problem record; no implementation |
| [`teamleaderleo/duckdb#8`](https://github.com/teamleaderleo/duckdb/pull/8) | test plus execution-applied patch | historical carrier | evidence source; superseded by clean branch |
| [`teamleaderleo/fieldwork#253`](https://github.com/teamleaderleo/fieldwork/pull/253) | immutable reproduction report | open retained record | prior-art and exact receipt |

## Deferred adjacent work

- Audit every `ROWS` arithmetic fallback — separate unit unless another defect is demonstrated.
- Consider wider boundary arithmetic — design-level change requiring maintainer direction.
- Add platform matrix coverage — valuable only after an eligible human-authored candidate exists.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | `de477da...`, run `30580996108` | accept defect | exact native baseline result and ordinary control | baseline no longer reproduces |
| 2026-07-31 | carrier `2cfe22d...`, run `30595242656` | select partition-end fallback | focused repair passed with one-line change | current-main failure or maintainer contract conflict |
| 2026-08-01 | upstream `63094a6f...`, current policy | disposition `HOLD` | source still affected; AI-generated PR policy requires human authorship | independent human implementation/review or policy change |
