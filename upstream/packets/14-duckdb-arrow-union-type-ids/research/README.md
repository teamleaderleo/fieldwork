# DuckDB Arrow follow-on research index

Date: 2026-08-06

These notes preserve read-only public-source inquiry and private Fieldwork characterization performed while unit 14 context was fresh. They do not expand unit 14's source scope, claim new numbered units, or authorize public upstream contact.

Newest public DuckDB main observed in this pass: `7a91c3658f9411ab17556e55f9df34b3b2140f6e`. Refresh every source-level claim before implementation.

## Research lanes

### 1. Dense-union ingestion

[`dense-union-ingestion.md`](dense-union-ingestion.md)

Substantial product candidate. Merged ADBC paths manually produce required dense unions while `arrow_scan` still rejects `+ud:`.

### 2. Arrow C Data validation

[`arrow-c-data-validation.md`](arrow-c-data-validation.md)

Small malformed-input units for child structure, parameter parsing, schema/array agreement, buffers, and metadata arithmetic.

### 3. Reference-consumer interoperability

[`reference-consumer-interop.md`](reference-consumer-interop.md)

PyArrow, Arrow C++, `arro3`, or nanoarrow oracles for layouts that DuckDB self-roundtrips cannot independently validate.

### 4. `arrow_scan` repeatability

[`arrow-scan-single-consumer.md`](arrow-scan-single-consumer.md)

Explicit multiple references and optimizer-introduced duplicate scans over one-shot providers.

### 5. Logical versus physical coordinates

[`arrow-coordinate-systems.md`](arrow-coordinate-systems.md)

Checked coordinate taxonomy for parent/chunk/list/dictionary/run-end/union/ListView traversal.

### 6. Pushdown capability contracts

[`arrow-pushdown-capability-contract.md`](arrow-pushdown-capability-contract.md)

Provider-, predicate-, scalar-, projection-, and whole-batch-specific pushdown safety.

### 7. Lifetime and ownership

[`arrow-lifetime-and-ownership.md`](arrow-lifetime-and-ownership.md)

Borrowed/moved/repeatable/one-shot/context-snapshot vocabulary and release-count matrices.

### 8. Metadata framing

[`arrow-metadata-framing.md`](arrow-metadata-framing.md)

Signed counts and lengths parsed from an unbounded raw pointer; separates immediate checks from a bounded internal parser.

### 9. Encoded-layout invariants

[`arrow-encoded-layout-invariants.md`](arrow-encoded-layout-invariants.md)

Structural, range, and full validation for dictionaries, run ends, lists/maps, ListView, arrays, and unions.

### 10. Extension-type contracts

[`arrow-extension-contracts.md`](arrow-extension-contracts.md)

Extension identity, storage, logical meaning, callback lifetime, degradation, and schema/appender parity. No built-in callback alias-lifetime defect was established.

### 11. C API projected-column ownership — confirmed

[`arrow-capi-zero-copy-ownership.md`](arrow-capi-zero-copy-ownership.md)

