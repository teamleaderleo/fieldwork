# Unit 14 verification — Arrow type-code contract and malformed-stream repair

Date: 2026-08-05

## Disposition

`REPAIR — exact-head CI queued`

This receipt supersedes signed-negative design claims in older unit 14 receipts. It does not erase historical evidence; it records why that design was rejected before clean publication.

## Exact identity

- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- characterization: `ed05ac593498fb4f95546ec591824ee23429088d`
- passing parent candidate: `c962ece64c1356015aef15a37c0cc636f63b376b`
- private repair PR: `teamleaderleo/duckdb#16`
- repair branch: `repair/262-arrow-union-malformed-map-controls`
- current carrier head: `c9938e6d637217d1cd4b41a739b2c179d97f6b2b`
- clean branch: `fix/arrow-union-type-id-mapping@2c9e51aa33dd07e928edae66304430aeb038edd7`
- focused run: `30929848690`, job `92061428854`
- Main run: `30929853935`
- stale characterization run: `30929848816`, expected red and not promotion evidence

## Why the repair ladder was longer than expected

The underlying production defect is narrow but consequential: Arrow sparse-union logical type IDs can differ from physical child indexes. Without a mapping, DuckDB can throw for non-sequential IDs or silently pair a valid tag with the wrong child value for reordered IDs. A nonzero sparse-union offset can compound the problem by selecting the correct logical ID but reading a child value from the wrong physical row.

The later repairs were mostly verification and boundary work, not repeated discovery of unrelated production defects:

1. propagate the sparse-union effective offset to all child conversion paths;
2. repair invalid Arrow fixture shapes so the native control reaches DuckDB conversion;
3. capture expected binder exceptions without treating them as unexpected failures;
4. verify Arrow's actual type-code domain against primary sources;
5. replace a heap-backed one-batch test stream with an ownership-safe stack-backed fixture.

## Primary-source contract correction

Arrow stores union type codes in an `int8_t` buffer. The Arrow C++ reference implementation nevertheless rejects codes below zero and above `kMaxTypeCode`, and its reverse map has `kMaxTypeCode + 1` entries. Therefore valid schema type codes are nonnegative, with the practical domain `0..127`.

The earlier private extension that accepted `[-128,127]` was over-broad and is superseded. Current production generation:

- retains a 128-entry map;
- rejects negative schema codes during format parsing;
- rejects duplicate nonnegative schema codes;
- rejects schema type-ID count mismatch;
- rejects negative runtime values before indexing;
- rejects nonnegative runtime values not present in the schema map.

## Production behavior retained

The current generator still:

- adds union-specific Arrow type information;
- maps logical type IDs to physical child indexes;
- writes the mapped child index as DuckDB's union tag;
- forwards `array.offset + parent_offset` through validity, default, dictionary, and run-end child conversion paths.

## Harness repair

Run `30845351615` at carrier `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c` passed the full debug build and all five then-configured positive controls. The first malformed control raised the intended duplicate-ID exception, but the fixture reported it as unexpected. LeakSanitizer then reported the heap allocation made by `BatchToArrayStream` because schema binding exited before the helper returned a result.

The current fixture uses a stack-backed `ArrowArrayStream` state and idempotent release callback. DuckDB may copy the stream struct into its wrapper, but no copied instance owns heap memory. Binder exceptions therefore cannot leak or double-free the test stream.

## Exact scope fences

Carrier relative to `c962ece...`:

1. `.github/workflows/fieldwork-arrow-union-type-id-candidate.yml`
2. `test/arrow/arrow_union_type_ids.cpp`
3. `tools/fieldwork/apply_arrow_union_type_id_hardening.py`

Generated production source:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`

Intended clean publication adds:

8. `test/arrow/CMakeLists.txt`
9. `test/arrow/arrow_union_type_ids.cpp`

## Current controls

Positive:

1. identity IDs `0,1,2`
2. non-sequential IDs `5,7,9`
3. reordered IDs `2,1,0`
4. upper-bound IDs `0,64,127`
5. sparse-union offset one over an ignored physical prefix

Malformed:

1. duplicate schema ID
2. negative schema ID
3. schema type-ID count mismatch
4. unmapped nonnegative runtime ID
5. negative runtime value

## Pending gate

Do not promote or contact public upstream until the same exact carrier head has:

- green Main;
- all ten native controls green;
- inspected artifact digest, generation markers, patch, and exact seven generated files;
- workflow-created clean branch verified as exactly nine target-source files from the exact target base.

## Continuation

Resume from focused run `30929848690`, job `92061428854`. If it fails, repair only the first demonstrated failure. If it passes, inspect the artifact and clean branch before changing disposition.
