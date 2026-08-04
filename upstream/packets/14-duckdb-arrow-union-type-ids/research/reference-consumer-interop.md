# Research lane — Arrow reference-producer/reference-consumer interoperability

Date: 2026-08-05

## Status

`INFRASTRUCTURE CANDIDATE — cross-implementation validation gap`

This note records a testing opportunity. It does not claim a product defect by itself and does not authorize public upstream contact.

## Why DuckDB-only round trips are insufficient

An Arrow producer and consumer implemented by the same codebase can agree on the same wrong interpretation. Several recent examples demonstrate this:

- unit 14: DuckDB's own Arrow exporter emits identity union type codes, so DuckDB-to-DuckDB round trips cannot expose ignored nonidentity schema mappings;
- nested extension bug `duckdb/duckdb#22444`: the schema declared `arrow.bool8` byte-packed storage while nested BOOLEAN buffers were bit-packed. A DuckDB-internal path could be self-consistent enough to miss the mismatch, while PyArrow exposed corrupted values;
- Arrow output-version buffer tests in core validate declared format versus buffer count and then perform a DuckDB self-roundtrip, but comments explicitly cite an external importer such as PyArrow as the real compatibility boundary;
- merged ADBC dense-union producers `#23230` and `#24196` use external Arrow consumers because `arrow_scan` cannot consume the dense arrays DuckDB creates.

## Existing useful pieces

### DuckDB core

`test/arrow/arrow_output_version_buffers.cpp` already provides reusable ideas:

- export an Arrow schema and array directly;
- recursively compare schema and runtime child counts;
- check fixed buffer counts implied by format strings;
- release schema/array trees explicitly;
- pair structural checks with data comparison.

Its limitation is that the data comparison is still DuckDB consuming DuckDB output.

### duckdb-python

The Python repository has genuine PyArrow validation for some formats. For example, string-view tests:

- call `pyarrow.Array.validate(full=True)`;
- compare values against manually constructed PyArrow arrays;
- ingest a PyArrow-produced table back into DuckDB;
- skip cleanly when the installed PyArrow lacks the required feature.

The discussion around closed `#22445` notes that duckdb-python can point its DuckDB submodule at a fork/branch for cross-repository testing, though maintainers also suggested a lighter core reference implementation such as `arro3` might be preferable.

## Proposed testing architecture

A useful lane would test both directions.

### DuckDB producer → reference consumer

1. produce schema/array through DuckDB's Arrow APIs;
2. hand the C Data objects to PyArrow, arro3, Arrow C++, or another independent implementation;
3. run full validation where available;
4. inspect logical type, field names, extension metadata, buffers, offsets, nulls, and values;
5. ensure the reference consumer owns/releases the imported objects correctly.

### Reference producer → DuckDB consumer

1. construct valid but noncanonical arrays in the reference implementation;
2. export through the Arrow C Data Interface;
3. consume through DuckDB `arrow_scan`;
4. compare member names/tags, values, nulls, and ordering;
5. include sliced, chunked, dictionary, view, extension, and nonidentity mapping cases.

## Candidate matrix

Prioritize layouts where self-roundtrips are weakest:

1. sparse union with nonidentity/reordered type codes;
2. dense union with compact children and repeated/nonmonotonic child offsets;
3. ListView with disjoint, overlapping, and out-of-order ranges;
4. nested extension types such as `arrow.bool8` under struct/list/map/union/array;
5. string/binary views with multiple variadic data buffers;
6. dictionary arrays with sliced dictionaries and nested offsets;
7. run-end encoded arrays with 16/32/64-bit run-end types;
8. arrays whose top-level and nested offsets are both nonzero;
9. extension metadata round trips, including unknown-extension fallback;
10. release/ownership behavior after bind errors and partial consumption.

## Placement options

### Option A — duckdb-python/PyArrow lane

Advantages:

- mature PyArrow validator and type coverage;
- easy value-level assertions;
- already has relevant Arrow tests.

Costs:

- cross-repository source pinning;
- Python/package-version matrix;
- slower and less suitable for every core PR.

### Option B — small core `arro3` or Arrow C++ oracle

Advantages:

- closer to core changes;
- can be a focused scheduled or opt-in job;
- independent parser/validator catches schema/layout drift.

Costs:

- new dependency/toolchain policy;
- C Data ownership bridge work;
- version pinning and platform maintenance.

### Option C — nanoarrow validation helpers

Advantages:

- C-oriented and close to C Data structures;
- potentially lightweight.

Costs:

- DuckDB intentionally carries a minimal nanoarrow subset;
- expanding the bundle is already an open architectural policy question in ADBC discussions;
- using the same bundled subset can reduce independence.

## Recommended first contribution

Start with a scheduled or explicit interop job rather than a mandatory full matrix on every PR:

1. build DuckDB or duckdb-python against one exact core commit;
2. run a small curated set of high-risk layouts;
3. require reference validation and bidirectional value checks;
4. retain generated schema descriptions and failure fixtures as artifacts;
5. promote stable fast cases into ordinary core tests over time.

The smallest discriminating pilot is unit 14's nonidentity sparse-union fixture plus one nested `arrow.bool8` case. Those two prove the lane catches bugs DuckDB's canonical self-output can hide.

## Ownership requirements

Interop tests should explicitly verify:

- import transfers or shares ownership exactly as documented;
- release callbacks are invoked once;
- exceptions do not leak partially imported streams or arrays;
- test helpers do not copy owning C structs in ways that permit double release;
- repeated scans are attempted only when the producer factory promises repeatability.

## Source links

- unit 14 clean source: `teamleaderleo/duckdb@05eb977f3001be4797379df9a0a978a144ca86a0`
- nested extension issue/repair: `duckdb/duckdb#22444`, closed `#22445`, merged `#23190`
- core buffer tests: `test/arrow/arrow_output_version_buffers.cpp`
- Python string-view reference tests: `duckdb/duckdb-python/tests/fast/arrow/test_arrow_string_view.py`
- ADBC dense-union producers: `duckdb/duckdb#23230`, `#24196`
