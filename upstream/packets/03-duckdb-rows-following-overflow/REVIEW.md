# Review — unit 03 ROWS FOLLOWING overflow

## In simple words

The intended candidate changes one overflow fallback and adds one SQLLogicTest file. Historical native execution and focused current-main Debug execution support the correction. The first current-main suite command used a bare directory filter. A corrected wildcard accepted the suite and retained its output; the candidate test passed in three seconds, while three unchanged `.test_slow` cases exceeded the bounded Debug timeout.

DuckDB's current pull-request workflow runs slow tests when a `.test_slow` file changes. Unit 03 adds a regular `.test`, so the controlling successor runs every regular window SQLLogicTest and records the excluded slow inventory. Public submission also requires independent human derivation, authorship or reimplementation, and review under DuckDB's contribution policy.

## Review subject

- Work class: upstream-fork research
- Target repository: `duckdb/duckdb`
- Proposed upstream base: `63094a6f725af5045113dda74e291c7d604f6a88`
- Canonical source branch: `teamleaderleo/duckdb:fix/window-rows-following-overflow`
- Exact source head: `63094a6f725af5045113dda74e291c7d604f6a88` — exact public base while gates execute
- Fieldwork packet branch: `p0/435-unit-03-duckdb-rows-following-overflow`
- Exact packet head: packet PR `#452` and latest `#435` handoff carry the exact current value
- Intended changed-file fence: `src/function/window/window_boundaries_state.cpp`; `test/sql/window/test_rows_following_overflow.test`
- Current carrier: `teamleaderleo/duckdb#17` at `243ff3929f34fa904bb96699005ac6848aab7f38`
- Current successor run/job: `30692119355` / `91348557949`
- Diagnostic run/job: `30689967043` / `91342817226`
- Diagnostic artifact: `8815977625`, digest `sha256:69ceb3c4720921b31b7b6c3ee03c61df4319fadc19538120cf0b1f5be6bd7642`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact carrier patch and test
6. diagnostic artifact and successor run
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact links

