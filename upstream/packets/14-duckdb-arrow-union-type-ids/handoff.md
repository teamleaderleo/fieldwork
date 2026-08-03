# Continuation handoff

## Disposition

`REPAIR — exact-head native hardening in progress`

The signed sparse-union mapping and production offset repair have passed exact generation, identity, signed-byte model, and ordinary Main checks. The only live gate is the focused native build/test/publish job at the current exact head.

No public upstream interaction occurred.

## Exact revisions

- packet branch: `p0/435-unit-14-duckdb-arrow-union-type-ids`
- canonical packet update: `81c5974522afe6c372c91dab7470b043f2dccc54`
- latest detailed receipt: `aad4da5b8eda040e42a01f712177b63193bb9fe7`
- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- characterization: `ed05ac593498fb4f95546ec591824ee23429088d`
- passing parent candidate: `c962ece64c1356015aef15a37c0cc636f63b376b`
- signed-ID repair examined: `bfb8434e380eb69765e8c154e57e6d092e43dd57`
- superseded invalid fixture: `c3513da03af17f6d1ab1166178a03f2d46e47230`
- current repair carrier: `repair/262-arrow-union-malformed-map-controls@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`
- private PR: `teamleaderleo/duckdb#16`
- clean branch: `fix/arrow-union-type-id-mapping@2c9e51aa33dd07e928edae66304430aeb038edd7`, still identical to target base until focused green

## Current tests

- Main run `30845355047`: **success** at exact head `6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`.
- focused run `30845351615`, job `91792186958`: **in progress**.
- focused steps already green: exact checkout, carrier fence, source generation, all three generation markers, signed-byte model, and dependency setup.
- current focused step: native debug build.
- remaining focused steps: five positive controls, five malformed controls, exact nine-file clean publication, and artifact retention.
- stale characterization run `30845352934`: expected red if executed.

## Current design and fixture

The production candidate maps signed `int8_t` Arrow union IDs through a 256-entry lookup, rejects duplicate/count/unmapped IDs, writes mapped child indexes as DuckDB tags, and forwards `array.offset + parent_offset` through every sparse-union child conversion path.

The current offset fixture uses:

- root struct offset `0`, length `3`;
- sparse union offset `1`, length `3`;
- four physical type IDs `{99,5,7,9}`;
- four physical values in each sparse child;
- expected logical tags/values `0:10`, `1:21`, `2:32`.

This replaces two earlier invalid parent/child length combinations that were rejected by `arrow_scan` before mapped-value assertions.

## Continuation sequence

1. Inspect focused run `30845351615`, job `91792186958`.
2. If a positive or malformed control fails, recover the exact first assertion/error and repair only that demonstrated path; do not weaken a control.
3. If all controls pass, verify that the workflow publishes `fix/arrow-union-type-id-mapping` from exact base `2c9e51aa33dd07e928edae66304430aeb038edd7` with exactly nine paths: seven generated source files plus `test/arrow/CMakeLists.txt` and `test/arrow/arrow_union_type_ids.cpp`.
4. Inspect the retained artifact for ZIP integrity, digest, all three generation markers, exact seven-file generated-source fence, and patch accounting.
5. Confirm ordinary Main and focused evidence refer to the same carrier head.
6. Update `README.md`, `tests.md`, this handoff, PR #16, and `teamleaderleo/fieldwork#435` with exact carrier, clean, packet, workflow, job, artifact, and test heads.
7. Keep public DuckDB upstream read-only.

## Durable locations

- packet: `upstream/packets/14-duckdb-arrow-union-type-ids/`
- current detailed receipt: `verification-2026-08-03-signed-offset-repair.md`
- parent candidate: https://github.com/teamleaderleo/duckdb/pull/14
- repair carrier: https://github.com/teamleaderleo/duckdb/pull/16
- coordination: https://github.com/teamleaderleo/fieldwork/issues/435

No material observation from this pass is intentionally left only in chat.
