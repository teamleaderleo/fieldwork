# Unit 03 — fix(window): saturate ROWS FOLLOWING overflow at partition end

## In simple words

DuckDB computes a `ROWS ... FOLLOWING` frame start by adding the requested offset to the current row number. With the largest signed 64-bit offset, that addition overflows for later rows. The overflow path resets the frame start to the beginning of the partition, which turns a frame wholly beyond the partition into the whole partition.

The bounded correction sends the overflowing start to the current partition end. Historical native execution passed the focused repair. Current-main execution also passed the focused regression, then the complete `test/sql/window` gate failed. The publisher correctly withheld the clean two-file commit. DuckDB's current contribution policy also asks contributors to avoid LLM-generated pull requests, so any eventual public contribution requires independent human authorship or reimplementation and review.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `OpenAI assistant, self-review only`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `duckdb/duckdb`
- Proposed upstream destination: `duckdb/duckdb` `main`
- Proposed title: `fix(window): saturate ROWS FOLLOWING overflow at partition end`
- Contribution synopsis: on signed-add overflow while computing an `EXPR_FOLLOWING_ROWS` frame start, use the row's partition end instead of its partition beginning; retain a SQLLogicTest covering the exact extreme offset, ordinary `1 FOLLOWING`, and independent partitions.
- Work class: `upstream-fork research`

## Exact identities

- Current public upstream base inspected: [`duckdb/duckdb@63094a6f725af5045113dda74e291c7d604f6a88`](https://github.com/duckdb/duckdb/commit/63094a6f725af5045113dda74e291c7d604f6a88)
- Historical reproducing source: [`duckdb/duckdb@de477da7606fc2d857f81117f0140d0550a5c42c`](https://github.com/duckdb/duckdb/commit/de477da7606fc2d857f81117f0140d0550a5c42c)
- Owned target fork: [`teamleaderleo/duckdb`](https://github.com/teamleaderleo/duckdb)
- Clean base branch: [`fieldwork/base-duckdb-63094a6-clean`](https://github.com/teamleaderleo/duckdb/tree/fieldwork/base-duckdb-63094a6-clean)
- Canonical source branch: [`fix/window-rows-following-overflow`](https://github.com/teamleaderleo/duckdb/tree/fix/window-rows-following-overflow)
- Canonical source head: `63094a6f725af5045113dda74e291c7d604f6a88` — clean upstream source; candidate publication was withheld after the complete window gate failed
- Fieldwork packet branch: [`p0/435-unit-03-duckdb-rows-following-overflow`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-03-duckdb-rows-following-overflow/upstream/packets/03-duckdb-rows-following-overflow)
- Fieldwork packet head: recorded in the latest `#435` handoff because this file cannot contain its own commit SHA
- Current execution carrier: [`teamleaderleo/duckdb#17`](https://github.com/teamleaderleo/duckdb/pull/17), carrier head `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Historical carriers: [`teamleaderleo/duckdb#8`](https://github.com/teamleaderleo/duckdb/pull/8), [`teamleaderleo/fieldwork#253`](https://github.com/teamleaderleo/fieldwork/pull/253)
- Packet review surface: [`teamleaderleo/fieldwork#453`](https://github.com/teamleaderleo/fieldwork/pull/453)

## Current code and tests

### Product code

- [Current upstream `WindowBoundariesState::FrameBegin` at `63094a6f...`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L720-L731) — the overflow branch still assigns `partition_begin_data[chunk_idx]`.
- [Historical exact one-line patch](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch) — changes that assignment to `partition_end_data[chunk_idx]`.
- Current clean source branch contains upstream source only because the current-main publisher stopped after the red window-directory gate.

### Target-native tests

- [Historical exact regression at `2cfe22d...`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/test/sql/window/test_rows_following_overflow.test) — exact extreme frame, ordinary control, and partition-isolation control.
- [Current carrier copy](https://github.com/teamleaderleo/duckdb/blob/bf703f57b15555c2db68520b1f4165e23ca737ae/fieldwork/unit-03/test_rows_following_overflow.test) — materialized into the current-main worktree for run `30674257475`.

### Required generated or dependency files

- Not applicable.

## Changed-file fence for an eligible human-owned candidate

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `src/function/window/window_boundaries_state.cpp` | production | yes |
| `test/sql/window/test_rows_following_overflow.test` | regression | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| The bug reproduces at the SQL result boundary | `target-executed` | Fieldwork run [`30580996108`](https://github.com/teamleaderleo/fieldwork/actions/runs/30580996108), report [`735a2e184bc6039c64a341449d01977f4091311e`](https://github.com/teamleaderleo/fieldwork/commit/735a2e184bc6039c64a341449d01977f4091311e) | historical source `de477da...` |
| The one-line saturation repair passes the focused regression and ordinary control | `target-executed` | owned-fork run [`30595242656`](https://github.com/teamleaderleo/duckdb/actions/runs/30595242656) | historical source and execution carrier |
| Current public main still contains the same fallback | `source-read` | [`63094a6f...` source](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L720-L731) | source inspection only |
| The materialized current-main candidate compiles and passes the focused regression | `target-executed` | run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475), job `91298115859` | candidate existed only in the runner worktree |
| The complete window-directory gate is green | `target-executed` | same run and job | failed; exact failing case remains unextracted from the connector-visible receipt |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issue checked: [`duckdb/duckdb#24307`](https://github.com/duckdb/duckdb/issues/24307), open, reproduced, zero comments at the last check
- PR searches checked: issue number, title terms, symbol, and overflow wording
- Equivalent implementation found: `no`
- Relationship to prior work: `independent repair candidate for an already public reproduced issue`

## Remaining work

Complete in this order:

1. Extract or reproduce the exact failing case from `test/sql/window` on the materialized current-main candidate and classify product overlap.
2. Repair the candidate or gate invocation as evidence requires, then rerun the focused regression, complete `test/sql/window`, and `make format-check`.
3. Publish and inspect an exact clean two-file source head only after every gate passes.
4. Require an independent human to author or reimplement and review any public candidate; obtain exact authority before public contact.

## Blockers and limits

- Current-main run `30674257475` passed compilation and the focused regression, then failed the complete `test/sql/window` gate. Formatting and publication were skipped by design.
- The connector-visible job receipt identifies the failed step but did not expose the exact failing test/output during this session.
- DuckDB's current `CONTRIBUTING.md` says: “Please do not submit pull requests generated by AI (LLMs).” This work is a research handoff, not a public submission candidate.
- Public upstream contact is unauthorized.
- Full `make unit`, `make allunit`, release/relassert, and platform matrices remain unexecuted on a clean candidate head.

## Latest handoff

State: `HOLD`  
Exact source head: `63094a6f725af5045113dda74e291c7d604f6a88` on `teamleaderleo/duckdb:fix/window-rows-following-overflow`; clean base only, no candidate commit published  
Exact packet head: recorded in the latest comment on `teamleaderleo/fieldwork#435`  
Tests: historical baseline reproduced; historical focused repair passed; current-main Debug compile passed; current-main focused regression passed; complete `test/sql/window` failed; formatting and publisher skipped  
Temporary machinery remaining: `teamleaderleo/duckdb#17`, `exec/unit-03-window-overflow-materialize`, historical `teamleaderleo/duckdb#8`, and accidental Fieldwork branch `dummy-no`  
Next worker action: obtain the exact `test/sql/window` failure from run `30674257475` or reproduce it on the same two-file worktree, then repair/rerun before publishing a candidate head  
Public upstream interaction: `none`
