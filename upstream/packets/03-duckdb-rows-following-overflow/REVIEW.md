# Review — unit 03 ROWS FOLLOWING overflow

## In simple words

The intended candidate changes one overflow fallback and adds one SQLLogicTest file. The source argument, historical native execution, and focused current-main execution support the correction. The complete current-main window directory failed, so the clean branch stayed at the upstream base. A reviewer must identify and classify that failure before accepting the technical candidate. Public submission also requires independent human authorship or reimplementation under DuckDB's current contribution policy.

## Review subject

- Work class: upstream-fork research
- Target repository: `duckdb/duckdb`
- Proposed upstream base: `63094a6f725af5045113dda74e291c7d604f6a88`
- Canonical source branch: `teamleaderleo/duckdb:fix/window-rows-following-overflow`
- Exact source head: `63094a6f725af5045113dda74e291c7d604f6a88` — clean base only
- Fieldwork packet branch: `p0/435-unit-03-duckdb-rows-following-overflow`
- Exact packet head: latest exact head is recorded in the final `teamleaderleo/fieldwork#435` handoff
- Intended changed-file fence: `src/function/window/window_boundaries_state.cpp`; `test/sql/window/test_rows_following_overflow.test`
- Current carrier: `teamleaderleo/duckdb#17` at `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Current run/job: `30674257475` / `91298115859`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. current carrier patch and test
6. run `30674257475`
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact links

- clean source compare: [`63094a6f...` to `fix/window-rows-following-overflow`](https://github.com/teamleaderleo/duckdb/compare/63094a6f725af5045113dda74e291c7d604f6a88...fix/window-rows-following-overflow) — empty because publication was withheld
- historical one-line production patch: [`2cfe22d...`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch)
- current carrier test: [`bf703f57...`](https://github.com/teamleaderleo/duckdb/blob/bf703f57b15555c2db68520b1f4165e23ca737ae/fieldwork/unit-03/test_rows_following_overflow.test)
- current run: [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475)
- generated or dependency files: none intended

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| partition end is the correct overflow fallback | source symmetry, historical run `30595242656`, current focused pass | Does any valid `ROWS FOLLOWING` interpretation require a different sentinel? |
| one production line is sufficient | current source map and exact baseline output | Is there another reachable ROWS arithmetic branch requiring atomic correction? |
| ordinary focused behavior remains stable | `1 FOLLOWING` and partition controls | Did the red complete-window case expose related behavior? |
| partition isolation is preserved | two-partition focused test | Does clamping always use the row-local partition end? |
| clean publication was correctly withheld | run `30674257475` | Was the window-directory failure product-related, flaky, environmental, or an invocation issue? |
| upstream submission requires human reimplementation | current DuckDB `CONTRIBUTING.md` | Has an independent human derived, authored, reviewed, and defended the eventual diff? |

## Known risks

- The exact failing test/output from the complete window-directory run remains unextracted from the connector-visible receipt.
- The focused test could pass while an adjacent existing window case catches a behavioral regression.
- The clean source branch currently contains no candidate, so branch links cannot serve as candidate evidence.
- A technically repaired generated candidate remains ineligible for public submission under the target's stated policy.

## Evidence limits

- Current clean-source worktree execution is Ubuntu Debug only.
- Complete DuckDB unit and all-unit suites remain unexecuted on a final head.
- No maintainer feedback has been requested or received.
- Production prevalence is unmeasured.

## Staleness check

- Current upstream head checked: `63094a6f725af5045113dda74e291c7d604f6a88` on `2026-08-01`
- Candidate base relationship: materialized directly over that exact base; unpublished
- Relevant source path changed semantically since historical execution: no for the defective fallback
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: no implementation PR; public issue `#24307` remains open
- Packet and target review descriptions synchronized: yes after run `30674257475`

## Source cleanliness

- [x] Canonical source branch has no Fieldwork-only files.
- [x] Canonical source branch has no temporary workflows or publishers.
- [x] Canonical source branch has no stale execution artifacts.
- [x] Canonical source branch has no unrelated churn.
- [x] Required snapshots or lock changes are not applicable.
- [ ] Commit-pinned candidate links exist — blocked because publication was withheld.

## Test review

- [x] Historical intended assertion ran.
- [x] Current-main focused assertion ran and passed.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated where evidence permits.
- [x] Ordinary and partition controls are present.
- [x] Platform and integration limits are explicit.
- [x] Complete window-directory gate ran.
- [ ] Exact complete-window failure is identified and classified.
- [ ] Formatting ran on the materialized candidate.
- [ ] A clean exact candidate head was published and reviewed.

## Draft review

- [x] Existing public issue prevents a duplicate issue draft.
- [x] PR draft describes the intended two-file correction and current red gate.
- [x] Target terminology is used.
- [x] Public draft excludes internal process links.
- [x] AI policy was checked directly.
- [ ] Human author and exact public-contact authority exist.

## Reviewer disposition

`HOLD`

Reviewed source head: `63094a6f725af5045113dda74e291c7d604f6a88`  
Reviewed packet input head: packet branch after current-main receipt update  
Reason: the focused current-main regression passes, while the complete window-directory gate fails and the exact case remains unresolved. The clean source branch correctly contains no candidate commit. Independent human authorship and review remain required for any eventual public submission.  
Clearing condition: identify and classify the window-directory failure, repair or rerun as evidence requires, pass focused plus full window plus formatting, publish and review an exact two-file head, then obtain eligible human authorship and contact authority.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The next reviewer should focus on:

1. extracting the exact failing test and output from run `30674257475` or reproducing the same materialized worktree;
2. deciding whether the red suite exposes a candidate regression or a gate/harness issue;
3. confirming partition end remains the correct overflow sentinel after that analysis;
4. independently deriving and owning any eventual public diff under DuckDB policy.

Suggested response:

`Unit 03 failure classified: <exact test and cause>; next action: <repair or rerun>`
