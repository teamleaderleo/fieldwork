# Upstream pull-request draft — fix(window): saturate ROWS FOLLOWING overflow at partition end

Draft status: `not ready — independent human authorship required by target policy`  
Proposed head: `teamleaderleo/duckdb:fix/window-rows-following-overflow` as a research reference only  
Proposed base: `duckdb/duckdb:main` from `63094a6f725af5045113dda74e291c7d604f6a88`  
Public interaction authorized: `no`

A human preparing an eligible submission should independently derive or reimplement the change, review every line, rerun the target gates, and use this text only after confirming it describes that human-owned candidate.

---

## Summary

- Saturate an overflowing `ROWS ... FOLLOWING` frame start at the current partition end.
- Add SQLLogicTest coverage for the extreme signed offset, ordinary following behavior, and independent partitions.

## Problem

`WindowBoundariesState::FrameBegin` computes an expression-based following start by adding the offset to the current row index. When this signed 64-bit addition overflows, the current fallback selects the partition beginning. The corresponding frame end saturates at the partition end, so the resulting frame covers the whole partition even though the requested frame lies beyond it.

The public reproduction in issue #24307 returns counts of three and lists every row for later rows in `range(3)`. Those frames should be empty.

## Change

Use `partition_end_data[chunk_idx]` when the `EXPR_FOLLOWING_ROWS` start addition overflows. The existing common clamp then keeps both frame bounds at the current partition end.

The test covers:

- `9223372036854775807 FOLLOWING` for both frame bounds;
- ordinary `1 FOLLOWING` behavior;
- two partitions, ensuring the overflow sentinel comes from each current partition.

## Tests

- `./build/fieldwork/test/run 'test/sql/window/test_rows_following_overflow.test'`
- `./build/fieldwork/test/run 'test/sql/window'`
- `make format-check`

Before submission, the human author should also run the current project-required unit and CI gates and replace these commands with the exact executed receipts.

## Compatibility

- public API: unchanged
- existing behavior retained: ordinary bounded following frames are covered by the regression
- platform or runtime notes: uses the existing checked signed-add helper and partition-bound vectors
- performance or allocation notes: replaces one array read with another on the overflow branch; no allocation
- migration or rollback: one-line revert and test removal

## Alternatives considered

- A shared saturating arithmetic helper would pull PRECEDING and other boundary modes into the same change.
- Wider intermediate arithmetic would widen type and conversion review.
- A second issue would duplicate #24307.

## Limits

- Production frequency is unmeasured.
- The research carrier covers Ubuntu and the window test directory; the eligible human candidate needs the project-requested complete gates.
- This generated branch itself must not be submitted under DuckDB's current generative-AI policy.

## Related work

- duckdb/duckdb#24307

---

## Submission checklist

- [ ] A human independently authors or reimplements and owns the candidate.
- [ ] Branch is a direct child or clean rebase of a recent upstream head.
- [ ] Diff contains only production source and target-native tests.
- [ ] Temporary workflows, patch carriers, and Fieldwork-only files are absent.
- [ ] Every changed file is reviewed at the exact proposed head.
- [ ] Focused regression fails on baseline and passes on candidate.
- [ ] Project-declared ordinary gates run and are recorded.
- [x] Current duplicate and overlap search found the existing issue and no implementation PR.
- [ ] Commit history and title follow current target conventions.
- [x] Target contribution and AI policy were checked.
- [ ] Exact user authorization to contact public upstream is recorded.
