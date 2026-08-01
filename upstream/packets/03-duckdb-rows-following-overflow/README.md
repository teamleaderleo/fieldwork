# Unit 03 — fix(window): saturate ROWS FOLLOWING overflow at partition end

## In simple words

DuckDB computes a `ROWS ... FOLLOWING` frame start by adding the requested offset to the current row number. With the largest signed 64-bit offset, that addition overflows for later rows. The current overflow path resets the frame start to the partition beginning, turning a frame wholly beyond the partition into the whole partition.

The bounded correction sends the overflowing start to the current partition end. Historical native execution passed the repair. Current-main Debug execution compiles and passes the focused regression. The original red window gate came from a bare directory filter. A corrected full wildcard then exposed three unrelated `.test_slow` cases that exceeded the bounded Debug runner's 600-second timeout. The current successor runs every regular window SQLLogicTest, matching DuckDB's pull-request policy for a regular `.test` change.

DuckDB's contribution policy asks contributors to avoid LLM-generated pull requests. Any eventual public candidate therefore requires independent human derivation, authorship or reimplementation, and review.

## Current disposition

`EXECUTE / HOLD`

Last verified: `2026-08-01`  
Worker: `OpenAI assistant, self-review only`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Public upstream contact authorized: `no`

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
- Canonical source head: `63094a6f725af5045113dda74e291c7d604f6a88` — exact public base while publication remains gated
- Packet branch: `teamleaderleo/fieldwork:p0/435-unit-03-duckdb-rows-following-overflow`
- Packet head: latest exact head is recorded on packet PR `#452` and the latest `#435` handoff
- Packet review surface: [`teamleaderleo/fieldwork#452`](https://github.com/teamleaderleo/fieldwork/pull/452)
- Execution carrier: [`teamleaderleo/duckdb#17`](https://github.com/teamleaderleo/duckdb/pull/17)
- Current carrier head: `243ff3929f34fa904bb96699005ac6848aab7f38`
- Current successor run/job: `30692119355` / `91348557949`
- Historical carriers: [`teamleaderleo/duckdb#8`](https://github.com/teamleaderleo/duckdb/pull/8), [`teamleaderleo/fieldwork#253`](https://github.com/teamleaderleo/fieldwork/pull/253)

## Current code and tests

### Product code

- [Current upstream source at `63094a6f...`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/function/window/window_boundaries_state.cpp#L720-L731) — the overflow branch assigns `partition_begin_data[chunk_idx]`.
- [Historical exact one-line patch](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/fieldwork/window_rows_following_overflow.patch) — assigns `partition_end_data[chunk_idx]`.
- The canonical source branch remains the exact public base until the current gates pass.

### Target-native tests

- [Historical exact regression](https://github.com/teamleaderleo/duckdb/blob/2cfe22d250f5501a097b5f994ca01498513b939c/test/sql/window/test_rows_following_overflow.test) — extreme frame, ordinary control, partition isolation.
- [Current carrier copy](https://github.com/teamleaderleo/duckdb/blob/243ff3929f34fa904bb96699005ac6848aab7f38/fieldwork/unit_03_test_rows_following_overflow.test) — materialized into the current-main worktree.

## Intended changed-file fence

| Path | Role |
| --- | --- |
| `src/function/window/window_boundaries_state.cpp` | production |
| `test/sql/window/test_rows_following_overflow.test` | regression |

The current carrier collects tracked and untracked paths, sorts them, and diffs the result against this exact two-file list before any build.

## Evidence summary

| Claim | Evidence | Result and limit |
| --- | --- | --- |
| Baseline defect reproduces | Fieldwork run `30580996108`; report head `735a2e184bc6039c64a341449d01977f4091311e` | historical source; rows one and two expand to the whole partition |
| One-line repair passes focused controls | owned run `30595242656` | historical source; execution-applied patch |
| Current main retains the same fallback | source at `63094a6f...` | source inspection |
| Current-main candidate compiles | runs `30674257475` and `30689967043` | pass; materialized worktrees |
| Current-main focused regression | run `30689967043`, job `91342817226` | `1 passed, 0 skipped in 3s` |
| Bare-directory gate classification | run `30674257475`, corrected by wildcard run `30689967043` | invocation issue |
| Full wildcard diagnostic | run `30689967043` | three unrelated `.test_slow` cases exceeded 600 seconds; job reached 60 minutes |
| Diagnostic artifact | artifact `8815977625` | digest `sha256:69ceb3c4720921b31b7b6c3ee03c61df4319fadc19538120cf0b1f5be6bd7642` |
| Ordinary regular window suite | successor `30692119355` | queued at this packet revision |
| Formatting and clean publication | same successor | gated behind regular suite |

## Slow-test classification

The diagnostic wildcard selected every window test, including `.test_slow` files. The retained log records 600-second timeouts for:

- `test/sql/window/window_partition_paging.test_slow`
- `test/sql/window/test_fill.test_slow`
- `test/sql/window/test_quantile_window.test_slow`

DuckDB's current Main workflow sets `run_slow_tests=true` for pull requests when `.test_slow` files change; unit 03 changes production source plus a regular `.test`. The current ordinary command is therefore:

```text
./build/fieldwork/test/run 'test/sql/window/*.test'
```

The carrier separately records every excluded `.test_slow` path.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue record](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Existing public issue: `duckdb/duckdb#24307`, open and reproduced at the last check
- Searches: issue number, title terms, symbol, and overflow wording
- Equivalent implementation found: `no`
- Relationship: independent repair research for an existing public issue

## Remaining work

1. Complete successor run `30692119355`: exact fence, Debug build, focused regression, every regular window SQLLogicTest, formatting, and publisher.
2. Inspect the published source compare and commit-pinned product/test files if every gate passes.
3. Update packet links, exact heads, review checklist, PR draft, and `#435` handoff.
4. Require an independent human to derive, author or reimplement, and review any public candidate; obtain exact authority before contact.

## Blockers and limits

- The current successor is waiting for or using an Actions runner at this packet revision.
- Three unchanged `.test_slow` cases exceed the bounded Debug diagnostic budget; their exact names and output are retained.
- Full `make unit`, `make allunit`, release/relassert, and platform matrices remain outside the current bounded carrier.
- DuckDB's contribution guide asks contributors to avoid LLM-generated pull requests.
- Public upstream contact is unauthorized.

## Latest handoff

State: `EXECUTE / HOLD`  
Exact source head: `63094a6f725af5045113dda74e291c7d604f6a88` on `teamleaderleo/duckdb:fix/window-rows-following-overflow`; exact public base while gates execute  
Exact carrier head: `243ff3929f34fa904bb96699005ac6848aab7f38`  
Exact successor: run `30692119355`, job `91348557949`  
Tests: historical baseline reproduced; historical repair passed; current-main compile passed twice; current-main focused regression passed in three seconds; full wildcard classified three unrelated slow timeouts; ordinary regular window suite pending  
Temporary machinery: `teamleaderleo/duckdb#17`, `exec/unit-03-window-overflow-materialize`, historical `teamleaderleo/duckdb#8`, accidental Fieldwork branch `dummy-no`  
Next action: settle run `30692119355`, inspect the exact source head if published, and synchronize every durable handoff  
Public upstream interaction: `none`
