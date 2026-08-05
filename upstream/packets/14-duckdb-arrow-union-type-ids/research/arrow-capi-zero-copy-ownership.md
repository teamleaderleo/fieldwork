# DuckDB Arrow C API zero-copy ownership

Date: 2026-08-05

## Status

Research and candidate-defect characterization plan only. The suspected multi-column lifetime problem below is source-supported but has not yet been executed in a native reproducer. Do not present it as confirmed until the release-count fixture runs.

No public write or new source claim is authorized by this note.

Source was inspected at DuckDB public commit `043e1894425b49984c5010f253589e5d9c5fdde4`; later source must be refreshed before implementation.

## API under review

The newer C conversion path separates schema conversion from array conversion:

```text
duckdb_schema_from_arrow(connection, schema, &converted_schema)
duckdb_data_chunk_from_arrow(connection, array, converted_schema, &chunk)
```

This is useful for repeated batches sharing one schema and supports zero-copy references where conversion permits them.

The contract must define:

- whether `ArrowArray` ownership is borrowed or moved;
- whether the entire root is retained until the DuckDB chunk dies;
- whether a converted schema may be reused across arrays;
- whether array child structure is revalidated against the converted schema;
- which vectors copy values and which alias producer buffers;
- what happens on partial failure after ownership transfer.

## Source-supported ownership hazard

At the inspected source, `duckdb_data_chunk_from_arrow` loops over DuckDB output columns. Inside each column iteration it:

1. creates a fresh `ArrowArrayScanState`;
2. creates a fresh `ArrowArrayWrapper` in that state;
3. copies the entire root `ArrowArray` into the wrapper;
4. sets the caller's root `arrow_array->release` to null, transferring ownership;
5. converts one child column;
6. lets the local scan state leave scope at the end of the iteration.

Pseudocode matching the current shape:

```text
for each column i:
    state = new ArrowArrayScanState
    state.owned_data = new ArrowArrayWrapper
    state.owned_data.arrow_array = *root
    root.release = nullptr
    convert(root.children[i], state)
    destroy state
```

`ArrowArrayWrapper` releases its held array when destroyed. Therefore, unless the converted vector attaches a surviving auxiliary reference to `state.owned_data`, the first loop iteration can release the root array tree before the second child is converted.

This risk is strongest when the first column is a copied fixed-width type such as INTEGER: the DuckDB vector no longer needs the Arrow data after conversion, so there may be no reason for it to retain auxiliary ownership. The temporary state can then be the only live owner.

Even if an aliased string, dictionary, or run-end vector retains ownership, relying on the first column's physical conversion mode to keep the entire root alive is not a valid root-array contract.

## Why existing tests may miss it

The current C API Arrow→DuckDB roundtrip test converts a table with one INTEGER column. A one-column array can be released after that column is copied without exposing use-after-release.

The test also uses DuckDB's own Arrow appender, whose release behavior may be less discriminating than an external producer that recursively frees children and poisons memory.

No multi-column `duckdb_data_chunk_from_arrow` test or release-count test was found in the inspected test section.

## Candidate failure modes

1. use-after-free while converting column two or later;
2. crash only with producers whose root release recursively destroys children;
3. silent incorrect values if freed child buffers remain readable;
4. double ownership if multiple wrappers copy the same non-null root release callback;
5. leaked root on an exception after `root.release` is nulled but before ownership reaches the output chunk;
6. dangling zero-copy strings after the returned chunk outlives a temporary state;
7. schema/array mismatch when a converted schema is reused with a structurally different array.

## Correct ownership shape

Root ownership should be transferred once, outside the per-column loop:

```text
root_owner = shared ArrowArrayWrapper(*root)
root.release = nullptr

for each column i:
    state = ArrowArrayScanState
    state.owned_data = root_owner
    convert(root.children[i], state)

attach root_owner to the DataChunk or every aliasing vector until chunk destruction
```

Two valid implementation strategies:

### A. Chunk-level owner

Add one auxiliary owner to `DataChunk` or a chunk-owned buffer object. All columns share it, including copied columns. The root remains alive through conversion and until chunk destruction.

### B. Outer owner plus alias-only retention

