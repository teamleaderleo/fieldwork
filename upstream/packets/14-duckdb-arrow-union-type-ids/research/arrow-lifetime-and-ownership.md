# DuckDB Arrow lifetime and ownership audit

Date: 2026-08-05

## Status

Research only. No public write, source branch, or new unit claim is created by this note.

## Core finding

DuckDB's Arrow boundary has several independently managed lifetimes:

1. the `ArrowArrayStream` object and its private data;
2. each schema returned by `get_schema`;
3. each array returned by `get_next`;
4. the stream-factory object used by replacement scans;
5. the DuckDB `ClientContext` used by Arrow extension callbacks;
6. extension registration/catalog state;
7. result objects consumed lazily after query or connection teardown.

Bugs appear when one layer assumes another object is borrowed, repeatable, or still alive.

## Historical ownership ambiguity

Closed unmerged `duckdb/duckdb#16050` identified a leak in the deprecated `duckdb_arrow_scan` path. The code called `get_schema`, modified child release callbacks, and never released the returned schema. Discussion correctly notes that every successful `get_schema` call returns a fresh ArrowSchema ownership obligation; the producer may allocate different children and private data each time.

The same discussion questions the API's basic ownership model: it tries to avoid releasing the caller's stream instead of clearly taking or borrowing ownership.

This is connected to the single-consumer research lane. A stream may be legally consumed once while its factory may or may not be able to create another stream.

## Context lifetime is a separate problem

Closed draft `duckdb/duckdb#22508` addresses lazy Arrow export after the originating connection has closed. Arrow extension callbacks promise a valid `ClientContext`, but schema or array production can happen later through:

- Arrow C Stream callbacks;
- ADBC;
- Python lazy consumption;
- callback-driven clients;
- extension-defined schema population.

The reported GeoArrow failure was an inactive transaction/context during `PopulateSchema`. A Python-side eager schema cache solved one surface but did not solve the general result/context lifetime contract.

The attempted core solution tied a shared `ClientContext` to query results and routed schema/array conversion through that context. It was closed unmerged, so the current architectural answer needs a fresh review.

## Current replacement-scan lifetime behavior

`ArrowScanBind` retains a `DependencyItem` when the replacement scan supplies an external dependency. This keeps the stream factory object alive. `ArrowScanInitGlobal` then asks the factory to produce a stream and stores it in the global state.

That protects the factory pointer, but it does not by itself define:

- whether `get_schema` may be called repeatedly;
- whether each produced stream is independent;
- whether the schema is cached or regenerated;
- whether extension callbacks require a live transaction;
- whether optimizer duplication may create multiple streams;
- which object releases the stream on binder, init, execution, cancellation, and exception paths.

## Proposed ownership vocabulary

Every Arrow-facing API should state one of these contracts explicitly:

- **borrowed immutable** — caller owns and object must outlive the operation;
- **moved/consumed** — callee owns and will release exactly once;
- **factory-repeatable** — factory may create independent streams repeatedly;
- **factory-one-shot** — one stream only; planner must materialize for repeated reads;
- **callback-snapshot** — all context-dependent schema information captured eagerly;
- **context-retained** — result holds a context lifetime until all callbacks finish.

The current interfaces mix these models implicitly.

## Candidate implementation directions

### A. Snapshot schema and extension decisions eagerly

At query/result creation:

- produce and own the complete Arrow schema;
- resolve extension metadata and physical layouts;
- store immutable schema state independent of catalog/transaction lifetime.

Later callbacks only deep-copy or expose the snapshot.

Advantages: small callback surface and deterministic schema.

Risk: some extensions may intentionally need late options or dynamic context.

### B. Retain a minimal Arrow conversion context

Rather than holding a full active `ClientContext`, capture:

- client Arrow options;
- resolved extension callbacks/data;
- allocator/state required by conversion;
- immutable logical types and names.

This avoids keeping a transaction-bearing connection alive solely for lazy conversion.

### C. Retain the full context through result lifetime

This matches the `#22508` direction and is simpler semantically, but it can prolong connection/catalog/transaction resources and create cycles. It needs explicit close/cancel behavior.

### D. New C API ownership cleanup

The newer Arrow C API should be the preferred hardening surface. Deprecated scan APIs can receive narrow leak/null checks, but new work should define move/borrow semantics around schema and array conversion functions and test every release path.

## Required lifecycle matrix

A focused test harness should count releases and callback calls for:

1. bind success then execution success;
2. bind failure after `get_schema`;
3. execution failure after one batch;
4. consumer stops early due to LIMIT;
5. cancellation/interruption;
6. empty stream;
7. `get_schema` called twice returning distinct allocations;
8. `get_next` error with `get_last_error`;
9. connection closed before lazy schema request;
10. connection closed before lazy batch request;
11. extension callback requiring type parsing;
12. one-shot and repeatable factories;
13. optimizer-introduced duplicate reads;
14. stream copied by value into a wrapper;
15. deprecated C API and new C API behavior.

For each case, assert:

- schema release count;
- array release count;
- stream release count;
- factory destruction;
- context destruction;
- no callback after required state is gone;
- no double release;
- no retained allocation after expected failure.

## Strong future unit candidates

1. **Schema release accounting for deprecated `duckdb_arrow_scan`** — narrow but API is deprecated.
2. **Eager immutable schema snapshot for lazy Arrow results** — useful across Python, ADBC, and C Stream.
3. **Binding-level stream repeatability/ownership metadata** — pairs with automatic materialization.
4. **Release-count test utility for Arrow C Data** — enabling infrastructure for many units.

## Links

- https://github.com/duckdb/duckdb/pull/16050
- https://github.com/duckdb/duckdb/pull/22508
- https://github.com/duckdb/duckdb-python/pull/423
- https://github.com/duckdb/duckdb-python/issues/70
- https://github.com/duckdb/duckdb-java/issues/713
