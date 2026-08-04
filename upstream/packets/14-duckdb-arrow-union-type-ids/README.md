# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`REPAIR — expected-error harness repair committed; exact-head CI queued`

The current private repair carrier is [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16) at exact head `7467f762292151925ceed1af3a030949241ca549`. The preceding exact head `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c` passed ordinary Main and all five positive native controls. Its first malformed control raised the intended DuckDB exception, but the fixture treated that expected binder exception as unexpected and leaked the unconsumed single-batch Arrow stream.

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
5. Valid offset fixture and positive-control head: `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`.
6. Current expected-error harness repair: `repair/262-arrow-union-malformed-map-controls@7467f762292151925ceed1af3a030949241ca549`.
7. Clean publication branch: `fix/arrow-union-type-id-mapping@2c9e51aa33dd07e928edae66304430aeb038edd7`, still identical to target base pending focused green.

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

The valid offset fixture uses an unsliced three-row root containing a sparse-union child with offset one and logical length three over four physical entries. This satisfies Arrow parent/child length invariants while directly exercising the offset supplied to the union's child conversions.

The current head changes only the expected-error fixture path relative to `6ff47e3...`:

- each malformed test supplies the exact intended DuckDB error substring;
- binder exceptions release the unconsumed Arrow stream before assertion;
- execution-time failures are checked through `QueryResult::HasError()` and `GetError()`;
- all five malformed controls remain present and are not weakened;
- production generators and generated-source scope are unchanged.

## Scope fence

Carrier changes relative to the passing parent candidate remain limited to:

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

The clean publication also includes `test/arrow/CMakeLists.txt` and `test/arrow/arrow_union_type_ids.cpp`, for an exact nine-file fence.

## Evidence

At `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`:

- Main `30845355047`: success;
- focused hardening `30845351615` / job `91792186958`: debug build success;
- identity mapping: pass;
- non-sequential mapping: pass;
- reordered mapping: pass;
- signed-boundary mapping: pass;
- nonzero sparse-union offset: pass;
- first malformed control: production raised the intended `Arrow union type ID 5 is duplicated` exception, but the fixture reported it as unexpected;
- LeakSanitizer then reported the unconsumed 152-byte single-batch stream allocation.

At current head `7467f762292151925ceed1af3a030949241ca549`:

- focused hardening run `30928499515`, job `92056903097`: queued;
- ordinary Main run `30928504166`: queued;
- stale characterization run `30928499578`: expected red if executed and is not promotion evidence.

## Public prior-art refresh

Read-only refresh found no superseding implementation:

- public issue `duckdb/duckdb#21842` remains open;
- focused PR `duckdb/duckdb#21843` remains closed and unmerged;
- broader dense-union PR `duckdb/duckdb#21898` remains closed and unmerged;
- newer merged union work addresses buffer/chunk offsets and appender behavior, not schema logical-ID-to-child-index mapping.

## Promotion gate

Do not merge or contact public upstream. Advance the clean branch only after the current exact head has:

1. green Main;
2. green identity, non-sequential, reordered, signed-boundary, and offset controls;
3. green duplicate-ID, duplicate-negative-ID, count-mismatch, unmapped-positive-ID, and unmapped-negative-ID controls;
4. an inspected artifact with all three generation markers and the exact seven generated source files;
5. a verified clean publication fence.

## Current receipt and continuation

Resume from `teamleaderleo/duckdb@7467f762292151925ceed1af3a030949241ca549`, focused run `30928499515`, job `92056903097`. Repair only a demonstrated new failure; do not weaken or remove any positive or malformed-input control.
