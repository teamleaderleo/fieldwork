# Analysis

## Defect

Arrow sparse unions carry a logical type-ID buffer. The values in that buffer identify children through the type-code list in the schema format, such as `+us:3,7`; they are not positional child indexes.

The characterized DuckDB path treated each logical type ID as a direct index into the child array. A row tagged `3` in a two-child union therefore became an out-of-range access even though schema code `3` validly names child zero. Parent array slicing also requires the type-ID buffer and child reads to honor the parent offset.

## Characterization

[`teamleaderleo/duckdb#12`](https://github.com/teamleaderleo/duckdb/pull/12) introduced an expected-failure carrier at `ed05ac593498fb4f95546ec591824ee23429088d`.

The test uses sparse logical IDs `{3, 7}` and parent offsets `1` and `2`. Its characterization workflow succeeded because the unpatched target failed in the expected way. The ordinary `Main` workflow also passed.

## Minimal candidate

[`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14) at `c962ece64c1356015aef15a37c0cc636f63b376b` generates a focused mapping change from base `2c9e51aa33dd07e928edae66304430aeb038edd7`.

The candidate:

- adds union-specific Arrow type information;
- parses sparse union type codes from the schema;
- stores a logical type-ID to child-index mapping;
- resolves every row's logical ID through that mapping;
- rejects unknown and out-of-range IDs;
- uses the resolved child index when constructing DuckDB union values;
- exercises sparse IDs and parent offsets.

Its targeted Ubuntu workflow and ordinary `Main` workflow passed. The old expected-failure characterization workflow became red because the candidate made the characterized case succeed; that red is stale-carrier behavior rather than contrary product evidence.

## Hardening child

[`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16) at `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2` adds:

- duplicate logical-ID rejection;
- validation that the Arrow type-ID storage uses `NANOARROW_TYPE_INT8` or `NANOARROW_TYPE_UINT8`;
- validity checks around the type-ID array;
- explicit `int8_t` reads;
- malformed `int16` type-ID storage coverage;
- offset and duplicate-ID controls.

The ordinary `Main` workflow passed. The targeted Fieldwork workflow failed after checkout, patch generation, carrier verification, and a clean debug build. The failed step was the targeted positive mapping test group. GitHub's retained artifact proves that both patch-generation phases completed and contains the exact generated patch and receipts. The available job-log response did not expose the assertion text, so the packet does not infer the failing row or expression.

## Generated patch review

Artifact `arrow-union-type-id-patch` from workflow run `30659465467`, artifact ID `8805129666`, contains:

- `arrow-union-type-id-hardened.patch`
- `candidate-generation.txt`
- `carrier-files.txt`
- `source-files.txt`

Receipts:

- `Arrow sparse union type-id mapping candidate applied`
- `Arrow sparse union type-id hardening applied`

The patch is 298 lines across seven files, with 177 insertions and 164 deletions. The substantive implementation changes are concentrated in:

- `src/function/table/arrow_conversion.cpp`
- `src/include/duckdb/function/table/arrow/arrow_conversion.hpp`

Five unrelated files show broad formatting churn and need exclusion from a clean source commit:

- `extension/parquet/decoder/ub_duckdb_json_decoder.cpp`
- `extension/parquet/writer/ub_duckdb_json_writer.cpp`
- `src/include/duckdb/common/arrow/appender/union_data.hpp`
- `src/include/duckdb/common/types/row/row_data_collection.hpp`
- `src/storage/compression/string_uncompressed.cpp`

The C++ test remains carrier input and therefore does not appear in that generated source diff.

## Public prior art

Read-only records:

- [`duckdb/duckdb#21842`](https://github.com/duckdb/duckdb/issues/21842) — public defect report.
- [`duckdb/duckdb#21843`](https://github.com/duckdb/duckdb/pull/21843) — prior source attempt.
- [`duckdb/duckdb#21898`](https://github.com/duckdb/duckdb/pull/21898) — later prior source attempt.

Both public pull requests closed through stale automation without maintainer review. No comment, reaction, issue, branch, or pull-request write was made in public upstream during this unit.

## Branch decision

The owned candidate and hardening branches are execution carriers. Comparing candidate base `2c9e51aa33dd07e928edae66304430aeb038edd7` to candidate head `c962ece64c1356015aef15a37c0cc636f63b376b` shows eight commits and only carrier workflow, test, CMake, and generator-script files. The generated product source is applied only inside CI.

A clean branch therefore requires deliberate source materialization, removal of unrelated formatting churn, addition of focused tests, and a fresh passing run. Because the hardening targeted test currently fails without an exposed assertion body, this packet leaves the branch absent and records `REPAIR` as the disposition.