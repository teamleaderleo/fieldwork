# Unit 14 verification — 2026-08-01

## Current disposition

**REPAIR**

Unit 14 remains limited to DuckDB Arrow sparse/dense union logical type-id to child-index mapping.

Selected repair source:

- repository: `teamleaderleo/duckdb`
- branch: `work/duckdb-arrow-union-type-id-hardening`
- exact head: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`
- passing predecessor branch: `work/duckdb-arrow-union-type-id-candidate`
- passing predecessor head: `c962ece64c1356015aef15a37c0cc636f63b376b`
- characterization head: `ed05ac593498fb4f95546ec591824ee23429088d`
- target baseline: `75b8037d80d34c2fe4187e1a5c00740e49322728`

A clean target-source branch has not been created. Creation is deferred until the hardening workflow passes at the selected source revision and the lookup representation is reconciled with the owner/prior-art guidance recorded below.

## Repository instructions read

The following records were read from `p0/435-upstream-packet-workflow`:

- `START_HERE.md`
- `AGENTS.md`
- `upstream/README.md`
- `upstream/INDEX.md`
- `upstream/packets/README.md`

`START_HERE.md` references `notes/PROGRAMME_GUIDE.md` and `AGENT_FIELD_GUIDE.md`; those paths are absent on the workflow branch. This repository-state gap does not expand unit scope.

## Durable record inventory read

Coordination and ownership:

- [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- [`teamleaderleo/linux-fieldwork#262`](https://github.com/teamleaderleo/linux-fieldwork/issues/262), including every comment

Owned carrier ladder:

