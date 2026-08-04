# Research lane — DuckDB Arrow dense-union ingestion

Date: 2026-08-05

## Status

`UNCLAIMED FOLLOW-ON — substantial separate contribution candidate`

This note is read-only research. It does not expand unit 14 source scope, claim a new numbered unit, or authorize public upstream contact.

## Why this is now a real interoperability gap

DuckDB current public main observed at `daa81697e31a3dc97a93f11220037cd2213af6cd` still accepts only sparse Arrow unions. The `+u` schema branch rejects any mode other than `s`, so `+ud:` cannot be consumed by `arrow_scan`.

The gap is no longer hypothetical:

- merged `duckdb/duckdb#23230` implements ADBC Statistics, whose `statistic_value` must be a dense union;
- merged `duckdb/duckdb#24196` implements ADBC `ConnectionGetInfo`, whose `info_value` must also be a dense union;
- both implementations manually construct Arrow schema/array trees because normal DuckDB Arrow export cannot produce the required dense layout;
- both explicitly avoid `arrow_scan` in their C++ validation because DuckDB cannot consume the dense result it just produced; external consumers such as PyArrow provide the end-to-end check.

A search found no current open DuckDB issue or pull request dedicated to dense-union ingestion.

## Prior art and what to reuse

Closed `duckdb/duckdb#21898` combined three concerns:

1. dense-union ingestion;
2. optional dense-union export;
3. logical type-ID mapping.

Its useful ingestion ideas are:

- retain union mode and logical type-ID mapping in union-specific Arrow type information;
- read the dense `int32` value-offset buffer;
- map the row's logical type code before selecting the compact child;
- keep chunk and array offsets in the union row coordinate system while dense child offsets remain child-local.

Do not revive the entire PR mechanically. Unit 14 now owns the focused logical-ID mapping and sparse child-offset repair with stronger validation. Export settings and appender behavior are separate review surfaces.

## Reference-model observations

Apache Arrow C++ models dense unions with:

- no validity bitmap;
- an `int8` type-code buffer;
- an `int32` value-offset buffer;
- compact child arrays whose lengths are independent of the union's logical row count.

Unlike sparse unions, slicing the parent does not slice every child. Each logical row selects one child through the type-code map and then selects one physical child value using that row's value offset.

This creates two coordinate systems:

- **union-row coordinate:** parent/array/chunk/nested offsets used to locate type code and value offset;
- **selected-child coordinate:** the `int32` dense value offset used only inside the mapped compact child.

Combining those coordinates is the central correctness risk.

## Proposed narrow source scope

A reviewable ingestion-only implementation would likely:

1. extend union-specific Arrow type information to retain sparse versus dense mode while reusing unit 14's validated `0..127` type-code map;
2. parse `+ud:` with the same full-token, count, range, and duplicate checks as `+us:`;
3. validate the runtime array shape before typed buffer access:
   - dense mode has the expected buffer count;
   - type-code and value-offset buffers exist;
   - array child count and child pointers match schema-derived union metadata;
4. compute the effective union-row offset exactly once;
5. for each output row:
   - read the logical type code;
   - map it to a child index;
   - read the corresponding `int32` dense child offset;
   - reject negative or out-of-range child offsets;
   - read the value from the mapped compact child at that child-local offset;
   - construct the DuckDB union using the mapped child index as the tag;
6. preserve dictionary, extension, view, and run-end child semantics without assuming each child has `size` logical rows.

The last point is why this is not a small modification to unit 14's sparse loop. Pre-converting every dense child to an output-sized vector is potentially wasteful and can be wrong when child offsets are sparse, repeated, or non-monotonic.

## Discriminating regression matrix

### Positive

1. identity codes with compact children;
2. non-sequential codes such as `+ud:5,7,9`;
3. reordered in-range codes such as `+ud:2,1,0`, checking member name/tag and value;
4. repeated references to the same compact child value;
5. interleaved child selection with independently growing child offsets;
6. sliced dense union with nonzero `ArrowArray.offset`;
7. multiple DuckDB scan chunks with nonzero `chunk_offset`;
8. dense union nested under struct, list, and fixed-size list parents;
9. dictionary/view/extension child;
10. direct ingestion of the ADBC GetInfo and Statistics result shapes already produced by DuckDB.

### Malformed

1. wrong buffer count or missing offsets buffer;
2. schema type-code count mismatch;
3. duplicate, negative, or out-of-range schema code;
4. runtime type code absent from mapping;
5. negative dense child offset;
6. dense child offset equal to or beyond selected child length;
7. array/schema child-count mismatch;
8. null child pointer;
9. offset arithmetic overflow or impossible sliced extent.

## Promotion boundary

Keep this separate from:

- sparse unit 14 delivery;
- dense-union export settings;
- ADBC result-construction refactors;
- broad Arrow validation issue `#21849`;
- nanoarrow bundle policy.

A good first milestone is ingestion-only support that can round-trip DuckDB's already-merged ADBC dense-union results through `arrow_scan` and an external reference consumer.

## Source links

- current sparse-only parser: `duckdb/duckdb@daa81697e31a3dc97a93f11220037cd2213af6cd`
- closed broad prior art: `duckdb/duckdb#21898`
- merged ADBC Statistics producer: `duckdb/duckdb#23230`
- merged ADBC GetInfo producer: `duckdb/duckdb#24196`
- Apache Arrow C++ union implementation: `apache/arrow` `cpp/src/arrow/array/array_nested.cc`
