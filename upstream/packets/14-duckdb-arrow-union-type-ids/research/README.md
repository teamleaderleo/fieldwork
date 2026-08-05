# DuckDB Arrow follow-on research index

Date: 2026-08-05

These notes preserve read-only inquiry performed while unit 14 context was fresh. They do not expand unit 14's nine-file source scope, claim new numbered units, or authorize public upstream contact.

The deepest source audit in this index was pinned to DuckDB public source `043e1894425b49984c5010f253589e5d9c5fdde4` (`Add checked cast helper to HTTPUtil`, 2026-08-05). Refresh every source-level claim before implementing a future unit.

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

## Earlier broad sweep

[`../adjacent-duckdb-arrow-research-2026-08-05.md`](../adjacent-duckdb-arrow-research-2026-08-05.md) records the initial routing-level survey and source links.

## Cross-lane themes

### Logical and physical coordinates

Dense unions, sparse unions, ListView, dictionaries, run ends, and fixed arrays all need explicit checked spans rather than ad hoc offset arithmetic.

### Capability belongs to the bound provider

Pushdown and repeatability cannot be inferred from a logical Arrow schema alone. The same schema may be backed by PyArrow, Java Arrow, a one-shot C Stream, or a repeatable factory.

### Lifetimes are part of the data contract

A valid schema or array is not enough if its producer, extension context, or release owner has already gone away.

### DuckDB self-roundtrip is necessary but insufficient

Reference consumers are needed to prove schema/data layout agreement, extension metadata semantics, and standards-conforming noncanonical inputs.

### Validation needs levels

Fast structural checks should prevent unsafe dereferences and arithmetic. Full content validation should exist as a strict/test oracle without automatically taxing every trusted scan.

## Suggested routing order

1. Finish unit 14 current-main reconciliation and complete-diff peer review.
2. Take **dense-union ingestion** as the strongest separate product contribution.
3. Take **metadata signed-length validation** and **schema child-structure validation** as small malformed-input units.
4. Build a reusable **release-count C Data fixture utility**.
5. Address **`arrow_scan` repeatability** with binding-specific capability or automatic materialization.
6. Add **reference-consumer interoperability** as enabling infrastructure.
7. Introduce **checked span helpers** before attempting broad encoded-layout validation.
8. Add **extension schema/appender parity** and unknown-extension degradation observability.
9. Revisit provider-specific pushdown after projection/residual-filter invariants are covered.

## Authority

- Public DuckDB contact: not authorized.
- Public repository writes during this research: none.
- New target-source branches or claims created by these notes: none.
