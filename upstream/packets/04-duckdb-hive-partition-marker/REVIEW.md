# EXECUTE — Unit 04 owner review

## Executive decision

**ACCEPT IMPLEMENTATION FOR OWNER REVIEW. EXECUTE EXACT-HEAD GATES.**

The source change is localized, reversible, and consistent with DuckDB's existing Hive URL codec. The clean branch is one commit over current public base and changes exactly the product source and its native regression test.

Formal packet disposition remains `EXECUTE` while exact-head run `30696673877`, job `91360634513`, waits for a GitHub runner. Public-upstream authority is separate and remains false.

## Exact review inputs

- public base: `duckdb/duckdb@81fcce7fa76a320dc65be54cb0825e5315ac6f5b`;
- clean source: `teamleaderleo/duckdb@1c931ed41822f0e27d66afb636be2730695dcf8d`;
- source branch: `upstream/04-hive-default-partition-marker`;
- source PR: [`teamleaderleo/duckdb#18`](https://github.com/teamleaderleo/duckdb/pull/18);
- execution carrier: [`teamleaderleo/duckdb#19`](https://github.com/teamleaderleo/duckdb/pull/19) at `67d78b2611cab36eb9736685ff86b6020e5a6667`;
- exact-head run: [`30696673877`](https://github.com/teamleaderleo/duckdb/actions/runs/30696673877), job `91360634513`;
- packet branch: `teamleaderleo/fieldwork:upstream/04-duckdb-hive-partition-marker`;
- packet PR: [`teamleaderleo/fieldwork#446`](https://github.com/teamleaderleo/fieldwork/pull/446).

Archived generations:

- prior clean pass: `866c8ee8e479789000dbd3acc1fd5a0444af41c2`;
- current-base pre-control head: `85aa945baaabae180d6e3c9e5e08b2a63d63545d`;
- historical carrier evidence: PR #7 and runs `30599145476` / `30599146006`.

## Clean-diff review

Comparison of base `81fcce7...` and head `1c931ed...` shows one commit, zero behind, and exactly:

1. `src/execution/operator/persistent/physical_copy_to_file.cpp` — +5/-1;
2. `test/sql/copy/parquet/parquet_hive_default_collision.test` — added native regression.

No workflow, Fieldwork file, retained patch, generated file, or staging path appears in the source generation.

## Product-source review

The hunk changes `PartitionFileRequestBuilder::BuildDirectory`.

For each non-NULL partition value it:

1. applies `HivePartitioning::Escape`;
2. compares the escaped value with raw `__HIVE_DEFAULT_PARTITION__`;
3. encodes the first underscore as `%5F` on exact equality;
4. appends the result to the partition path.

Acceptance reasons:

- correction occurs before directory and file identity are lost;
- raw marker ownership remains with SQL NULL;
- existing URL decoding restores the literal marker;
- ordinary values retain their existing codec;
- API, schema, payload, transaction, cleanup, retry, and cancellation behavior remain unchanged;
- cost is one equality comparison per non-NULL partition segment and one small allocation on the exact literal.

## Target-test review

The regression covers:

- fixed-filename overwrite and two-row preservation;
- exact raw and encoded path names;
- distinct file identity;
- literal equality and SQL NULL filter pruning;
- UUID filenames as a semantic control;
- injectivity against literal `%5F_HIVE_DEFAULT_PARTITION__` via `%255F...`;
- nested multi-column partitions under repeated parents;
- existing raw-marker compatibility.

The test uses isolated fixture names and output roots and requires Parquet through DuckDB's native SQLLogic harness.

## Correctness model

| Logical value | On-disk token | Reader result |
| --- | --- | --- |
| SQL NULL | `__HIVE_DEFAULT_PARTITION__` | SQL NULL |
| `__HIVE_DEFAULT_PARTITION__` | `%5F_HIVE_DEFAULT_PARTITION__` | literal marker |
| `%5F_HIVE_DEFAULT_PARTITION__` | `%255F_HIVE_DEFAULT_PARTITION__` | literal `%5F...` |

The mapping is injective under the existing encoder/decoder. UUID files confirm file uniqueness alone cannot repair a shared partition token. Filter cases confirm the identity survives path-derived constant evaluation before file open.

## Evidence classification

### Target-executed

- unpatched control run `30599146006`, job `91065692552`: expected one-row failure;
- historical patched run `30599145476`, job `91057888706`: pass;
- prior focused materialization run `30674271134`, job `91298159055`: pass at archived clean head `866c8ee...`.

### Source-read and exact-diff reviewed

- current writer, `HivePartitioning::Escape`, `GetValue`, `IsNull`, URL encoder/decoder, and `MultiFileReader` path-constant flow at base `81fcce7...`;
- exact clean source diff `81fcce7...1c931ed`;
- new alias and pruning controls.

### Pending execution

- stock Main run `30696400414`: pending before job creation, zero code evidence;
- owner-review run `30696673877`: queued, checks out exact source SHA and requests repository prepare gates, focused regression, and complete native test runner.

## Prior art and duplicate state

- public issue #24308 remains the exact duplicate/problem record;
- PR #20512 established raw marker semantics for SQL NULL;
- PR #21731 addressed type detection around NULL markers;
- PR #24318 handled the adjacent literal `NULL` ambiguity;
- PR #8540 supplies historical marker discussion;
- current source search found no equivalent writer escape on base `81fcce7...`.

## Additional context findings

The wider code pass produced separate candidates without changing unit 04:

1. escaped partition keys remain encoded; existing `hive_partition_escape.test` expects binder failure for a writer-produced reserved-character column name;
2. slashes after `?` can re-enable partition candidacy in `HivePartitioning::Parse`, creating a source-inferred query-fragment phantom partition risk;
3. duplicate external partition keys collapse through map insertion.

Each requires its own minimal reproduction and issue-first packet. Details are in `APPROACHES.md` and source PR #18.

## Remaining risks and limits

1. External Hive-compatible readers have not consumed the encoded literal path.
2. Semantic execution remains Parquet-focused until the current carrier completes.
3. Windows and remote object stores remain unexecuted.
4. Public-upstream authority remains false.
5. Any source-head movement expires this review.

## Owner inspection guide

1. Confirm PR #18 head is `1c931ed41822f0e27d66afb636be2730695dcf8d` and base is `81fcce7fa76a320dc65be54cb0825e5315ac6f5b`.
2. Review the four-line writer rule before the test.
3. Inspect fixed-name, filter, UUID, alias, nested, and compatibility sections in order.
4. Confirm the literal `%5F...` case maps to `%255F...` and reads back unchanged.
5. Read run `30696673877` when terminal.
6. On pass, accept packet as `READY`; on failure, preserve the first failing step and return unit 04 to `REPAIR`.

## Current review decision

**EXECUTE.** The implementation is checked off for owner review. The exact-head test receipt is the remaining formal gate.
