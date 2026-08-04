# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`REPAIR — Arrow type-code contract corrected; exact-head CI queued`

The current private repair carrier is [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16) at exact head `44a210f581789e5635f24d20cfa5a957ba0b4dd6`.

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
3. Initial child-offset repair: `9c6a7d4f5ccbe47a6338233954471586df271968`.
4. Valid offset fixture and positive-control head: `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`.
5. Expected-error capture repair: `7467f762292151925ceed1af3a030949241ca549`.
6. Arrow type-code contract correction commits: `208c9e8b163062aeb6460baa68d92efbce267baf`, `c0509b5b674df3e53e699c8b7c05f45977860a86`, and current head `44a210f581789e5635f24d20cfa5a957ba0b4dd6`.
7. Clean publication branch: `fix/arrow-union-type-id-mapping@2c9e51aa33dd07e928edae66304430aeb038edd7`, still identical to target base pending focused green.

## Correct Arrow contract

Arrow's union type-code buffer uses signed 8-bit storage. That does not make negative logical codes valid. The Arrow C++ reference implementation explicitly rejects codes below zero, rejects codes above `kMaxTypeCode`, and builds a reverse map of `kMaxTypeCode + 1` entries. The packet's earlier signed-negative extension is superseded.

The current repair therefore:

- accepts schema type codes only across `0..127`;
- retains the parent candidate's 128-entry type-ID-to-child-index table;
- rejects negative schema codes before construction;
- rejects duplicate nonnegative schema codes;
- rejects schema-ID count mismatch;
- rejects unmapped nonnegative runtime codes;
- rejects negative runtime buffer values before indexing;
- writes the mapped child index as DuckDB's union tag;
- passes `array.offset + parent_offset` through sparse-union child validity, default, dictionary, and run-end conversion paths.

## Fixture and harness repairs

The offset fixture uses an unsliced three-row root containing a sparse-union child with offset one and logical length three over four physical entries. This satisfies Arrow parent/child length invariants while directly exercising the offset supplied to the union's child conversions.

Malformed controls provide exact expected error substrings. Binder exceptions release the unconsumed single-batch Arrow stream before assertion; execution-time failures are checked through `QueryResult::HasError()` and `GetError()`.

## Scope fence

Carrier changes relative to the passing parent candidate remain exactly:

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

## Previous exact-head evidence

At `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`:

- Main `30845355047`: success;
- focused hardening `30845351615` / job `91792186958`: debug build success;
- identity mapping: pass;
- non-sequential mapping: pass;
- reordered mapping: pass;
- then-configured signed-boundary mapping: pass as implementation behavior, but later superseded because negative schema codes violate Arrow's contract;
- nonzero sparse-union offset: pass;
- first malformed control: production raised the intended duplicate-ID exception, but the fixture reported it as unexpected;
- LeakSanitizer reported the unconsumed 152-byte single-batch stream allocation.

## Current exact-head controls

Positive:

- identity IDs `0,1,2`;
- non-sequential IDs `5,7,9`;
- reordered IDs `2,1,0`;
- upper-bound IDs `0,64,127`;
- sparse-union offset one over an ignored physical prefix entry.

Malformed:

- duplicate schema ID;
- negative schema ID;
- schema type-ID count mismatch;
- unmapped nonnegative runtime ID;
- negative runtime buffer value.

Current runs at `44a210f581789e5635f24d20cfa5a957ba0b4dd6`:

- focused hardening `30929505318`: queued;
- ordinary Main `30929509618`: queued;
- stale characterization `30929504904`: expected red if executed and not promotion evidence.

## Public prior-art refresh

Read-only refresh found no superseding logical-ID mapping implementation:

- public issue `duckdb/duckdb#21842` remains open;
- focused PR `duckdb/duckdb#21843` remains closed and unmerged;
- broader dense-union PR `duckdb/duckdb#21898` remains closed and unmerged;
- newer merged union work addresses buffer/chunk offsets and appender behavior, not schema logical-ID-to-child-index mapping.

## Promotion gate

Do not merge or contact public upstream. Advance the clean branch only after the current exact head has:

1. green Main;
2. green identity, non-sequential, reordered, upper-bound, and offset controls;
3. green duplicate-ID, negative-schema-ID, count-mismatch, unmapped-runtime-ID, and negative-runtime-ID controls;
4. an inspected artifact with all three generation markers and the exact seven generated source files;
5. a verified clean publication fence.

## Current receipt and continuation

Resume from `teamleaderleo/duckdb@44a210f581789e5635f24d20cfa5a957ba0b4dd6`, focused run `30929505318`. Repair only a demonstrated new failure; do not weaken or remove any positive or malformed-input control.
