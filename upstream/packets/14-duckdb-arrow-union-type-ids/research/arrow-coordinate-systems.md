# Research lane — Arrow logical versus physical coordinate systems

Date: 2026-08-05

## Status

`CROSS-CUTTING AUDIT IDEA — recurring correctness pattern`

This note is a taxonomy, not a claim that every Arrow path is currently wrong. It identifies where future reviews should make coordinate systems explicit and use discriminating external C Data fixtures.

## Core observation

Many Arrow bugs are not ordinary off-by-one errors. They arise because one integer called “offset,” “size,” or “index” belongs to a different coordinate system than the code using it.

Relevant coordinate systems include:

1. logical output row index inside the current DuckDB vector;
2. scan `chunk_offset` within an Arrow batch;
3. `ArrowArray.offset` of a sliced parent;
4. inherited parent offset through struct nesting;
5. list/array child start offset;
6. fixed-size-list child offset multiplied by array width;
7. dictionary index position versus dictionary value position;
8. run-end position versus decoded logical row;
9. sparse-union logical row position versus same-row position in every child;
10. dense-union logical row position versus selected compact-child value offset;
11. ListView logical entry versus minimum/maximum referenced physical child span.

A formula can be locally plausible while combining two incompatible systems.

## Confirmed examples

### Sparse-union type-code buffer

Merged work before unit 14 fixed the union type-code buffer ignoring effective array/chunk offsets. Unit 14 then found that reading the correct logical type code was not enough: sparse child conversion also needed the union's offset. Otherwise the tag came from one physical row and the child value from another.

The nested fixed-size-list control further proved that inherited `nested_offset` and ordinary `parent_offset` cannot simply be added the same way in every traversal path. The expected-negative characterization captured the exact double-application signature.

### ListView child span

Open `duckdb/duckdb#24483` fixes code that summed logical list lengths and treated that sum as the physical child scan length. Disjoint, out-of-order, or overlapping ranges require the full minimum-to-maximum referenced span instead. Logical cardinality is not physical extent.

### Dictionary children under nested offsets

Current `arrow_dict_nested_offset.cpp` contains targeted cases for:

- leading list child gaps;
- later scan chunks where `chunk_offset` differs from the child start;
- multiple child elements per logical row;
- dictionary children under struct/list/fixed-size array nesting;
- validity positions that discriminate the exact physical slot read.

These tests are valuable because values alone can repeat. Strategic null placement exposes which physical slot was actually selected.

### Run-end encoding

Historical `duckdb/duckdb#21847` fixed an INT64 run-end buffer being read with an INT32 template. The wrong physical element width changed both value interpretation and stride. This is another coordinate failure: byte position and logical run position diverged after the first entry.

## Review checklist

For every nested/encoded Arrow conversion, document:

- what coordinate each input offset uses;
- whether it is absolute or relative;
- whether slicing has already been applied to a pointer;
- whether `chunk_offset` is a row count, child-element count, or byte count;
- whether a child is sparse/logically aligned or compact/independently indexed;
- whether a nested offset supersedes or composes with a parent offset;
- whether multiplication can overflow;
- whether the same value pattern could hide an incorrect physical read.

Avoid variable names such as `offset` when a more precise name is available:

- `union_row_offset`;
- `selected_child_offset`;
- `list_child_start`;
- `physical_child_span`;
- `dictionary_index_position`;
- `decoded_row_index`.

## Discriminating fixture design

A strong offset fixture should contain:

1. an ignored physical prefix with values that would be obviously wrong if read;
2. nonrepeating child values tied to physical position;
3. strategically placed nulls in only the wrong/right slots;
4. at least one chunk boundary;
5. a nested parent whose offset differs from the child's own offset;
6. reordered or overlapping logical references where the format permits them;
7. tag/member-name assertions as well as value assertions;
8. an expected-negative pre-fix run when possible.

Controls should include a canonical zero-offset case, because a bug often passes when all coordinate systems happen to start at zero.

## Candidate audit order

1. dense-union ingestion, because it introduces a compact-child coordinate system;
2. ListView after `#24483`, especially nested/dictionary/view children;
3. run-end encoded values nested under sliced parents;
4. dictionary/view children under list/array/map and multi-chunk scans;
5. extension types whose storage conversion changes element width or vector layout;
6. validity-mask realignment at non-byte-aligned offsets.

## Testing heuristic

Whenever a test description says only “nonzero offset,” ask which offset. A meaningful test name should state the coordinate boundary, for example:

- “union offset propagated to sparse children”;
- “fixed-size-list parent offset converted to child element offset”;
- “ListView disjoint ranges scan full physical child span”;
- “dictionary validity uses list child start, not scan row offset.”

## Source links

- unit 14 repair and characterization: `teamleaderleo/duckdb#16`, closed `#27`, clean source `05eb977f3001be4797379df9a0a978a144ca86a0`
- active ListView span repair: `duckdb/duckdb#24483`
- dictionary offset tests: `test/arrow/arrow_dict_nested_offset.cpp`
- run-end width repair: `duckdb/duckdb#21847`
