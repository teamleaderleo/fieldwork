# Upstream pull-request draft — fix(window): saturate ROWS FOLLOWING overflow at partition end

Draft status: `held — independent human authorship required by target policy`  
Research branch: `teamleaderleo/duckdb:fix/window-rows-following-overflow`  
Proposed base: `duckdb/duckdb:main` from inspected revision `63094a6f725af5045113dda74e291c7d604f6a88`  
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

Research execution retained so far:

- historical native baseline reproduction;
- historical one-line repaired focused pass;
- current-main Ubuntu Debug native runner build;
- current-main focused regression: `1 passed, 0 skipped in 3s`;
- diagnostic full wildcard, which identified three unchanged `.test_slow` timeout cases;
- current ordinary PR-equivalent gate: every regular `test/sql/window/*.test` plus `make format-check`, run `30692119355`.

DuckDB's current Main workflow enables slow tests on pull requests when `.test_slow` files change. This contribution adds a regular `.test`; the carrier records the excluded slow-test inventory separately.

Before public submission, the human author should rerun the current project-required gates on the independently authored candidate and replace this section with exact final receipts.

## Compatibility

- public API: unchanged
- ordinary bounded behavior: covered by `1 FOLLOWING`
- partition behavior: covered with independent partitions
- runtime mechanism: uses the existing checked signed-add helper and partition-bound vectors
- allocation: unchanged
- migration or rollback: one-line revert and test removal

## Alternatives considered

- A shared saturating arithmetic helper would pull PRECEDING and other boundary modes into the same change.
- Wider intermediate arithmetic would widen type and conversion review.
- A second issue would duplicate #24307.

## Limits

- Production frequency is unmeasured.
- Current research execution is Ubuntu Debug.
- Full unit, release/relassert, and platform matrices remain for an eligible human-owned candidate.
- Three unchanged `.test_slow` files exceeded the bounded Debug diagnostic budget; the ordinary PR-equivalent suite excludes them according to the target workflow condition.
- This generated research branch itself must stay outside public submission under DuckDB's current generative-AI policy.

## Related work

- duckdb/duckdb#24307

---

## Submission checklist

- [ ] A human independently derives, authors or reimplements, and owns the candidate.
- [ ] Branch is a direct child or clean rebase of a recent upstream head.
- [ ] Diff contains only production source and target-native tests.
- [ ] Temporary workflows, patch carriers, and Fieldwork-only files are absent.
- [ ] Every changed file is reviewed at the exact proposed head.
- [x] Focused regression fails on baseline and passes on the research candidate.
- [ ] Ordinary regular window suite and formatting pass on the final human candidate.
- [ ] Project-declared complete gates requested by maintainers run and are recorded.
- [x] Current duplicate and overlap search found the existing issue and no implementation PR.
- [ ] Commit history and title follow current target conventions.
- [x] Target contribution and AI policy were checked.
- [ ] Exact user authorization to contact public upstream is recorded.
