# Deep dive — unit 03 ROWS FOLLOWING overflow

## In simple words

A `ROWS` window frame uses row positions. DuckDB stores those positions in an unsigned index type but computes expression offsets through signed 64-bit arithmetic. For a frame start such as `9223372036854775807 FOLLOWING`, row zero reaches the largest signed value and later rows overflow. The current overflow fallback selects the partition beginning. The later frame-end calculation selects the partition end, so the resulting frame spans the whole partition. Selecting the partition end for the overflowing start makes both bounds meet at the correct empty position.

## Governing invariant

> A `ROWS ... FOLLOWING` frame whose start lies beyond the current partition must clamp to that partition's end and remain empty.

## Current behavior

- entrypoint: `WindowBoundariesState::FrameBegin`
- state owner: `WindowBoundariesState`, with per-row partition begin/end vectors
- caller-visible result: later rows return whole-partition aggregates for an extreme following offset
- side effects: none; result computation only
- cleanup owner: not applicable
- persistence or publication boundary: query result
- relevant concurrency, cancellation, retry, or failure ordering: none for the defect; the faulty path is deterministic signed-add overflow

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| frame start | [`src/function/window/window_boundaries_state.cpp`, `FrameBegin`, `63094a6f...`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L681-L813) | computes raw frame beginnings and clamps them to partition bounds | [`test_rows_following_overflow.test@2cfe22d...`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/test/sql/window/test_rows_following_overflow.test) |
| frame end | [`src/function/window/window_boundaries_state.cpp`, `FrameEnd`, `63094a6f...`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L818-L932) | computes raw frame endings; FOLLOWING overflow already selects partition end | same regression |
| clamp | `ClampFrame` call at the end of `FrameBegin` and `FrameEnd` | restricts computed indices to each row's partition | ordinary and partition controls in the same test |

## Reproduction or characterization

### Setup

- exact upstream revision: `de477da7606fc2d857f81117f0140d0550a5c42c`
- environment: GitHub Actions Ubuntu, DuckDB native `unittest` runner
- fixture or input: `range(3)` ordered by `i`
- command: native SQLLogicTest invocation retained in Fieldwork run `30580996108`

### Baseline result

Query:

```sql
SELECT i,
       count(*) OVER (
         ORDER BY i
         ROWS BETWEEN 9223372036854775807 FOLLOWING
                  AND 9223372036854775807 FOLLOWING
       ) AS cnt,
       list(i) OVER (
         ORDER BY i
         ROWS BETWEEN 9223372036854775807 FOLLOWING
                  AND 9223372036854775807 FOLLOWING
       ) AS members
FROM range(3) t(i)
ORDER BY i;
```

Expected:

```text
0  0  NULL
1  0  NULL
2  0  NULL
```

Observed on the baseline, repeatedly:

```text
0  0  NULL
1  3  [0, 1, 2]
2  3  [0, 1, 2]
```

The ordinary `1 FOLLOWING` control passed.

### Candidate result

The historical source-repair carrier passed the extreme regression and ordinary control in run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656). Current-main run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475) is the clean revalidation surface.

## Failure model

1. `row_idx` is converted to `int64_t`.
2. `boundary_begin.GetCell<int64_t>` returns `INT64_MAX`.
3. `TryAddOperator` fails for rows one and two.
4. The failure branch assigns `partition_begin_data[chunk_idx]` to `window_start`.
5. `FrameEnd` independently saturates its overflowing following endpoint to `partition_end_data[chunk_idx]`.
6. `ClampFrame` preserves the pair `[partition_begin, partition_end]`.
7. The aggregate receives the whole partition instead of an empty frame.

Steps 1–6 are confirmed by source. Step 7 is confirmed by native execution.

## Consequence and claim boundary

### Established

- The exact extreme offset produces incorrect non-empty frames on the pinned historical source.
- Current public main at `63094a6f...` still contains the same overflow fallback.
- A one-line fallback change passed the focused historical regression and ordinary control.
- The repair applies per row and uses that row's partition end.

### Inferred

- Any row where `row_idx + following_offset` overflows signed 64-bit arithmetic can enter the same fallback.
- The wrong whole-partition result can affect every aggregate that consumes the computed frame.

### Unknown or unmeasured

- Production prevalence.
- Full platform matrix behavior.
- Complete `make unit` and `make allunit` outcomes on the final current-main head.
- Maintainer preference for the exact test location or commit presentation.

## Selected implementation

The frame-start computation owns the invariant. Its `EXPR_FOLLOWING_ROWS` overflow branch already knows the row's `partition_end_data`; assigning that value gives the closest representable location consistent with “past the partition.” The later common clamp keeps the value within the current partition. The change touches no parser, binder, aggregate, storage, or public API path.

The regression contains three controls:

1. exact `INT64_MAX FOLLOWING` result;
2. ordinary `1 FOLLOWING` behavior;
3. two independent partitions, proving saturation uses each current partition end.

## Compatibility analysis

- public API: unchanged
- source compatibility: unchanged
- binary or wire compatibility: unchanged
- persistence or format compatibility: not applicable
- platform behavior: integer overflow helper and existing partition vectors; no platform-specific branch added
- performance and allocation: one existing array read replaces another on the rare overflow branch; no allocation
- cancellation, retry, and recovery: not applicable
- generated output: none
- migration or rollback: one-line revert plus test removal

## Adversarial and edge controls

- re-entry: not applicable
- concurrency: query-local deterministic calculation
- cancellation or interruption: outside this pure calculation
- failure before ownership transfer: not applicable
- failure after partial effect: not applicable
- cleanup failure: not applicable
- same-key or same-resource collision: not applicable
- unrelated-resource isolation: ordinary `1 FOLLOWING` control
- platform or runtime boundary: signed 64-bit overflow through `TryAddOperator`
- partition boundary: two-partition regression

## Review risks

- **Risk: partition end may be the wrong sentinel for a frame start.** The frame-end overflow path already uses partition end, and the common clamp accepts partition end as the empty boundary. The focused test confirms the result contract.
- **Risk: a shared saturating helper would be clearer.** The defect is one asymmetric fallback. A helper would widen review and could alter PRECEDING or RANGE/GROUPS semantics.
- **Risk: historical evidence has drifted.** Current-main source inspection finds the same branch, and run `30674257475` revalidates the clean patch against current upstream head.
- **Risk: the candidate cannot be sent upstream as authored.** DuckDB's current generative-AI policy requires a human-authored or independently reimplemented submission.

## Reversing evidence

The conclusion should be reopened if:

- a current-main native regression shows partition-end saturation produces a non-empty or cross-partition frame;
- maintainers define signed-overflow handling for `ROWS FOLLOWING` differently;
- current upstream replaces the branch with an equivalent repair;
- an independent human review identifies a second affected computation that must be fixed atomically.

## Adjacent work excluded

- `RANGE` and `GROUPS` boundary behavior
- `PRECEDING` overflow paths
- unsigned or wider internal boundary representations
- unrelated window executor refactors
- filing or commenting on the existing public issue without exact authority
