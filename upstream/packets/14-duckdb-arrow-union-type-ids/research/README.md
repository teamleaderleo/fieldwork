# DuckDB Arrow follow-on research index

Date: 2026-08-06

These notes preserve read-only public-source inquiry and private Fieldwork characterization performed while unit 14 context was fresh. They do not expand unit 14's nine-file source scope, claim new numbered units, or authorize public upstream contact.

The newest public DuckDB main observed during this pass is `7a91c3658f9411ab17556e55f9df34b3b2140f6e`. The focused source audits and active C API characterization are pinned to `58c019320e250a7b369efd756f84c6dfd68bedcb`; the intervening public changes inspected were unrelated benchmark infrastructure. Refresh every source claim before implementation.

## Research lanes

### 1. Dense-union ingestion

[`dense-union-ingestion.md`](dense-union-ingestion.md)

A substantial separate capability candidate. DuckDB has merged ADBC paths that manually produce required dense unions, while `arrow_scan` still rejects `+ud:`. The note defines the two-coordinate conversion model, narrow ingestion-only scope, validation boundaries, and a discriminating regression matrix.

### 2. Arrow C Data validation

[`arrow-c-data-validation.md`](arrow-c-data-validation.md)

A sequence of small malformed-input hardening units under public issue `duckdb/duckdb#21849`: schema child structure, parameterized format parsing, schema/array agreement, buffer structure, and metadata arithmetic.

### 3. Reference-consumer interoperability

[`reference-consumer-interop.md`](reference-consumer-interop.md)

A testing-infrastructure candidate. DuckDB-only round trips can miss schema/layout incompatibilities. The note compares duckdb-python/PyArrow, a small core Arrow C++ or `arro3` oracle, and nanoarrow-based options, with a bidirectional fixture matrix.

### 4. `arrow_scan` repeatability and single-consumer semantics

[`arrow-scan-single-consumer.md`](arrow-scan-single-consumer.md)

A correctness lane covering explicit multiple references and optimizer-introduced duplicate scans. It compares capability flags, binding-specific repeatability, automatic materialization, and narrow rewrite guards.

### 5. Logical versus physical coordinates

[`arrow-coordinate-systems.md`](arrow-coordinate-systems.md)

A cross-cutting taxonomy for parent offsets, chunk offsets, list child starts, dictionary positions, run ends, sparse/dense unions, and ListView spans. It includes fixture-design guidance intended to expose the exact physical slot read.

### 6. Pushdown capability contract

[`arrow-pushdown-capability-contract.md`](arrow-pushdown-capability-contract.md)

Pushdown safety depends on predicate kind, scalar construction, whole-batch layout, projection identity, residual-filter handling, and stream provider—not only the filtered DuckDB type. The note proposes a binding-specific capability model and plan-and-result test matrix.

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

An audit of extension identity, physical storage, DuckDB logical meaning, callback/context lifetime, unknown-extension degradation, and schema/appender agreement. Current built-in callbacks copy output or preserve DuckDB buffer references; no core alias-lifetime defect was established there.

### 11. C API projected-column ownership

[`arrow-capi-zero-copy-ownership.md`](arrow-capi-zero-copy-ownership.md)

