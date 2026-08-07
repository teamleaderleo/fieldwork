# C API Arrow multi-column ownership characterization — 2026-08-08

## Status

`EXECUTION STARTED — private expected-negative characterization wired on exact public source; CI pending`

This note follows the source audit in [`arrow-capi-zero-copy-ownership.md`](arrow-capi-zero-copy-ownership.md). It does not expand unit 14's source scope and does not authorize public upstream contact.

## Exact current source

The characterization was refreshed from the earlier `58c019320e250a7b369efd756f84c6dfd68bedcb` observation to public DuckDB main:

- source: `duckdb/duckdb@e500d77864fe565f90e68f06d729c25b11e775c5`;
- public commit date: 2026-08-07;
- private fork base mirror: `fieldwork/capi-arrow-multicolumn-ownership-base` moved to the same source;
- private execution base: `fieldwork/capi-arrow-multicolumn-ownership-exec-base@d9904223a885461cf47fbf59f63ef9e3b83a45ff`;
- private characterization PR: `teamleaderleo/duckdb#34`;
- characterization head: `27a01551acd3b5f2e330f7ab6ce4cc631d3017bc`.

The execution-base workflow is private and exists only to run the characterization. No public DuckDB branch, issue, PR, comment, reaction, or review was modified.

## Source signal retained on current main

`duckdb_data_chunk_from_arrow` still performs root ownership transfer inside the per-column loop:

1. it creates a fresh `ArrowArrayScanState` for each output column;
2. it creates a fresh `ArrowArrayWrapper` and copies the root `ArrowArray` into that state;
3. it sets the caller root's `release` pointer to null;
4. it converts that one column;
5. the loop then advances to the next column.

At the same source revision, primitive direct conversion is zero-copy: `DirectConversion` points the DuckDB vector buffer at the Arrow value buffer with `FlatVector::SetData` rather than copying the values.

That combination creates a concrete ownership-timing question: the first per-column state may be destroyed before the next column is converted and before the returned `DataChunk` is destroyed.

## Discriminating fixture

The private characterization adds exactly:

- `test/api/capi/test_capi_arrow_ownership.cpp`;
- one registration line in `test/api/capi/CMakeLists.txt`.

The test constructs a two-column root Arrow array with a recursive root release counter, then calls:

- `duckdb_schema_from_arrow`;
- `duckdb_data_chunk_from_arrow`.

The oracle does not depend on allocator reuse, crashes, ASAN, or freed-memory contents. It checks ownership timing directly:

1. caller root `release` becomes null because ownership is transferred;
2. producer root release count must still be zero while the returned DuckDB chunk is alive;
3. both zero-copy integer columns remain readable as `11` and `22`;
4. `duckdb_destroy_data_chunk` must then make the root release count exactly one.

Current expected-negative signature if the source signal is real:

```text
probe.root_array_releases == 0
```

A failure at that assertion would demonstrate early producer release while a supposedly ownership-retaining DuckDB chunk is alive. A pass would disprove this candidate and the lane should be closed without repair.

## Private execution carrier

`teamleaderleo/duckdb#34` is draft, private, and characterization-only. Its body explicitly forbids merge or public contact.

The execution workflow:

- checks out the exact characterization head;
- verifies the characterization remains based on `e500d77864fe565f90e68f06d729c25b11e775c5`;
- builds the Debug test runner;
- runs only `C API Arrow chunk retains multi-column root ownership`;
- retains build and characterization logs.

At the time of this note, the repository's ordinary `Main` run for the characterization head is pending. The focused private workflow has been added to the execution base and characterization head; no result is claimed here until GitHub reports it.

## Decision rule

- If the focused test passes: mark the candidate disproved, close the private characterization PR without merge, and preserve the passing receipt.
- If the focused test fails at the release-count oracle after a successful build: classify as a confirmed C API ownership defect and prepare a separate repair unit; do not fold the fix into unit 14.
- If compilation or harness setup fails first: repair only the characterization harness, without changing production source.

## Authority

- public DuckDB contact: not authorized;
- public DuckDB writes: none;
- production source changes in characterization: none;
- merge authorization: none.
