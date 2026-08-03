# Private upstream pull-request draft

> Draft only. Public upstream contact requires explicit authorization.

## Title

fix(arrow): map signed sparse union type IDs to child indices

## Summary

Arrow sparse-union type IDs are signed 8-bit logical schema codes, not positional child indexes. Parse the schema's type-ID list, retain a signed logical-ID-to-child-index mapping, and use the mapped child index during conversion.

The conversion must also forward the sparse union's effective offset to its child arrays. Otherwise a valid sliced union can read the correct logical type ID while pairing it with a child value from the wrong physical row.

## Proposed source scope

- add union-specific Arrow type information containing children and a 256-entry signed-byte ID map;
- parse and validate signed sparse-union type IDs across `[-128,127]`;
- reject schema type-ID count mismatch and duplicate signed IDs;
- resolve runtime type-ID buffer values through the map;
- reject unmapped positive and negative runtime IDs;
- write the mapped child index as DuckDB's union tag;
- pass `array.offset + parent_offset` through child validity, default, dictionary, and run-end conversion;
- keep the diff free of Fieldwork workflows/scripts and unrelated changes.

## Focused tests

Positive:

- identity IDs `0,1,2`;
- non-sequential IDs `5,7,9`;
- reordered IDs `2,1,0`;
- signed-boundary IDs `-128,0,127`;
- sparse-union offset one over an ignored physical prefix entry.

Malformed:

- duplicate positive schema IDs;
- duplicate negative schema IDs;
- schema type-ID count mismatch;
- unmapped positive runtime ID;
- unmapped negative runtime ID.

The offset fixture uses an unsliced three-row root with a sparse-union child of offset one and length three over four physical type IDs and four physical values in each child.

## Exact private evidence

- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`;
- characterization: `ed05ac593498fb4f95546ec591824ee23429088d`;
- passing parent candidate: `c962ece64c1356015aef15a37c0cc636f63b376b`;
- current repair carrier: `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`;
- current Main run `30845355047`: success;
- current focused run `30845351615`, job `91792186958`: in progress;
- clean branch `fix/arrow-union-type-id-mapping`: still exact target base until focused green.

## Proposed clean source fence

Seven generated production files:

- `src/common/enum_util.cpp`
- `src/function/table/arrow.cpp`
- `src/function/table/arrow/arrow_duck_schema.cpp`
- `src/function/table/arrow/arrow_type_info.cpp`
- `src/function/table/arrow_conversion.cpp`
- `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
- `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`

Focused test files:

- `test/arrow/CMakeLists.txt`
- `test/arrow/arrow_union_type_ids.cpp`

## Pre-publication checklist

- [x] correct target base and carrier ladder;
- [x] review signed-ID production design and exact changed-file fences;
- [x] pass ordinary Main at the current exact carrier head;
- [ ] pass all ten native focused controls at the same exact head;
- [ ] inspect the retained artifact, markers, digest, patch, and seven generated files;
- [ ] verify the workflow's exact nine-file clean publication from the target base;
- [ ] run relevant checks on the clean source revision or exact equivalent;
- [ ] update exact clean source head and test links in the packet;
- [ ] obtain explicit authorization before any public write.
