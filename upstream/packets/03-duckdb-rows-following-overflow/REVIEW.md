# Review — unit 03 ROWS FOLLOWING overflow

## In simple words

The candidate changes one overflow fallback and adds one SQLLogicTest file. The source argument and historical native execution support the correction. A reviewer should challenge whether partition end is the correct empty-frame sentinel for every affected row and confirm the final current-main branch contains exactly the two intended files. Upstream submission stays paused because DuckDB's current policy asks contributors to avoid LLM-generated pull requests.

## Review subject

- Work class: upstream-fork research
- Target repository: `duckdb/duckdb`
- Proposed upstream base: `63094a6f725af5045113dda74e291c7d604f6a88`
- Canonical source branch: `teamleaderleo/duckdb:fix/window-rows-following-overflow`
- Exact source head: pending current-main execution publication
- Fieldwork packet branch: `p0/435-unit-03-duckdb-rows-following-overflow`
- Exact packet head: latest exact head is recorded in the final `teamleaderleo/fieldwork#435` handoff
- Complete changed-file fence: `src/function/window/window_boundaries_state.cpp`; `test/sql/window/test_rows_following_overflow.test`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact product diff
6. exact test diff
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: pending canonical source publication
- production file: [branch view](https://github.com/teamleaderleo/duckdb/blob/fix/window-rows-following-overflow/src/function/window/window_boundaries_state.cpp)
- test: [branch view](https://github.com/teamleaderleo/duckdb/blob/fix/window-rows-following-overflow/test/sql/window/test_rows_following_overflow.test)
- generated or dependency files: none

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| partition end is the correct overflow fallback | source symmetry plus run `30595242656` | Does any valid `ROWS FOLLOWING` interpretation require a different sentinel? |
| one production line is sufficient | current source map and exact baseline output | Is there a second frame-start or frame-end branch that must change atomically? |
| ordinary behavior remains stable | `1 FOLLOWING` control and complete window-directory plan | Does the final current-main window suite pass? |
| partition isolation is preserved | two-partition test | Does clamping ever use global input end instead of row-local partition end? |
| upstream submission requires human reimplementation | current DuckDB `CONTRIBUTING.md` | Has an independent human authored and defended the eventual submitted diff? |

## Known risks

- Current-main execution may expose source drift or a broader test failure.
- The current carrier's generic Main workflow can report failures unrelated to the clean candidate because carrier-only files are part of its synthetic merge.
- A generated candidate may appear technically ready while remaining ineligible for upstream submission under project policy.

## Evidence limits

- Current clean-source run is Ubuntu only.
- Complete DuckDB unit and all-unit suites remain unexecuted on the final head.
- No maintainer feedback has been requested or received.
- Production prevalence is unmeasured.

## Staleness check

- Current upstream head checked: `63094a6f725af5045113dda74e291c7d604f6a88` on `2026-08-01`
- Candidate base relationship: direct child intended
- Relevant source paths changed upstream since historical execution: yes, repository advanced; affected branch remained semantically unchanged
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: no; issue `#24307` only
- Packet and target PR descriptions synchronized: packet yes; canonical owned review PR pending source publication

## Source cleanliness

- [ ] No Fieldwork-only files in target source diff — verify after publication.
- [ ] No temporary workflows or publishers — verify after publication.
- [ ] No stale execution artifacts — verify after publication.
- [ ] No unrelated formatting or generated churn — verify exact compare.
- [x] Required snapshots or lock changes are not applicable.
- [ ] Commit-pinned links resolve to the reviewed head — add after publication.

## Test review

- [x] Historical intended assertion ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Cleanup paths are not applicable to the pure calculation.
- [x] Ordinary and partition controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Current-main focused and complete window results are recorded.

## Draft review

- [x] Issue record avoids a duplicate filing and avoids prevalence claims.
- [x] PR draft describes the intended two-file diff.
- [x] Target terminology is used.
- [x] Public draft text excludes internal process links.
- [x] AI policy was checked directly.

## Reviewer disposition

`HOLD`

Reviewed source head: pending  
Reviewed packet input head: packet branch current at review write  
Reason: technical evidence supports the local repair, while exact current-main execution and independent human authorship remain required.  
Clearing condition: current-main clean two-file execution passes, then an independent human authors or reimplements and reviews an eligible upstream candidate under DuckDB's policy.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether partition end is the correct sentinel for the overflowing start;
2. whether any related `ROWS` arithmetic branch needs the same correction;
3. whether the final clean head contains exactly two files and passes the complete window directory;
4. whether the human can independently derive, explain, and own the submission under target policy.

Suggested response:

`Unit 03 technical candidate is understood; I independently authored or reimplemented the eligible change`  
—or—  
`Unit 03 concern: <specific source, test, compatibility, or policy issue>`
