# DuckDB encoded Arrow layout invariants

Date: 2026-08-05

## Status

Research only. No public write or source claim is authorized by this note.

Source observations were pinned to public DuckDB source `043e1894425b49984c5010f253589e5d9c5fdde4`.

## Core finding

Dictionary encoding, run-end encoding, lists, ListView, fixed-size arrays, maps, and unions all translate a logical row coordinate into another physical coordinate system. DuckDB supports many of these layouts, but structural checks, offset arithmetic, and content validation are uneven.

The right design is not to put full O(n) validation in every hot scan by default. It is to distinguish:

- **structural validation** — O(1) or proportional to child count;
- **range validation** — O(number of accessed spans/runs), often necessary for safe access;
- **full semantic validation** — O(n), suitable for a strict mode, test oracle, or import boundary where trust is low.

This resembles Arrow implementations that separate `Validate` from `ValidateFull`.

## Shared structural invariants

Before conversion, every nested/encoded type should be able to assert:

- required buffer count;
- required non-null buffer pointers;
- schema child count;
- array child count;
- non-null child-pointer arrays;
- schema/array child-count agreement;
- child count agreement with retained DuckDB Arrow type information;
- nonnegative array length, offset, and null count where required;
- checked `offset + length` arithmetic;
- checked multiplication for fixed-size children;
- dictionary pointer agreement between schema and array;
- no unexpected validity buffer for layouts that prohibit one.

## Raw buffer helper risk

Current `ArrowBufferData<T>` directly indexes `array.buffers[buffer_idx]` and casts the pointer. This is appropriate only after a type-specific validator has established buffer count and pointer validity.

A useful refactor would make the unsafe nature explicit:

- `UnsafeArrowBufferData<T>` for already-validated paths;
- `GetArrowBuffer<T>(array, index, type_name)` returning a checked pointer or controlled error;
- one structural validation call per array/type before hot loops.

## Validity bitmap boundary

For a misaligned validity offset, current code copies one extra byte before shifting the bitmap. Tests sometimes pad the fixture explicitly to keep this read in bounds.

A producer-valid array may have exactly enough bitmap bytes for `offset + length`, but an implementation that reads one byte beyond the final logical bit needs to prove that byte exists. Safer approaches:

- copy only available bytes and zero the synthetic final byte;
- handle the final partial byte separately;
- compute required bitmap bytes from `offset + size` and validate them when buffer sizes are known;
- avoid assuming producer padding.

The raw C Data ABI does not include buffer sizes, so the no-overread implementation is preferable.

## Dictionary encoding

Required checks:

- index physical type is supported;
- dictionary array/schema pointers are present and released correctly;
- each non-null index is within dictionary length;
- negative signed indexes are rejected unless a documented sentinel convention applies;
- the null-index sentinel, if synthesized internally, cannot collide with a valid dictionary position;
- parent/list/array offsets are applied to the index array exactly once;
- dictionary values use their own offset and validity coordinates;
- zero-row paths do not assert that a dictionary is absent merely because no values are accessed.

Existing nested dictionary tests are valuable because they mark exact physical child slots and cross vector-size boundaries. The lingering source comment about offset support indicates this area deserves a complete invariant review rather than assuming all nested cases are solved.

Discriminating cases:

1. signed negative index;
2. index equal to dictionary length;
3. maximum supported unsigned index;
4. nullable index array with nonzero offset;
5. dictionary values with their own nonzero offset;
6. dictionary child under LIST with leading unused slots;
7. dictionary child under fixed-size ARRAY with parent offset;
8. dictionary child under sparse union;
9. dictionary of nested values;
10. empty logical range with a dictionary present.

## Run-end encoding

Required schema invariants:

- exactly two children: `run_ends` and `values`;
- run-end type is supported signed integer width;
- run-end and value child pointers exist;
- value count is compatible with run count.

Required content invariants:

- run ends are non-null;
- run ends are strictly increasing;
- first run end is positive for a nonempty logical array;
- final run end covers the requested logical end;
- no run end exceeds the representable logical coordinate;
- sliced/chunked scans locate the first covering run correctly;
- parent and nested offsets are not applied to both logical run coordinates and compact value positions;
- the run-end iterator uses the correct physical width.

The historical INT64 template bug demonstrates that a width mismatch can silently corrupt all subsequent boundaries. Tests should use values whose upper and lower 32-bit halves differ, not small run ends that accidentally survive a 32-bit read.

Discriminating cases:

