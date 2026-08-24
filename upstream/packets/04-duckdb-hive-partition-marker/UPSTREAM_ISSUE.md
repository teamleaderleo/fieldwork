# Upstream issue draft — Partitioned COPY collapses SQL NULL and the literal Hive default marker

Draft status: `not applicable — existing issue #24308 tracks the exact defect`  
Public interaction authorized: `no`

## Current public record

DuckDB issue [#24308](https://github.com/duckdb/duckdb/issues/24308), `Partitioned COPY can lose data`, already contains the minimal two-row reproduction, observed one-row result, DuckDB version, client, platform, and full SQL. It remained open, unassigned, and without comments during the 2026-08-01 duplicate check.

Creating another issue would duplicate the current public record. Fieldwork has made no public comment, reaction, assignment, or filing.

---

## Maintainer-ready supplemental detail

This section is retained for a human who may later add detail to the existing public issue after explicit authorization.

### Summary

Partitioned `COPY` uses raw `__HIVE_DEFAULT_PARTITION__` for SQL NULL. A non-NULL string containing that exact value passes through Hive URL escaping unchanged, so both values receive the same partition directory.

### Minimal reproduction

```sql
CREATE TABLE t AS
SELECT * FROM (VALUES ('__HIVE_DEFAULT_PARTITION__', 1), (NULL, 2)) v(p, id);

COPY t TO '/tmp/hive-marker-collision'
(FORMAT PARQUET, PARTITION_BY (p), OVERWRITE);

SELECT p IS NULL AS is_null, p, id
FROM read_parquet('/tmp/hive-marker-collision/**/*.parquet', hive_partitioning=true)
ORDER BY id;
```

### Observed behavior

Only the SQL NULL row survives with fixed output filenames because both logical values use `p=__HIVE_DEFAULT_PARTITION__`.

With UUID filenames, both files can survive while both still inherit SQL NULL partition semantics from the shared directory token.

### Expected behavior

The literal string and SQL NULL should use distinct partition directory identities and round trip as distinct values.

### Current source observation

At public revision `63094a6f725af5045113dda74e291c7d604f6a88`:

- [`PartitionFileRequestBuilder::BuildDirectory`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/execution/operator/persistent/physical_copy_to_file.cpp#L2980-L3001) writes the raw token for NULL and `HivePartitioning::Escape(value)` for non-NULL values;
- [`HivePartitioning::GetValue`](https://github.com/duckdb/duckdb/blob/63094a6f725af5045113dda74e291c7d604f6a88/src/common/hive_partitioning.cpp#L91-L101) recognizes the exact raw token as SQL NULL before VARCHAR decoding;
- underscores remain unchanged by ordinary URL escaping, producing the collision.

### Candidate direction

Reserve the raw marker for SQL NULL and encode one underscore for the exact colliding literal:

```text
__HIVE_DEFAULT_PARTITION__
→ %5F_HIVE_DEFAULT_PARTITION__
```

DuckDB's existing URL decoder restores the literal value.

### Compatibility and risks

- existing raw-marker directories retain SQL NULL semantics;
- one exact literal receives a new encoded directory name;
- no public API changes;
- external-reader behavior depends on Hive URL decoding;
- generic writer code is source-inspected, while current execution is Parquet-focused.

### Evidence limits

- Ubuntu native execution only;
- no external-engine matrix;
- no prevalence estimate;
- no remote-filesystem execution;
- public submission remains blocked by authorization and DuckDB's current generative-AI contribution policy.

### Versions and environment

- current source inspected: `63094a6f725af5045113dda74e291c7d604f6a88`;
- historical executed source: `de477da7606fc2d857f81117f0140d0550a5c42c`;
- platform: GitHub Actions Ubuntu 24.04;
- harness: DuckDB native SQLLogic tests with Parquet.

### Related public work

- [issue #24308](https://github.com/duckdb/duckdb/issues/24308) — exact defect;
- [PR #20512](https://github.com/duckdb/duckdb/pull/20512) — adopted the raw marker for SQL NULL;
- [PR #21731](https://github.com/duckdb/duckdb/pull/21731) — NULL-marker type detection;
- [issue #24309](https://github.com/duckdb/duckdb/issues/24309) and [PR #24318](https://github.com/duckdb/duckdb/pull/24318) — adjacent literal `NULL` ambiguity.

---

## Filing checklist

- [x] Current issue and PR search repeated on 2026-08-01.
- [x] Existing exact issue identified.
- [x] Reproduction confirmed through native evidence.
- [x] Severity wording limited to demonstrated data loss/semantic collapse conditions.
- [x] Internal links excluded from the supplemental public text.
- [x] DuckDB contribution and AI policy checked at `63094a6`.
- [ ] Exact user authorization for a public comment or filing.

## Decision

Do not open another issue. A future authorized human may add the UUID semantic-control detail to issue #24308 after independently validating and writing the public comment.
