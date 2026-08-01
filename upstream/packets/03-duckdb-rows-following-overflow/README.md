# Unit 03 — fix(window): saturate ROWS FOLLOWING overflow at partition end

## In simple words

DuckDB computes a `ROWS ... FOLLOWING` frame start by adding the requested offset to the current row number. With the largest signed 64-bit offset, that addition overflows for later rows. The overflow path resets the frame start to the beginning of the partition, turning a frame wholly beyond the partition into the whole partition.

The bounded correction sends the overflowing start to the current partition end. Historical native execution passed the focused repair. Current-main execution also passed the focused regression, then the complete `test/sql/window` gate failed. The publisher withheld the clean two-file commit. DuckDB's current contribution policy also asks contributors to avoid LLM-generated pull requests, so any eventual public contribution requires independent human derivation, authorship or reimplementation, and review.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `OpenAI assistant, self-review only`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target: `duckdb/duckdb` `main`
- Proposed title: `fix(window): saturate ROWS FOLLOWING overflow at partition end`
- Intended change: on signed-add overflow for an `EXPR_FOLLOWING_ROWS` frame start, use the row's partition end instead of its partition beginning; add a SQLLogicTest for the extreme offset, ordinary `1 FOLLOWING`, and independent partitions.
- Work class: `upstream-fork research`

## Exact identities

- Current public base inspected: `63094a6f725af5045113dda74e291c7d604f6a88`
- Historical reproducing source: `de477da7606fc2d857f81117f0140d0550a5c42c`
- Clean base branch: `teamleaderleo/duckdb:fieldwork/base-duckdb-63094a6-clean`
- Canonical source branch: `teamleaderleo/duckdb:fix/window-rows-following-overflow`
- Canonical source head: `63094a6f725af5045113dda74e291c7d604f6a88` — clean upstream source; candidate publication withheld after the complete window gate failed
- Packet branch: `teamleaderleo/fieldwork:p0/435-unit-03-duckdb-rows-following-overflow`
- Packet head: recorded in the latest `#435` handoff because this file cannot contain its own commit SHA
- Packet review surface: [`teamleaderleo/fieldwork#452`](https://github.com/teamleaderleo/fieldwork/pull/452)
- Current execution carrier: [`teamleaderleo/duckdb#17`](https://github.com/teamleaderleo/duckdb/pull/17), head `bf703f57b15555c2db68520b1f4165e23ca737ae`
- Historical carriers: [`teamleaderleo/duckdb#8`](https://github.com/teamleaderleo/duckdb/pull/8), [`teamleaderleo/fieldwork#253`](https://github.com/teamleaderleo/fieldwork/pull/253)

## Current code and tests

### Product code

- [Current upstream source at `63094a6f...`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L720-L731) — the overflow branch still assigns `partition_begin_data[chunk_idx]`.
- [Historical exact one-line patch](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch) — assigns `partition_end_data[chunk_idx]` instead.
- Current clean source branch contains upstream source only because the current-main publisher stopped after the red window-directory gate.

### Target-native tests

- [Historical exact regression](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/test/sql/window/test_rows_following_overflow.test) — extreme frame, ordinary control, partition isolation.
- [Current carrier copy](https://github.com/teamleaderleo/duckdb/blob/bf703f57b15555c2db68520b1f4165e23ca737ae/fieldwork/unit-03/test_rows_following_overflow.test) — materialized into the current-main worktree for run `30674257475`.

## Intended changed-file fence

| Path | Role |
| --- | --- |
| `src/function/window/window_boundaries_state.cpp` | production |
| `test/sql/window/test_rows_following_overflow.test` | regression |

## Evidence summary

| Claim | Evidence | Result and limit |
| --- | --- | --- |
| Baseline defect reproduces | Fieldwork run `30580996108`; report head `735a2e184bc6039c64a341449d01977f4091311e` | historical source `de477da...`; rows 1 and 2 expand to the whole partition |
| One-line repair passes focused controls | owned run `30595242656` | historical source; execution-applied patch |
| Current main retains the same fallback | source at `63094a6f...` | source-read only |
| Current-main materialized candidate compiles | run `30674257475`, job `91298115859` | pass; runner worktree only |
| Current-main focused regression | same run/job | pass |
| Complete `test/sql/window` | same run/job | fail; exact failing case remains unextracted from the connector-visible receipt |
| Formatting and clean publication | same workflow | skipped after suite failure |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue record](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Existing public issue: `duckdb/duckdb#24307`, open, reproduced, zero comments at the last check
- Searches: issue number, title terms, symbol, and overflow wording
- Equivalent implementation found: `no`
- Relationship: independent repair research for an existing public issue

## Remaining work

1. Extract or reproduce the exact failing case from `test/sql/window` on the same current-main two-file worktree.
2. Repair the candidate or gate invocation as evidence requires; rerun focused regression, complete `test/sql/window`, and `make format-check`.
3. Publish and inspect a clean two-file source head only after every gate passes.
4. Require an independent human to derive, author or reimplement, and review any public candidate; obtain exact authority before public contact.

## Blockers and limits

- Run `30674257475` passed compilation and focused regression, then failed complete `test/sql/window`; formatting and publication were skipped.
- The connector-visible receipt identified the failed step but did not expose the exact failing test/output during this session.
- DuckDB's contribution guide asks contributors to avoid LLM-generated pull requests.
- Public upstream contact is unauthorized.
- Full `make unit`, `make allunit`, release/relassert, and platform matrices remain unexecuted on a clean candidate head.

## Latest handoff

State: `HOLD`  
Exact source head: `63094a6f725af5045113dda74e291c7d604f6a88` on `teamleaderleo/duckdb:fix/window-rows-following-overflow`; clean base only  
Exact packet head: latest comment on `teamleaderleo/fieldwork#435`  
Tests: historical baseline reproduced; historical focused repair passed; current-main Debug compile passed; current-main focused regression passed; complete `test/sql/window` failed; formatting and publisher skipped  
Temporary machinery: `teamleaderleo/duckdb#17`, `exec/unit-03-window-overflow-materialize`, historical `teamleaderleo/duckdb#8`, accidental Fieldwork branch `dummy-no`  
Next action: obtain the exact `test/sql/window` failure from run `30674257475` or reproduce it on the same two-file worktree, then repair/rerun before publishing a candidate head  
Public upstream interaction: `none`
