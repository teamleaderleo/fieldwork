# Unit 14 — DuckDB sparse Arrow union type IDs

## Current disposition

`EXECUTED HISTORICAL UNIT SOURCE — pinned current-main restack queued. Two adjacent C API defects confirmed with separate one-file repair carriers queued.`

The unit-14 sparse-union source repair is complete and historically executed. The exact clean source passed all twelve focused controls, ordinary Main, and Zizmor. Remaining unit work is pinned current-main publication, refresh to actual latest main, complete-diff review, and delivery routing.

Two adjacent Arrow C API defects were confirmed during the deeper audit. They remain separate from unit 14's nine-file union source scope and have separate private repair carriers.

No public DuckDB issue, pull request, review, comment, reaction, or branch has been modified. Public upstream remains read-only and unauthorized for contact.

## Unit 14 assignment

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

Discriminating pre-fix evidence:

- closed carrier `teamleaderleo/duckdb#27@8cb06618d78ed76bde92f080fe6059a79219cca1`;
- run/job `30934009223` / `92075441520` — success;
- artifact `8906058848`;
- digest `sha256:e633f5b6b5d47853aa027f5ad65e90caf366a3f50e05ad62d8013812f05bebe2`;
- exact signature:

```text
nested-parent-offset expected child-offset=1 actual child-offset=2 outer-offset=1
```

The repaired source passes the same nested fixed-size-list fixture.

## Unit 14 production contract

The executed source:

- accepts schema type IDs only across `0..127`;
- maps logical type ID to physical child index through a 128-entry table;
- rejects negative, duplicate, count-mismatched, and unmapped IDs;
- rejects runtime union child-count/pointer disagreement;
- writes the mapped child index as DuckDB's union tag;
- reads the discriminant at the effective union offset;
- propagates union offsets through default, validity, dictionary, and run-end paths;
- distinguishes ordinary parent traversal from list/array nested traversal.

Executed positive controls:

1. identity IDs `0,1,2`;
2. non-sequential IDs `5,7,9`;
3. reordered IDs `2,1,0`;
4. upper-bound IDs `0,64,127`;
5. top-level nonzero sparse-union offset;
6. sparse-union offset nested in a fixed-size list.

Executed malformed controls:

1. duplicate schema ID;
2. negative schema ID;
3. schema ID-count mismatch;
4. runtime child-count mismatch;
5. unmapped runtime ID;
6. negative runtime ID.

## Unit 14 source fence

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

Execution history:

1. CMake overlap — `30948605826` / `92124739354`, artifact `8913206740`.
2. system formatter selection — `30971571206` / `92196843611`, artifact `8917080054`.
3. interpreter-directory PATH rewrite — `30975073370` / `92207294809`, artifact `8917962298`.
4. unified venv exposed missing `typos` — `31102660606` / `92619838993`, artifact `8968255091`, digest `sha256:d9a1b7365d5616d9c52d9976ed2142cba1d33197e49c78f074a35930152bd802`.
5. repository-declared tools passed, then fence accounting failed — `31103378104` / `92622266648`, artifact `8968685807`, digest `sha256:1c63e52f1ae315834dbb5326024df0d6d2803417d4e200e1f43d25ad1be05a27`.

Attempt five proved Python, clang-format 11.0.1, `typos` 1.45.1, patch application, C API generation, grammar generation, and formatting. Its apparent four-file delta was a receipt bug: `git apply --3way` staged applied files, while plain `git diff` reported only unstaged changes.

Current head repairs exact accounting with:

- `git diff --check HEAD`;
- `git diff --name-only HEAD`;
- `git diff --binary HEAD -- <expected files>`.

## Latest-main refresh classification

Newest public main observed: `7a91c3658f9411ab17556e55f9df34b3b2140f6e`, 110 commits above the pinned execution base.

Only four unit-14 fence files moved:

- generated `src/common/enum_util.cpp`;
- `src/function/table/arrow.cpp` through Identifier migration commit `3359f6bb448a65b95759add290b89ab986afed13`;
- `src/function/table/arrow_conversion.cpp` through ListView span commit `4a900ff05cbb788eca32f414548aec1ed55a6154`;
- `test/arrow/CMakeLists.txt` through ListView test registration.

The two human-source overlaps are in different functions from unit 14's union mapping and offset logic. No semantic collision is currently apparent. Final latest-main work must still regenerate enum output and preserve current CMake registrations.

## Confirmed adjacent defect 1 — projected later-column ownership

Closed private characterization:

- PR: `teamleaderleo/duckdb#29` — closed without merge;
- base/head: `58c019320e250a7b369efd756f84c6dfd68bedcb` / `b2017ce61d9c39c5faee8899bc4c50ca71a46bd0`;
- focused run/job: `31102985877` / `92620944568` — success;
- artifact: `8969221973`;
- digest: `sha256:036913d4415c1473c7f1a66ebf582330f59c58f4b9e54c9f49db2db698e3861d`.

The existing C API Arrow conversion control passed. The expected-negative reproduced exactly:

