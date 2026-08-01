# Upstream pull-request draft — fix(window): saturate ROWS FOLLOWING overflow at partition end

Draft status: `not ready — complete window gate red; independent human authorship required`  
Proposed head: a future human-owned branch; `teamleaderleo/duckdb:fix/window-rows-following-overflow` currently remains at clean base `63094a6f725af5045113dda74e291c7d604f6a88`  
Proposed base: current `duckdb/duckdb:main` after a fresh rebase and duplicate check  
Public interaction authorized: `no`

A human preparing an eligible submission should independently derive or reimplement the correction, review every line, reproduce and resolve the complete-window failure from research run `30674257475`, rerun current target gates, and use this draft only after confirming it describes the human-owned candidate.

---

## Summary

- Saturate an overflowing `ROWS ... FOLLOWING` frame start at the current partition end.
- Add SQLLogicTest coverage for the extreme signed offset, ordinary following behavior, and independent partitions.

## Problem

`WindowBoundariesState::FrameBegin` computes an expression-based following start by adding the offset to the current row index. When this signed 64-bit addition overflows, the current fallback selects the partition beginning. The corresponding frame end saturates at the partition end, so the resulting frame covers the whole partition even though the requested frame lies beyond it.

The existing public reproduction returns counts of three and lists every row for later rows in `range(3)`. Those frames should be empty.

## Change

Use `partition_end_data[chunk_idx]` when the `EXPR_FOLLOWING_ROWS` start addition overflows. The existing common clamp then keeps both frame bounds at the current partition end.

The test covers:

- `9223372036854775807 FOLLOWING` for both frame bounds;
- ordinary `1 FOLLOWING` behavior;
- two partitions, ensuring the overflow sentinel comes from each current partition.

## Research test receipts

- Historical focused native repair run `30595242656`: pass.
- Current-main Debug compile in run `30674257475`, job `91298115859`: pass.
- Current-main focused regression: pass.
- Current-main complete `test/sql/window`: fail; exact failing case remains to be extracted or reproduced.
- Current-main `make format-check`: skipped after the failed suite.
- Clean publisher: skipped; canonical source branch remains the upstream base.

## Required tests before any public submission

- focused regression on the exact human-owned head;
- complete `test/sql/window` with the current red case resolved and recorded;
- `make format-check`;
- current project-required unit and CI gates;
- relevant platform/build matrix chosen by the human author.

## Compatibility

- public API: unchanged
- existing behavior retained: ordinary bounded following frames are covered by the focused regression
- platform or runtime notes: uses the existing checked signed-add helper and partition-bound vectors
- performance or allocation notes: replaces one array read with another on the overflow branch; no allocation
- migration or rollback: one-line revert and test removal

## Alternatives considered

- A shared saturating arithmetic helper would pull PRECEDING and other boundary modes into the same change.
- Wider intermediate arithmetic would widen type and conversion review.
- A second issue would duplicate the existing public issue.

## Limits

- The complete current-main window suite is red and unresolved.
- Production frequency is unmeasured.
- Research execution covers Ubuntu Debug plus historical native execution.
- This generated research branch itself must never be submitted under DuckDB's current generative-AI policy.

## Related work

- Existing public issue: `duckdb/duckdb#24307`

---

## Submission checklist

- [ ] A human independently derives, authors or reimplements, and owns the candidate.
- [ ] The exact current window-directory failure is identified and resolved.
- [ ] Branch is a direct child or clean rebase of a fresh upstream head.
- [ ] Diff contains only production source and target-native tests.
- [ ] Temporary workflows, patch carriers, and Fieldwork-only files are absent.
- [ ] Every changed file is reviewed at the exact proposed head.
- [ ] Focused regression fails on baseline and passes on candidate.
- [ ] Complete `test/sql/window` passes on the exact candidate head.
- [ ] Formatting and project-declared ordinary gates pass and are recorded.
- [x] Current duplicate and overlap search found the existing issue and no implementation PR.
- [ ] Commit history and title follow current target conventions.
- [x] Target contribution and AI policy were checked.
- [ ] Exact user authorization to contact public upstream is recorded.
