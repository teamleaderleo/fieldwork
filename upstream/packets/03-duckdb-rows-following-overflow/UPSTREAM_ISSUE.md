# Upstream issue record — ROWS ... FOLLOWING gives incorrect non-empty frames

Draft status: `not applicable — exact public issue already exists`  
Public interaction authorized: `no`

---

## Existing public record

DuckDB issue [`#24307`](https://github.com/duckdb/duckdb/issues/24307), “ROWS ... FOLLOWING gives incorrect non-empty frames,” already contains the exact `INT64_MAX FOLLOWING` reproduction, observed whole-partition result, DuckDB revision, and environment. At the 2026-08-01 check it remained open, carried the `reproduced` label, and had zero comments.

A second issue would duplicate the public report. No comment, reaction, assignment, or other upstream interaction occurred during this unit.

## Summary

For ordered `ROWS` frames, adding the largest signed 64-bit following offset to later row positions overflows. The current frame-start fallback selects the partition beginning. The frame end selects the partition end, producing a non-empty whole-partition frame where the requested frame lies beyond the partition.

## Reproduction

1. Build or run DuckDB from a revision containing the current `WindowBoundariesState::FrameBegin` fallback.
2. Execute the query below.
3. Inspect rows one and two.

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

## Observed behavior

```text
0  0  NULL
1  3  [0, 1, 2]
2  3  [0, 1, 2]
```

The result was reproduced through DuckDB's native test runner on source `de477da7606fc2d857f81117f0140d0550a5c42c`. Current public main at `63094a6f725af5045113dda74e291c7d604f6a88` still contains the same fallback.

## Expected behavior

```text
0  0  NULL
1  0  NULL
2  0  NULL
```

Every frame lies beyond the partition and should be empty.

## Current source observation

In `WindowBoundariesState::FrameBegin`, the `EXPR_FOLLOWING_ROWS` branch uses `TryAddOperator`. When the add fails, it assigns the row's partition beginning to `window_start`. `FrameEnd` uses the row's partition end for its corresponding overflow branch. The common clamp therefore retains a full-partition range.

## Candidate direction

Use the row's partition end as the overflow fallback for the following frame start. Add a SQLLogicTest covering:

- the exact extreme offset;
- ordinary `1 FOLLOWING` behavior;
- independent partitions.

## Compatibility and risks

- Public API and stored formats remain unchanged.
- The change affects the signed-add overflow branch only.
- A broad arithmetic helper could alter unrelated PRECEDING, RANGE, or GROUPS paths and should stay separate.

## Evidence limits

- Production frequency is unmeasured.
- Current-main Ubuntu execution is tracked in owned run `30674257475`.
- Full unit, all-unit, and platform matrices remain outside the current research carrier.

## Versions and environment

- project version or commit: reproduced at `de477da...`; source reconfirmed at `63094a6f...`
- platform: GitHub Actions Ubuntu; original public report lists macOS
- runtime/compiler: DuckDB native C++ test runner
- relevant configuration: ordered window over `range(3)`

## Additional context

- Existing issue: [`duckdb/duckdb#24307`](https://github.com/duckdb/duckdb/issues/24307)

---

## Filing checklist

- [x] Current upstream issue and PR search repeated.
- [x] Existing issue contains the exact reproduction.
- [x] Severity and prevalence wording stays within evidence.
- [x] A duplicate filing is avoided.
- [x] Public interaction remains absent without authority.
- [x] Target contribution and generative-AI policy checked.
- [ ] Any future public comment receives exact user authorization and independent human review.
