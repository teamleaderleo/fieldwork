# DuckDB sparse-union signed type-ID repair receipt

Status: `REPAIR — corrected sliced-array fixture is running exact-head native gates`

Recorded: 2026-08-03  
Public upstream contact authorized: `false`

## Exact identities

- public target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- stack-base PR/head: `teamleaderleo/duckdb#14@c962ece64c1356015aef15a37c0cc636f63b376b`
- active repair PR: `teamleaderleo/duckdb#16`
- active repair branch: `repair/262-arrow-union-malformed-map-controls`
- exact current carrier head: `c3513da03af17f6d1ab1166178a03f2d46e47230`

Carrier fence relative to the stack base:

1. `.github/workflows/fieldwork-arrow-union-type-id-candidate.yml`
2. `test/arrow/arrow_union_type_ids.cpp`
3. `tools/fieldwork/apply_arrow_union_type_id_hardening.py`

Expected clean source fence after successful publication:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`
8. `test/arrow/CMakeLists.txt`
9. `test/arrow/arrow_union_type_ids.cpp`

## Selected source contract

- preserve Arrow sparse-union type IDs separately from DuckDB child indexes;
- accept the full signed-byte schema domain `[-128,127]`;
- use a 256-entry lookup indexed by the type ID's byte representation;
- reject duplicate signed schema IDs;
- reject type-ID count mismatch;
- reject unmapped positive and negative runtime IDs;
- map each runtime type ID to the DuckDB child index before selecting a value;
- apply the union array offset plus incoming parent offset to child conversion exactly once;
- emit DuckDB's mapped child index as the output union tag.

## Ten focused controls

Positive:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. signed boundaries `-128,0,127`;
5. nonzero parent offset with an ignored physical prefix row.

Negative:

6. duplicate positive schema IDs;
7. duplicate negative schema IDs;
8. schema type-ID count mismatch;
9. unmapped positive runtime ID;
10. unmapped negative runtime ID.

## Previous native result

Run `30763647825`, job `91538497603`, completed a full debug build. Identity, non-sequential, reordered, and signed-boundary controls all passed natively.

The parent-offset control then failed before union conversion with `arrow_scan: array length mismatch`. The fixture had exposed a logical root length of `3` but a union child length of `4`. The fourth entry is physical prefix backing data, not a fourth logical row.

## Fixture correction

At exact head `c3513da03af17f6d1ab1166178a03f2d46e47230`:

- root length remains `3` and root offset remains `1`;
- union logical length is corrected to `3`;
- type-ID and child-value buffers retain `4` physical entries.

This models a sliced parent without violating Arrow's logical child-length contract.

## Current execution

- hardening run: `30830192515`;
- characterization run: `30830195196`;
- Main run: `30830196586`.

At receipt creation, the hardening job had verified exact carrier identity, generated the hardened source, passed the signed-byte map model, installed build dependencies, and was building the debug test runner. No final pass is claimed here.

## Upstream precedent and duplicate audit

Historical closed upstream PRs:

- `duckdb/duckdb#21843` — sparse type-ID-to-child-index mapping;
- `duckdb/duckdb#21898` — dense-union support plus sparse mapping.

The current repair is a narrowed, hardened revival, not a claim of novel architecture. Audit on 2026-08-03 found no active matching upstream issue or pull request. No public upstream interaction occurred.

## Promotion boundary

Do not mark READY until the exact current carrier completes all ten focused controls, publishes or proves the exact nine-file source fence, and receives complete-diff review on the resulting immutable source head.