1. INT16, INT32, and INT64 run ends;
2. duplicate run ends;
3. descending run end;
4. zero or negative first run end;
5. final run end shorter than logical length;
6. extra runs beyond logical length;
7. sliced array beginning inside a run;
8. chunk boundary beginning inside a run;
9. nested REE child with parent/list offset;
10. null run-end entry;
11. value count less than run count;
12. large INT64 boundaries with nonzero high bits.

## Sequential LIST and MAP offsets

For regular list/map arrays:

- offsets must be monotonic nondecreasing;
- subtraction must not underflow;
- first and final referenced offsets must be within child length;
- `offset + size` arithmetic must be checked;
- list size accumulation must not overflow;
- null parent rows still need safe offsets according to Arrow rules;
- map entry child must be a two-field struct;
- map key field and entries struct must have required non-nullability semantics;
- key/value child lengths must match;
- DuckDB's stricter no-null-key/no-duplicate-key rules should raise controlled input errors.

Unsigned offset reads avoid negative values but can turn malformed signed producer bytes into very large positive positions. Range checks remain required.

## ListView

ListView ranges may be disjoint, overlapping, or out of order. The physical child span is:

```text
[min(offset_i), max(offset_i + size_i))
```

for nonempty valid entries, not the sum of row sizes.

Open upstream PR `#24483` already owns the immediate child-span fix and should not be duplicated. Remaining validation questions include:

- checked `offset + size` overflow;
- range within child length;
- negative values for signed offset buffers;
- null entries and whether their offsets/sizes are ignored safely;
- very large sparse spans and allocation pressure;
- overlapping ranges with child dictionaries or extensions;
- sliced ListView parent plus disjoint ranges.

## Fixed-size arrays

The key physical calculation is generally:

```text
child_start = effective_parent_offset * array_size
child_count = logical_row_count * array_size
```

Both multiplication and addition need checked arithmetic. Required checks:

- one child in schema and array;
- positive fixed size according to supported DuckDB rules;
- child length covers `child_start + child_count`;
- parent validity broadcast cannot write past child vector capacity;
- dictionary/REE/default children receive the same child coordinate;
- nested fixed-size arrays multiply dimensions without overflow.

## Sparse and dense unions

Sparse-union invariants are covered in unit 14: logical type-code mapping, child count, type-code range, offset propagation, and malformed runtime IDs.

Dense union adds:

- exactly three buffers under the C Data layout;
- signed `int8` type codes;
- signed `int32` value offsets;
- mapping from type code to child;
- each value offset nonnegative and within the selected compact child;
- compact child coordinates independent of parent row coordinates;
- slices/chunks apply to type-code and value-offset buffers, not child positions;
- no validity bitmap at the union level.

This reinforces treating dense ingestion as a separate unit.

## Proposed validation architecture

### Phase 1 — structural validators

One function per physical layout, called before conversion:

- `ValidateArrowListStructure`;
- `ValidateArrowDictionaryStructure`;
- `ValidateArrowRunEndStructure`;
- `ValidateArrowUnionStructure`;
- etc.

These verify counts, pointers, and static relationships.

### Phase 2 — safe range calculations

Use checked helpers returning explicit spans:

```text
ArrowSpan { start, length }
CheckedListSpan(...)
CheckedFixedArraySpan(...)
CheckedDenseUnionPosition(...)
```

Conversion consumes spans rather than recomputing arithmetic ad hoc.

### Phase 3 — optional full validation

A test/debug/import option validates every index, run, offset, or union position. This could be exposed only in test utilities initially.

## Test-oracle strategy

For every valid noncanonical fixture:

- validate with Apache Arrow C++ or PyArrow `validate(full=True)` where possible;
- scan with DuckDB;
- assert exact values/nulls;
- assert exact physical slot markers;
- repeat with chunk boundaries and slices.

For malformed fixtures:

- require DuckDB controlled failure;
- do not require the external reference implementation to construct the invalid array through high-level APIs; use raw C Data structs;
- count releases on all failure paths.

## Suggested future units

1. validity bitmap no-overread;
2. regular LIST/MAP offset range validation;
3. REE structural and monotonic validation;
4. dictionary index range and sentinel semantics;
5. fixed-size array checked span arithmetic;
6. dense-union ingestion and position validation;
7. optional full-validation test utility.

## Links

- https://github.com/duckdb/duckdb/issues/21849
- https://github.com/duckdb/duckdb/pull/21847
- https://github.com/duckdb/duckdb/pull/9836
- https://github.com/duckdb/duckdb/pull/24483
- https://github.com/apache/arrow/pull/7248
