# Deep dive — Unit 04: preserve the literal Hive default-partition marker

## In simple words

DuckDB writes partition values into directory names. SQL NULL uses the reserved Hive directory token `__HIVE_DEFAULT_PARTITION__`. A real string containing that exact token currently reaches the same directory, so two distinct values can overwrite or merge into one path. The selected correction keeps the raw token for SQL NULL and URL-escapes the first underscore of the literal value. DuckDB's existing Hive URL decoder restores the literal string when reading.

The defect and the repair mechanism have already run in DuckDB's native SQLLogic harness. This packet refreshes the work onto current public main, adds UUID-filename and nested multi-column controls, and records a submission-policy hold.

## Governing invariant

> Distinct logical partition values must produce distinct partition directory identities, while the raw Hive default-partition token remains the SQL NULL representation.

## Current behavior

- entrypoint: partitioned `COPY` reaches `PartitionFileRequestBuilder::BuildDirectory`.
- state owner: the copy operator builds each partition directory segment before opening the output file.
- caller-visible result: the literal string `__HIVE_DEFAULT_PARTITION__` and SQL NULL can resolve to one directory.
- side effects: one logical partition can overwrite, append into, or become indistinguishable from the other depending on file naming and overwrite options.
- cleanup owner: ordinary copy/file-system cleanup; the defect occurs before file identity is safely separated.
- persistence boundary: the generated directory path.
- ordering: both values independently pass through the same directory builder; collision occurs deterministically.

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| partition writer | [`physical_copy_to_file.cpp` at `63094a6`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/execution/operator/persistent/physical_copy_to_file.cpp#L2980-L3001), `PartitionFileRequestBuilder::BuildDirectory` | emits raw marker for NULL and escaped text for non-NULL values | [`parquet_hive_null.test` at `63094a6`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/test/sql/copy/parquet/parquet_hive_null.test) |
| Hive path codec | [`hive_partitioning.cpp` at `63094a6`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/common/hive_partitioning.cpp#L73-L101) | URL-encodes values, URL-decodes values, and recognizes the exact raw marker as SQL NULL | same Parquet Hive tests |
| filename control | [`format_uuid.test` at `63094a6`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/test/sql/copy/format_uuid.test) | establishes `{uuid}` filename behavior | unit 04 UUID matrix |
| unit 04 candidate | [`upstream/04-hive-default-partition-marker`](https://github.com/teamleaderleo/duckdb/tree/upstream/04-hive-default-partition-marker) | clean owned source branch after materialization | [`parquet_hive_default_collision.test`](https://github.com/teamleaderleo/duckdb/blob/upstream/04-hive-default-partition-marker/test/sql/copy/parquet/parquet_hive_default_collision.test) |

## Reproduction or characterization

### Setup

- historical exact upstream revision: `de477da7606fc2d857f81117f0140d0550a5c42c`.
- current exact upstream revision inspected: `63094a6f725af5045113dda74e291c7d604f6a88`.
- environment: GitHub Actions Ubuntu 24.04, DuckDB native SQLLogic runner with Parquet.
- fixture: one row partitioned by literal `__HIVE_DEFAULT_PARTITION__`, one by SQL NULL.
- baseline ordinary run: [`30599146006`](https://github.com/teamleaderleo/duckdb/actions/runs/30599146006).
- applied-patch focused run: [`30599145476`](https://github.com/teamleaderleo/duckdb/actions/runs/30599145476).

### Baseline result

The unpatched ordinary workflow built successfully and ran the changed SQLLogic test. The test expected two rows and observed one row, `NULL / id=2`, after retries. The literal row had collided with the NULL partition path.

### Candidate result

The applied-patch focused workflow passed the original 11-assertion collision and raw-marker compatibility test. The current-head materialization run adds:

1. fixed-name overwrite collision;
2. `{uuid}` filenames, proving unique filenames alone do not repair partition identity;
3. nested `(region, p)` partitions across two parent values;
4. existing raw-marker compatibility.

The exact current-head receipt is recorded in `TESTS.md` and the latest handoff on issue #435.

## Failure model

1. SQL NULL enters `BuildDirectory`; DuckDB emits raw `__HIVE_DEFAULT_PARTITION__`.
2. The literal string enters the non-NULL branch; `HivePartitioning::Escape` leaves underscores unchanged.
3. Both produce the same `p=__HIVE_DEFAULT_PARTITION__` path segment.
4. File naming decides whether data is overwritten or co-located, while Hive parsing treats the directory value as SQL NULL.
5. The reader cannot recover the original literal value because path identity was already lost.

Every step above is confirmed by source and native execution.

## Consequence and claim boundary

### Established

- two distinct logical values can produce one partition directory;
- fixed filenames can lose one row through overwrite;
- UUID filenames can keep both files yet still read both partitions as SQL NULL without directory disambiguation;
- escaping one leading underscore preserves distinct paths and round trips the literal through DuckDB's existing URL decoder;
- nested multi-column output exercises the same value-segment rule independently under each parent directory.

### Inferred

- every partitioned `COPY` caller using this generic directory builder receives the repaired path identity.

### Unknown or unmeasured

- ecosystem prevalence;
- behavior in external readers that decline Hive URL decoding;
- full format-by-format execution outside Parquet;
- Windows and remote object-store execution;
- performance beyond source inspection of one string comparison and one short allocation path for the reserved literal.

## Selected implementation

The writer owns the collision because it creates the irreversible path identity. After ordinary Hive escaping, the writer compares the escaped value with the reserved raw marker. On equality, it replaces the first underscore with `%5F`:

```text
__HIVE_DEFAULT_PARTITION__
→ %5F_HIVE_DEFAULT_PARTITION__
```

The raw token remains exclusive to SQL NULL. Existing `HivePartitioning::Unescape` turns `%5F` back into `_` for literal values. No reader special case, public option, or new marker is added.

## Compatibility analysis

- public API: unchanged.
- source compatibility: unchanged.
- binary or wire compatibility: unchanged.
- persistence or format compatibility: newly written literal reserved-token partitions receive an encoded directory name; existing raw-token directories keep SQL NULL semantics.
- platform behavior: path segment uses existing URL-encoding conventions.
- performance and allocation: one equality check for each non-NULL partition value; one replacement allocation only for the exact reserved literal.
- cancellation, retry, and recovery: unchanged.
- generated output: one directory-name change for one exact literal value.
- migration or rollback: reverting the source hunk restores prior behavior; data written with `%5F` remains readable through existing URL decoding.

## Adversarial and edge controls

- same-key collision: fixed-name overwrite case;
- overwrite-independent semantic control: `{uuid}` filenames;
- nested path control: two parent values and literal/NULL child values;
- compatibility: raw marker still represents SQL NULL;
- unrelated values: ordinary partition values continue through the existing escape path;
- repeated parents: north/south controls show no cross-parent leakage.

Concurrency, cancellation, cleanup failure, remote filesystems, and non-Parquet readers remain outside the executed matrix.

## Review risks

1. **Encoded literal interoperability.** Review whether Hive-compatible readers are expected to URL-decode partition values. DuckDB already defines `Escape`/`Unescape` for this path.
2. **Generic source boundary, Parquet-only execution.** The writer code is shared, while the retained target-native semantic test is Parquet. Broader format claims stay source-supported and unexecuted.
3. **Future configurable NULL marker.** A configurable marker would widen API and compatibility work. This unit repairs the current fixed-marker collision only.
4. **Project AI policy.** Current `CONTRIBUTING.md` says contributors should avoid LLM-generated pull requests. Public submission therefore requires an independently human-authored replacement and fresh review.

## Reversing evidence

Reopen the implementation decision if:

- current DuckDB main introduces an equivalent exact-marker escape;
- maintainers define literal raw-marker values as intentionally unrepresentable;
- an authoritative Hive path contract forbids the existing URL-escape route for this value;
- a current native test shows `%5F_HIVE_DEFAULT_PARTITION__` failing to round trip;
- a human-authored alternative satisfies the same invariant with narrower compatibility cost.

## Adjacent work excluded

- configurable Hive NULL marker;
- literal string `NULL` handling, addressed by merged DuckDB PR #24318;
- Hive type inference around NULL markers, addressed by merged PR #21731;
- remote/object-store publication behavior;
- other partition escaping collisions;
- external-engine compatibility matrices.