- characterization PR [`teamleaderleo/duckdb#12`](https://github.com/teamleaderleo/duckdb/pull/12), branch `work/duckdb-arrow-union-type-id-characterization`, head `ed05ac593498fb4f95546ec591824ee23429088d`
- candidate PR [`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14), branch `work/duckdb-arrow-union-type-id-candidate`, head `c962ece64c1356015aef15a37c0cc636f63b376b`
- hardening PR [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16), branch `work/duckdb-arrow-union-type-id-hardening`, head `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

Public prior art, read-only:

- issue [`duckdb/duckdb#21842`](https://github.com/duckdb/duckdb/issues/21842)
- focused PR [`duckdb/duckdb#21843`](https://github.com/duckdb/duckdb/pull/21843), head `abc424169f09c752f5ac06cfe44c1fb8c909a626`
- broader PR [`duckdb/duckdb#21898`](https://github.com/duckdb/duckdb/pull/21898), head `e22d8d3e39538acd32997a803cbcabb5fda341a4`
- all visible conversation comments on both public PRs

No public upstream contact was made.

## Current exact-head test receipts

### Characterization head `ed05ac593498fb4f95546ec591824ee23429088d`

- [`Fieldwork unit 14 Arrow union characterization` run 30651534363](https://github.com/teamleaderleo/duckdb/actions/runs/30651534363): **success**
- [`Main` run 30651534354](https://github.com/teamleaderleo/duckdb/actions/runs/30651534354): **success**

Interpretation: the characterization carrier demonstrates the two target failure modes while preserving the ordinary repository workflow.

### Candidate head `c962ece64c1356015aef15a37c0cc636f63b376b`

- [`Fieldwork unit 14 Arrow union candidate` run 30654275395](https://github.com/teamleaderleo/duckdb/actions/runs/30654275395): **success**
- [`Main` run 30654275400](https://github.com/teamleaderleo/duckdb/actions/runs/30654275400): **success**
- [`Fieldwork unit 14 Arrow union characterization` run 30654275393](https://github.com/teamleaderleo/duckdb/actions/runs/30654275393): **failure**

Interpretation: candidate and ordinary workflows pass. The characterization workflow remains intentionally red after the source fix because it expects the old failure behavior.

### Hardening head `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

- [`Main` run 30659465479](https://github.com/teamleaderleo/duckdb/actions/runs/30659465479): **success**
- [`Fieldwork unit 14 Arrow union hardening` run 30659465467](https://github.com/teamleaderleo/duckdb/actions/runs/30659465467): **failure**
  - job: `hardened-regression-suite`, job id `91251921754`
  - failing step: `Run Arrow union focused tests`
  - checkout and setup steps completed successfully
- [`Fieldwork unit 14 Arrow union characterization` run 30659465474](https://github.com/teamleaderleo/duckdb/actions/runs/30659465474): **failure**

Interpretation: ordinary CI passes at the selected repair head. The dedicated hardening suite has a real unresolved focused-test failure. The stale characterization workflow remains red for the expected post-fix reason.

## Artifact validation executed

Local artifact examined:

- file: `unit14-hardening-artifact.zip`
- SHA-256: `d1b45bb15115b08560413b00d46a1aa30983cad28101ea8b0c26f76e2f5fbd4c`
- `unzip -t`: **success**, five files, zero archive errors
- embedded generation revision: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

Artifact inventory:

- `arrow-union-type-id-hardened.patch`
- `candidate-generation.txt`
- `carrier-files.txt`
- `source-files.txt`
- `unit14-files.txt`

Carrier-only files recorded in the artifact:

- [`.github/workflows/fieldwork-unit14-arrow-union-hardening.yml`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/.github/workflows/fieldwork-unit14-arrow-union-hardening.yml)
- [`test/arrow/test_arrow_union_type_ids.py`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/test/arrow/test_arrow_union_type_ids.py)
- [`test/arrow/test_arrow_union_type_ids_hardened.py`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/test/arrow/test_arrow_union_type_ids_hardened.py)

Generated source patch inventory:

- [`src/common/enum_util.cpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/common/enum_util.cpp)
- [`src/common/types/arrow.cpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/common/types/arrow.cpp)
- [`src/common/types/arrow/schema_metadata.cpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/common/types/arrow/schema_metadata.cpp)
- [`src/common/types/arrow/type_info.cpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/common/types/arrow/type_info.cpp)
- [`src/function/table/arrow_conversion.cpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/function/table/arrow_conversion.cpp)
- [`src/include/duckdb/common/arrow/arrow.hpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/include/duckdb/common/arrow/arrow.hpp)
- [`src/include/duckdb/common/arrow/schema_metadata.hpp`](https://github.com/teamleaderleo/duckdb/blob/fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2/src/include/duckdb/common/arrow/schema_metadata.hpp)

Patch accounting from `git apply --numstat`:

- seven source files
- 120 insertions
- 29 deletions

The patch contains an `ArrowUnionInfo` representation and explicit duplicate-ID rejection through `InvalidInputException`.

## Correction to the earlier packet observation

Fresh artifact inspection shows only the seven intended Arrow source files listed above. The artifact does not contain the previously reported Parquet/storage formatting-only paths. This verification supersedes that artifact-scope observation while preserving the earlier record as history.

## Technical observations and selected approach

1. Arrow union logical type IDs and child positions are separate concepts. Import must map the logical ID from the union type buffer to the corresponding child position before selecting a child vector.
2. The focused public prior art and owner record favor retaining a dedicated `ArrowUnionInfo` representation.
3. The owner record recommends a validated fixed-range lookup for IDs `0..127`, initialized with an invalid sentinel, with duplicate and malformed schema IDs rejected during construction.
4. The current hardening patch uses `unordered_map<int8_t, uint8_t>` for `union_id_to_child`. This diverges from the recorded fixed-range approach and remains a repair item.
5. Offset handling must occur exactly once. The positive-offset control belongs in the focused hardening suite because a second offset adjustment can silently select the wrong logical ID.
6. Duplicate IDs require explicit rejection. The hardening source includes this guard.

## Existing drafts and packet records

The following durable records remain part of the packet and were reviewed:

- `README.md`
- `analysis.md`
- `approaches.md`
- `tests.md`
- `references.md`
- `issue-draft.md`
- `pr-draft.md`
- `handoff.md`

The issue and PR drafts remain private packet material. They must stay unsubmitted until the hardening source reaches a passing exact head and the clean source branch is prepared.

## Remaining blockers

1. The dedicated hardening workflow fails at `Run Arrow union focused tests` on exact head `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`.
2. The exact failing assertion must be recovered from the focused test execution and repaired; the positive-offset control should be inspected first because offset application is the highest-risk semantic edge in the hardening child.
3. The lookup representation should be aligned with the validated fixed 128-entry approach documented in `teamleaderleo/linux-fieldwork#262` and focused prior art, or the deviation must receive a concrete technical justification in the packet.
4. A source-only patch must be regenerated after repair and checked against the seven-file source inventory.
5. The clean target-source branch remains deferred until the repaired hardening workflow and ordinary `Main` workflow both pass at the same exact revision.

## Continuation-ready handoff

Resume only unit 14 from `work/duckdb-arrow-union-type-id-hardening` at `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`.

1. Reproduce or recover the exact assertion from hardening run `30659465467`, job `91251921754`.
2. Inspect `test_arrow_union_type_ids_hardened.py`, beginning with the positive-offset control and malformed/duplicate-ID cases.
3. Repair the source while preserving single offset application and explicit duplicate-ID rejection.
4. Replace the current hash lookup with a validated fixed-range lookup, unless a documented benchmark or correctness constraint supports the existing representation.
5. Run the dedicated hardening workflow and ordinary `Main` workflow at the same source head.
6. Regenerate the source-only artifact, verify its hash and file inventory, then create the clean target-source branch from the accepted baseline.
7. Update this packet, the drafts, and issue `teamleaderleo/fieldwork#435` with the exact new source and packet heads.

Public upstream remains read-only throughout continuation.