Active private characterization: [`teamleaderleo/duckdb#29`](https://github.com/teamleaderleo/duckdb/pull/29), exact base `58c019320e250a7b369efd756f84c6dfd68bedcb`.

The original broad hypothesis—release during ordinary per-column conversion—was corrected. Generic conversion attaches each column's copied root wrapper to the output vector buffer, so the complete source chunk remains safe. The refined risk is that only column zero's wrapper carries the actual root release callback. A later-column projection can outlive the source chunk while retaining only a no-op wrapper. The expected-negative fixture keeps column two, destroys the source chunk, and uses a root release callback that poisons column two.

Correct behavior keeps the root alive until the surviving projection is destroyed. The expected defect signature is:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

No defect should be called confirmed until the exact-head focused workflow reproduces that signature.

### 12. Arrow C Stream error contracts

[`arrow-stream-error-contracts.md`](arrow-stream-error-contracts.md)

A small wrapper-level hardening candidate. Arrow permits `get_last_error` to return `NULL`; DuckDB currently constructs a `string` directly from that optional pointer after stream callback failures. The note defines null-detail, missing-callback, partial-output, numeric-error, and release-count controls.

### 13. C API schema/array agreement

[`arrow-capi-schema-array-agreement.md`](arrow-capi-schema-array-agreement.md)

A high-confidence structural validation candidate. `duckdb_data_chunk_from_arrow` uses the converted-schema column count and dereferences runtime child pointers without first checking root child count, child table presence, required child pointers, release state, or logical spans. The note defines deterministic non-crashing mismatch fixtures and a pre-transfer O(1) validator.

### 14. Dictionary cache identity

[`arrow-dictionary-cache-identity.md`](arrow-dictionary-cache-identity.md)

Audited and closed as a defect avenue for conforming producers. DuckDB's cached dictionary vector retains the owning root array. Arrow forbids the producer from mutating or recycling that dictionary object before release, so pointer identity remains adequate while ownership retention is preserved.

## Earlier broad sweep

[`../adjacent-duckdb-arrow-research-2026-08-05.md`](../adjacent-duckdb-arrow-research-2026-08-05.md) records the initial routing-level survey and source links.

## Cross-lane themes

### Logical and physical coordinates

Dense unions, sparse unions, ListView, dictionaries, run ends, and fixed arrays need explicit checked spans rather than ad hoc offset arithmetic.

### Capability belongs to the bound provider

Pushdown and repeatability cannot be inferred from a logical Arrow schema alone. The same schema may be backed by PyArrow, Java Arrow, a one-shot C Stream, or a repeatable factory.

### Lifetimes are part of the data contract

A valid schema or array is not enough if its producer, root owner, extension context, or release holder has gone away. A shared root owner should be represented once and propagated to every alias, not copied after its release callback has already been moved away.

### DuckDB self-roundtrip is necessary but insufficient

Reference consumers are needed to prove schema/data layout agreement, extension metadata semantics, and standards-conforming noncanonical inputs.

### Validation needs levels

Fast structural checks should prevent unsafe dereferences and arithmetic. Full content validation should exist as a strict/test oracle without automatically taxing every trusted scan.

### Losing avenues must stay recorded

The dictionary-cache analysis and the corrected broad ownership hypothesis are retained to stop future workers from repeating the same incomplete reasoning.

## Priority board

### Active characterization

**Projected later-column C API ownership** — exact private PR #29, narrow public API boundary, deterministic poisoned-buffer oracle.

### Highest-confidence next hardening

**C API schema/array agreement** — child-count and pointer checks before ownership transfer or conversion.

### Strongest product contribution

**Dense-union ingestion** — already demanded by merged ADBC producers and external standards.

### Best small hardening slices

- null-safe Arrow stream error detail;
- negative metadata count/length rejection;
- schema child-count and pointer validation;
- validity bitmap no-overread;
- run-end structural/monotonic validation.

### Best enabling infrastructure

- release-count Arrow C Data fixture utility;
- reference-consumer interop lane;
- checked span helpers for nested and encoded layouts.

## Suggested routing order

1. Finish unit 14's pinned current-main execution path, then refresh to actual latest main and obtain complete-diff review.
2. Resolve private characterization PR #29: confirm the refined projected-column defect or close it as disproven.
3. Characterize C API schema/array disagreement with non-crashing count and pointer fixtures.
4. Take dense-union ingestion as the strongest separate product contribution.
5. Take stream-null-error, metadata signed-length, and schema child-structure validation as small units.
6. Build a reusable release-count C Data fixture utility.
7. Address `arrow_scan` repeatability with binding-specific capability or automatic materialization.
8. Add reference-consumer interoperability as enabling infrastructure.
9. Introduce checked span helpers before broad encoded-layout validation.
10. Revisit provider-specific pushdown after projection and residual-filter invariants are covered.

## Authority

- Public DuckDB contact: not authorized.
- Public repository writes during this research: none.
- Private characterization PRs are execution evidence only and must not merge.
- No new numbered unit is claimed by these notes.
