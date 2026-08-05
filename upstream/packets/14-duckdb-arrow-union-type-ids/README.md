# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`EXECUTED HISTORICAL SOURCE — current-main publication blocked before build by generation-tool environment; pinned restack base is behind latest inspected main`

Unit 14's focused source repair is complete and executed. The exact historical clean source passed all twelve native controls, ordinary Main, and Zizmor. The remaining work is current-main reconstruction, fresh complete-diff review, and delivery routing.

The current-main carrier has not reached compilation. Its latest failure is a deterministic DuckDB generation-environment problem, not an Arrow source or test failure.

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

The repair passes the same nested fixed-size-list fixture, proving that the control distinguishes the actual offset-propagation defect.

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

All twelve controls passed at the exact repair head.

## Historical clean source fence

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

Execution-only carrier:

- PR: `teamleaderleo/duckdb#28`
- branch: `exec/262-arrow-union-current-main-restack`
- current observed PR head: `eebf9eb188d7603f192566b8babe3746e5ba6163`
- workflow base: `daa81697e31a3dc97a93f11220037cd2213af6cd`
- intended output: `candidate/14-arrow-union-type-id-current-main`
- output status: not published
- newest public source inspected during this research: `043e1894425b49984c5010f253589e5d9c5fdde4`

The restack base is already behind the newest inspected main. A final current-main refresh remains required after the mechanical execution path is green.

### Attempt 1 — CMake overlap

- run/job: `30948605826` / `92124739354`
- artifact: `8913206740`
- digest: `sha256:e360f2922d56d9c2de4f9382b5de2dff5b74bae4ba0c98cb6a513d038221e3b3`
- result: source compatible; historical CMake file conflicted with current `arrow_output_version_buffers.cpp` registration.

### Attempt 2 — formatter selection

- run/job: `30971571206` / `92196843611`
- artifact: `8917080054`
- digest: `sha256:af1a46808a9b11cf75adef089bc1f8915a56ef309e742db7a70ae48e081128b8`
- result: seven human-owned files applied and current CMake was edited; `make generate-files` selected system clang-format 18 instead of installed 11.

### Attempt 3 — shell PATH alone was insufficient

- run/job: `30975073370` / `92207294809`
- artifact: `8917962298`
- digest: `sha256:580b0b1d2620ee3a62678506665adb8b9a7ddebca913766a3a9044961c7a905c`
- result: shell assertions proved `$HOME/.local/bin/clang-format` 11.0.1 was selected, but `scripts/capi_v1_regen.sh` hardcoded `python3 scripts/format.py`. `format.py` prepended the `/usr/bin/python3` executable directory to PATH and consequently selected `/usr/bin/clang-format` 18.

No attempt reached formatting gates, build, focused controls, or source publication.

The exact receipt and recommended venv repair are in [`verification-2026-08-05-current-main-restack-toolchain.md`](verification-2026-08-05-current-main-restack-toolchain.md).

## Follow-on DuckDB research

The research index is [`research/README.md`](research/README.md).

Ten preserved lanes now cover:

1. dense-union ingestion;
2. Arrow C Data validation hardening;
3. reference-producer/reference-consumer interoperability;
4. `arrow_scan` repeatability and one-shot stream semantics;
5. logical-versus-physical coordinate systems;
6. provider- and predicate-specific pushdown capabilities;
7. stream/schema/array/context lifetime and release ownership;
8. metadata framing and bounded parsing;
9. dictionary/REE/list/view/array/union encoded-layout invariants;
10. Arrow extension identity, storage, callback, and schema/appender contracts.

The earlier routing sweep remains in [`adjacent-duckdb-arrow-research-2026-08-05.md`](adjacent-duckdb-arrow-research-2026-08-05.md).

These notes do not expand unit 14's source scope or claim new numbered units.

## Remaining work

1. repair the execution environment with one venv containing Python and all declared generation tools;
2. verify generated source and current CMake registration are stable;
3. build and rerun all twelve controls;
4. publish and inspect the exact nine-file tested current-main source;
5. refresh the restack from `daa81697...` to the actual latest public main;
6. classify every overlapping change;
7. obtain fresh complete-diff peer review;
8. route accepted source through Fieldwork review/delivery desks;
9. keep public filing separately unauthorized.

## Continuation

Resume from `teamleaderleo/duckdb#28@eebf9eb188d7603f192566b8babe3746e5ba6163` and the latest failed run `30975073370`.

Use a virtual environment whose `bin` contains both `python3` and `clang-format` 11.0.1, so `scripts/format.py` prepends the same environment rather than `/usr/bin`. Repair only that demonstrated execution blocker first. Once the pinned-base workflow is green, restack the exact tested source on the actual latest main and repeat the source gates and twelve controls before review.
