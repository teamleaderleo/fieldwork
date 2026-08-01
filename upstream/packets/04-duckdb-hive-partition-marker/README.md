# Unit 04 — DuckDB literal Hive default-partition marker

## Current disposition

**EXECUTE — implementation accepted for owner review**

The clean candidate is technically coherent, current, and ready for direct owner inspection. The formal `READY` gate waits for exact-head execution run `30696673877`, job `91360634513`, to leave the GitHub runner queue and complete.

Public-upstream authority is tracked separately. No public DuckDB interaction occurred.

## Canonical records

| Record | Location |
| --- | --- |
| packet directory | `upstream/packets/04-duckdb-hive-partition-marker/` |
| packet branch | [`teamleaderleo/fieldwork:upstream/04-duckdb-hive-partition-marker`](https://github.com/teamleaderleo/fieldwork/tree/upstream/04-duckdb-hive-partition-marker/upstream/packets/04-duckdb-hive-partition-marker) |
| packet PR | [`teamleaderleo/fieldwork#446`](https://github.com/teamleaderleo/fieldwork/pull/446) |
| clean source branch | [`teamleaderleo/duckdb:upstream/04-hive-default-partition-marker`](https://github.com/teamleaderleo/duckdb/tree/upstream/04-hive-default-partition-marker) |
| source PR | [`teamleaderleo/duckdb#18`](https://github.com/teamleaderleo/duckdb/pull/18) |
| exact-head execution carrier | [`teamleaderleo/duckdb#19`](https://github.com/teamleaderleo/duckdb/pull/19) |
| historical evidence PR | [`teamleaderleo/duckdb#7`](https://github.com/teamleaderleo/duckdb/pull/7) |
| owning finding | [`teamleaderleo/fieldwork#223`](https://github.com/teamleaderleo/fieldwork/issues/223) |
| unit coordination | [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435) |
| public duplicate | [`duckdb/duckdb#24308`](https://github.com/duckdb/duckdb/issues/24308) |

## Exact source generation

- public base: `duckdb/duckdb@81fcce7fa76a320dc65be54cb0825e5315ac6f5b`;
- clean source head: `teamleaderleo/duckdb@1c931ed41822f0e27d66afb636be2730695dcf8d`;
- relation: one commit ahead, zero behind;
- archived prior clean head: `866c8ee8e479789000dbd3acc1fd5a0444af41c2`;
- archived pre-control current-base head: `85aa945baaabae180d6e3c9e5e08b2a63d63545d`.

## Clean diff

Exactly two files differ from the public base:

1. `src/execution/operator/persistent/physical_copy_to_file.cpp`;
2. `test/sql/copy/parquet/parquet_hive_default_collision.test`.

The source hunk reserves raw `__HIVE_DEFAULT_PARTITION__` for SQL NULL and emits `%5F_HIVE_DEFAULT_PARTITION__` for the exact literal marker. The reader's existing URL decode restores the literal.

## Owner-review additions

The refreshed target test adds two adversarial controls beyond the earlier passing generation:

- filter pruning for `p = '__HIVE_DEFAULT_PARTITION__'` and `p IS NULL`;
- injectivity against the literal `%5F_HIVE_DEFAULT_PARTITION__`, which receives `%255F_HIVE_DEFAULT_PARTITION__` on disk.

The existing fixed-name, UUID, nested multi-column, and raw-marker compatibility cases remain.

## Evidence summary

| Evidence | Result |
| --- | --- |
| Fieldwork characterization run `30580996108` | pass |
| unpatched control run `30599146006`, job `91065692552` | expected failure: one SQL NULL row survived |
| historical patched run `30599145476`, job `91057888706` | pass |
| prior focused materialization run `30674271134`, job `91298159055` | pass at archived clean head `866c8ee8...` |
| stock Main run `30696400414` | pending before job creation; queue receipt only |
| exact-head owner-review run `30696673877`, job `91360634513` | queued against clean source `1c931ed...` |

## Additional DuckDB findings

The context review found two independent issue-first candidates and one lower-priority ambiguity. They remain outside unit 04's source diff:

1. Hive partition keys containing reserved characters remain encoded and cannot bind back to the original writer column name; the existing `hive_partition_escape.test` expects this binder failure.
2. A slash inside a URL query fragment can re-enable partition candidacy in `HivePartitioning::Parse`, potentially producing a phantom partition from a path-like query value; this remains source-inferred until a runnable probe confirms it.
3. Repeated external path keys such as `a=1/a=2` collapse through map insertion; intended behavior requires definition before a fix.

Full evidence and next tests are in `APPROACHES.md` and the context-review comment on source PR #18.

## Packet contents

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — source map, failure model, compatibility, and reversing evidence;
- [`APPROACHES.md`](./APPROACHES.md) — selected mechanism, alternatives, losing controls, prior art, and adjacent candidates;
- [`TESTS.md`](./TESTS.md) — exact commands, matrix, receipts, and current run;
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — duplicate disposition and supplemental issue detail;
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — PR review aid and authority boundary;
- [`REVIEW.md`](./REVIEW.md) — exact-head full-diff review and acceptance state.

## Remaining gates and limits

- exact-head run `30696673877` must complete before formal `READY`;
- external Hive-compatible reader behavior remains unexecuted;
- Windows and remote object-store execution remain unexecuted;
- public-upstream authority remains false.

## Continuation

1. Inspect source PR #18 at exact head `1c931ed41822f0e27d66afb636be2730695dcf8d`.
2. Read the source diff and target test as one unit.
3. Check run `30696673877`; on success, change packet disposition from `EXECUTE` to `READY` without moving the source head.
4. On failure, preserve the exact failing step and repair only unit 04.
5. Keep the adjacent parser/key candidates in issue-first status until each has a minimal reproduction.
6. Record the next exact packet head and terminal disposition on Fieldwork issue #435.
