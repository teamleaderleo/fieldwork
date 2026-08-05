# DuckDB Arrow pushdown capability contract

Date: 2026-08-05

## Status

Research only. This does not expand unit 14, claim a numbered unit, or authorize public upstream contact.

Public source and discussion were reviewed read-only. Current source observations should be refreshed against the then-current DuckDB main before implementation.

## Core finding

Arrow filter pushdown is currently expressed as a small table-function interface but depends on a much larger, consumer-specific contract.

`arrow_scan` exposes `supports_pushdown_type` per filtered column. In practice, whether a predicate can be pushed depends on at least:

- the filtered column's Arrow storage type;
- the predicate operator (`=`, `IN`, range, null, nested child);
- how DuckDB materializes the constant into the consumer's scalar type;
- whether any other column in the batch has a layout the consumer's filter kernel cannot process;
- whether the stream factory is PyArrow-backed, a PyCapsule, Java Arrow, or another provider;
- projection identity and the location of unsupported residual filters;
- time-unit and extension-metadata compatibility.

This mismatch has produced repeated correctness or execution failures rather than only missed optimization.

## Evidence pattern

### Per-column checks are insufficient

Merged/public work around string and binary views found that PyArrow can reject filtering a whole record batch when any column is a view type, even when the predicate targets another column. DuckDB therefore uses a coarse whole-table view check rather than only checking the filtered column.

Relevant prior art:

- `duckdb/duckdb#20165` — do not push a VARCHAR predicate for Arrow string-view columns;
- `duckdb/duckdb#20703` — disable pushdown if the table contains a string/binary view anywhere;
- `duckdb/duckdb#22382` — an optimizer projection/lifetime bug surfaced in an Arrow view workload and required both semantic and plan-shape tests.

### Predicate kind matters

`duckdb/duckdb#23368` documents two interacting failures:

1. the multi-element `IN` path created an `InFilter` for a type that did not support constant-filter pushdown;
2. extracting that unsupported filter corrupted the empty `projection_ids` identity convention, dropping projected columns or misaligning types.

A type-level boolean cannot describe that `=` may remain residual while `IN` is incorrectly pushed.

### Scalar construction matters

Historical fixes show that a semantically compatible DuckDB constant may still be incompatible with the consumer scalar:

- timestamp-with-time-zone values with different Arrow time units (`#8856`);
- integer constants inferred by PyArrow at an unsuitable width (`#9155`);
- BLOB constants needing Python `bytes` (`#14553`);
- decimals needing `decimal.Decimal`, not an integer representation (`#14995`).

### Provider identity matters

PyCapsule Arrow streams intentionally disable PyArrow-dependent pushdown (`#13386`). The same logical Arrow schema therefore has different pushdown capability depending on the stream factory implementation.

### Projection and residual-filter semantics matter

When a pushed filter must be pulled back into DuckDB, the scanner output, `column_ids`, `projection_ids`, residual predicate bindings, and filter-only columns must remain aligned. The failures in `#22382` and `#23368` show this is a general table-function planning contract, not merely Python glue.

## Proposed model

A future design should make pushdown capability binding-specific and operator-specific.

A possible capability object could answer:

- `CanPushComparison(column, comparison, constant)`;
- `CanPushIn(column, constants)`;
- `CanPushNullTest(column)`;
- `CanFilterBatch(schema)`;
- `CanMaterializeScalar(column_arrow_type, duckdb_value)`;
- `NeedsResidualRecheck()`;
- `RequiresFilterColumnsInOutput()`.

The capability should be produced by the bound stream factory or provider, not inferred only from DuckDB logical types.

For Arrow replacement scans, useful provider classes include:

- PyArrow dataset/table scanner;
- Arrow C Stream PyCapsule with no Python dependency;
- Java Arrow stream;
- generic callback stream with no filter support;
- future native Arrow/Acero provider.

## Safer incremental path

A full capability object may be too invasive for one contribution. Smaller steps:

1. make predicate-kind checks consistent (`IN` must obey the same type capability as comparison filters);
2. add explicit tests for empty `projection_ids` identity when unsupported filters are extracted;
3. separate whole-schema compatibility from per-column compatibility;
4. expose provider-supplied capability through bind data;
5. only then add richer operator/scalar capability.

## Discriminating test matrix

Each candidate should verify result values and plan shape.

1. supported integer equality with multi-column projection;
2. unsupported string-view equality remains residual;
3. unsupported multi-value `IN` remains residual without changing projected columns;
4. filter on INTEGER while an unrelated string-view column exists;
5. TIMESTAMP_TZ predicate where source and DuckDB units differ;
6. DECIMAL below one and a high-precision decimal constant;
7. BLOB equality and `IN` constants;
8. STRUCT child predicate and projected sibling columns;
9. PyArrow provider versus PyCapsule provider for the same schema;
10. filter-only column removed after residual evaluation;
11. empty and non-empty `projection_ids` paths;
12. query verification enabled to compare optimized and unoptimized results.

## Routing recommendation

This is a credible future core/table-function unit, but it should not start as an Arrow-only patch if the root issue is projection/residual-filter planning. Begin with the smallest reproducible planner invariant, then add provider capabilities separately.

## Links

- https://github.com/duckdb/duckdb/pull/20165
- https://github.com/duckdb/duckdb/pull/20703
- https://github.com/duckdb/duckdb/pull/22382
- https://github.com/duckdb/duckdb/pull/23368
- https://github.com/duckdb/duckdb/pull/13386
- https://github.com/duckdb/duckdb/pull/8856
- https://github.com/duckdb/duckdb/pull/9155
- https://github.com/duckdb/duckdb/pull/14553
- https://github.com/duckdb/duckdb/pull/14995
