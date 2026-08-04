# DuckDB Arrow follow-on research index

Date: 2026-08-05

These notes preserve read-only inquiry performed while unit 14 context was fresh. They do not expand unit 14's nine-file source scope, claim new numbered units, or authorize public upstream contact.

## Research lanes

### 1. Dense-union ingestion

[`dense-union-ingestion.md`](dense-union-ingestion.md)

A substantial separate capability candidate. DuckDB now has merged ADBC paths that manually produce required dense unions, while `arrow_scan` still rejects `+ud:`. The note defines the two-coordinate conversion model, narrow ingestion-only scope, validation boundaries, and a discriminating regression matrix.

### 2. Arrow C Data validation

[`arrow-c-data-validation.md`](arrow-c-data-validation.md)

A proposed sequence of small malformed-input hardening units under public issue `duckdb/duckdb#21849`: schema child structure, parameterized format parsing, schema/array child agreement, buffer structure, and metadata arithmetic.

### 3. Reference-consumer interoperability

[`reference-consumer-interop.md`](reference-consumer-interop.md)

A testing-infrastructure candidate. DuckDB-only round trips can miss schema/layout incompatibilities. The note compares duckdb-python/PyArrow, a small core `arro3` or Arrow C++ oracle, and nanoarrow-based options, with a bidirectional fixture matrix.

### 4. `arrow_scan` repeatability and single-consumer semantics

[`arrow-scan-single-consumer.md`](arrow-scan-single-consumer.md)

A correctness lane covering explicit multiple references and optimizer-introduced duplicated scans. It compares capability flags, binding-specific repeatability, automatic materialization, and narrow rewrite guards.

### 5. Logical versus physical coordinates

[`arrow-coordinate-systems.md`](arrow-coordinate-systems.md)

A cross-cutting audit taxonomy for parent offsets, chunk offsets, list child starts, dictionary positions, run ends, sparse/dense unions, and ListView spans. It includes fixture-design guidance intended to expose the exact physical slot read.

## Earlier broad sweep

[`../adjacent-duckdb-arrow-research-2026-08-05.md`](../adjacent-duckdb-arrow-research-2026-08-05.md) records the initial routing-level survey and source links.

## Suggested routing order

1. Finish unit 14 current-main restack and complete-diff peer review.
2. Treat dense-union ingestion as the strongest separate product contribution.
3. Take Arrow C Data validation as a series of small, source-native malformed-input units.
4. Pursue reference-consumer testing as enabling infrastructure for both ingestion and export work.
5. Address `arrow_scan` repeatability generically enough to cover optimizer duplication and explicit multiple references.
6. Use the coordinate-system checklist during every nested Arrow review.

## Authority

- Public DuckDB contact: not authorized.
- Public repository writes during this research: none.
- New target-source branches or claims created by these notes: none.
