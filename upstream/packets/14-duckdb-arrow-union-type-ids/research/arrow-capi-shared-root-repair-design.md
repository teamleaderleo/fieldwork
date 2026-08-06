# C API Arrow shared-root transactional repair design

Date: 2026-08-06

Status: `DESIGN DRAFT — REQUIRES CHARACTERIZATION RESULTS`

Public upstream contact remains unauthorized. This is a private Fieldwork design note, not an implemented repair.

## Problem cluster

Three related C API surfaces are under investigation:

1. a projected later column may outlive the original chunk while holding a copied root wrapper whose release callback is null;
2. the runtime ArrowArray child structure is not checked against the previously converted schema before child dereference;
3. conversion can null the caller's root release callback and later return an error without returning the DataChunk named by the ownership documentation.

Private characterization PRs #29 and #30 test the first two independently. The third remains a planned failure-atomicity characterization.

## Design goal

Represent the incoming Arrow root exactly once. Every output vector that aliases Arrow memory must reference that same owner. Ownership should move from the caller only after structural validation and all conversion work succeed.

## Transactional sequence

Pseudocode:

```cpp
// Validate API handles and initialize output deterministically.
*out_chunk = nullptr;
ValidateRootAgainstConvertedSchema(*arrow_array, *arrow_table);

// Borrow the root during conversion. The temporary shared owner contains all
// pointers/private_data but is disarmed, so error cleanup cannot consume caller data.
auto root_owner = make_shared_ptr<ArrowArrayWrapper>();
root_owner->arrow_array = *arrow_array;
auto caller_release = root_owner->arrow_array.release;
root_owner->arrow_array.release = nullptr;

// Every column state receives the exact same shared owner.
for (idx_t i = 0; i < column_count; i++) {
    auto state = make_uniq<ArrowArrayScanState>(*context);
    state->owned_data = root_owner;
    ConvertColumn(..., *state, ...);
}

// Commit only after complete success.
root_owner->arrow_array.release = caller_release;
arrow_array->release = nullptr;
*out_chunk = reinterpret_cast<duckdb_data_chunk>(dchunk.release());
```

If conversion throws, partially built vectors release references to the disarmed shared owner. The caller still owns the original ArrowArray and its release callback remains intact.

## Structural validation before borrowing

Minimum O(1) root checks:

- root `release` is non-null;
- `length`, `offset`, `null_count`, `n_buffers`, and `n_children` are nonnegative when required by the ABI;
- root child count equals the converted-schema column count;
- child pointer table exists when columns are expected;
- every required child pointer is non-null;
- every required child has a non-null release callback;
- root logical window arithmetic does not overflow.

Then dispatch type-specific validators before accessing buffers:

- required minimum buffer count and buffer table;
- dictionary pointer agreement;
- run-end child structure;
- list/list-view offset and size buffers;
- struct/union/fixed-array child count and spans;
- dense-union discriminant/offset buffers;
- child logical span covers the effective root window where the Arrow layout requires it.

Full O(n) content validation remains optional and separate.

## Ownership invariants

### Success

- caller release callback becomes null exactly once;
- release count remains zero while the DataChunk or any referenced output vector survives;
- arbitrary column projection order does not matter;
- dropping column zero cannot release data still referenced by column N;
- root release count becomes one after the final Arrow-backed alias is destroyed.

### Validation failure

- `out_chunk` is null;
- caller release callback is unchanged;
- release count remains zero until the caller releases;
- no child callback or buffer is touched after the failed validation point.

### Conversion failure

- same invariants as validation failure;
- partial vectors may be constructed and destroyed, but their shared owner is disarmed;
- the reusable converted schema remains usable for a later valid array.

### Copy/reference behavior

- `Vector::Ref`, `Reference`, `ReferenceColumns`, dictionary caches, list children, struct children, and run-end intermediate vectors preserve the same root-owner shared pointer whenever they alias Arrow storage;
- conversion paths that fully copy data may retain the owner harmlessly, but an optimization can later avoid attaching it only if copy semantics are proven for that path.

## Error handling

The validator and conversion should return ordinary invalid-input/conversion errors. Error text should include:

- operation (`duckdb_data_chunk_from_arrow`);
- field or child index;
- expected and actual structural values;
- no raw addresses or provider-private details.

Set `*out_chunk = nullptr` at entry so every error path is deterministic.

## Characterization-to-repair gate

Do not implement a combined repair until:

1. PR #29 proves or disproves the projected later-column release signature;
2. PR #30 proves or disproves runtime child-count acceptance;
3. a separate later-column conversion-failure fixture records current ownership behavior;
4. the API documentation and maintainers' existing conventions are checked for success-only versus consume-on-entry transfer.

If #29 is disproven, retain one shared owner as a simplification only if it still improves failure atomicity and does not add unnecessary retention. If #30 is disproven, preserve the existing validator responsible and narrow the repair accordingly.

## Focused repair scope if both active hypotheses reproduce

Expected source surface:

- `src/main/capi/arrow-c.cpp`;
- one small internal root validator, preferably colocated initially;
- `test/api/capi/test_capi_arrow.cpp` or one focused ownership/validation test file;
- `test/api/capi/CMakeLists.txt` only if a new test file is used.

Do not mix this repair with Arrow scan streams, union mapping, dense union support, metadata parsing, or optimizer repeatability.

## Review questions

- Does any supported caller depend on consume-on-error semantics?
- Can a custom Arrow extension conversion retain a raw pointer without sharing the source vector buffer?
- Does every nested conversion state inherit `owned_data` from the shared root?
- Are dictionary caches permitted to outlive the result chunk, and do they keep the same owner?
- Can commit of the release callback throw? It should be a no-throw final state transition.
- Should root validation live in the general Arrow converter so `arrow_scan` and the C API can share checks, or remain at the C API boundary initially?

## Disposition

This design unifies projected-column lifetime, structural validation ordering, and failure-atomic ownership. It remains conditional on exact-head characterization evidence.
