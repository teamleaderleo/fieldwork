# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`REPAIR — exact-head native hardening in progress`

The current private repair carrier is [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16) at exact head `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`. Ordinary Main run `30845355047` is green at that head. Focused native hardening run `30845351615`, job `91792186958`, is executing.

No public DuckDB issue, pull request, review, comment, or branch has been modified. Public upstream remains read-only and unauthorized for contact.

## Assignment

- unit: `14`
- target: DuckDB
- proposed contribution: `fix(arrow): map sparse union type IDs to child indices`
- owner record: [`teamleaderleo/linux-fieldwork#262`](https://github.com/teamleaderleo/linux-fieldwork/issues/262)
- coordination issue: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- packet branch: `p0/435-unit-14-duckdb-arrow-union-type-ids`
- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`

## Exact source ladder

1. Characterization: [`teamleaderleo/duckdb#12`](https://github.com/teamleaderleo/duckdb/pull/12), `ed05ac593498fb4f95546ec591824ee23429088d`.
2. Passing parent mapping candidate: [`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14), `c962ece64c1356015aef15a37c0cc636f63b376b`.
3. Signed-ID repair examined: `bfb8434e380eb69765e8c154e57e6d092e43dd57`.
4. Superseded invalid offset fixture: `c3513da03af17f6d1ab1166178a03f2d46e47230`.
5. Current repair carrier: `repair/262-arrow-union-malformed-map-controls@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`.
6. Clean publication branch: `fix/arrow-union-type-id-mapping@2c9e51aa33dd07e928edae66304430aeb038edd7`, still identical to target base pending focused green.

## Current design

The repair treats Arrow sparse-union type IDs as signed 8-bit values:

- accepts the full `[-128, 127]` domain;
- uses a 256-entry type-ID-to-child-index table;
- indexes each `int8_t` by its unsigned-byte representation;
- rejects duplicate signed schema IDs;
- rejects schema-ID count mismatch;
- rejects unmapped positive and negative runtime IDs;
- writes the mapped child index as DuckDB's union tag;
- passes `array.offset + parent_offset` through sparse-union child validity, default, dictionary, and run-end conversion paths.

The current fixture repair changes only `test/arrow/arrow_union_type_ids.cpp` relative to the previous head. It uses an unsliced three-row root containing a sparse-union child with offset one and logical length three over four physical entries. This satisfies Arrow parent/child length invariants while directly exercising the offset supplied to the union's child conversions.

## Scope fence

Carrier changes relative to the passing parent candidate are limited to:

- `.github/workflows/fieldwork-arrow-union-type-id-candidate.yml`
- `test/arrow/arrow_union_type_ids.cpp`
- `tools/fieldwork/apply_arrow_union_type_id_hardening.py`

The generated production fence remains exactly seven Arrow source files:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`

The current workflow's clean publication also includes `test/arrow/CMakeLists.txt` and `test/arrow/arrow_union_type_ids.cpp`. Verify that nine-file fence against the repository instructions before advancing the clean branch.

## Evidence

Previously confirmed at `bfb8434e380eb69765e8c154e57e6d092e43dd57` in focused run `30763647825`:

- identity mapping: pass;
- non-sequential mapping: pass;
- reordered mapping: pass;
- signed-boundary mapping: pass;
- offset control: rejected before assertions because the fixture described an invalid Arrow array shape.

At current head `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`:

- Main `30845355047`: success;
- focused hardening `30845351615` / job `91792186958`: in progress;
- stale characterization `30845352934`: expected red if executed.

## Promotion gate

Do not merge or contact public upstream. Advance the clean branch only after the current exact head has:

1. green Main;
2. green identity, non-sequential, reordered, signed-boundary, and offset controls;
3. green duplicate-ID, duplicate-negative-ID, count-mismatch, unmapped-positive-ID, and unmapped-negative-ID controls;
4. an inspected artifact with all three generation markers and the exact seven generated source files;
5. a verified clean publication fence.

## Current receipt and continuation

The newest detailed receipt is `verification-2026-08-03-signed-offset-repair.md`, committed on this packet branch at `aad4da5b8eda040e42a01f712177b63193bb9fe7`.

Resume from `teamleaderleo/duckdb@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`, focused run `30845351615`, job `91792186958`. Repair only the first demonstrated failure; do not weaken or remove any positive or malformed-input control.
