# Unit 14 signed sparse-union type-ID repair — 2026-08-03

## In simple words

The first hardening pass treated negative Arrow union type IDs as malformed. That premise is wrong. Arrow stores union type IDs as signed 8-bit integers, and the C++ API represents the schema codes as `int8_t`.

The retained hardening run therefore failed for a useful reason: it encoded only the nonnegative half of the type-ID domain. The repaired design covers all signed-byte values while preserving duplicate-schema and unmapped-runtime rejection.

## Exact identities

- Target repository: `teamleaderleo/duckdb`
- Target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- Parent mapping carrier: PR #14, head `c962ece64c1356015aef15a37c0cc636f63b376b`
- Hardening carrier: PR #16, branch `repair/262-arrow-union-malformed-map-controls`
- Failed hardening head: `c8552f49b0ae1896a40296973725aae297a7671a`
- Failed run/job: `30694359081` / `91354527257`
- Current repaired carrier head: `bfb8434e380eb69765e8c154e57e6d092e43dd57`
- Current hardening run: `30763647825`
- Guarded clean branch: `fix/arrow-union-type-id-mapping`, initially exact target base
- Upstream contact authorized: `false`

## Rejected premise

The old generated implementation used:

- a 128-entry mapping table;
- schema bounds `[0, 127]`;
- explicit rejection of negative schema and runtime IDs.

The old focused fixture also asserted that a negative runtime ID must fail. That test encoded the implementation mistake rather than Arrow's contract.

## Selected repair

- accept schema type IDs in `[-128, 127]`;
- store a 256-entry type-ID-to-child-index table;
- index through `static_cast<uint8_t>(type_id)` so every signed-byte bit pattern has one stable slot;
- reject duplicate signed schema IDs before conversion;
- reject any positive or negative runtime ID whose slot remains unmapped;
- retain the existing sparse-union parent-offset repair.

The mapping is not a reinterpretation of child indexes. DuckDB's output union tag remains the mapped child index; the signed Arrow type ID is only the schema/runtime discriminator.

## Controls

Positive:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. signed boundary IDs `-128,0,127`;
5. nonzero parent offset.

Negative:

6. duplicate positive schema IDs;
7. duplicate negative schema IDs;
8. schema type-ID count mismatch;
9. unmapped positive runtime ID;
10. unmapped negative runtime ID.

## Pre-execution checks

- Generator anchor simulation against the retained generated-source artifact: passed; every intended replacement applied exactly once.
- Python signed-byte map model: prepared in the target workflow.
- Compiled C++17 signed-byte map model with `-Wall -Wextra -Werror`: passed.

These are `model-executed` checks only. Target-native DuckDB build and ten focused controls remain required.

## Clean publication guard

The hardening workflow may publish only after all focused controls pass. It refuses to write unless `fix/arrow-union-type-id-mapping` still points to target base `2c9e51aa...`. The final staged fence must be exactly seven generated Arrow source files plus `test/arrow/CMakeLists.txt` and `test/arrow/arrow_union_type_ids.cpp`.

No public upstream interaction occurred.
