# C API Arrow schema/array agreement

Date: 2026-08-06

Status: `CONFIRMED ROOT CHILD-COUNT DEFECT — FOCUSED REPAIR ACTIVE`

Public upstream contact remains unauthorized. This is a private Fieldwork research note only.

## Exact confirmed evidence

Private characterization:

- PR: `teamleaderleo/duckdb#30` — closed without merge;
- immutable base: `7a91c3658f9411ab17556e55f9df34b3b2140f6e`;
- exact head: `41c76c97cdcbf5fbd6ecfc7b1f130b4f853166af`;
- ordinary Main: `31103829101` — success;
- focused run/job: `31103828472` / `92623801218`;
- artifact: `8969719861`;
- artifact digest: `sha256:a81a04c00cd838b13b321e44545ee820eae57ff3414220373f3781453d0e5876`;
- artifact name: `fieldwork-capi-arrow-schema-array-agreement`.

The focused workflow was red only because its grep expected one unwrapped diagnostic line. The retained test log is authoritative.

## Confirmed behavior

`duckdb_schema_from_arrow` builds a reusable converted schema. `duckdb_data_chunk_from_arrow` then initializes a DuckDB chunk from that schema and loops over the schema-derived output column count.

Inside that loop it dereferences:

```cpp
auto &array = parent_array.children[i];
```

without first requiring the runtime root array's declared child count to agree with the converted schema.

The expected-negative used:

- a converted schema with two INT32 fields;
- a runtime root with `n_children = 1`;
- a deliberately padded two-entry `children` allocation;
- both child pointers valid;
- values `11,12` and `21,22`.

This avoided an uncontrolled process crash while proving whether the declared count was enforced.

DuckDB accepted the malformed root and returned two columns. The exact retained failure was:

```text
CHECK( error != nullptr )
with expansion:
  nullptr != nullptr
with message:
  declared runtime child count=1 accepted=1 output columns=2 second output=21,
  22
```

The existing C API Arrow conversion control and ordinary Main passed.

## User-visible and safety impact

Ignoring `n_children` means behavior depends on the physical allocation behind `children`, not the ArrowArray contract:

- a padded allocation can expose undeclared children;
- a normal one-entry allocation can lead to out-of-bounds pointer reads;
- later conversion can dereference null, released, or unrelated objects;
- converted-schema reuse does not validate each runtime array independently.

The fixture proves contract violation without requiring a crash.

## Active focused repair

Private draft PR: `teamleaderleo/duckdb#33`

- base: `7a91c3658f9411ab17556e55f9df34b3b2140f6e`;
- head: `d96e1053801c5f8514e21c17a51c5a93dd1f345d`;
- focused run: `31107012002` — queued at this note update;
- ordinary Main: `31107013196` — queued;
- generated production fence: exactly `src/main/capi/arrow-c.cpp`.

The repair intentionally handles only the confirmed root child-count mismatch:

1. initialize `*out_chunk = nullptr` after argument validation;
2. compare runtime `n_children` with converted-schema column count;
3. reject disagreement before chunk allocation, ownership transfer, or child dereference;
4. return `DUCKDB_ERROR_INVALID_INPUT` with stable message:
   `Arrow array child count mismatch: expected 2, got 1`;
5. leave the caller's root release callback and ownership intact on failure.

The regression asserts error type, exact message, null output chunk, unchanged release callback, zero release count before caller cleanup, and exactly one release after caller cleanup.

## Remaining structural candidates

The confirmed count repair does not yet prove or repair:

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

Correct behavior: reject the logical inconsistency before reading padding.

### Root offset and child length

A struct root with nonzero offset should require every child to cover the effective `[offset, offset + length)` logical window.

### Negative structural fields

Negative `length`, `offset`, `n_children`, `n_buffers`, or impossible `null_count` should be rejected before numeric casts or allocation.

## Broader validator direction

After the focused child-count repair is executed and inspected, a later structural validator can add, in small characterized slices:

1. released root rejection;
2. nonnegative structural fields;
3. child-table presence;
4. required child-pointer presence;
5. child release state;
6. type-specific checked spans;
7. ownership transfer only after fast structural validation.

Keep full O(n) content validation separate.

## Relationship to ownership work

- confirmed projected-column ownership is repaired separately in PR #32;
- this child-count check occurs before ownership transfer and therefore already exercises success-only behavior for this validation failure;
- conversion-failure ownership after structural validation remains a separate contract lane.

## Disposition

The child-count defect is established. PR #33 is the narrow repair authority. Close the repair carrier without merge after focused evidence transfer and publish any accepted source through a clean source-only branch.
