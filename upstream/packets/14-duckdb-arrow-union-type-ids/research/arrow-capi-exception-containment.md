# C API Arrow exception containment

Date: 2026-08-06

Status: `SOURCE-SUPPORTED C ABI SAFETY CANDIDATE`

Public upstream contact remains unauthorized. This is a private Fieldwork note only.

## Source pin

DuckDB public main inspected at `7a91c3658f9411ab17556e55f9df34b3b2140f6e`.

Relevant function:

- `src/main/capi/arrow-c.cpp::duckdb_data_chunk_from_arrow`

## Current exception boundary

The function's `try` blocks cover only type-specific per-column conversion. Several operations that can throw or fault happen earlier:

1. `NumericCast<idx_t>(arrow_array->length)` during `DataChunk::Initialize`;
2. allocation and initialization of the output chunk;
3. a second `NumericCast<idx_t>(arrow_array->length)` for cardinality;
4. `arrow_types.at(i)`;
5. per-column state allocation;
6. root and child table access before the conversion `try`;
7. `parent_array.children[i]` when the table is null or too short.

A C API function returning `duckdb_error_data` should not allow a C++ exception to escape across the C ABI, and malformed Arrow input should not reach an unchecked null or out-of-bounds dereference.

## High-value deterministic characterizations

### Negative root length

Create a valid one-column converted schema and a root array with:

- `length = -1`;
- otherwise valid child/table/release fields.

Call inside a C++ test harness that catches any escaped exception.

Correct behavior:

- function does not throw;
- returns `DUCKDB_ERROR_INVALID_INPUT`;
- `out_chunk` is null;
- caller ownership remains intact;
- exact message identifies negative Arrow array length.

Current source strongly suggests `NumericCast<idx_t>` throws before the conversion catch block.

### Excessive root length

Use a length too large for `idx_t` or for safe chunk allocation, without allocating corresponding buffers because validation should reject first.

Correct behavior: ordinary error, no allocation attempt, no ownership transfer.

### Null child table

After child-count validation succeeds, set `children = nullptr` with a nonzero expected column count.

Correct behavior: ordinary invalid-input error before dereference.

### Null required child pointer

Provide a valid child table with one required entry null.

Correct behavior: ordinary error identifying child index.

### Missing converted-schema column metadata

If a malformed or stale converted schema can make `arrow_types.at(i)` throw, the C boundary must convert that exception into `duckdb_error_data`.

### Allocation failure simulation

Where test infrastructure permits, force or mock an allocation exception during chunk initialization and verify no exception crosses the ABI and caller ownership is unchanged.

## Repair layers

### Layer 1: fast structural validation

Before allocation or numeric cast:

- initialize `*out_chunk = nullptr`;
- reject negative length, offset, child count, and buffer count;
- reject impossible null count;
- require root child-count agreement;
- require child table and required child pointers.

This removes most malformed-input exceptions before they arise.

### Layer 2: full C API containment

Wrap the complete conversion body after trivial argument validation in one outer `try`/`catch`:

```cpp
try {
    ValidateRoot(...);
    BuildAndConvert(...);
    *out_chunk = ...;
    return nullptr;
} catch (const duckdb::Exception &ex) {
    return duckdb_create_error_data(DUCKDB_ERROR_INVALID_INPUT, ex.what());
} catch (const std::exception &ex) {
    return duckdb_create_error_data(DUCKDB_ERROR_INVALID_INPUT, ex.what());
} catch (...) {
    return duckdb_create_error_data(DUCKDB_ERROR_INVALID_INPUT,
                                    "Unknown error occurred during Arrow conversion");
}
```

Specific unsupported-type paths can retain `DUCKDB_ERROR_NOT_IMPLEMENTED` through explicit exceptions or status conversion.

### Layer 3: failure-atomic ownership

The outer catch is not enough if caller ownership has already moved. Pair containment with the transactional shared-root design:

- borrow through a disarmed shared owner during conversion;
- commit the release callback only after success;
- leave caller ownership intact on any exception.

## Error taxonomy

Do not map every internal exception blindly to invalid input. Suggested distinctions:

- malformed Arrow structure/content: `DUCKDB_ERROR_INVALID_INPUT`;
- unsupported valid Arrow layout: `DUCKDB_ERROR_NOT_IMPLEMENTED`;
- allocation/resource failure: preserve the closest available error type;
- unexpected internal invariant: return an error object without letting the exception cross the ABI, while retaining internal-error classification where supported.

## Relationship to active repairs

- PR #33 adds the first pre-transfer child-count validation and deterministic null output on that failure.
- PR #32 repairs successful projected-column ownership only and intentionally preserves existing error semantics.
- A later failure-atomic repair should consolidate outer containment, prevalidation, and transactional ownership after focused characterizations.

## Disposition

Do not broaden PR #32 or #33 with uncharacterized exception handling. Characterize negative length first on exact current main, then repair exception containment in a separate source carrier or as part of the explicitly scoped transactional ownership unit.
