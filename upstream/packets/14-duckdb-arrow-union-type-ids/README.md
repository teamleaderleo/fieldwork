# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`EXECUTED HISTORICAL SOURCE — pinned current-main execution path repaired through declared generation tools; run 31103378104 queued; final latest-main refresh still required`

Unit 14's focused source repair is complete and executed. The historical clean source passed all twelve native controls, ordinary Main, and Zizmor. Remaining unit work is mechanical current-main reconstruction, exact-source publication, complete-diff review, and delivery routing.

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
- current carrier head: `60b540592bdc8ef01cd7d28371bf039d691ffe62`
- pinned workflow base: `daa81697e31a3dc97a93f11220037cd2213af6cd`
- newest public main observed: `7a91c3658f9411ab17556e55f9df34b3b2140f6e`
- intended output: `candidate/14-arrow-union-type-id-current-main`
- output status: not published
- current run: `31103378104` — queued

The pinned base is behind latest main. The pinned workflow must prove the mechanical source-generation and test path first; then the same source must be refreshed onto actual latest main and rerun before review.

### Attempt 1 — CMake overlap

- run/job: `30948605826` / `92124739354`
- artifact: `8913206740`
- digest: `sha256:e360f2922d56d9c2de4f9382b5de2dff5b74bae4ba0c98cb6a513d038221e3b3`
- source applied; historical CMake conflicted with the newer `arrow_output_version_buffers.cpp` registration.

### Attempt 2 — formatter selection

- run/job: `30971571206` / `92196843611`
- artifact: `8917080054`
- digest: `sha256:af1a46808a9b11cf75adef089bc1f8915a56ef309e742db7a70ae48e081128b8`
- `make generate-files` selected system clang-format 18 instead of installed 11.

### Attempt 3 — shell PATH insufficient

- run/job: `30975073370` / `92207294809`
- artifact: `8917962298`
- digest: `sha256:580b0b1d2620ee3a62678506665adb8b9a7ddebca913766a3a9044961c7a905c`
- `capi_v1_regen.sh` hardcoded `python3`; `format.py` prepended that interpreter's directory and restored `/usr/bin/clang-format` 18.

### Attempt 4 — unified venv exposed missing declared spell tool

- carrier head: `40b88981ca27c23806941e13d764a4d25352f632`
- run/job: `31102660606` / `92619838993`
- artifact: `8968255091`
- digest: `sha256:d9a1b7365d5616d9c52d9976ed2142cba1d33197e49c78f074a35930152bd802`
- one venv correctly supplied Python 3.12 and clang-format 11.0.1;
- generation reached header formatting and then failed because `typos` was absent;
- this is repository tooling, not source behavior.

### Attempt 5 — repository-declared toolchain

Current carrier `60b540592bdc8ef01cd7d28371bf039d691ffe62` additionally invokes DuckDB's own `make spell_tools`, pinned by the repository to `typos` 1.45.1. Run `31103378104` is the current authority.

No current-main attempt has yet reached source gates, compilation, focused controls, or publication.

The earlier environment receipt is [`verification-2026-08-05-current-main-restack-toolchain.md`](verification-2026-08-05-current-main-restack-toolchain.md). It should be supplemented with attempt-four and attempt-five evidence after the current run resolves.

## Follow-on DuckDB research

The research index is [`research/README.md`](research/README.md).

Fourteen preserved lanes cover:

1. dense-union ingestion;
2. Arrow C Data validation hardening;
3. reference-consumer interoperability;
4. `arrow_scan` repeatability and one-shot stream semantics;
5. logical-versus-physical coordinate systems;
6. provider- and predicate-specific pushdown capabilities;
7. stream/schema/array/context lifetime and release ownership;
8. metadata framing and bounded parsing;
9. dictionary/REE/list/view/array/union encoded-layout invariants;
10. Arrow extension identity, storage, callback, and schema/appender contracts;
11. C API projected later-column root ownership;
12. Arrow C Stream null-detail and error preservation;
13. C API schema/array structural agreement;
14. dictionary cache identity, audited and closed as a defect avenue for conforming producers.

### Active private characterization

- PR: `teamleaderleo/duckdb#29`
- title: `[CHARACTERIZATION] C API Arrow projected-column root ownership`
- exact base: `58c019320e250a7b369efd756f84c6dfd68bedcb`
- current head: `b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`
- focused run: `31102985877` — queued
- ordinary Main: `31102986494` — queued
- changed-files fence: exactly one workflow, CMake registration, and one focused C API test.

The original broad early-release hypothesis was corrected. Generic conversion retains each per-column wrapper through vector auxiliary data. The refined expected-negative checks whether a reference to column two survives destruction of the original source chunk, given that only column zero's wrapper appears to carry the actual root release callback.

Expected defect signature:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

Do not call this defect confirmed until the exact-head run reproduces both lines. The characterization carrier must close without merge after evidence transfer.

### Strong structural candidate

`duckdb_data_chunk_from_arrow` does not first prove that the runtime root array agrees with the converted schema's child count and required pointers before dereferencing children. The deterministic fixture plan is in [`research/arrow-capi-schema-array-agreement.md`](research/arrow-capi-schema-array-agreement.md).

### Stream error candidate

Arrow permits `get_last_error` to return null. DuckDB currently constructs a string directly from that optional pointer after callback failures. The null-safe error-preservation matrix is in [`research/arrow-stream-error-contracts.md`](research/arrow-stream-error-contracts.md).

The broad routing sweep remains in [`adjacent-duckdb-arrow-research-2026-08-05.md`](adjacent-duckdb-arrow-research-2026-08-05.md).

These notes do not expand unit 14's source scope or claim new numbered units.

## Remaining work

1. observe pinned restack run `31103378104`;
2. repair only its first demonstrated mechanical failure, if any;
3. verify source gates, debug build, all twelve controls, exact artifact, and nine-file publication;
4. refresh the exact tested source from pinned `daa81697...` to actual latest public main;
5. rerun generation, source gates, build, and all twelve controls on that refreshed base;
6. classify every overlapping change and obtain complete-diff peer review;
7. resolve characterization PR #29 and preserve its receipt;
8. characterize C API schema/array disagreement next if #29 is disproven or completed;
9. route accepted unit-14 source through Fieldwork review/delivery desks;
10. keep public filing separately unauthorized.

## Continuation

Resume unit 14 from `teamleaderleo/duckdb#28@60b540592bdc8ef01cd7d28371bf039d691ffe62`, run `31103378104`.

Resume projected-column ownership characterization from `teamleaderleo/duckdb#29@b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`, focused run `31102985877`.

Do not merge either execution carrier. If the pinned restack succeeds, inspect its artifact and exact published candidate before refreshing to latest main. If PR #29's focused workflow succeeds, that means the expected-negative reproduced; inspect the exact logs and release-count artifact before designing any repair.
