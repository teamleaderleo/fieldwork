# C API Arrow schema/array agreement

Date: 2026-08-06

Status: `HIGH-CONFIDENCE STRUCTURAL VALIDATION CANDIDATE`

Public upstream contact remains unauthorized. This is a private Fieldwork research note only.

## Source pin

DuckDB source inspected at `58c019320e250a7b369efd756f84c6dfd68bedcb`.

Relevant code:

- `src/main/capi/arrow-c.cpp`
- `src/function/table/arrow_conversion.cpp`
- `test/api/capi/test_capi_arrow.cpp`

## Current boundary

`duckdb_schema_from_arrow` builds a reusable converted schema. `duckdb_data_chunk_from_arrow` then initializes a DuckDB chunk from that schema and loops over the schema-derived output column count.

Inside that loop it dereferences:

```cpp
auto &array = parent_array.children[i];
```

without first proving that the runtime root array:

- has the same `n_children` as the converted schema;
- has a non-null `children` pointer when columns are expected;
- has a non-null child pointer at every required position;
- contains unreleased child arrays;
- has child lengths and offsets compatible with the root logical window.

The existing Arrow-to-DuckDB C API roundtrip test uses one column and therefore does not exercise schema/array disagreement.

## Why this is separate from type-specific validation

This is an O(1) root-structure contract. It should be checked before ownership transfer and before dispatching into dictionary, run-end, nested, or primitive converters.

A valid converted schema does not make a later ArrowArray valid. The API explicitly allows reusing the converted schema for multiple arrays, so every array needs independent structural validation.

## Deterministic characterizations

### Child-count mismatch accepted

Create a converted schema with two INT32 fields. Supply a root array with:

- `n_children = 1`;
- a two-entry `children` allocation;
- both child pointers valid.

Current code is expected to read both children despite the declared count. Correct behavior is an ordinary invalid-input error mentioning expected and actual child counts.

This fixture avoids a crash while proving that `n_children` is ignored.

### Missing child table

Two-field schema with `n_children = 2` and `children = nullptr`.

Correct behavior: ordinary invalid-input error before ownership transfer.

### Null child pointer

Two-field schema with `children[1] = nullptr`.

Correct behavior: ordinary invalid-input error identifying child index one.

### Released child

Two-field schema whose second child has `release = nullptr`.

Correct behavior: ordinary invalid-input error rather than conversion of a released array.

### Child logical span shorter than root

Root length three, child length one, but a padded backing buffer prevents a process crash.

Correct behavior: reject the structural inconsistency before reading the padding. This is especially important because the C Data ABI does not provide buffer byte lengths; the declared logical lengths are one of the few available safety boundaries.

### Root offset and child length

Exercise a struct root with nonzero offset and prove every child covers the effective `[offset, offset + length)` logical span.

## Repair direction

Add one root validator before creating per-column scan states:

1. reject a released root array;
2. reject negative `length`, `offset`, `n_children`, and `n_buffers`;
3. require runtime child count to equal converted-schema column count;
4. require `children` and each required child pointer;
5. require each child to be unreleased;
6. validate type-specific child spans through checked helpers before buffer access;
7. perform ownership transfer only after all O(1) structural checks pass.

On validation failure, leave the caller's root release callback untouched unless the documented API contract explicitly states that ownership transfers at function entry.

## Error-path contract to settle

The current function nulls `arrow_array->release` during conversion. A future unit should explicitly decide whether ownership transfers:

- at successful return only; or
- unconditionally once validation succeeds.

The tests should assert the chosen rule on first-column failure, later-column failure, and unsupported physical type.

## Scope recommendation

Start with child-count/pointer/release checks and deterministic C API tests. Keep buffer-count and encoded-layout checks in their respective narrow units.
