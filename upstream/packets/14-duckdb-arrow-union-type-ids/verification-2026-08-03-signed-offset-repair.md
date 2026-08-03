# Unit 14 signed-ID and offset-fixture repair — 2026-08-03

This receipt supersedes current-state fields in `verification-2026-08-01-repair.md` while preserving that file as historical evidence.

## Disposition

**REPAIR — exact-head native CI queued**

No public DuckDB issue, pull request, review, comment, or branch was modified. All work remains in `teamleaderleo` repositories.

## Exact identity

- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- characterization: `work/duckdb-arrow-union-type-id-characterization@ed05ac593498fb4f95546ec591824ee23429088d`
- passing parent candidate: `work/duckdb-arrow-union-type-id-candidate@c962ece64c1356015aef15a37c0cc636f63b376b`
- private repair PR: `teamleaderleo/duckdb#16`
- current repair carrier: `repair/262-arrow-union-malformed-map-controls@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`
- signed-ID repair head examined: `bfb8434e380eb69765e8c154e57e6d092e43dd57`
- superseded invalid fixture head: `c3513da03af17f6d1ab1166178a03f2d46e47230`
- exact-head focused run: `30845351615`, job `91792186958`, queued
- exact-head ordinary Main run: `30845355047`, queued
- stale characterization run: `30845352934`, queued and expected red if executed
- clean publication branch: `fix/arrow-union-type-id-mapping@2c9e51aa33dd07e928edae66304430aeb038edd7`, still identical to target base

## New private work examined

The branch had advanced beyond the older `c8552f49b0ae1896a40296973725aae297a7671a` packet state.

Commit `bfb8434e380eb69765e8c154e57e6d092e43dd57` correctly repaired the parent candidate's unsigned-ID assumption:

- Arrow union IDs are treated as signed 8-bit values in `[-128, 127]`;
- the lookup contains 256 entries;
- each `int8_t` value is indexed by its unsigned-byte representation;
- duplicate signed schema IDs remain rejected;
- schema-ID count mismatch remains rejected;
- unmapped positive and negative runtime IDs remain rejected;
- DuckDB receives the mapped child index as its union tag;
- `array.offset + parent_offset` is passed into sparse-union child validity, default, dictionary, and run-end conversion paths.

No competing helper branch, review, issue comment, or later commit was found that solved the remaining native offset failure.

## Native evidence before the current repair

Focused run `30763647825` at `bfb8434e380eb69765e8c154e57e6d092e43dd57` built DuckDB's debug test runner and passed:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. signed-boundary IDs `-128,0,127`.

Its offset control failed before mapped-value assertions with:

```text
Invalid Input Error: arrow_scan: array length mismatch
```

That was a fixture-shape failure, not evidence against the signed lookup or generated source repair.

Commit `c3513da03af17f6d1ab1166178a03f2d46e47230` attempted to set the sparse-union child length to three while retaining a top-level struct offset of one. Main run `30830192523` passed, but focused run `30830192515` still failed because the top-level array's physical extent remained four while its child exposed only three rows.

## Current fixture repair

Commit `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c` changes only `test/arrow/arrow_union_type_ids.cpp` relative to `c3513da03af17f6d1ab1166178a03f2d46e47230`.

The positive offset control now uses a valid Arrow shape:

- root struct: offset `0`, logical length `3`;
- sparse-union child: offset `1`, logical length `3`;
- physical type-ID buffer: `{99,5,7,9}`;
- each sparse child array: four physical integer values;
- expected logical output: tags `0,1,2` and values `10,21,32`.

This directly exercises the sparse union's offset as the parent offset supplied to its children without violating the root/child logical-length invariant.

## Scope review

Relative to parent candidate `c962ece64c1356015aef15a37c0cc636f63b376b`, the repair carrier changes only:

- `.github/workflows/fieldwork-arrow-union-type-id-candidate.yml`
- `test/arrow/arrow_union_type_ids.cpp`
- `tools/fieldwork/apply_arrow_union_type_id_hardening.py`

The generated production fence remains exactly:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`

Production-code review at the current head found no unrelated broadening. The 256-entry mapping, duplicate/count/unmapped checks, mapped child tags, and all child offset paths are retained.

## Promotion gate

Do not merge PR #16 or contact public upstream.

Keep the clean branch unchanged until exact head `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c` has:

1. a green ordinary Main run;
2. green identity, non-sequential, reordered, signed-boundary, and offset controls;
3. green duplicate-ID, duplicate-negative-ID, count-mismatch, unmapped-positive-ID, and unmapped-negative-ID controls;
4. an inspected artifact with the three generation markers and exact seven-file generated source fence.

After that, verify the workflow's intended nine-file clean publication (seven generated source files plus `test/arrow/CMakeLists.txt` and `test/arrow/arrow_union_type_ids.cpp`) against repository instructions before advancing the clean branch.

## Continuation

Resume from `teamleaderleo/duckdb@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`. First inspect focused run `30845351615` / job `91792186958` and Main run `30845355047`. Repair only the first demonstrated failure; do not weaken or remove any positive or malformed-input control.
