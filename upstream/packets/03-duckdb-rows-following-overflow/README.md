# Unit 03 — fix(window): saturate ROWS FOLLOWING overflow at partition end

## In simple words

DuckDB computes a `ROWS ... FOLLOWING` frame start by adding the requested offset to the current row number. With the largest signed 64-bit offset, that addition overflows for later rows. The overflow path currently resets the frame start to the beginning of the partition, which turns a frame wholly beyond the partition into the whole partition. The bounded repair sends that start to the current partition end, matching the existing overflow treatment for the frame end and yielding an empty frame.

A minimal native regression already passed on the historical reproducing revision. A clean current-main candidate is executing in the owned fork. The contribution remains on `HOLD` because DuckDB's current contribution policy asks contributors to avoid LLM-generated pull requests. A human must independently author or reimplement and review any upstream submission.

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

- Public upstream base inspected: [`duckdb/duckdb@63094a6f725af5045113dda74e291c7d604f6a88`](https://github.com/duckdb/duckdb/commit/63094a6f725af5045113dda74e291c7d604f6a88)
- Owned target fork: [`teamleaderleo/duckdb`](https://github.com/teamleaderleo/duckdb)
- Canonical source branch: [`fix/window-rows-following-overflow`](https://github.com/teamleaderleo/duckdb/tree/fix/window-rows-following-overflow)
- Canonical source head: pending current-main execution run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475)
- Fieldwork packet branch: [`p0/435-unit-03-duckdb-rows-following-overflow`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-03-duckdb-rows-following-overflow/upstream/packets/03-duckdb-rows-following-overflow)
- Fieldwork packet head: exact current head is recorded in the latest `#435` handoff; this file cannot contain the SHA of its own commit.
- Execution carriers: [`teamleaderleo/duckdb#17`](https://github.com/teamleaderleo/duckdb/pull/17), historical [`teamleaderleo/duckdb#8`](https://github.com/teamleaderleo/duckdb/pull/8)
- Superseded carriers: historical test-and-workflow carrier `teamleaderleo/duckdb#8` after receipt transfer

## Current code and tests

### Product code

- [Current upstream `WindowBoundariesState::FrameBegin` at `63094a6f...`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L720-L731) — the overflow branch still assigns `partition_begin_data[chunk_idx]`.
- [Current owned source branch](https://github.com/teamleaderleo/duckdb/blob/fix/window-rows-following-overflow/src/function/window/window_boundaries_state.cpp) — commit-pinned candidate link will replace this branch link after publication.

### Target-native tests

- [Historical exact regression at `2cfe22d...`](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/test/sql/window/test_rows_following_overflow.test) — exact extreme frame, ordinary control, and partition-isolation control.
- [Current owned source branch test](https://github.com/teamleaderleo/duckdb/blob/fix/window-rows-following-overflow/test/sql/window/test_rows_following_overflow.test) — commit-pinned candidate link will replace this branch link after publication.

### Required generated or dependency files

- Not applicable.

## Changed-file fence

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
| The current-main clean candidate passes focused and ordinary affected-suite gates | `integration-executed` | current run [`30674257475`](https://github.com/teamleaderleo/duckdb/actions/runs/30674257475) | pending at this packet revision |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues/PRs checked: [`duckdb/duckdb#24307`](https://github.com/duckdb/duckdb/issues/24307), PR searches for issue number, title terms, symbol, and overflow wording
- Equivalent implementation found: `no`
- Relationship to prior work: `independent repair candidate for an already public reproduced issue`

## Remaining work

Complete in this order:

1. Finish current-main focused regression, complete `test/sql/window`, and formatting execution.
2. Publish and inspect the exact clean two-file source head.
3. Require an independent human to author or reimplement and review any upstream candidate under DuckDB's current generative-AI policy; obtain exact authority before any public contact.

## Blockers and limits

- DuckDB's current `CONTRIBUTING.md` says: “Please do not submit pull requests generated by AI (LLMs).” This candidate therefore serves as research and a human handoff, not a submission-ready branch.
- Public upstream contact is unauthorized.
- Full `make unit`, all-unit, and platform matrix execution remain outside the current focused carrier unless later run by an eligible human-authored branch.

## Latest handoff

State: `HOLD`  
Exact source head: pending run `30674257475`  
Exact packet head: recorded in the latest comment on `teamleaderleo/fieldwork#435`  
Tests: historical reproduction and focused repaired execution complete; current-main build and affected-suite run in progress  
Temporary machinery remaining: `teamleaderleo/duckdb#17` and its workflow; historical carrier `teamleaderleo/duckdb#8` awaiting retirement after final transfer  
Next worker action: inspect run `30674257475`, record its exact source head, then close the execution carriers and require human authorship before upstream preparation  
Public upstream interaction: `none`
