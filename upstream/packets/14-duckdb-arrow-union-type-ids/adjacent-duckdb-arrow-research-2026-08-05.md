# Adjacent DuckDB Arrow research — 2026-08-05

## Scope and authority

This is read-only follow-on research made while unit 14 context was fresh. It does not expand unit 14's implementation scope, claim another unit, or authorize public upstream contact. No public issue, pull request, review, comment, reaction, or branch was modified.

Public DuckDB main observed at `daa81697e31a3dc97a93f11220037cd2213af6cd`.

## 1. Dense-union ingestion is a real, separate capability gap

Current main still accepts only sparse Arrow unions. In `src/function/table/arrow/arrow_duck_schema.cpp`, `+u` formats whose third character is not `s` raise `NotImplementedException`; `+ud:` is therefore not consumable by `arrow_scan`.

This is now more than a hypothetical feature request:

- merged `duckdb/duckdb#23230` implements ADBC Statistics and must manually construct a dense-union `statistic_value` because DuckDB Arrow export cannot produce the required layout;
- merged `duckdb/duckdb#24196` similarly constructs the ADBC `ConnectionGetInfo` dense-union result manually;
- both PRs explicitly state that their C++ tests cannot feed the result through `arrow_scan`, so they inspect buffers directly and use an external Arrow consumer for end-to-end validation.

No open issue or open PR specifically implementing dense-union ingestion was found in the refresh.

### Why this should not be folded into unit 14

Dense unions add a second per-row offsets buffer and compact child arrays. Correct ingestion needs a coordinate model distinct from sparse unions:

- map logical type code to child index;
- read the dense value offset for the row;
- index only the selected compact child at that offset;
- preserve chunk, parent, array, and nested offsets without double application;
- validate buffer count, offset width/range, child count, and mapped child bounds.

This is substantial enough for a separate future unit. Unit 14's `ArrowUnionInfo` design could be reused, but the conversion and regression matrix should remain independent.

## 2. Arrow C Data validation remains an open hardening program

Public issue `duckdb/duckdb#21849` is still open and has no comments or linked implementation found. It calls out broad trust of producer-supplied Arrow structures, including unchecked child dereferences, buffer assumptions, metadata lengths, and structural invariants guarded only by `D_ASSERT`.

Current main still contains nearby examples:

- list and ListView schema branches dereference `schema.children[0]` without first validating `n_children` and the child pointer;
- union format parsing indexes `format[0]`, `format[1]`, `format[2]`, and `format[3]`, with the colon invariant checked only by `D_ASSERT`;
- map schema conversion uses `D_ASSERT` for the two-child entry structure before dereferencing it;
- union conversion relies on array child counts and pointers matching the logical member/type-info counts.

Unit 14 already demonstrates a useful small-slice pattern: validate one format family completely, keep errors controlled, and retain native malformed C Data fixtures. A future validation program should be split into reviewable pieces rather than one large defensive rewrite.

Candidate slices, in likely order:

1. schema child-count/null-pointer validation for list, ListView, fixed-size list, map, struct, and run-end encoded formats;
2. format-string length/delimiter/full-token validation for every parameterized format;
3. array buffer-count/null-pointer validation before typed buffer access;
4. cross-check schema and array child counts against retained type information;
5. metadata length and overflow validation.

These are research candidates only. Each requires a discriminating malformed-input regression before implementation.

## 3. Reference-consumer testing is a recurring infrastructure gap

The Arrow nested-extension bug in `duckdb/duckdb#22444` exposed a schema/data-layout mismatch: nested BOOLEAN values were bit-packed while the schema declared `arrow.bool8` byte-packed storage. The first proposed fix, `duckdb/duckdb#22445`, was closed in favor of merged `duckdb/duckdb#23190`, which fixed extension propagation and selection-vector handling.

The discussion explicitly notes that testing against a reference implementation is cumbersome. Suggested paths included duckdb-python/PyArrow and a core test against another implementation such as `arro3`. No dedicated `arro3` or equivalent reference-consumer test path was found in the core repository refresh.

This matters because DuckDB-to-DuckDB round trips can be self-consistent while still violating Arrow layout semantics. Unit 14 has the same testing lesson: canonical DuckDB output uses identity union IDs, so only a manually constructed external Arrow schema/array reveals the mapping bug.

A useful future infrastructure contribution would provide a small interop gate for representative C Data layouts:

- DuckDB-produced schema/array validated and consumed by a reference implementation;
- reference-produced noncanonical but valid arrays consumed by DuckDB;
- explicit ownership/release checks on both success and expected-error paths;
- focused coverage for union, ListView, nested extensions, dictionary, run-end encoded, and sliced/chunked arrays.

This is probably more valuable than adding many DuckDB-only round trips.

## 4. Active upstream work confirms the offset/span pattern

Open `duckdb/duckdb#24483` fixes Arrow ListView child scanning for disjoint, out-of-order, and overlapping ranges. The old code summed row lengths, which was only correct for tightly packed ranges; the repair scans the full minimum-to-maximum referenced child span and rebases entries.

This is already owned upstream and should not be duplicated. It is useful pattern evidence:

- logical row ranges do not necessarily form one canonical physical block;
- tests must construct valid noncanonical external arrays;
- values, offsets, and child span must be asserted together;
- summing logical lengths is not equivalent to determining the physical span.

That same distinction between logical coordinates and physical storage coordinates is central to unit 14.

## 5. Current-main unit 14 relevance remains confirmed

At `daa81697e31a3dc97a93f11220037cd2213af6cd`, current main still:

- discards the sparse-union type-code list after parsing;
- stores union children as `ArrowStructInfo`;
- uses the runtime type-ID byte as the direct child/tag index;
- passes only the inherited parent offset into sparse-union child conversion rather than including the union array's own offset.

Therefore the unit 14 mapping and child-offset repair has not been superseded by the adjacent merged Arrow work.

## Suggested future routing

1. Finish unit 14 exact-head CI, artifact inspection, and clean nine-file publication first.
2. Consider a separate high-priority unit for dense-union ingestion, using the merged ADBC dense-union producers as real interoperability fixtures.
3. Consider a series of small Arrow C Data validation units under public issue `#21849`.
4. Consider a testing-infrastructure unit for reference-producer/reference-consumer C Data interoperability.
5. Do not duplicate open ListView PR `#24483` or merged nested-extension PR `#23190`.

## Links

- unit 14 public defect: https://github.com/duckdb/duckdb/issues/21842
- Arrow validation umbrella: https://github.com/duckdb/duckdb/issues/21849
- closed focused mapping PR: https://github.com/duckdb/duckdb/pull/21843
- closed broad dense-union PR: https://github.com/duckdb/duckdb/pull/21898
- merged ADBC Statistics dense-union producer: https://github.com/duckdb/duckdb/pull/23230
- merged ADBC GetInfo dense-union producer: https://github.com/duckdb/duckdb/pull/24196
- merged nested-extension repair: https://github.com/duckdb/duckdb/pull/23190
- active ListView child-span repair: https://github.com/duckdb/duckdb/pull/24483