Confirmed by closed, unmerged private PR [`teamleaderleo/duckdb#29`](https://github.com/teamleaderleo/duckdb/pull/29):

- base/head: `58c019320e250a7b369efd756f84c6dfd68bedcb` / `b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`;
- run/job: `31102985877` / `92620944568` — success;
- artifact: `8969221973`;
- digest: `sha256:036913d4415c1473c7f1a66ebf582330f59c58f4b9e54c9f49db2db698e3861d`.

Existing C API control passed. The exact expected-negative reproduced:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

Only column zero's copied wrapper carries the real root release callback. A later-column alias can outlive the source chunk while retaining only a no-op wrapper.

### 12. Arrow C Stream error contracts

[`arrow-stream-error-contracts.md`](arrow-stream-error-contracts.md)

Null optional `get_last_error` details, callback validation, partial outputs, numeric codes, and release handling.

### 13. C API schema/array agreement — confirmed

[`arrow-capi-schema-array-agreement.md`](arrow-capi-schema-array-agreement.md)

Confirmed by closed, unmerged private PR [`teamleaderleo/duckdb#30`](https://github.com/teamleaderleo/duckdb/pull/30):

- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `41c76c97cdcbf5fbd6ecfc7b1f130b4f853166af`;
- ordinary Main `31103829101` — success;
- focused run/job `31103828472` / `92623801218`;
- artifact `8969719861`;
- digest `sha256:a81a04c00cd838b13b321e44545ee820eae57ff3414220373f3781453d0e5876`.

The workflow's grep missed because Catch wrapped the diagnostic. The artifact proved exact acceptance:

```text
CHECK( error != nullptr )
with expansion:
  nullptr != nullptr
with message:
  declared runtime child count=1 accepted=1 output columns=2 second output=21,
  22
```

Focused repair [`teamleaderleo/duckdb#33`](https://github.com/teamleaderleo/duckdb/pull/33) is active:

- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `d96e1053801c5f8514e21c17a51c5a93dd1f345d`;
- generated production fence: exactly `src/main/capi/arrow-c.cpp`;
- focused run `31107012002` and Main `31107013196` queued;
- regression requires stable invalid-input text, null output, unchanged caller release, and zero pre-caller release count.

### 14. Dictionary cache identity — closed avenue

[`arrow-dictionary-cache-identity.md`](arrow-dictionary-cache-identity.md)

No defect established for conforming producers because the cached dictionary retains the owning Arrow root.

### 15. C API conversion failure ownership

[`arrow-capi-failure-ownership.md`](arrow-capi-failure-ownership.md)

The stable API describes ownership moving to the returned `DataChunk`, while current conversion may consume the root before a later error returns no chunk.

### 16. Transactional shared-root repair design

[`arrow-capi-shared-root-repair-design.md`](arrow-capi-shared-root-repair-design.md)

One shared root owner, structural validation before transfer, and success-only commit as the coherent full design.

A narrower confirmed-defect repair is active in private draft [`teamleaderleo/duckdb#32`](https://github.com/teamleaderleo/duckdb/pull/32):

- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `35ceeae91aa02eef76cbd737dfbd68b26f17ba5e`;
- generated production fence: exactly `src/main/capi/arrow-c.cpp`;
- current behavior preserved on errors;
- one shared root wrapper is assigned to every column state;
- focused run `31106146125` and Main `31106148007` queued.

### 17. Null optional Arrow field names

[`arrow-null-field-names.md`](arrow-null-field-names.md)

Active private PR [`teamleaderleo/duckdb#31`](https://github.com/teamleaderleo/duckdb/pull/31), base/head `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `301993f1832aa66f05edf210b1bef3fd36f16848`.

Arrow permits `ArrowSchema.name = NULL`; DuckDB constructs a string before applying its empty-name fallback.

Expected-negative:

```text
empty field name accepted=1 null field name accepted=0
```

### 18. C API exception containment

[`arrow-capi-exception-containment.md`](arrow-capi-exception-containment.md)

Negative lengths, chunk initialization, schema-map access, state allocation, and child-table dereferences occur outside the current per-column conversion catch block. The next focused characterization should prove whether negative root length lets a C++ exception escape the C ABI.

## Cross-lane findings

### One root owner, not one copy per column

Every output vector aliasing any child buffer must retain the same shared root owner, independent of column order or projection.

### Structural validation precedes transfer

Child counts, pointer tables, required children, release state, and checked spans belong before dereference or ownership movement.

### Failure ownership must be explicit

Either transfer is success-only and transactional, or the API must explicitly document consume-on-entry semantics. Current behavior should not remain implicit.

### C ABI containment is separate from validation

Fast validation should prevent predictable malformed-input failures. One outer exception boundary must still prevent allocation, cast, and unexpected conversion exceptions from escaping the C API.

### Losing avenues stay recorded

The dictionary-cache analysis and corrected broad early-release hypothesis prevent repeated incomplete reasoning.

## Priority board

1. Finish unit 14 pinned restack, then refresh to actual latest main.
2. Execute and inspect shared-root repair PR #32.
3. Execute and inspect child-count repair PR #33.
4. Resolve null-name PR #31.
5. Characterize negative-length exception containment.
6. Characterize conversion-failure ownership before broadening the shared-root repair.
7. Take dense-union ingestion as the strongest separate product contribution.
8. Take stream-null-error, metadata signed-length, and child-pointer validation as small units.
9. Build reusable release-count and checked-span helpers.
10. Add reference-consumer interoperability.

## Authority

- Public DuckDB contact: not authorized.
- Public repository writes during this research: none.
- Private execution and characterization PRs must not merge.
- No new numbered unit is claimed by these notes.
