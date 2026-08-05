# DuckDB Arrow follow-on research index

Date: 2026-08-05

These notes preserve read-only inquiry performed while unit 14 context was fresh. They do not expand unit 14's nine-file source scope, claim new numbered units, or authorize public upstream contact.

The main deep source audit was pinned to DuckDB public source `043e1894425b49984c5010f253589e5d9c5fdde4`. The C API ownership pattern was rechecked and remained present at newer public source `58c019320e250a7b369efd756f84c6dfd68bedcb`. Refresh every source-level claim before implementing a future unit.

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

### 6. Pushdown capability contract

[`arrow-pushdown-capability-contract.md`](arrow-pushdown-capability-contract.md)

A planner/provider contract investigation. Pushdown safety depends on predicate kind, scalar construction, whole-batch layout, projection identity, residual-filter handling, and stream provider—not only the filtered DuckDB type. The note proposes a binding-specific capability model and a plan-and-result test matrix.

### 7. Lifetime and ownership

[`arrow-lifetime-and-ownership.md`](arrow-lifetime-and-ownership.md)

An audit of stream, schema, array, factory, result, extension, and `ClientContext` lifetimes. It defines explicit borrowed/moved/repeatable/one-shot/context-snapshot vocabulary and a release-count matrix for success, failure, cancellation, early stop, and lazy consumption.

### 8. Metadata framing

[`arrow-metadata-framing.md`](arrow-metadata-framing.md)

A concrete hardening slice. Current metadata parsing consumes signed counts and lengths from a raw pointer without a total byte length. The note separates checks possible on the raw ABI from a stronger bounded internal parser and defines duplicate reserved-key and unknown-extension policies.

### 9. Encoded-layout invariants

[`arrow-encoded-layout-invariants.md`](arrow-encoded-layout-invariants.md)

A type-by-type validation and safe-span program for dictionaries, run-end encoding, regular lists/maps, ListView, fixed-size arrays, sparse unions, and dense unions. It distinguishes O(1) structural validation from range checks and optional O(n) full validation.

### 10. Extension-type contracts

[`arrow-extension-contracts.md`](arrow-extension-contracts.md)

An audit of extension identity, physical storage, DuckDB logical meaning, callback/context lifetime, unknown-extension degradation, and schema/appender agreement. It proposes explicit resolution states and parity tests across output versions, views, offsets, and nested storage.

### 11. C API zero-copy ownership

[`arrow-capi-zero-copy-ownership.md`](arrow-capi-zero-copy-ownership.md)

A source-supported candidate defect in `duckdb_data_chunk_from_arrow`. Root `ArrowArray` ownership is transferred inside the per-column conversion loop, while the existing roundtrip test covers only one column. The note defines a two-column recursive-release fixture that can prove or disprove release-before-later-column conversion without prematurely claiming a confirmed bug.

## Earlier broad sweep

[`../adjacent-duckdb-arrow-research-2026-08-05.md`](../adjacent-duckdb-arrow-research-2026-08-05.md) records the initial routing-level survey and source links.

## Cross-lane themes

### Logical and physical coordinates

Dense unions, sparse unions, ListView, dictionaries, run ends, and fixed arrays all need explicit checked spans rather than ad hoc offset arithmetic.

### Capability belongs to the bound provider

Pushdown and repeatability cannot be inferred from a logical Arrow schema alone. The same schema may be backed by PyArrow, Java Arrow, a one-shot C Stream, or a repeatable factory.

### Lifetimes are part of the data contract

A valid schema or array is not enough if its producer, extension context, or release owner has already gone away. Ownership must be retained at the root/chunk level rather than accidentally depending on which column aliases producer memory.

### DuckDB self-roundtrip is necessary but insufficient

Reference consumers are needed to prove schema/data layout agreement, extension metadata semantics, and standards-conforming noncanonical inputs.

### Validation needs levels

Fast structural checks should prevent unsafe dereferences and arithmetic. Full content validation should exist as a strict/test oracle without automatically taxing every trusted scan.

## Priority board

### Highest-priority characterization

**C API multi-column ownership**: narrow public API boundary, strong source signal, missing multi-column test, deterministic release-count oracle.

### Strongest product contribution

**Dense-union ingestion**: already demanded by merged ADBC producers and external standards.

### Best small hardening slices

- negative metadata count/length rejection;
- schema child-count and pointer validation;
- validity bitmap no-overread;
- run-end structural/monotonic validation.

### Best enabling infrastructure

- release-count Arrow C Data fixture utility;
- reference-consumer interop lane;
- checked span helpers for nested/encoded layouts.

## Suggested routing order

1. Finish unit 14 current-main reconciliation and complete-diff peer review.
2. Privately characterize the **C API multi-column ownership** candidate on exact current source.
3. Take **dense-union ingestion** as the strongest separate product contribution.
4. Take **metadata signed-length validation** and **schema child-structure validation** as small malformed-input units.
5. Build a reusable **release-count C Data fixture utility**.
6. Address **`arrow_scan` repeatability** with binding-specific capability or automatic materialization.
7. Add **reference-consumer interoperability** as enabling infrastructure.
8. Introduce **checked span helpers** before attempting broad encoded-layout validation.
9. Add **extension schema/appender parity** and unknown-extension degradation observability.
10. Revisit provider-specific pushdown after projection/residual-filter invariants are covered.

## Authority

- Public DuckDB contact: not authorized.
- Public repository writes during this research: none.
- New target-source branches or claims created by these notes: none.
