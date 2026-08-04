# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`EXECUTED — historical clean source passed all 12 native controls; current-main restack is queued`

Unit 14's focused source repair is no longer waiting on its original CI gate. The exact historical clean source has been published and validated. A separate execution-only carrier is now restacking that source on exact current DuckDB main so generated enum output is regenerated rather than overwritten.

No public DuckDB issue, pull request, review, comment, reaction, or branch has been modified. Public upstream remains read-only and unauthorized for contact.

## Assignment

- unit: `14`
- target: DuckDB
- contribution: `fix(arrow): map sparse union type IDs to child indices`
- owner record: [`teamleaderleo/linux-fieldwork#262`](https://github.com/teamleaderleo/linux-fieldwork/issues/262)
- coordination issue: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- packet branch: `p0/435-unit-14-duckdb-arrow-union-type-ids`

## Executed historical source

- immutable target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- passing parent candidate: `teamleaderleo/duckdb#14@c962ece64c1356015aef15a37c0cc636f63b376b`
- executed repair carrier: `teamleaderleo/duckdb#16@c8a62c8c1d9c6516ecf495f749e65d1ddc150647`
- clean source branch/head: `fix/arrow-union-type-id-mapping@05eb977f3001be4797379df9a0a978a144ca86a0`
- focused repair run/job: `30934594107` / `92077250638` — success
- ordinary Main: `30934599818` — success
- Zizmor: `30934601489` — success
- repair artifact: `8909309475`
- repair digest: `sha256:21599bccc627362fcc702ed238152eeb2b8cd93b994b16cbd7f09eb02958232d`

## Discriminating pre-fix characterization

- expected-negative carrier: closed `teamleaderleo/duckdb#27@8cb06618d78ed76bde92f080fe6059a79219cca1`
- run/job: `30934009223` / `92075441520` — success
- artifact: `8906058848`
- digest: `sha256:e633f5b6b5d47853aa027f5ad65e90caf366a3f50e05ad62d8013812f05bebe2`
- retained signature:

```text
nested-parent-offset expected child-offset=1 actual child-offset=2 outer-offset=1
```

The repair passes the same nested fixed-size-list fixture, proving that the test distinguishes the actual offset-propagation defect.

## Correct production contract

The executed source:

- accepts Arrow union schema type codes only across `0..127`;
- creates a 128-entry logical type-ID-to-child-index map;
- rejects negative, duplicate, count-mismatched, and unmapped IDs before unsafe indexing;
- rejects runtime array/schema child-count and child-pointer disagreement;
- writes the mapped child index as DuckDB's union tag;
- reads the type-ID buffer at the union's effective logical offset;
- propagates the union offset to child validity, default, dictionary, and run-end conversion;
- uses `array.offset + parent_offset` for ordinary parent traversal;
- uses `array.offset + nested_offset` when reached through list/array nested traversal, avoiding double application.

## Executed controls

### Positive

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. upper-bound IDs `0,64,127`;
5. top-level sparse-union offset over an ignored physical prefix;
6. sparse-union offset while nested in a fixed-size list.

### Malformed

1. duplicate schema ID;
2. negative schema ID;
3. schema type-ID count mismatch;
4. runtime array/schema child-count mismatch;
5. unmapped nonnegative runtime ID;
6. negative runtime type-ID value.

All 12 controls passed at the exact repair head.

## Clean source fence

Exactly nine target-source files:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`
8. `test/arrow/CMakeLists.txt`
9. `test/arrow/arrow_union_type_ids.cpp`

The clean branch contains no Fieldwork workflow, generator, dependency, lock, or unrelated source files.

## Current-main reconciliation

Public main observed at `daa81697e31a3dc97a93f11220037cd2213af6cd` has newer generated `src/common/enum_util.cpp` content. Blindly cherry-picking the historical nine-file source would overwrite unrelated current enum entries.

Execution-only current-main carrier:

- PR: `teamleaderleo/duckdb#28`
- carrier head: `00bd1d019cf2069e2864781ac61ab4db59405040`
- run: `30948605826` — queued
- output branch: `candidate/14-arrow-union-type-id-current-main`

The workflow applies only the eight human-owned source/test files, regenerates enum output on exact current main, verifies the nine-file fence and generation stability, runs all 12 controls, and pushes the exact tested source commit. The carrier must close without merge after evidence transfer.

## Follow-on DuckDB research

The research index is [`research/README.md`](research/README.md).

Preserved lanes:

- dense-union ingestion;
- Arrow C Data validation hardening;
- reference-producer/reference-consumer interoperability;
- `arrow_scan` repeatability and one-shot stream semantics;
- logical-versus-physical coordinate-system auditing.

The earlier routing sweep remains in [`adjacent-duckdb-arrow-research-2026-08-05.md`](adjacent-duckdb-arrow-research-2026-08-05.md).

These notes do not expand unit 14's source scope or claim new numbered units.

## Remaining work

1. observe current-main restack run `30948605826`;
2. verify the published current-main candidate is exactly nine files and the exact tested SHA;
3. compare all overlapping current-main changes and classify them;
4. obtain fresh complete-diff peer review;
5. route accepted source through Fieldwork review/delivery desks;
6. keep public filing separately unauthorized.

## Continuation

Resume from `teamleaderleo/duckdb#28@00bd1d019cf2069e2864781ac61ab4db59405040` and run `30948605826`. If the workflow fails, repair only the first demonstrated current-main reconciliation failure. If it passes, verify the artifact and `candidate/14-arrow-union-type-id-current-main`, update this packet with the exact tested source head, and close the execution-only carrier without merge.
