# HOLD — Unit 04 review

## Executive disposition

The selected source change is technically coherent and historically validated in DuckDB's native SQLLogic runner. Current-head materialization is executing against public DuckDB revision `63094a6f725af5045113dda74e291c7d604f6a88` with the widened regression matrix.

The unit remains **HOLD** for public submission. DuckDB's current contribution guide asks contributors to avoid LLM-generated pull requests, and public upstream contact lacks authorization. The owned branch remains useful as research evidence and a human rewrite guide.

## Exact review inputs

- public source base: `duckdb/duckdb@63094a6f725af5045113dda74e291c7d604f6a88`;
- historical source base: `duckdb/duckdb@de477da7606fc2d857f81117f0140d0550a5c42c`;
- historical owned evidence head: `teamleaderleo/duckdb@85a2cf96a2e6fe67157ca0d8d8b7dc1494a8e058`;
- current temporary carrier head: `teamleaderleo/duckdb@a69d945a7b8d42ec17fb716e33a816f7c6b93e58`;
- current target branch: `teamleaderleo/duckdb:upstream/04-hive-default-partition-marker`;
- packet branch: `teamleaderleo/fieldwork:upstream/04-duckdb-hive-partition-marker`;
- exact clean candidate head: pending current materialization receipt and recorded in the final #435 handoff.

## Full-diff review

### Product source

The intended product hunk changes only `PartitionFileRequestBuilder::BuildDirectory` in `src/execution/operator/persistent/physical_copy_to_file.cpp`.

For each non-NULL partition value it:

1. calls the existing `HivePartitioning::Escape`;
2. compares the escaped value with the exact raw reserved token;
3. replaces the first underscore with `%5F` on equality;
4. appends the resulting segment to the partition path.

Review result:

- path identity is repaired before file creation;
- raw marker ownership remains with SQL NULL;
- the existing reader URL decoder restores the literal string;
- ordinary values keep the existing path codec;
- no API, configuration, schema, or file payload changes;
- the source hunk is compact and independently reversible.

### Target-native test

The intended test adds `test/sql/copy/parquet/parquet_hive_default_collision.test`.

Review result:

- reproduces destructive fixed-filename collision;
- asserts raw and encoded directories separately;
- proves distinct file identity;
- adds UUID filenames as a semantic control;
- adds nested multi-column partition paths beneath repeated parents;
- preserves raw-marker compatibility;
- uses DuckDB's native SQLLogic style and Parquet requirement.

### Cleanliness gate

The materialization workflow resets to exact public base, applies the product hunk, copies the test, stages only those two paths, runs `git diff --check`, commits, executes the focused native test, and force-publishes the resulting clean generation. The final branch review must confirm exactly these two changed files and zero Fieldwork/workflow files.

## Correctness reasoning

The defect occurs at the writer boundary. Once two values receive the same directory, a reader-only repair cannot reconstruct overwritten data or identify which file belonged to which logical value. Encoding the exact colliding literal at write time preserves a reversible one-to-one mapping:

| Logical value | Directory token | Reader result |
| --- | --- | --- |
| SQL NULL | `__HIVE_DEFAULT_PARTITION__` | SQL NULL |
| literal marker | `%5F_HIVE_DEFAULT_PARTITION__` | `__HIVE_DEFAULT_PARTITION__` |

UUID filenames demonstrate why file-level uniqueness alone is insufficient: both files can survive inside one raw-marker directory while both inherit SQL NULL partition semantics.

## Compatibility review

- API and source callers: unchanged;
- binary/wire protocol: unchanged;
- data payload: unchanged;
- directory persistence: one exact literal receives a new encoded path;
- existing raw-marker directories: continue to mean SQL NULL;
- rollback: source can be reverted; encoded directories remain readable through current decoding;
- performance: one equality comparison for each non-NULL partition segment and one replacement allocation for the exact reserved literal;
- retry, cancellation, cleanup, and transaction behavior: unchanged by the reviewed hunk.

## Prior-art review

- public issue #24308 tracks the exact unresolved collision;
- merged PR #20512 established the current raw-marker NULL contract;
- merged PR #21731 adjusted type inference around NULL markers;
- merged PR #24318 fixed the adjacent literal string `NULL` ambiguity and is already in the current base;
- merged PR #8540 supplies historical marker discussion;
- current source search found no equivalent exact-marker writer escape.

## Evidence reviewed

- Fieldwork issue #223 and all comments;
- Fieldwork PR #253 and retained execution receipts;
- owned DuckDB PR #7, complete diff, review comments, and both focused/ordinary workflow logs;
- public DuckDB issue #24308;
- public issue #24309 and PRs #20512, #21731, #24318, and #8540;
- current writer, codec, Parquet Hive NULL test, UUID filename test, contribution guide, and target test guide;
- packet workflow and repository guidance linked by issue #435.

## Remaining review risks

1. External Hive-compatible readers were not executed against the encoded literal directory.
2. The source boundary is generic while retained semantic execution is Parquet-focused.
3. Windows, remote object stores, and full-suite execution remain unmeasured.
4. A future configurable NULL marker would need a separate API and persistence review.
5. Current source and prose are AI-assisted, triggering DuckDB's contribution-policy hold.

## Required continuation

1. Read the public issue and current source without copying the generated patch as authored work.
2. Independently derive and write the source and test changes on a fresh branch from the then-current DuckDB main.
3. Run the focused native regression and ordinary project gates on that human-authored head.
4. Recheck duplicate work and current contribution policy.
5. Obtain explicit authorization before any public comment, issue, or pull request.
6. Preserve the replacement head, receipts, and disposition on Fieldwork issue #435.

## Review decision

**HOLD.** Retain the owned candidate and packet. Public upstream remains untouched. A fresh independently human-authored replacement is the only submission path described by this packet.
