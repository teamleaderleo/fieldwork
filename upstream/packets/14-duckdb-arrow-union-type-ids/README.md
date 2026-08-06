# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`EXECUTED HISTORICAL SOURCE — pinned current-main restack has cleared tool installation and generation; exact nine-file fence accounting repaired; run 31104694815 queued`

The unit-14 source repair is complete and historically executed. The exact clean source passed all twelve focused controls, ordinary Main, and Zizmor. Remaining unit work is current-main publication, refresh to actual latest main, complete-diff review, and delivery routing.

No public DuckDB issue, pull request, review, comment, reaction, or branch has been modified. Public upstream remains read-only and unauthorized for contact.

## Assignment

- unit: `14`
- target: DuckDB
- contribution: `fix(arrow): map sparse union type IDs to child indices`
- owner record: [`teamleaderleo/linux-fieldwork#262`](https://github.com/teamleaderleo/linux-fieldwork/issues/262)
- coordination issue: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- packet branch: `p0/435-unit-14-duckdb-arrow-union-type-ids`

## Executed historical source

- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- passing parent: `teamleaderleo/duckdb#14@c962ece64c1356015aef15a37c0cc636f63b376b`
- repair carrier: `teamleaderleo/duckdb#16@c8a62c8c1d9c6516ecf495f749e65d1ddc150647`
- clean source: `fix/arrow-union-type-id-mapping@05eb977f3001be4797379df9a0a978a144ca86a0`
- focused run/job: `30934594107` / `92077250638` — success
- ordinary Main: `30934599818` — success
- Zizmor: `30934601489` — success
- artifact: `8909309475`
- digest: `sha256:21599bccc627362fcc702ed238152eeb2b8cd93b994b16cbd7f09eb02958232d`

## Discriminating pre-fix evidence

- carrier: closed `teamleaderleo/duckdb#27@8cb06618d78ed76bde92f080fe6059a79219cca1`
- run/job: `30934009223` / `92075441520` — success
- artifact: `8906058848`
- digest: `sha256:e633f5b6b5d47853aa027f5ad65e90caf366a3f50e05ad62d8013812f05bebe2`
- signature:

```text
nested-parent-offset expected child-offset=1 actual child-offset=2 outer-offset=1
```

The repaired source passes the same nested fixed-size-list fixture.

## Production contract

The executed source:

- accepts schema type IDs only across `0..127`;
- maps logical type ID to physical child index through a 128-entry table;
- rejects negative, duplicate, count-mismatched, and unmapped IDs;
- rejects runtime union child-count/pointer disagreement;
- writes the mapped child index as DuckDB's union tag;
- reads the discriminant at the effective union offset;
- propagates union offsets through default, validity, dictionary, and run-end paths;
- distinguishes ordinary `array.offset + parent_offset` traversal from list/array nested traversal.

## Executed controls

Positive:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. upper-bound IDs `0,64,127`;
5. top-level nonzero sparse-union offset;
6. sparse-union offset nested in a fixed-size list.

Malformed:

1. duplicate schema ID;
2. negative schema ID;
3. schema ID-count mismatch;
4. runtime child-count mismatch;
5. unmapped runtime ID;
6. negative runtime ID.

## Source fence

The historical clean commit contains exactly nine target files:

1. `src/common/enum_util.cpp`
2. `src/function/table/arrow.cpp`
3. `src/function/table/arrow/arrow_duck_schema.cpp`
4. `src/function/table/arrow/arrow_type_info.cpp`
5. `src/function/table/arrow_conversion.cpp`
6. `src/include/duckdb/function/table/arrow/arrow_type_info.hpp`
7. `src/include/duckdb/function/table/arrow/enum/arrow_type_info_type.hpp`
8. `test/arrow/CMakeLists.txt`
9. `test/arrow/arrow_union_type_ids.cpp`

## Pinned current-main execution

Execution-only carrier:

- PR: `teamleaderleo/duckdb#28`
- branch: `exec/262-arrow-union-current-main-restack`
- current head: `37990d09f8493fe3bcca05f81aa8fd2b806c6205`
- pinned base: `daa81697e31a3dc97a93f11220037cd2213af6cd`
- current run: `31104694815` — queued
- intended output: `candidate/14-arrow-union-type-id-current-main`
- output status: not published

### Attempt history

1. **CMake overlap** — run/job `30948605826` / `92124739354`; artifact `8913206740`; current source added `arrow_output_version_buffers.cpp`.
2. **Formatter selection** — `30971571206` / `92196843611`; artifact `8917080054`; generation selected clang-format 18.
3. **Interpreter-directory PATH rewrite** — `30975073370` / `92207294809`; artifact `8917962298`; `capi_v1_regen.sh` used `/usr/bin/python3`, whose directory displaced the pinned formatter.
4. **Unified venv** — `31102660606` / `92619838993`; artifact `8968255091`; Python and clang-format were correct, exposing missing `typos`.
5. **Repository-declared tools** — `31103378104` / `92622266648`; artifact `8968685807`; Python, clang-format 11.0.1, `typos` 1.45.1, patch application, generation, grammar, and formatting all succeeded.

Attempt five then failed at exact-file accounting. The apparent four-file delta was not source absorption: `git apply --3way` staged applied files, while the workflow used plain `git diff`, which reports only unstaged changes. Five files remained staged and disappeared from the count; four files touched by later generation/formatting appeared as unstaged.

Current head `37990d09...` repairs the receipt and fence by using:

- `git diff --check HEAD`;
- `git diff --name-only HEAD`;
- `git diff --binary HEAD -- <expected files>`.

This captures staged and unstaged content and generates the complete nine-file patch.

## Latest-main refresh classification

Newest public main observed: `7a91c3658f9411ab17556e55f9df34b3b2140f6e`, 110 commits above the pinned execution base.

Only four unit-14 fence files moved in that range:

- `src/common/enum_util.cpp` — generated output;
- `src/function/table/arrow.cpp` — table-function bind names changed from strings to `Identifier` in commit `3359f6bb448a65b95759add290b89ab986afed13`;
- `src/function/table/arrow_conversion.cpp` — ListView physical child-span calculation changed in `4a900ff05cbb788eca32f414548aec1ed55a6154`;
- `test/arrow/CMakeLists.txt` — ListView test registration added.

The two human-source overlaps are in different functions/regions from unit 14's union mapping and offset logic. No semantic conflict is currently apparent. Generated enum output must still be regenerated, and current CMake registrations must be preserved.

## Follow-on research

The current index is [`research/README.md`](research/README.md). Fifteen lanes are preserved, including dense unions, validation levels, reference interoperability, stream repeatability, coordinate systems, pushdown capabilities, lifetimes, metadata framing, encoded layouts, extensions, projected-column ownership, stream error detail, schema/array agreement, dictionary-cache closure, and failure-atomic C API ownership.

### Active characterization PR #29

- title: `[CHARACTERIZATION] C API Arrow projected-column root ownership`
- base: `58c019320e250a7b369efd756f84c6dfd68bedcb`
- head: `b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`
- focused run/job: `31102985877` / `92620944568` — building

The fixture keeps a reference to column two, destroys the source chunk, and poisons column two when the root release callback fires. Expected-negative signature:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

### Active characterization PR #30

- title: `[CHARACTERIZATION] C API Arrow schema-array child-count agreement`
- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `41c76c97cdcbf5fbd6ecfc7b1f130b4f853166af`
- ordinary Main: `31103829101` — success
- focused run: `31103828472` — queued

The runtime root declares one child while a two-field converted schema and a padded two-pointer allocation are supplied. Expected-negative signature:

```text
declared runtime child count=1 accepted=1 output columns=2 second output=21,22
```

### Failure-atomic ownership

The C API documentation says Arrow ownership moves to the returned `DataChunk`, but conversion currently nulls the caller's release callback before all columns succeed. The preferred coherent model is:

1. validate root structure before transfer;
2. use one shared root wrapper for every output alias;
3. borrow with wrapper `release = nullptr` during conversion;
4. after every column succeeds, move the original release callback into that shared wrapper and null the caller;
5. on error, destroy temporary vectors without consuming the caller's array.

The detailed matrix is in [`research/arrow-capi-failure-ownership.md`](research/arrow-capi-failure-ownership.md).

## Remaining work

1. observe restack run `31104694815`;
2. repair only its first demonstrated failure, if any;
3. inspect the exact artifact and nine-file candidate after success;
4. refresh the tested source onto actual latest main and rerun all gates and twelve controls;
5. classify the complete latest-main diff and obtain peer review;
6. resolve PRs #29 and #30, preserving exact receipts and closing without merge;
7. route accepted unit-14 source through Fieldwork review/delivery desks;
8. keep public filing separately unauthorized.

## Continuation

Resume unit 14 from `teamleaderleo/duckdb#28@37990d09f8493fe3bcca05f81aa8fd2b806c6205`, run `31104694815`.

Resume projected ownership from `teamleaderleo/duckdb#29@b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`, run `31102985877`.

Resume schema/array agreement from `teamleaderleo/duckdb#30@41c76c97cdcbf5fbd6ecfc7b1f130b4f853166af`, run `31103828472`.

Do not merge any execution or characterization carrier. Do not contact public upstream.
