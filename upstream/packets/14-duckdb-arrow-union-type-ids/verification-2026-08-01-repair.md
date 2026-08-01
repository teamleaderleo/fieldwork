# Unit 14 repair verification — 2026-08-01

This file supersedes stale factual fields in `verification-2026-08-01.md` while preserving that file as an immutable historical receipt.

## Current disposition

**REPAIR**

The sparse-union logical type-ID mapping candidate is still the correct direction. The hardening suite exposed a second correctness defect in nonzero parent-offset handling. A private repair is committed and ordinary `Main` is green, but the exact focused workflow is still queued and therefore no clean source branch is promoted yet.

No public-upstream issue, pull request, review, or comment was created or modified.

## Exact revisions

Target and carrier ladder:

- verified DuckDB target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- characterization branch/head: `work/duckdb-arrow-union-type-id-characterization@ed05ac593498fb4f95546ec591824ee23429088d`
- passing mapping candidate branch/head: `work/duckdb-arrow-union-type-id-candidate@c962ece64c1356015aef15a37c0cc636f63b376b`
- repair carrier branch/head: `repair/262-arrow-union-malformed-map-controls@c8552f49b0ae1896a40296973725aae297a7671a`
- source-repair transform commit: `9c6a7d4f5ccbe47a6338233954471586df271968`
- superseded failing hardening head: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

The earlier packet value `75b8037d80d34c2fe4187e1a5c00740e49322728` is not a commit in `teamleaderleo/duckdb`. PR #14 and direct commit verification identify `2c9e51aa33dd07e928edae66304430aeb038edd7` as the actual target base.

Current private PR:

- [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16)
- title: `Reject ambiguous Arrow sparse-union type-ID maps`
- state: open draft
- base: `fieldwork/262-arrow-union-type-id-candidate@c962ece64c1356015aef15a37c0cc636f63b376b`
- head: `repair/262-arrow-union-malformed-map-controls@c8552f49b0ae1896a40296973725aae297a7671a`

## Repository instructions re-read

From `teamleaderleo/fieldwork@p0/435-upstream-packet-workflow`:

- `START_HERE.md`
- `AGENTS.md`
- `CODE_FIRST.md`
- `CONTRIBUTING.md`
- `REVIEWING.md`
- `upstream/README.md`
- `upstream/INDEX.md`
- `upstream/packets/README.md`

The governing constraints remain evidence-first execution, exact revision receipts, a narrow changed-file fence, durable GitHub records, and no public-upstream contact without authorization.

`START_HERE.md` references `notes/PROGRAMME_GUIDE.md` and `AGENT_FIELD_GUIDE.md`; those files remain absent on the workflow branch. This repository-state gap does not expand unit scope.

## Unit records read

Coordination and ownership:

- [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435), including comments
- [`teamleaderleo/linux-fieldwork#262`](https://github.com/teamleaderleo/linux-fieldwork/issues/262), including comments

Private carrier ladder:

- [`teamleaderleo/duckdb#12`](https://github.com/teamleaderleo/duckdb/pull/12), characterization
- [`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14), passing mapping candidate
- [`teamleaderleo/duckdb#16`](https://github.com/teamleaderleo/duckdb/pull/16), malformed-map and offset repair
- every visible branch diff, review/comment, workflow run, job/step record, and retained artifact for those carriers

Public prior art, read-only:

- [`duckdb/duckdb#21842`](https://github.com/duckdb/duckdb/issues/21842)
- [`duckdb/duckdb#21843`](https://github.com/duckdb/duckdb/pull/21843), focused type-ID mapping approach
- [`duckdb/duckdb#21898`](https://github.com/duckdb/duckdb/pull/21898), broader test ideas only
- current `duckdb/duckdb` Arrow conversion source around struct and union child conversion

## Exact defect found

The generated mapping candidate correctly uses an effective offset for the sparse-union type-ID buffer. However, the union's child vectors were still converted with the old parent-offset behavior.

In the nonzero-parent-offset control:

1. the containing struct has an offset of one physical row;
2. union type IDs start from the correct logical row because `GetEffectiveOffset` includes the incoming parent offset;
3. primitive union child values still start from physical row zero because the union child conversion path omits the union's own and incoming parent offsets;
4. tags and values are therefore shifted relative to each other.

This is a source correctness defect, not a schema-validation or build defect.

Current public DuckDB `main` shows the same asymmetry: struct child conversion passes `array.offset`, while union child conversion omits an equivalent child parent offset. That observation is read-only prior art, not public authority.

## Repair applied

Only `tools/fieldwork/apply_arrow_union_type_id_hardening.py` was changed for the semantic repair at commit `9c6a7d4f5ccbe47a6338233954471586df271968`.

The transform now generates:

```cpp
const auto union_child_parent_offset = NumericCast<uint64_t>(array.offset) + parent_offset;
```

That offset is passed through all sparse-union child paths:

- child validity calculation;
- default child conversion;
- dictionary-encoded child conversion;
- run-end-encoded child conversion.

`GetEffectiveOffset` continues to own final offset calculation. When `nested_offset != -1`, it ignores `parent_offset`, preventing double application in nested-offset paths.

The transform retains:

- fixed 128-entry type-ID lookup with invalid sentinels;
- schema type-ID count validation;
- type-ID range validation;
- explicit duplicate schema type-ID rejection;
- runtime negative-ID and unmapped-ID rejection;
- logical type-ID to DuckDB child/tag mapping.

Repair markers:

- `FIELDWORK_262_PATCH=arrow-union-type-id-mapping`
- `FIELDWORK_262_HARDENING=duplicate-type-id-rejection`
- `FIELDWORK_262_REPAIR=union-child-parent-offset`

## Changed-file fences

Carrier files relative to the passing parent candidate:

- `.github/workflows/fieldwork-arrow-union-type-id-candidate.yml`
- `test/arrow/arrow_union_type_ids.cpp`
- `tools/fieldwork/apply_arrow_union_type_id_hardening.py`

The final workflow is configured to require and retain exactly these generated source files:

- `src/common/enum_util.cpp`
- `src/function/table/arrow.cpp`
- `src/function/table/arrow/arrow_duck_schema.cpp`
- `src/function/table/arrow/arrow_type_info.cpp`
- `src/function/table/arrow_conversion.cpp`
- `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
- `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`

The workflow now retains the exact patch, generation receipts, carrier/source lists, and complete generated copies of all seven source files. That bundle is intended to construct the clean source-only branch after the focused run is green.

## Tests and workflow receipts

### Characterization `ed05ac593498fb4f95546ec591824ee23429088d`

- characterization run [`30651534363`](https://github.com/teamleaderleo/duckdb/actions/runs/30651534363): **success**
- Main run [`30651534354`](https://github.com/teamleaderleo/duckdb/actions/runs/30651534354): **success**

### Passing candidate `c962ece64c1356015aef15a37c0cc636f63b376b`

- candidate run [`30654275395`](https://github.com/teamleaderleo/duckdb/actions/runs/30654275395): **success**
- Main run [`30654275400`](https://github.com/teamleaderleo/duckdb/actions/runs/30654275400): **success**
- stale characterization run [`30654275393`](https://github.com/teamleaderleo/duckdb/actions/runs/30654275393): **expected red** after the mapping fix

### Superseded hardening `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`

- Main run [`30659465479`](https://github.com/teamleaderleo/duckdb/actions/runs/30659465479): **success**
- hardening run [`30659465467`](https://github.com/teamleaderleo/duckdb/actions/runs/30659465467): **failure**
- job `91251921754`
- failure localized to positive mapping controls before malformed-input controls
- stale characterization run [`30659465474`](https://github.com/teamleaderleo/duckdb/actions/runs/30659465474): **expected red**

### Repaired transform `9c6a7d4f5ccbe47a6338233954471586df271968`

- Main run [`30694147348`](https://github.com/teamleaderleo/duckdb/actions/runs/30694147348): **success**
- hardening run `30694147076`: **cancelled** by the final carrier-only artifact update
- characterization run `30694147136`: **cancelled** by the final carrier-only artifact update

Cancellation is not a test result.

### Current carrier `c8552f49b0ae1896a40296973725aae297a7671a`

- Main run [`30694359500`](https://github.com/teamleaderleo/duckdb/actions/runs/30694359500): **success**
- hardening run [`30694359081`](https://github.com/teamleaderleo/duckdb/actions/runs/30694359081): **queued** for job `91354527257` on `ubuntu-24.04`; no code conclusion yet
- stale characterization run [`30694359128`](https://github.com/teamleaderleo/duckdb/actions/runs/30694359128): **pending**; expected red if executed

Focused controls configured at the current exact head:

Positive:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. nonzero parent offset with an ignored physical prefix row.

Negative:

5. duplicate schema IDs `5,5,9`;
6. schema type-ID count mismatch;
7. runtime ID absent from the schema map;
8. negative runtime ID.

## Prior artifact correction

The retained failed-run artifact is:

- artifact ID: `8805129666`
- artifact name: `arrow-union-type-id-hardening-30659465467-1`
- ZIP size: 3,992 bytes
- ZIP SHA-256: `d1b45f44e57328b0d01009a6e7d227851d5530db18e5fa1ba992f6bd94b10f52`
- patch SHA-256: `d0d9f95690c875f6f0c370d52d4a55dcf58caa1ce4c14ae3f3fb9e5c4ce8d821`
- archive integrity test: **success**
- patch accounting: 120 insertions, 29 deletions across exactly the seven source files listed above

This corrects the mistyped ZIP hash and incorrect file/path inventory in the older verification file.

## Clean target-source branch

Planned branch: `fix/arrow-union-type-id-mapping`.

It has **not** been created. Creating it before the focused workflow runs would convert a reasoned repair into an unverified source proposal. Once run `30694359081` succeeds, download its generated-source artifact, verify hashes and the seven-file fence, create the branch directly from `2c9e51aa33dd07e928edae66304430aeb038edd7`, and commit only those seven source files.

## Draft and handoff status

- Private PR #16 body was updated at current head with the target-base correction, offset defect, exact repair, tests, receipts, and clean-branch gate.
- Existing `issue-draft.md` and `pr-draft.md` remain private packet drafts and must not be submitted publicly.
- This verification is the current continuation source for unit 14.

## Remaining blockers

1. Focused hardening run `30694359081` is queued for a hosted runner; it has not produced a pass/fail result.
2. Until that run succeeds, the generated source bundle and exact repaired patch are unavailable for final hash and scope verification.
3. The clean source-only branch must remain deferred until the focused suite and Main are green at the same exact source carrier revision.
4. After branch creation, compare the clean branch against target base and confirm only the seven expected source files differ.

## Continuation-ready handoff

Resume only unit 14 from `teamleaderleo/duckdb` branch `repair/262-arrow-union-malformed-map-controls` at exact head `c8552f49b0ae1896a40296973725aae297a7671a`.

1. Check hardening run `30694359081`, job `91354527257`.
2. If it fails, recover the exact first failing control and repair only that semantic path; do not weaken or remove the offset, duplicate-ID, malformed-count, unmapped-ID, or negative-ID controls.
3. If it succeeds, download the retained artifact and verify its digest, generation markers, patch, and seven generated source files.
4. Create `fix/arrow-union-type-id-mapping` from `2c9e51aa33dd07e928edae66304430aeb038edd7` with only the seven generated source files.
5. run ordinary Main and the focused controls against the clean branch or an exact equivalent source revision.
6. Update the packet, private drafts, PR #16, and `teamleaderleo/fieldwork#435` with exact source, clean-branch, packet, artifact, and test heads.

Public upstream remains read-only throughout continuation.
