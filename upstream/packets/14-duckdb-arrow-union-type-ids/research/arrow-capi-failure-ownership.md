# C API Arrow conversion failure ownership

Date: 2026-08-06

Status: `CONTRACT AND FAILURE-ATOMICITY CANDIDATE`

Public upstream contact remains unauthorized. This is a private Fieldwork research note only.

## Source and API pins

DuckDB source and generated C API inspected at public main `7a91c3658f9411ab17556e55f9df34b3b2140f6e`.

Relevant surfaces:

- `src/main/capi/arrow-c.cpp`
- `src/include/duckdb.h`
- `duckdb_data_chunk_from_arrow`

The stable API documentation says the input Arrow data ownership is passed to DuckDB's returned `DataChunk`, and the caller no longer owns the underlying data.

## Current implementation sequence

For each output column, `duckdb_data_chunk_from_arrow` currently:

1. allocates a per-column `ArrowArrayScanState`;
2. copies the complete root `ArrowArray` into that state's wrapper;
3. sets the caller's `arrow_array->release = nullptr`;
4. attempts column conversion inside a `try` block;
5. catches conversion errors and returns `duckdb_error_data` without returning a chunk.

This means ownership transfer begins before conversion success is known.

On first-column failure, the loop-local owner can release the root during unwinding. On later-column failure, earlier output vectors and the partially built chunk can retain or release the moved owner during cleanup. In either case the caller may receive an error with its root release callback already nulled and no `DataChunk` through which the documented ownership can be exercised.

## Contract question

One of two policies must be explicit and tested.

### Transactional success-only transfer

- validation and conversion failure leave caller ownership intact;
- `arrow_array->release` remains unchanged on error;
- ownership moves exactly once only after all columns convert successfully;
- the returned chunk owns one shared root owner.

This most closely matches “ownership is passed to the returned DataChunk.”

### Consume-on-entry transfer

- DuckDB consumes and eventually releases the array even when conversion fails;
- the API documentation must state that the input is consumed once the function accepts the arguments, regardless of return status;
- error paths must release exactly once;
- callers must never release after any call, successful or failed.

This can be valid, but it is a materially different API contract.

## Recommended direction

Prefer success-only transfer:

1. perform all O(1) root/schema/child validation before changing the caller object;
2. create one shared root owner, but keep the caller callback restorable until conversion commits;
3. have every per-column state reference that same shared owner;
4. convert all columns;
5. only after success, null the caller release callback and commit the chunk to `out_chunk`;
6. on failure, destroy temporary DuckDB vectors without invoking the caller's root release and leave caller ownership unchanged.

If zero-copy vectors require the owner during conversion, use a temporary owner whose destructor is disarmed on failure rather than copying and moving the root callback per column.

## Characterization matrix

Every test needs an exact recursive root release counter and an initialized `out_chunk = nullptr`.

### Validation failure before conversion

- schema/runtime child-count mismatch;
- null child table;
- null required child pointer;
- released child array.

Expected under success-only transfer:

- error returned;
- `out_chunk` remains null;
- caller root release callback remains non-null;
- release count remains zero until caller releases.

### First-column conversion failure

Use a structurally valid schema/array whose first converter throws an ordinary DuckDB exception without process failure.

Assert the same four properties.

### Later-column conversion failure

Column zero must convert zero-copy successfully; column one then throws. This proves partial vector construction does not consume the root on a failed call.

### Success control

- conversion succeeds;
- caller root release becomes null;
- release count is zero while chunk lives;
- release count becomes one when chunk and all aliases are destroyed.

### Reused converted schema

A failed array followed by a valid array using the same converted schema must behave predictably and must not inherit stale ownership or scan state.

## Relationship to active characterizations

- PR #29 tests whether projected later columns share one real root owner after successful conversion.
- PR #30 tests schema/runtime child-count enforcement before conversion.
- This lane tests whether ownership transfer is failure-atomic when no chunk is returned.

The preferred repair—one shared root owner plus pre-transfer structural validation—can address all three surfaces coherently, but they should be characterized independently before a combined repair is proposed.

## Scope recommendation

Keep this a C API ownership and error-path unit. Do not mix it with dense unions, Arrow stream ownership, or type-specific buffer validation.
