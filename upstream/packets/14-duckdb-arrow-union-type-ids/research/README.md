# DuckDB Arrow follow-on research index

Date: 2026-08-06

These notes preserve read-only public-source inquiry and private Fieldwork characterization performed while unit 14 context was fresh. They do not expand unit 14's source scope, claim new numbered units, or authorize public upstream contact.

The newest public DuckDB main observed during this pass is `7a91c3658f9411ab17556e55f9df34b3b2140f6e`. Refresh every source-level claim before implementing a future unit.

## Research lanes

### 1. Dense-union ingestion

[`dense-union-ingestion.md`](dense-union-ingestion.md)

A substantial separate capability candidate. DuckDB has merged ADBC paths that manually produce required dense unions, while `arrow_scan` still rejects `+ud:`. The note defines the two-coordinate conversion model, narrow ingestion-only scope, validation boundaries, and a discriminating regression matrix.

### 2. Arrow C Data validation

[`arrow-c-data-validation.md`](arrow-c-data-validation.md)

A sequence of small malformed-input hardening units under public issue `duckdb/duckdb#21849`: schema child structure, parameterized format parsing, schema/array agreement, buffer structure, and metadata arithmetic.

### 3. Reference-consumer interoperability

[`reference-consumer-interop.md`](reference-consumer-interop.md)

A testing-infrastructure candidate. DuckDB-only round trips can miss schema/layout incompatibilities. The note compares duckdb-python/PyArrow, Arrow C++, `arro3`, and nanoarrow options with a bidirectional fixture matrix.

### 4. `arrow_scan` repeatability

[`arrow-scan-single-consumer.md`](arrow-scan-single-consumer.md)

Covers explicit multiple references and optimizer-introduced duplicate scans. It compares capability flags, binding-specific repeatability, automatic materialization, and narrow rewrite guards.

### 5. Logical versus physical coordinates

[`arrow-coordinate-systems.md`](arrow-coordinate-systems.md)

A taxonomy for parent offsets, chunk offsets, list child starts, dictionary positions, run ends, sparse/dense unions, and ListView spans.

### 6. Pushdown capability contracts

[`arrow-pushdown-capability-contract.md`](arrow-pushdown-capability-contract.md)

Pushdown safety depends on predicate kind, scalar construction, whole-batch layout, projection identity, residual-filter handling, and provider—not merely the filtered logical type.

### 7. Lifetime and ownership

[`arrow-lifetime-and-ownership.md`](arrow-lifetime-and-ownership.md)

An audit of stream, schema, array, factory, result, extension, and `ClientContext` lifetimes, with explicit borrowed/moved/repeatable/one-shot vocabulary and release-count matrices.

### 8. Metadata framing

[`arrow-metadata-framing.md`](arrow-metadata-framing.md)

Current metadata parsing consumes signed counts and lengths from a raw pointer without a total byte length. The note separates checks possible on the raw ABI from a bounded internal parser.

### 9. Encoded-layout invariants

[`arrow-encoded-layout-invariants.md`](arrow-encoded-layout-invariants.md)

A type-by-type safe-span program for dictionaries, run-end encoding, lists/maps, ListView, fixed arrays, sparse unions, and dense unions.

### 10. Extension-type contracts

[`arrow-extension-contracts.md`](arrow-extension-contracts.md)

Audits extension identity, physical storage, DuckDB logical meaning, callback/context lifetime, unknown-extension degradation, and schema/appender parity. No built-in callback alias-lifetime defect was established.

### 11. C API projected-column ownership

[`arrow-capi-zero-copy-ownership.md`](arrow-capi-zero-copy-ownership.md)

Active private characterization: [`teamleaderleo/duckdb#29`](https://github.com/teamleaderleo/duckdb/pull/29), base `58c019320e250a7b369efd756f84c6dfd68bedcb`, head `b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`.

The original broad hypothesis—release during ordinary per-column conversion—was corrected. Generic conversion attaches each copied wrapper to its output vector. The refined risk is that only column zero's wrapper carries the real root release callback. A later-column `Vector::Ref` can outlive the source chunk while retaining only a no-op wrapper.

Expected-negative signature:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

No defect is confirmed until the exact-head workflow reproduces both lines.

### 12. Arrow C Stream error contracts

[`arrow-stream-error-contracts.md`](arrow-stream-error-contracts.md)

Arrow permits `get_last_error` to return `NULL`; DuckDB currently constructs a `string` directly from that optional pointer after callback failures. The note defines null-detail, callback, partial-output, numeric-error, and release controls.

### 13. C API schema/array agreement

[`arrow-capi-schema-array-agreement.md`](arrow-capi-schema-array-agreement.md)

Active private characterization: [`teamleaderleo/duckdb#30`](https://github.com/teamleaderleo/duckdb/pull/30), base `7a91c3658f9411ab17556e55f9df34b3b2140f6e`, head `41c76c97cdcbf5fbd6ecfc7b1f130b4f853166af`.

The converted schema declares two INT32 fields while the runtime root declares `n_children = 1`. The allocation deliberately contains two valid pointers, avoiding a crash. Acceptance proves the runtime count is ignored.

Expected-negative signature:

```text
declared runtime child count=1 accepted=1 output columns=2 second output=21,22
```

### 14. Dictionary cache identity

[`arrow-dictionary-cache-identity.md`](arrow-dictionary-cache-identity.md)

Audited and closed as a defect avenue for conforming producers. The cached dictionary vector retains the owning root; Arrow forbids mutation or recycling before release, so pointer identity remains adequate while that retention remains intact.

### 15. C API conversion failure ownership

[`arrow-capi-failure-ownership.md`](arrow-capi-failure-ownership.md)

The stable API says ownership moves to the returned `DataChunk`, but the current implementation nulls the caller's root release before all columns convert. An error can therefore consume the array without returning a chunk. The note compares success-only transactional transfer with consume-on-entry semantics and proposes exact first-column, later-column, validation, and success controls.

## Cross-lane findings

### One root owner, not one copy per column

The coherent C API direction is one shared root owner referenced by every output vector. For success-only transfer, that owner can borrow with `release = nullptr` during conversion, acquire the original release callback only after every column succeeds, and then null the caller's callback.

### Structural validation precedes ownership transfer

Root child counts, pointer tables, required child pointers, release state, and checked logical spans should be validated before any buffer access or move.

### Coordinates require checked spans

Dense/sparse unions, ListView, dictionaries, run ends, and fixed arrays should use explicit checked logical and physical spans rather than ad hoc offset arithmetic.

### Capability belongs to the bound provider

Pushdown and repeatability cannot be inferred from an Arrow schema alone. PyArrow, Java Arrow, one-shot C Streams, and repeatable factories have different capabilities.

### Losing avenues remain valuable

The dictionary-cache analysis and corrected broad ownership hypothesis are preserved to prevent repeated incomplete reasoning.

## Priority board

1. Finish unit 14's pinned restack execution path, then refresh to actual latest main.
2. Resolve projected-column ownership PR #29.
3. Resolve schema/array agreement PR #30.
4. Characterize failure-atomic ownership using one shared-root design as the likely repair model.
5. Take dense-union ingestion as the strongest separate product contribution.
6. Take stream-null-error, metadata signed-length, and child-pointer validation as small hardening units.
7. Build reusable release-count and checked-span fixture helpers.
8. Add reference-consumer interoperability.

## Authority

- Public DuckDB contact: not authorized.
- Public repository writes during this research: none.
- Private characterization PRs are evidence carriers only and must not merge.
- No new numbered unit is claimed by these notes.
