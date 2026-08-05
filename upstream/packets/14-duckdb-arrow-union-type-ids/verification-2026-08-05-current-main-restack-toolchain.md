# Unit 14 current-main restack — mechanical and toolchain receipts

Date: 2026-08-05

## Disposition

`EXECUTED HISTORICAL SOURCE — current-main publication remains blocked before build by restack/toolchain integration`

This receipt does not weaken the historical source evidence. The clean source at `05eb977f3001be4797379df9a0a978a144ca86a0` passed all twelve focused native controls, ordinary Main, and Zizmor. The failures below concern reconstructing that source on a later DuckDB main while preserving newer generated and CMake content.

No public upstream write was made.

## Exact identities

- historical immutable base: `2c9e51aa33dd07e928edae66304430aeb038edd7`
- executed historical clean source: `05eb977f3001be4797379df9a0a978a144ca86a0`
- execution-only restack PR: `teamleaderleo/duckdb#28`
- restack branch: `exec/262-arrow-union-current-main-restack`
- current observed restack head: `eebf9eb188d7603f192566b8babe3746e5ba6163`
- restack base pinned by the workflow: `daa81697e31a3dc97a93f11220037cd2213af6cd`
- latest public source inspected during research: `043e1894425b49984c5010f253589e5d9c5fdde4`
- intended output branch: `candidate/14-arrow-union-type-id-current-main`
- output branch status at this receipt: not published

The restack base is therefore no longer the newest observed public main. Even after the current mechanical blocker is repaired, a final overlap refresh against the actual then-current main is required.

## Historical behavioral evidence retained

- focused repair run/job: `30934594107` / `92077250638` — success
- ordinary Main: `30934599818` — success
- Zizmor: `30934601489` — success
- repair artifact: `8909309475`
- repair digest: `sha256:21599bccc627362fcc702ed238152eeb2b8cd93b994b16cbd7f09eb02958232d`
- pre-fix characterization run/job: `30934009223` / `92075441520` — success
- characterization artifact: `8906058848`
- characterization digest: `sha256:e633f5b6b5d47853aa027f5ad65e90caf366a3f50e05ad62d8013812f05bebe2`
- expected negative:

```text
nested-parent-offset expected child-offset=1 actual child-offset=2 outer-offset=1
```

## Restack attempt 1 — CMake overlap

- run/job: `30948605826` / `92124739354`
- conclusion: failure in restack step
- artifact: `8913206740`
- digest: `sha256:e360f2922d56d9c2de4f9382b5de2dff5b74bae4ba0c98cb6a513d038221e3b3`

### Result

The production source and new test source were compatible. The historical `test/arrow/CMakeLists.txt` content conflicted because current main had added `arrow_output_version_buffers.cpp` after the historical clean source was produced.

No formatting, build, focused test, or publication step was reached.

### Correct repair direction

Do not apply the historical CMake file wholesale. Edit the current registration list at an exact current anchor and append only `arrow_union_type_ids.cpp`.

## Restack attempt 2 — formatter executable selection

- run/job: `30971571206` / `92196843611`
- conclusion: failure in `make generate-files`
- artifact: `8917080054`
- digest: `sha256:af1a46808a9b11cf75adef089bc1f8915a56ef309e742db7a70ae48e081128b8`

### Result

- seven human-owned files applied cleanly;
- current CMake registration was edited rather than overwritten;
- `generate-files-deps` installed `clang_format==11.0.1` in the user environment;
- `make generate-files` nevertheless invoked Ubuntu clang-format 18.1.3 and stopped on DuckDB's version guard.

No source behavior failure was reached.

## Restack attempt 3 — shell PATH assertion still insufficient

- run/job: `30975073370` / `92207294809`
- conclusion: failure in `make generate-files`
- artifact: `8917962298`
- digest: `sha256:580b0b1d2620ee3a62678506665adb8b9a7ddebca913766a3a9044961c7a905c`

### Result

The workflow explicitly:

```text
echo "$HOME/.local/bin" >> "$GITHUB_PATH"
export PATH="$HOME/.local/bin:$PATH"
test "$(command -v clang-format)" = "$HOME/.local/bin/clang-format"
clang-format --version  # 11.0.1
```

The next step repeated the `command -v` assertion successfully. All seven human-owned source/test files applied cleanly and the CMake anchor edit succeeded.

`make generate-files` still reported:

```text
you need to run `pip install clang_format==11.0.1 - ` Ubuntu clang-format version 18.1.3
```

No build or native control was reached.

## Exact root cause of attempt 3

DuckDB's `generate-files` target invokes `scripts/capi_v1_regen.sh`. That script hardcodes:

```text
python3 scripts/format.py ...
```

At startup, `scripts/format.py` prepends the directory containing `sys.executable` to `PATH`:

```text
python_bin_dir = dirname(sys.executable)
PATH = python_bin_dir + PATH
```

The workflow's `python3` is `/usr/bin/python3`. The formatter script therefore re-prepends `/usr/bin`, causing its `clang-format` subprocess to resolve `/usr/bin/clang-format` 18 even though the calling shell had selected `$HOME/.local/bin/clang-format` 11.

This is deterministic tool selection behavior, not a flaky runner or an Arrow source failure.

## Recommended mechanical repair

Use one isolated virtual environment containing both Python and all generation tools:

1. create a venv in the workflow;
2. install the declared generation dependency group into that venv;
3. prepend the venv `bin` directory to `PATH`;
4. verify `python3`, `clang-format`, `black`, `cmake-format`, and `capigen` all resolve inside the same venv;
5. run `make generate-files`;
6. retain the executable paths and versions in the receipt.

Because `capi_v1_regen.sh` calls `python3`, the venv's `python3` must be first on PATH. Then `format.py` will prepend that same venv directory, where clang-format 11 is installed.

An alternative is to change the script to use DuckDB's configured Python executable, but altering current public source solely for the execution carrier is broader and less representative than fixing the workflow environment.

## Required next gate

After the venv repair:

1. verify all human-owned files apply;
2. preserve current CMake registrations;
3. regenerate current enum output;
4. require the exact nine-file source fence;
5. require repeat generation to be clean;
6. build the debug runner;
7. run all six positive controls;
8. run all six malformed controls;
9. publish the exact tested source commit;
10. inspect the artifact and branch;
11. refresh from `daa81697...` to the actual latest public main before final review if main has advanced;
12. close the execution-only carrier without merge after evidence transfer.

## Authority

- Historical source behavior: executed and green.
- Current-main source behavior: not yet executed.
- Current blocker: generation tool environment.
- Public upstream contact: not authorized.
- Public upstream writes: none.
