# Tests and exact receipts

## Current exact head

Carrier: `repair/262-arrow-union-malformed-map-controls@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`

Target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`

Private PR: `teamleaderleo/duckdb#16`

| Run/job | Result | Meaning |
| --- | --- | --- |
| Main `30845355047` | success | Ordinary repository workflow is green at the current exact carrier head. |
| Hardening `30845351615`, job `91792186958` | in progress | Exact checkout, carrier fence, generated-source fence, three generation markers, signed-byte model, and dependency setup passed; native debug build is executing. |
| Characterization `30845352934` | queued, expected red | The old failure characterization is stale after applying the mapping repair. |

## Current focused controls

Positive controls:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered in-range IDs `2,1,0`;
4. signed-boundary IDs `-128,0,127`;
5. sparse-union offset `1` over an ignored physical prefix entry.

Malformed controls:

6. duplicate positive schema IDs;
7. duplicate negative schema IDs;
8. schema type-ID count mismatch;
9. unmapped positive runtime ID;
10. unmapped negative runtime ID.

The workflow must pass all ten controls before it can publish the clean branch.

## Current offset fixture

The current fixture repair at `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c` uses:

- root struct: offset `0`, logical length `3`;
- sparse-union child: offset `1`, logical length `3`;
- type-ID buffer: `{99,5,7,9}`;
- each sparse child: four physical integer values;
- expected logical tags and values: `0:10`, `1:21`, `2:32`.

This satisfies the parent/child logical-length invariant while exercising the offset supplied by the sparse union to its children.

## Signed-ID repair evidence

Head `bfb8434e380eb69765e8c154e57e6d092e43dd57` introduced the 256-entry signed-byte lookup and signed malformed controls.

Focused run `30763647825` built the native debug test runner and passed:

- identity mapping;
- non-sequential mapping;
- reordered mapping;
- signed-boundary mapping.

Its offset control failed before mapped-value assertions with:

```text
Invalid Input Error: arrow_scan: array length mismatch
```

That failure was classified as an invalid fixture shape, not a generated production-code result.

## Superseded fixture evidence

Head `c3513da03af17f6d1ab1166178a03f2d46e47230` attempted to shorten the union child while retaining a top-level struct offset.

| Run | Result | Meaning |
| --- | --- | --- |
| Main `30830192523` | success | Ordinary repository build remained green. |
| Hardening `30830192515`, job `91741925204` | failure | The positive offset control was still rejected with an array-length mismatch before value assertions. |

The current head replaces that shape with an unsliced root and a sliced sparse-union child.

## Earlier exact receipts

### Characterization

Head: `ed05ac593498fb4f95546ec591824ee23429088d`

- characterization `30651534363`: success;
- Main `30651534354`: success.

### Passing parent candidate

Head: `c962ece64c1356015aef15a37c0cc636f63b376b`

- focused candidate `30654275395`: success;
- Main `30654275400`: success;
- stale characterization `30654275393`: expected red.

### Superseded unsigned hardening

Head: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

- Main `30659465479`: success;
- focused hardening `30659465467`, job `91251921754`: failure in positive controls;
- retained artifact `8805129666`.

### Parent-offset source repair and artifact carrier

- semantic transform commit: `9c6a7d4f5ccbe47a6338233954471586df271968`;
- artifact carrier head: `c8552f49b0ae1896a40296973725aae297a7671a`;
- Main `30694359500`: success;
- focused hardening `30694359081`, job `91354527257`: failure in the invalid positive offset fixture;
- artifact `8817935353`;
- ZIP SHA-256 `a0f01a87e621e4968ccf4a6cda00981e1ad2697255492f663fd68e5c6a9e95bb`;
- patch SHA-256 `698020100ff40bf202cff4e5ba01b174c876dd535f158874702d3ef2eaaedfe7`;
- artifact integrity and exact seven-file generated-source fence: success.

## Generated-source fence

Every current hardening run requires exactly:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`

Generation markers required by the current workflow:

```text
FIELDWORK_262_PATCH=arrow-union-type-id-mapping
FIELDWORK_262_HARDENING=signed-type-id-duplicate-rejection
FIELDWORK_262_REPAIR=union-child-parent-offset
```

## Clean publication gate

The workflow publishes only after all native controls pass. It resets to exact target base `2c9e51aa33dd07e928edae66304430aeb038edd7`, applies the generated production patch, adds the focused test registration and source, verifies an exact nine-file staged fence, commits, and pushes `fix/arrow-union-type-id-mapping`.

Until focused run `30845351615` completes successfully, the clean branch remains intentionally unchanged at the target base.