Keep one root owner alive for the entire conversion loop. Attach shared ownership only to vectors that alias Arrow buffers. After conversion:

- if no vector aliases, release root immediately;
- if any vector aliases, their auxiliary data retains the root.

This is more memory-efficient but requires every conversion path to accurately report aliasing.

For simplicity and safety, chunk-level ownership may be preferable initially.

## Partial-failure contract

Ownership transfer occurs before conversion. If column conversion throws:

- the root must be released exactly once;
- `out_chunk` must remain null;
- no partially built vector may retain a dangling pointer;
- the caller must not release the moved array;
- the API documentation must state that ownership was consumed even on conversion failure, or transfer must be delayed until all validation succeeds.

A cleaner sequence is:

1. validate root and all child structure without taking ownership;
2. allocate output chunk;
3. establish one RAII root owner;
4. null caller release to commit the move;
5. perform conversions;
6. transfer owner into returned chunk;
7. RAII releases on any failure.

## Schema reuse invariants

`duckdb_schema_from_arrow` retains DuckDB type information derived from one schema. Every later array passed with that converted schema should be checked for:

- root child count equals schema column count;
- non-null root child pointer array;
- each child layout matches retained physical Arrow type;
- dictionary presence agrees with schema;
- nested child counts agree;
- array length/offset arithmetic is valid;
- extension storage layout remains compatible.

A schema handle should not make raw arrays trusted.

## Discriminating native reproducer

Construct a two-column root array with a recursive release callback that:

- increments a release counter;
- poisons or frees both child buffers;
- sets child pointers to a recognizable invalid state;
- sets root release to null.

Columns:

1. INTEGER fixed-width copied column;
2. VARCHAR or INTEGER second column whose values are checked after conversion.

Expected correct behavior:

- `duckdb_data_chunk_from_arrow` succeeds;
- both columns have exact values;
- caller root release is null after the move;
- release count is zero during conversion;
- release count becomes one only when the returned DuckDB chunk is destroyed, or immediately after conversion only if all values were copied and the contract intentionally releases early;
- never more than one release.

To expose timing, the root release callback can set a global `released` flag. The second child's buffer accessor or a guarded memory region should fail deterministically if read after release.

## Expanded matrix

1. two copied fixed-width columns;
2. fixed-width first, string second;
3. string first, fixed-width second;
4. dictionary first/second;
5. run-end encoded first/second;
6. nested list or struct child;
7. three or more columns;
8. zero columns;
9. second-column conversion error;
10. root child-count mismatch;
11. reused converted schema with different array layout;
12. caller destroys converted schema before returned chunk;
13. returned chunk outlives connection;
14. caller attempts to release moved array and observes documented null release;
15. allocation failure after validation but before committed ownership transfer.

## Documentation issue

The generated C API documentation should say explicitly:

- whether the function consumes `ArrowArray` ownership;
- when the producer may free buffers;
- whether the converted schema is borrowed and must outlive the call only or the returned chunk;
- whether the connection must outlive the returned chunk;
- how errors affect array ownership.

The implementation currently nulls `arrow_array->release`, which strongly implies a move, but this must be stated as an API guarantee.

## Routing recommendation

This is a strong focused characterization candidate because:

- it concerns a public C API ownership boundary;
- the source pattern is suspicious and the existing test is single-column;
- a release-count fixture can prove or disprove it without a broad rewrite;
- the likely repair is localized to `duckdb_data_chunk_from_arrow` and its tests.

First action should be a private expected-negative test on exact current source. Do not implement until the test demonstrates release-before-second-column or another concrete failure signature.

## Relevant source

- `src/main/capi/arrow-c.cpp`
- `src/include/duckdb/function/table/arrow.hpp`
- `src/function/table/arrow/arrow_array_scan_state.cpp`
- `src/function/table/arrow_conversion.cpp`
- `test/api/capi/test_capi_arrow.cpp`

## Related prior art

- `duckdb/duckdb#16050` — schema ownership/leak ambiguity in deprecated Arrow scan API;
- `duckdb/duckdb#22508` — context lifetime for lazy Arrow conversion;
- unit 14 malformed-stream work — release accounting on expected errors.
