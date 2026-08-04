# Research lane — Arrow C Data validation hardening

Date: 2026-08-05

## Status

`OPEN HARDENING PROGRAM — split into small malformed-input units`

This is a read-only audit against DuckDB public main `daa81697e31a3dc97a93f11220037cd2213af6cd`. It does not claim that every inspected path is exploitable, and it does not authorize public contact. Each candidate requires a source-native malformed C Data regression before implementation.

Public umbrella issue `duckdb/duckdb#21849` remains open with no comments or implementation found. It identifies the broad problem: Arrow C Data input is often treated as trusted, while buffer, child, metadata, and structural invariants may be guarded only by assertions or not checked locally.

## Inspection findings

### 1. Nested schema child pointers are often dereferenced before shape validation

In `ArrowType::GetTypeFromFormat`:

- `+l`, `+L`, `+vl`, and `+vL` immediately dereference `schema.children[0]`;
- fixed-size list `+w:NN` parses the width and then immediately dereferences `schema.children[0]`;
- map `+m` immediately dereferences the outer child, then relies on `D_ASSERT` for the required two-child entry struct before dereferencing both children;
- run-end encoded `+r` relies on `D_ASSERT` for exactly two named children before dereferencing them;
- struct iterates `schema.n_children` and assumes `schema.children` and every entry are non-null.

Candidate controlled errors should distinguish:

- negative child count;
- nonzero child count with null `children` pointer;
- null individual child pointer;
- wrong child count for fixed-arity formats;
- released child schema.

### 2. Parameterized format parsing is inconsistent

Fixed-size list checks the colon position, then calls `std::stoi` on the remaining string without verifying full-token consumption. Candidate cases include:

- trailing junk (`+w:3x`);
- leading/trailing whitespace;
- empty parameter;
- zero width if disallowed by DuckDB's ARRAY contract;
- negative width;
- integer overflow.

The public sparse-union parser indexes `format[0]`, `[1]`, `[2]`, and `[3]`; the colon is a `D_ASSERT`, not a release-build validation boundary. Unit 14's candidate already demonstrates the preferred pattern for that format family: length check, delimiter check, full-token parse, range/count/duplicate checks, and controlled errors.

Other parameterized Arrow formats should be audited for the same full-token contract rather than fixed one by one with ad hoc parsing.

### 3. Schema and runtime array shape can diverge

Arrow type information is built from the schema, but runtime conversion often iterates or indexes using `ArrowArray.n_children` and raw child pointers. Candidate invariants include:

- array child count equals schema-derived/type-info child count;
- `children` pointer is present when count is nonzero;
- each runtime child pointer is non-null;
- fixed-arity nested layouts preserve their expected child structure;
- dictionary schema presence agrees with array dictionary presence;
- child array physical lengths cover the parent logical extent for sparse layouts.

Unit 14's executed repair adds union array/schema child-count and child-pointer validation. That should be treated as a pattern, not silently broadened to every nested type in one patch.

### 4. Buffer count and null-pointer validation should precede typed access

Current conversion code frequently selects a buffer index from mode and calls typed access helpers. A future audit should build a per-format contract:

- expected minimum/exact `n_buffers`;
- which buffer positions may legally be null;
- required byte extent for `offset + length` or `chunk_offset + size`;
- multiplication/addition overflow checks for fixed-width buffers;
- separate requirements for view/variadic-buffer formats.

High-value first targets are formats with multiple coordinate systems or several buffers:

- dense unions;
- ListView/LargeListView;
- run-end encoded arrays;
- string/binary views;
- dictionary arrays.

### 5. Release-build structural checks deserve explicit classification

`D_ASSERT` is useful for internal impossibilities but should not be the only boundary for producer-controlled C Data structures. The audit should classify each assertion as:

1. internal invariant established by a prior checked conversion;
2. external Arrow producer invariant that needs a controlled error;
3. performance-only assertion that can remain debug-only.

Changing assertions blindly can hide internal bugs or impose unnecessary per-row checks. The validation should be concentrated at schema bind and batch acquisition boundaries wherever possible.

## Proposed reviewable slices

### Slice A — schema child structure

Formats: list, large list, ListView, fixed-size list, map, struct, run-end encoded.

Tests: null children pointer, null child entry, wrong child count, released child schema.

### Slice B — parameterized format strings

Formats: fixed-size list and every colon/comma parameterized format.

Tests: empty, truncated, wrong delimiter, trailing junk, overflow, negative/zero where invalid.

### Slice C — array/schema child agreement

Formats: struct, map, list/array, run-end encoded, union.

Tests: mismatched counts and pointers at runtime after a valid schema bind.

### Slice D — buffer structure

Start with one format family. Validate count, pointer, and extent before typed access. Avoid a cross-format mega-PR.

### Slice E — metadata lengths and overflow

Audit Arrow schema metadata parsing separately. Negative or oversized encoded lengths should fail before conversion to unsigned allocation/index sizes.

## Test-harness requirements

Every malformed fixture should:

- construct a minimal external Arrow C schema/array directly;
- prove the failure occurs at the intended bind or execution phase;
- assert a stable error category and focused substring;
- use ownership-safe release callbacks on success and exception paths;
- run under LeakSanitizer/ASAN when practical;
- retain a valid neighboring control to ensure the format remains supported.

## Priority recommendation

1. Finish unit 14 delivery and current-main restack.
2. Take schema child-structure validation first: it is localized, cheap to test, and removes several null-dereference/undefined-structure paths.
3. Follow with parameterized-format full-token parsing.
4. Treat buffer extents and metadata arithmetic as separate higher-risk reviews.

## Source links

- validation umbrella: `duckdb/duckdb#21849`
- current parser: `src/function/table/arrow/arrow_duck_schema.cpp` at `daa81697e31a3dc97a93f11220037cd2213af6cd`
- current converter: `src/function/table/arrow_conversion.cpp` at the same head
- unit 14 executed validation pattern: `teamleaderleo/duckdb#16` and clean source `05eb977f3001be4797379df9a0a978a144ca86a0`
