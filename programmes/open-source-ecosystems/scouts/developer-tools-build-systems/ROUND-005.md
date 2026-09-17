# Developer tools and build systems — Round 005

Snapshot: 2026-08-03  
Programme: [`open-source-ecosystems`](../../README.md) / issue [`#207`](https://github.com/teamleaderleo/fieldwork/issues/207)  
Scout lane: [`#210`](https://github.com/teamleaderleo/fieldwork/issues/210)  
Fieldwork base: `main` at `d82277ce8b170faeeeb3e74809f5ab8bf902d232`  
Public upstream contact: **none; unauthorized**

## In simple words

This round reviewed four reports against current source, current tests, current ownership, and four owned forks.

Two reports have bounded local implementation candidates:

1. **Meson #16046** — source introspection ignores a project option value that has already been loaded, then serializes the unresolved value as a fake dependency named `unknown`.
2. **ShellCheck #3263** — the first Bats false positive is caused by an artificial `export foo=value` reference being checked before the same command's replacement assignment.

Two reports should not receive speculative production changes yet:

3. **uv #20871** — current source does not reuse the surrounding project environment; ambient Python import variables remain the leading explanation and a local matrix now distinguishes that from a real environment-selection defect.
4. **Cargo #16574** — current tests explicitly expect the original git source to be fetched for a patched dependency, and the issue is marked `S-needs-design`; a failing contract test and design checklist are prepared, but production code is held.

All work is on owned forks and the Fieldwork repository. No issue comment, reaction, claim, pull request, email, or other target-project contact was made.

## Exact source and fork state

| Target | Inspected upstream revision | Owned branch | Current packet head | Evidence state |
| --- | --- | --- | --- | --- |
| Meson | [`0b5b32e284709eb5b23ed30207fe978362d30a3d`](https://github.com/mesonbuild/meson/commit/0b5b32e284709eb5b23ed30207fe978362d30a3d) | [`fieldwork/16046-source-option-dependency`](https://github.com/teamleaderleo/meson/tree/fieldwork/16046-source-option-dependency) | `4a53c7ff7972252595e1021f85ed41283e7a75bb` | source-reviewed; target-test-prepared |
| ShellCheck | [`9af7ee28ce587baadd950b85dd6826a16b9c068d`](https://github.com/koalaman/shellcheck/commit/9af7ee28ce587baadd950b85dd6826a16b9c068d) | [`fieldwork/3263-bats-synthetic-export-read`](https://github.com/teamleaderleo/shellcheck/tree/fieldwork/3263-bats-synthetic-export-read) | `520bb0d22e49d5f7a3d77db60b499dd46d1e4f15` | source-reviewed; target-test-prepared |
| uv | [`79bbface771210df216b738e9bdc7df95e5a9e6b`](https://github.com/astral-sh/uv/commit/79bbface771210df216b738e9bdc7df95e5a9e6b) | [`fieldwork/20871-uvx-environment-isolation`](https://github.com/teamleaderleo/uv/tree/fieldwork/20871-uvx-environment-isolation) | `1dc19a15a89f315ac2dcce1c867f1c04bb79d88d` | source-reviewed; reproducer-prepared |
| Cargo | [`614ec56f126eb6925f19ba538d6ecda2ef333a9c`](https://github.com/rust-lang/cargo/commit/614ec56f126eb6925f19ba538d6ecda2ef333a9c) | [`fieldwork/16574-patch-source-fetch`](https://github.com/teamleaderleo/cargo/tree/fieldwork/16574-patch-source-fetch) | `683ee83e4e2215d227a930d1b8dbdba78d8a373c` | source-and-test-reviewed; failing-test-prepared; design hold |

The Meson, ShellCheck, and Cargo fork bases matched the inspected upstream heads. The uv default fork head was 34 commits behind current upstream; the Fieldwork branch was therefore created directly at exact upstream commit `79bbface...` rather than analyzing the stale default head.

No test result is claimed below. The environment could read and write through the GitHub connector but could not resolve `github.com` or `api.github.com` from the execution container, so target-native commands could not be run locally. Prepared tests remain evidence level `target-test-prepared` or `reproducer-prepared` until fork CI or a capable runner executes them.

## Ownership and overlap refresh

| Target | Upstream state at snapshot | Overlap conclusion |
| --- | --- | --- |
| [Meson #16046](https://github.com/mesonbuild/meson/issues/16046) | open, unassigned, no comments; no matching repair PR found | locally actionable candidate; refresh again before any external proposal |
| [ShellCheck #3263](https://github.com/koalaman/shellcheck/issues/3263) | open, unassigned; one later reproducer in the same issue; no matching repair PR found | original case locally actionable; later source/include case is separate and not claimed fixed |
| [uv #20871](https://github.com/astral-sh/uv/issues/20871) | open with `needs-mre`; maintainer reports trivial reproduction does not fail and asks about `PYTHONPATH` and the Python executable; no matching repair PR found | experiment first; no production candidate until environment source is identified |
| [Cargo #16574](https://github.com/rust-lang/cargo/issues/16574) | open, unassigned, labeled `S-needs-design`; no matching accepted implementation found | design hold; current contribution rules reject implementation-first work on unaccepted issues |

A dated overlap check does not reserve any target. Recheck issue assignment, comments, linked commits, and pull requests immediately before implementation promotion or any separately authorized upstream interaction.

## Meson #16046 — option-derived dependency becomes `unknown`

### Reported consequence

Packaging automation consumes `meson introspect --dependencies meson.build`. For a build file that does:

```meson
logind = get_option('logind')
dependency(logind, version: '>= 209')
```

source introspection emits a dependency object whose name is literally `unknown`. Downstream tools can convert that fabricated name into invalid package requirements.

### Source map and verified mechanism

- `mesonbuild/ast/introspection.py`
  - `IntrospectionInterpreter` maps `dependency()` to `func_dependency()`.
  - `func_project()` calls `_load_option_file()` before later project statements are analyzed.
  - it does not override the base `get_option()` behavior.
- `mesonbuild/ast/interpreter.py`
  - base `AstInterpreter` maps `get_option` to `func_do_nothing()`.
  - `func_do_nothing()` produces `UnknownValue`.
  - `IntrospectionDependency.name` explicitly permits `UnknownValue`.
- `mesonbuild/mintro.py`
  - `IntrospectionEncoder` serializes every `UnknownValue` as the JSON string `"unknown"`.
  - `list_deps_from_source()` emits dependency names without distinguishing a real package named `unknown` from an unresolved expression.
- the normal build interpreter resolves an `OptionKey` through `coredata.optstore`; source introspection already has the same option-file defaults available.

### Candidate

The fork packet contains an apply-ready patch that maps `get_option` to a narrow source-only resolver. It accepts one literal option name, uses the current subproject key, and returns only primitive JSON-safe values. Dynamic names, missing options, feature wrappers, and unsupported structured values remain unresolved.

This candidate is intentionally smaller than copying the full normal-interpreter method. Source introspection must not pretend to configure a build, and it does not yet implement feature-option method calls.

### Test matrix

- combo/string default used directly as a dependency name;
- explicit source-introspection option override, if supported by the command interface;
- literal dependency control;
- dynamic option name control;
- missing option control;
- subproject option key control;
- feature option remains safely unresolved rather than producing a crash or arbitrary string;
- no unresolved expression becomes a dependency literally named `unknown`.

### Disposition

**Promote after fork execution.** The source mechanism is specific and the implementation boundary is small. First run the focused source-introspection fixture, Python checks, and Meson's normal unit suite. If primitive option lookup is rejected as too broad, the fallback policy is to omit or explicitly mark unresolved dependencies; continuing to serialize them as a real package name is the behavior to avoid.

## ShellCheck #3263 — Bats export assignments trigger SC2030/SC2031

### Reported consequence

Two independent Bats tests each export the same variable with a literal value. ShellCheck says the second test reads a value that was modified in the first test's subshell, although the second command replaces that value.

### Source map and verified mechanism

- `src/ShellCheck/AnalyzerLib.hs`
  - every `T_BatsTest` opens a `SubshellScope "@bats test"`;
  - assignments leaving that scope are correctly marked dead;
  - `export`, `declare -x`, and related commands add synthetic references so exported variables count as externally used;
  - `export foo=value` also adds an ordinary assignment.
- `src/ShellCheck/Analytics.hs`
  - `findSubshelled()` checks each `Reference` against dead state before later flow entries;
  - the synthetic export reference uses the `T_Assignment` token itself;
  - the replacement assignment follows it in flow, so the second test warns before `foo` becomes alive;
  - existing property 20 deliberately warns when one Bats test assigns a variable and another actually reads it. A broad per-test reset would therefore be wrong.

### Candidate

Ignore only a subshell-check reference whose reference token is `T_Assignment` for the same variable. That token represents the synthetic “exported externally” use, not a read of the old value.

A real right-hand-side read such as `export foo=$foo` is represented by its dollar-expansion token and remains warnable. General unused/export analysis is unchanged because the synthetic reference remains in variable flow and is ignored only by `subshellAssignmentCheck`.

### Required properties

- literal export in both tests: no SC2030/SC2031;
- first test assigns, second test uses `export foo=$foo`: warning retained;
- first test assigns, second test echoes `$foo`: warning retained;
- ordinary pipeline, command substitution, background, and subshell diagnostics unchanged.

### Separate sourced-function reproducer

The later issue comment re-sources a file containing a function from inside one Bats test, then calls the function in a later test. The linear include traversal visits an assignment inside that function at the source site and can mark it dead when the first test ends. This is a function/include control-flow problem, not the synthetic export ordering bug.

The fork retains both reproductions and explicitly does not claim that the narrow patch fixes the sourced-function case. That follow-up likely belongs in CFG-backed function invocation/source modeling rather than more exceptions in SC2030/SC2031.

### Disposition

**Promote the narrow original-case candidate after fork execution. Retain the sourced-function case as a separate experiment.**

## uv #20871 — uvx allegedly imports the surrounding project's dependency

### Reported consequence

A tool pins one dependency version, but running `uvx` from inside another project allegedly imports that project's incompatible version. The report says `--isolated` still shows the wrong version.

### Source map and verified mechanism

`crates/uv/src/commands/tool/run.rs` shows:

- interpreter selection uses `EnvironmentPreference::OnlySystem`, not the project virtual environment;
- normal reuse checks uv's installed-tools store, not a discovered project `.venv`;
- fresh tool environments use `CachedEnvironment::from_spec`;
- `--isolated` skips installed-tool reuse;
- the launched child receives a new `PATH` beginning with the tool environment's scripts directory;
- other ambient environment variables are inherited; `PYTHONPATH` and `PYTHONHOME` are not removed, and `PYTHONNOUSERSITE` or safe-path mode is not added.

This source review contradicts the initial “uvx reuses the project dependencies” interpretation. It supports the maintainer's request to inspect `PYTHONPATH`, the selected executable, and import paths.

### Prepared discriminator

The fork contains a local `uvx --from` tool with an installed module marker and an ambient directory containing a conflicting module of the same name. `probe.sh` records:

1. clean environment;
2. conflicting `PYTHONPATH`;
3. conflicting `PYTHONPATH` with `--isolated`;
4. sanitized environment with `PYTHONPATH` unset and user site disabled.

Every row prints the imported marker, module file, `sys.executable`, `sys.prefix`, current directory, `PYTHONPATH`, and complete `sys.path`.

### Decision boundary

- If only ambient `PYTHONPATH` causes the conflict, the current report is environmental contamination, not project-environment reuse.
- A product policy may still choose to sanitize Python import variables under `--isolated`; that is a compatibility decision and should be documented and tested separately.
- If the clean row imports the wrong package, inspect entry-point shebangs, cache identity, interpreter discovery, `.pth` files, and current-directory insertion before changing resolution.

### Disposition

**Experiment first; no source patch promoted.** A plausible bounded future change is to make `--isolated` remove `PYTHONPATH` and `PYTHONHOME` and set `PYTHONNOUSERSITE=1`, but only after the matrix proves that this is the actual cause and the desired meaning of isolation is agreed.

## Cargo #16574 — local git patch still accesses original URL

### Reported consequence

A manifest declares a git dependency, while local `.cargo/config.toml` patches that source/package to a path. Cargo still tries to access the git URL, which fails in an offline or credential-free environment.

### Current contract found in tests

`tests/testsuite/patch.rs::patch_git` already constructs a git dependency and a local path patch. Its expected output explicitly contains:

```text
UPDATING git repository ...
```

before Cargo selects and checks the local path package. The reported behavior is therefore not just an accidental missing optimization; it is encoded in the present test contract.

### Why the fetch occurs

`[patch]` augments a source's candidate set during dependency resolution. It is not a textual replacement of one dependency declaration. Cargo may need the original source to determine:

- packages and versions available from the repository;
- whether the path package's name and version satisfy the dependency;
- whether another package from the same git workspace is needed;
- whether a branch, tag, or revision selector changes source identity;
- whether the patch is unused;
- how an existing or new lockfile should identify the selected package.

Skipping the source merely because a same-name path patch exists can silently accept a candidate Cargo currently rejects or leave another needed package unavailable.

### Process boundary

The issue is labeled `S-needs-design`. Cargo's repository contribution guide says only `S-accepted` issues will be reviewed and asks for design discussion before implementation. No external discussion is authorized here, so production code must remain on hold.

### Prepared artifacts

- a self-contained unreachable-git reproducer;
- a deliberately failing Cargo test expressing the requested no-fetch invariant;
- a ten-question design checklist covering selection proof, versions, repository multiplicity, revision selectors, transitive graph use, lockfiles, unused patches, config scope, offline modes, and identity/checksums.

The safer architectural direction may be a new explicit local-only exact-override mechanism rather than silently changing `[patch]` semantics.

### Disposition

**Hold for design.** Keep the failing test as an executable contract proposal. Do not short-circuit source loading until exact replacement rules and companion controls are defined.

## Ranked work order

1. **Meson** — apply the candidate to product source in the fork, wire the fixture into the native source-introspection suite, and run focused plus full unit gates.
2. **ShellCheck original case** — apply the narrow `T_Assignment` synthetic-reference filter and run focused properties plus analyzer tests.
3. **uv** — execute the four-row local matrix; promote a change only if the clean row proves a uv defect or the isolated-mode policy is explicitly selected.
4. **ShellCheck sourced-function follow-up** — characterize include/function flow separately after the narrow fix is proven.
5. **Cargo** — retain the failing test and design packet; no production implementation until accepted semantics exist.

## Fork artifact index

### Meson

- [`README.md`](https://github.com/teamleaderleo/meson/blob/fieldwork/16046-source-option-dependency/fieldwork/16046/README.md)
- [`candidate.patch`](https://github.com/teamleaderleo/meson/blob/fieldwork/16046-source-option-dependency/fieldwork/16046/candidate.patch)
- [`reproducer/meson.build`](https://github.com/teamleaderleo/meson/blob/fieldwork/16046-source-option-dependency/fieldwork/16046/reproducer/meson.build)
- [`reproducer/meson.options`](https://github.com/teamleaderleo/meson/blob/fieldwork/16046-source-option-dependency/fieldwork/16046/reproducer/meson.options)

### ShellCheck

- [`README.md`](https://github.com/teamleaderleo/shellcheck/blob/fieldwork/3263-bats-synthetic-export-read/fieldwork/3263/README.md)
- [`candidate.patch`](https://github.com/teamleaderleo/shellcheck/blob/fieldwork/3263-bats-synthetic-export-read/fieldwork/3263/candidate.patch)
- [`original.bats`](https://github.com/teamleaderleo/shellcheck/blob/fieldwork/3263-bats-synthetic-export-read/fieldwork/3263/original.bats)
- [`resourced/`](https://github.com/teamleaderleo/shellcheck/tree/fieldwork/3263-bats-synthetic-export-read/fieldwork/3263/resourced)

### uv

- [`README.md`](https://github.com/teamleaderleo/uv/blob/fieldwork/20871-uvx-environment-isolation/fieldwork/20871/README.md)
- [`probe.sh`](https://github.com/teamleaderleo/uv/blob/fieldwork/20871-uvx-environment-isolation/fieldwork/20871/probe.sh)
- [`tool/`](https://github.com/teamleaderleo/uv/tree/fieldwork/20871-uvx-environment-isolation/fieldwork/20871/tool)
- [`ambient/`](https://github.com/teamleaderleo/uv/tree/fieldwork/20871-uvx-environment-isolation/fieldwork/20871/ambient)

### Cargo

- [`README.md`](https://github.com/teamleaderleo/cargo/blob/fieldwork/16574-patch-source-fetch/fieldwork/16574/README.md)
- [`DESIGN.md`](https://github.com/teamleaderleo/cargo/blob/fieldwork/16574-patch-source-fetch/fieldwork/16574/DESIGN.md)
- [`reproducer.sh`](https://github.com/teamleaderleo/cargo/blob/fieldwork/16574-patch-source-fetch/fieldwork/16574/reproducer.sh)
- [`candidate-test.patch`](https://github.com/teamleaderleo/cargo/blob/fieldwork/16574-patch-source-fetch/fieldwork/16574/candidate-test.patch)

## Authority and contact boundary

This round authorizes reading public source and maintaining internal branches, notes, reproducers, candidate patches, tests, issues, and draft pull requests in repositories owned by `teamleaderleo`. It does not authorize comments, reactions, issue claims, pull requests, emails, patches, or any other interaction with Meson, ShellCheck, uv, Cargo, or their maintainers.

Before any separately authorized upstream proposal:

1. rerun overlap and ownership checks;
2. execute target-native focused and full tests;
3. convert patch artifacts into ordinary source commits on clean branches;
4. inspect the complete fork diff;
5. preserve project-specific contribution and acceptance rules;
6. keep third-party GitHub links in interaction text behind `redirect.github.com`.