```text
root release count after source chunk destroy=1
surviving second output=-9999,-9999,-9999
```

Diagnosis: only column zero's copied root wrapper carries the real release callback. A later-column alias can outlive the source chunk while retaining only a no-op wrapper. Destroying the source chunk releases the Arrow root and invalidates the surviving column.

### Focused repair 1 — one shared root owner

- PR: `teamleaderleo/duckdb#32`
- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `35ceeae91aa02eef76cbd737dfbd68b26f17ba5e`
- focused run: `31106146125` — queued
- ordinary Main: `31106148007` — queued
- carrier fence: one workflow, one generator, CMake registration, one regression test
- generated production fence: exactly `src/main/capi/arrow-c.cpp`.

The repair creates one shared `ArrowArrayWrapper` before the column loop and assigns the same owner to every column state. It intentionally preserves current consume-on-error behavior; transactional failure ownership remains separate.

## Confirmed adjacent defect 2 — runtime root child count ignored

Closed private characterization:

- PR: `teamleaderleo/duckdb#30` — closed without merge;
- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `41c76c97cdcbf5fbd6ecfc7b1f130b4f853166af`;
- ordinary Main: `31103829101` — success;
- focused run/job: `31103828472` / `92623801218`;
- artifact: `8969719861`;
- digest: `sha256:a81a04c00cd838b13b321e44545ee820eae57ff3414220373f3781453d0e5876`.

The focused workflow's grep missed only because Catch wrapped the diagnostic. The retained artifact proves DuckDB accepted a runtime root declaring one child and returned two columns:

```text
CHECK( error != nullptr )
with expansion:
  nullptr != nullptr
with message:
  declared runtime child count=1 accepted=1 output columns=2 second output=21,
  22
```

### Focused repair 2 — validate count before conversion

- PR: `teamleaderleo/duckdb#33`
- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `d96e1053801c5f8514e21c17a51c5a93dd1f345d`
- focused run: `31107012002` — queued
- ordinary Main: `31107013196` — queued
- generated production fence: exactly `src/main/capi/arrow-c.cpp`.

The repair:

1. initializes `*out_chunk = nullptr`;
2. compares runtime child count with converted-schema column count;
3. rejects disagreement before allocation, ownership transfer, or child dereference;
4. returns stable invalid-input text;
5. leaves caller ownership intact on validation failure.

## Active conformance characterization — null optional field name

- PR: `teamleaderleo/duckdb#31`
- base/head: `7a91c3658f9411ab17556e55f9df34b3b2140f6e` / `301993f1832aa66f05edf210b1bef3fd36f16848`
- ordinary Main: `31105521009` — success
- focused run: `31105519352` — queued
- expected-negative:

```text
empty field name accepted=1 null field name accepted=0
```

## Follow-on research

The current index is [`research/README.md`](research/README.md). Eighteen lanes are preserved, including dense unions, validation levels, reference interoperability, stream repeatability, coordinate systems, pushdown, lifetimes, metadata, encoded layouts, extensions, two confirmed C API defects, stream errors, failure ownership, transactional shared-root design, null field names, and C ABI exception containment.

Failure-atomic ownership remains explicitly separate. The stable C API describes ownership moving to the returned `DataChunk`, while current conversion may consume the root before returning an error with no chunk. The preferred full model is validation first, one disarmed shared owner during conversion, and release-callback commit only after complete success.

Several pre-conversion operations also sit outside the current conversion catch block, including negative-length casts, chunk initialization, metadata lookup, state allocation, and child-table dereference. The next focused characterization should test negative root length and confirm whether an exception escapes the C ABI.

## Remaining work

1. observe unit-14 restack run `31104694815`;
2. inspect the exact artifact and nine-file candidate after success;
3. refresh the tested unit-14 source onto actual latest main and rerun all gates and twelve controls;
4. inspect repair PR #32 and publish a clean source-only candidate after focused green;
5. inspect repair PR #33 and publish a clean source-only candidate after focused green;
6. resolve PR #31, preserving exact receipt and closing without merge;
7. characterize negative-length exception containment;
8. characterize failure-atomic ownership before broadening either C API repair;
9. classify complete latest-main diffs and obtain peer review;
10. route accepted source through Fieldwork review/delivery desks;
11. keep public filing separately unauthorized.

## Continuation

- unit 14: `teamleaderleo/duckdb#28@37990d09f8493fe3bcca05f81aa8fd2b806c6205`, run `31104694815`;
- shared-root repair: `teamleaderleo/duckdb#32@35ceeae91aa02eef76cbd737dfbd68b26f17ba5e`, run `31106146125`;
- child-count repair: `teamleaderleo/duckdb#33@d96e1053801c5f8514e21c17a51c5a93dd1f345d`, run `31107012002`;
- null-name characterization: `teamleaderleo/duckdb#31@301993f1832aa66f05edf210b1bef3fd36f16848`, run `31105519352`.

Do not merge any execution, repair, or characterization carrier. Do not contact public upstream.