- clean source compare: [`63094a6f...` to `fix/window-rows-following-overflow`](https://github.com/teamleaderleo/duckdb/compare/63094a6f725af5045113dda74e291c7d604f6a88...fix/window-rows-following-overflow) — empty while publication is gated
- historical production patch: [`2cfe22d...`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch)
- current carrier test: [`243ff392...`](https://github.com/teamleaderleo/duckdb/blob/243ff3929f34fa904bb96699005ac6848aab7f38/fieldwork/unit_03_test_rows_following_overflow.test)
- diagnostic run: [`30689967043`](https://github.com/teamleaderleo/duckdb/actions/runs/30689967043)
- successor run: [`30692119355`](https://github.com/teamleaderleo/duckdb/actions/runs/30692119355)
- generated or dependency files: none intended

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| partition end is the correct overflow fallback | source symmetry, historical run `30595242656`, current focused pass | Does any valid `ROWS FOLLOWING` interpretation require another sentinel? |
| one production line is sufficient | current source map and exact baseline output | Is another reachable ROWS arithmetic branch part of the same defect? |
| ordinary focused behavior remains stable | `1 FOLLOWING` and partition controls | Does the successor regular window suite stay green? |
| partition isolation is preserved | two-partition focused test | Does clamping always use the row-local partition end? |
| slow-test diagnostic is unrelated | artifact `8815977625`; unchanged `.test_slow` paths; focused pass | Do the three timeouts reveal any candidate dependency, or only bounded Debug capacity? |
| ordinary gate matches target policy | DuckDB Main workflow `run_slow_tests` condition | Is `test/sql/window/*.test` the correct PR-equivalent affected suite for this regular test change? |
| upstream submission requires human reimplementation | current DuckDB `CONTRIBUTING.md` | Has an independent human derived, authored, reviewed, and defended the eventual diff? |

## Diagnostic classification

Run `30689967043` passed materialization, Debug build, and the focused regression. The focused log reports `1 passed, 0 skipped in 3s`.

The full wildcard log records 600-second timeouts for:

- `test/sql/window/window_partition_paging.test_slow`
- `test/sql/window/test_fill.test_slow`
- `test/sql/window/test_quantile_window.test_slow`

The job reached its 60-minute limit during that suite. Artifact `8815977625` preserves the exact product patch, focused output, changed-file receipt, and partial suite output. This result classifies the prior red state as a combination of the original bare-directory invocation and unrelated slow-test capacity in the corrected diagnostic.

## Known risks

- The successor regular suite could expose a genuine adjacent regression.
- The clean source branch currently contains the public base, so candidate links remain pending.
- Full unit, release/relassert, and platform matrices remain outside the bounded carrier.
- A technically green generated research branch remains ineligible for public submission under target policy.

## Evidence limits

- Current execution is Ubuntu Debug only.
- Slow `.test_slow` cases remain excluded from the ordinary PR-equivalent gate and are explicitly inventoried.
- Complete DuckDB unit and all-unit suites remain unexecuted on a final head.
- No maintainer feedback has been requested or received.
- Production prevalence is unmeasured.

## Staleness check

- Current upstream head checked: `63094a6f725af5045113dda74e291c7d604f6a88` on `2026-08-01`
- Candidate relationship: materialized directly over that exact base
- Defective fallback semantics changed since historical execution: no
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: no implementation PR; public issue `#24307` remains open
- Packet and carrier descriptions synchronized: yes through diagnostic run `30689967043` and successor `30692119355`

## Source cleanliness

- [x] Canonical source branch has no Fieldwork-only files.
- [x] Canonical source branch has no temporary workflows or publishers.
- [x] Canonical source branch has no stale execution artifacts.
- [x] Canonical source branch has no unrelated churn.
- [x] Required snapshots or lock changes are inapplicable.
- [ ] Commit-pinned candidate links exist — pending publisher success.

## Test review

- [x] Historical intended assertion ran.
- [x] Current-main focused assertion ran and passed twice.
- [x] Baseline/candidate relationship is clear.
- [x] Bare-directory invocation was classified.
- [x] Full wildcard diagnostic retained exact slow-test timeout output.
- [x] Ordinary and partition controls are present.
- [x] Platform and integration limits are explicit.
- [x] Exact two-file fence now includes the untracked regression.
- [ ] Successor regular window suite passes.
- [ ] Formatting passes on the materialized candidate.
- [ ] A clean exact candidate head is published and reviewed.

## Draft review

- [x] Existing public issue prevents a duplicate issue draft.
- [x] PR draft describes the intended two-file correction.
- [x] Target terminology is used.
- [x] Public draft excludes internal process links.
- [x] AI policy was checked directly.
- [ ] Draft test section is refreshed from the final successor receipt.
- [ ] Human author and exact public-contact authority exist.

## Reviewer disposition

`EXECUTE / HOLD`

Reviewed source head: `63094a6f725af5045113dda74e291c7d604f6a88`  
Reviewed carrier head: `243ff3929f34fa904bb96699005ac6848aab7f38`  
Reason: the focused current-main candidate is green, and the prior suite failures are classified. The successor regular window suite, formatting, publication, and exact candidate review remain. Independent human authorship and review remain mandatory for public use.  
Technical clearing condition: successor `30692119355` passes exact fencing, Debug build, focused regression, every regular window SQLLogicTest, formatting, and publication; then inspect the exact two-file source head.  
Public clearing condition: eligible human derivation/authorship or reimplementation, independent review, and explicit contact authority.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The next reviewer should focus on:

1. the exact successor suite and formatting output;
2. the final two-file compare and commit-pinned test;
3. whether partition end is the correct overflow sentinel in every affected partition case;
4. independently deriving and owning any eventual public diff under DuckDB policy.

Suggested response:

`Unit 03 successor classified: <exact result>; source head: <SHA>; human ownership: <status>`
