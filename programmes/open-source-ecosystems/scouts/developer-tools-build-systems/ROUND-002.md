# Developer tools and build systems — Round 002

Snapshot: 2026-08-01  
Programme: [`open-source-ecosystems`](../../README.md) / issue [`#207`](https://github.com/teamleaderleo/fieldwork/issues/207)  
Scout lane: [`#210`](https://github.com/teamleaderleo/fieldwork/issues/210)  
Public upstream contact: **none; unauthorized**

## In simple words

This round looked beyond the Ruff and pip work retained in Round 001. It inspected current pytest, ShellCheck, Meson, uv, and Cargo source and issue state, then separated three kinds of findings:

1. **Good first probes** — a small local fixture can distinguish the suspected bug from configuration, environment, or intended behavior.
2. **Issue-first design questions** — the behavior is consequential, but the correct contract needs maintainer direction before a patch.
3. **Stops and references** — a pull request, assignee, or active equivalent implementation already owns the work.

The strongest unclaimed first probes are:

1. **uv #20871** — determine why `uvx` can import a parent project's incompatible dependency despite tool isolation.
2. **Meson #16046** — reduce option-derived dependency names becoming `"unknown"` in source introspection used by distro build-requirement generators.
3. **Cargo #16574** — characterize exactly when a local `[patch]` can avoid contacting an unavailable original Git source, separating a possible exact-version regression from the broader source-resolution policy.

ShellCheck's Bats false positives are also useful, but one report still needs reduction from a large sourced library before implementation should begin.

## Scope and exact source revisions

| Target | Inspected revision | Main owning areas | Native test areas |
| --- | --- | --- | --- |
| pytest | [`f306da747e70403ca75ae6d9e1dd61f2ad1b8979`](https://github.com/pytest-dev/pytest/commit/f306da747e70403ca75ae6d9e1dd61f2ad1b8979) | `src/_pytest/fixtures.py`, `src/_pytest/python.py`, hook specifications | `testing/python/fixtures.py`, marker/collection tests |
| ShellCheck | [`9af7ee28ce587baadd950b85dd6826a16b9c068d`](https://github.com/koalaman/shellcheck/commit/9af7ee28ce587baadd950b85dd6826a16b9c068d) | `src/ShellCheck/Analytics.hs`, CFG and AST helpers | property examples embedded beside checks; parser/analyzer suites |
| Meson | [`0b5b32e284709eb5b23ed30207fe978362d30a3d`](https://github.com/mesonbuild/meson/commit/0b5b32e284709eb5b23ed30207fe978362d30a3d) | `mesonbuild/ast/introspection.py`, `mesonbuild/backend/backends.py`, dependency/compiler modules | `unittests/`, `run_unittests.py`, focused platform test cases |
| uv | [`79bbface771210df216b738e9bdc7df95e5a9e6b`](https://github.com/astral-sh/uv/commit/79bbface771210df216b738e9bdc7df95e5a9e6b) | `crates/uv/src/commands/tool/run.rs`, project/environment and resolver layers | `crates/uv/tests/tool/tool_run.rs`, project and cache integration suites |
| Cargo | [`ef229e47b92dfb5d3804f4c1604709d321a3610f`](https://github.com/rust-lang/cargo/commit/ef229e47b92dfb5d3804f4c1604709d321a3610f) | `src/workspace/registry.rs`, source loading and resolver query paths | `tests/testsuite/patch.rs`, Git-source and config tests |

A dated scan does not reserve any issue. Pull requests, assignments, contributor-intent comments, linked commits, and project claim mechanisms must be refreshed immediately before a branch is created.

## Ranked candidate queue

Rank combines consequence, reproducibility, code-boundary clarity, environment cost, ownership state, and likely review size.

| Rank | Target | Candidate | Consequence | Ownership / overlap at snapshot | Next distinguishing probe | Disposition |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | uv | [`#20871`](https://github.com/astral-sh/uv/issues/20871) — `uvx` uses parent project dependencies | a tool can silently run with a dependency version that violates its exact requirement; `--isolated` is reported not to protect it | open, unassigned, zero comments, no matching PR found | fully local two-version package fixture inside/outside a parent project; compare import path, `sys.path`, and resolved version with and without `--isolated` | **promote experiment** |
| 2 | Meson | [`#16046`](https://github.com/mesonbuild/meson/issues/16046) — source introspection reports dependency name `unknown` | distro macros generate invalid build requirements such as `pkgconfig(unknown)` | open, unassigned, zero comments, no matching PR found | tiny combo-option project; compare literal dependency, default option value, explicit option value, and conditional placement | **promote experiment** |
| 3 | Cargo | [`#16574`](https://github.com/rust-lang/cargo/issues/16574) — patch still contacts original Git URL | offline/private-mirror development fails even when a local replacement exists | open, unassigned, no matching PR found; labeled `S-needs-design` | current-head matrix for exact/range version, matching/missing features, committed/no lockfile | **issue-first experiment** |
| 4 | ShellCheck | [`#3263`](https://github.com/koalaman/shellcheck/issues/3263) — Bats test blocks produce SC2030/SC2031 cross-test false positives | independent tests are modeled as one value-flow chain, creating noise in ordinary Bats suites | open, unassigned, no matching PR found; minimal two-test example already supplied | add embedded analyzer property proving sibling `@test` blocks are separate execution roots while preserving real subshell warnings | **promote reduction** |
| 5 | ShellCheck | [`#3509`](https://github.com/koalaman/shellcheck/issues/3509) — later re-source causes earlier SC2218 | a later test changes diagnostics for an earlier independent test; real suites can receive many false errors | open, unassigned, zero comments, no matching PR found; report depends on a 1069-line library | delta-debug the sourced file while preserving the later-source/earlier-call reversal; compare include graph and function-definition ordering | **reduce before promotion** |
| 6 | uv | [`#20765`](https://github.com/astral-sh/uv/issues/20765) — index overrides not propagated to package-specific sources | a repository configured for internal mirrors can still resolve a source-selected package from a public URL | open at snapshot; overlap refresh required before branch | local dual-index fixture with identical index names and distinct sentinel package versions/URLs | **promote after overlap refresh** |
| 7 | Meson | [`#14979`](https://github.com/mesonbuild/meson/issues/14979) — `components:` mishandled through wrap fallback | a valid fallback dependency can fail because CMake-specific component semantics leak into another resolution path | open at snapshot; overlap refresh required | wrap fixture with primary miss and fallback hit; assert `components` is consumed only by matching dependency methods | **retain / likely current-CI probe** |
| 8 | uv | [`#19622`](https://github.com/astral-sh/uv/issues/19622) — dangling Windows managed-Python junction cannot self-heal | one broken minor-version link poisons install, reinstall, discovery, and every dependent tool launch | open at snapshot; Windows-specific; overlap refresh required | Windows test creates valid patch directory plus dangling minor junction, then runs reinstall and discovery | **Windows capability queue** |
| 9 | Meson | [`#15456`](https://github.com/mesonbuild/meson/issues/15456) — Qt private headers leak host paths into cross build | cross compilation can silently include host headers, compromising correctness and reproducibility | open at snapshot; cross/Qt environment required | synthetic host/target Qt trees with sentinel private header; assert target compiler never receives host path | **cross-build queue** |
| 10 | Cargo | [`#17142`](https://github.com/rust-lang/cargo/issues/17142) — `build.warnings=deny` disagrees with `-Dwarnings` for linker messages | stabilized warning policy can unexpectedly break builds for diagnostics rustc intentionally exempts | open at snapshot; release-sensitive; overlap refresh required | fake linker emits stderr; compare default, `RUSTFLAGS=-Dwarnings`, config, and environment form | **issue-first / release check** |
| 11 | uv | [`#13073`](https://github.com/astral-sh/uv/issues/13073) — source ignored with conflict table and groups/extras | private path/Git packages become unsatisfiable or an unselected remote source is fetched | old open issue; no ownership refresh completed | reduce to one private package, two groups, two conditional sources, and no package index | **retain for resolver probe** |
| 12 | Meson | [`#15601`](https://github.com/mesonbuild/meson/issues/15601) — RTEMS library linkability probe too strict | `find_library` rejects libraries on a supported embedded target after a Meson regression | open at snapshot; RTEMS toolchain required | capture old/new probe command and model target-specific absence of ordinary executable linkage | **toolchain capability queue** |
| 13 | ShellCheck | [`#3499`](https://github.com/koalaman/shellcheck/issues/3499) — POSIX arithmetic comma operator not diagnosed | non-portable shell code passes analysis and can fail or change behavior under POSIX shells | open at snapshot; small consequence and likely small patch | add dialect matrix for `sh`, `dash`, `bash`, and arithmetic contexts | **small diagnostic candidate** |
| 14 | Meson | [`#16044`](https://github.com/mesonbuild/meson/issues/16044) — VS RUN TESTS output contract mismatch | incremental Visual Studio builds repeatedly warn or rebuild because the declared output is absent | open at snapshot; Windows/VS backend required | inspect generated custom-build output contract and run two no-change builds | **Windows backend queue** |
| 15 | Meson | [`#13498`](https://github.com/mesonbuild/meson/issues/13498) — subproject `build_by_default:false` ignored with install | optional subproject targets can enter the default build unexpectedly | older open issue; overlap refresh required | parent/subproject matrix over install and build-by-default flags | **retain after semantic refresh** |

## Explicit stops and retained references

| Target | Candidate | Existing ownership | Retained value |
| --- | --- | --- | --- |
| pytest | [`#14800`](https://github.com/pytest-dev/pytest/issues/14800) | [`PR #14801`](https://github.com/pytest-dev/pytest/pull/14801) fixes stale finalizers when fixture setup hooks raise | excellent exact-once finalizer and parametrized-state regression pattern; do not compete |
| pytest | [`#14737`](https://github.com/pytest-dev/pytest/issues/14737) | [`PR #14740`](https://github.com/pytest-dev/pytest/pull/14740) and [`PR #14798`](https://github.com/pytest-dev/pytest/pull/14798) both target package marker propagation | collector inheritance and package-module marker test pattern; do not create a third implementation |
| Meson | [`#16010`](https://github.com/mesonbuild/meson/issues/16010) | [`PR #16039`](https://github.com/mesonbuild/meson/pull/16039), superseding #16011 | Windows `PATH` growth and target-type filtering regression pattern |
| Meson | [`#15740`](https://github.com/mesonbuild/meson/issues/15740) | assigned to maintainer `dcbaker`, release milestone, active discussion | Cython/Python dependency consistency and conda fixture design; coordinate only |
| uv | [`#20477`](https://github.com/astral-sh/uv/issues/20477) | [`PR #20631`](https://github.com/astral-sh/uv/pull/20631) preserves original path spelling | lockfile portability and local-metadata precedence regression pattern |

## Probe 1 — uv tool isolation versus parent project

### Question

Can a tool environment that resolves its own exact dependency still import an incompatible version from the current project's `.venv`, and does `--isolated` change that result?

### Why this is distinguishing

Current `tool/run.rs` builds or reuses a separate tool environment. The command is launched from that environment's scripts directory, and the source contains a future-looking TODO about possibly layering project tools rather than code intentionally doing so today. If the report reproduces, likely causes include inherited import-path environment, interpreter/script selection, cached environment identity, or packaging metadata—not intended project layering.

### Fully local fixture

Build three tiny wheels with the existing uv test index helpers:

- `fieldwork-dep==1.0.0`, exporting `VERSION = "tool"`;
- `fieldwork-dep==2.0.0`, exporting `VERSION = "project"`;
- `fieldwork-tool==1.0.0`, requiring `fieldwork-dep==1.0.0`, with console entry point printing:
  - dependency version;
  - dependency `__file__`;
  - interpreter path;
  - `sys.prefix`, `sys.base_prefix`, and complete `sys.path`.

Create a parent project requiring `fieldwork-dep==2.0.0`, sync its `.venv`, but do not activate it. Run from a nested project directory:

1. `uvx fieldwork-tool` outside any project;
2. `uvx fieldwork-tool` inside the project;
3. `uvx --isolated fieldwork-tool` inside the project;
4. the same three cases with `VIRTUAL_ENV`, `PYTHONPATH`, `PYTHONHOME`, and shell activation variables explicitly absent;
5. a negative control with an intentionally set `PYTHONPATH` pointing at project site-packages.

All package acquisition stays on the local fixture index. No PyPI publication or network is required.

### Expected evidence

- The first four clean-environment cases should print version `1.0.0` and a path under the tool cache.
- Only the explicit `PYTHONPATH` negative control may import version `2.0.0`, unless uv promises to sanitize that too.
- If a clean case imports the project version, capture the generated console-script shebang, process environment, and `sys.path` ordering.

### Owning code and tests

- `crates/uv/src/commands/tool/run.rs`
  - `run()` command construction and inherited environment;
  - `get_or_create_environment()` interpreter discovery, installed-tool reuse, and cached environment creation.
- `crates/uv/tests/tool/tool_run.rs`
- project-run tests for comparison with intentionally project-aware behavior.

### Promotion rule

Promote a code branch only after the local fixture reproduces on exact current head and identifies whether the leak enters through environment inheritance, cached environment reuse, or script/interpreter selection. If the clean fixture does not reproduce, retain a high-quality upstream clarification packet describing the missing environmental precondition.

## Probe 2 — Meson source introspection with option-derived dependency names

### Question

When `dependency()` receives a value returned by `get_option()`, should source-only introspection report the option's default, enumerate possible names, or mark the dependency dynamic without emitting a fake package named `unknown`?

### Why this is distinguishing

`IntrospectionInterpreter.func_dependency()` records a dependency name as either a string or `UnknownValue`. The external JSON currently serializes that unknown value as a package name, and distro tooling turns it into invalid build requirements. The bug is real even if the final semantic choice needs discussion.

### Minimal fixture

`meson_options.txt`:

```meson
option(
  'logind',
  type: 'combo',
  choices: ['systemd', 'elogind', 'none'],
  value: 'systemd',
)
```

`meson.build`:

```meson
project('fieldwork-introspection', 'c')

logind = get_option('logind')
if logind != 'none'
  dependency(logind, version: '>=209', required: false)
endif
```

Run and preserve JSON for:

1. `meson introspect --dependencies meson.build`;
2. a literal `dependency('systemd', ...)` control;
3. option default `systemd` versus an explicit `elogind` selection if the command accepts project options;
4. the call outside versus inside the conditional;
5. a string variable assigned literally rather than through `get_option()`.

### Expected evidence

The result must not claim that a build dependency named `unknown` exists. Candidate contracts to take upstream for judgment:

- resolve the declared option default for source introspection;
- return alternatives plus conditional metadata;
- represent a dynamic name as non-emittable/unknown metadata rather than a literal dependency name.

### Owning code and tests

- `mesonbuild/ast/introspection.py`
  - `IntrospectionInterpreter.func_project()` loads option files;
  - `func_dependency()` accepts `str | UnknownValue` and stores the result.
- `mesonbuild/ast/interpreter.py` for option evaluation and flattening.
- introspection unit tests and a tiny source-tree fixture.

### Promotion rule

The reduced failing fixture is implementation-ready as a test. The production patch is **issue-first** unless existing Meson contracts clearly establish that the default option value must be used. Avoid merely stringifying or dropping `UnknownValue`; distro consumers need an explicit, stable representation.

## Probe 3 — Cargo patch source loading matrix

### Question

Which patch configurations can safely avoid contacting the original source, and is the exact-version short circuit working on current Cargo?

### Source fact

At current head, `src/workspace/registry.rs` still contains a deliberate short circuit: when exactly one patch matches and `dep.is_locked()` is true, Cargo returns the patch candidate before `ensure_loaded()` loads the original source. For unlocked requirements, Cargo loads the original source so it can compare available versions. Maintainer discussion notes that feature mismatches can still require fallback to the original Git source and that changing the broad policy can be breaking.

### Fully local test matrix

Use Cargo's testsuite project builder with an intentionally unreachable URL such as `ssh://invalid.fieldwork.test/foo.git` and a local path patch. Never contact a real server.

Cases:

1. dependency `foo = { git = URL, version = "=0.1.0" }`; local patch version `0.1.0`;
2. dependency version `^0.1`; matching local patch;
3. exact version with one requested feature present in the patch;
4. exact version with a requested feature absent from the patch;
5. each case with and without a committed lockfile;
6. path patch and local Git patch controls;
7. `cargo build --offline`, `cargo update --offline`, and ordinary commands with a process-level guard proving no SSH child is attempted.

### Expected evidence

- If case 1 avoids source loading, the current report is primarily a broader design request rather than a regression.
- If case 1 contacts the source, current code and behavior disagree; inspect how dependency locking is computed before registry query.
- Range requirements are expected to need source comparison under current policy.
- Missing-feature cases determine whether an offline error can explain why the patch is unusable without trying the inaccessible source.

### Owning code and tests

- `src/workspace/registry.rs`
  - patch candidate collection;
  - `dep.is_locked()` short circuit;
  - `ensure_loaded()` boundary.
- `tests/testsuite/patch.rs`
- Git source/config tests for unreachable and offline sources.

### Promotion rule

Do not implement “patch means never contact original” without maintainer direction. Promote either:

- a narrow regression repair if the exact-version short circuit is broken; or
- an issue-first diagnostic/offline-behavior proposal if current behavior matches the existing resolver contract.

## Additional code maps and branch questions

### pytest reference map

- Fixture lifecycle: `FixtureDef.execute()` registers finalizers; `FixtureDef.finish()` drains them and fires `pytest_fixture_post_finalizer`.
- Native tests: `testing/python/fixtures.py`.
- Package marker propagation: package collector/import path in `src/_pytest/python.py`; marker inheritance tests.
- Use these as patterns for exact-once cleanup, setup failure, and parent/child metadata inheritance. Do not create competing branches for #14800 or #14737.

### ShellCheck map

- `src/ShellCheck/Analytics.hs` runs tree checks including `checkUseBeforeDefinition`, subshell assignment analysis, and embedded QuickCheck/example properties.
- Related Bats issues suggest a shared missing abstraction: each `@test` body is a separate runtime root, while setup hooks are predecessors of every test.
- A durable repair should model that execution graph rather than add one-rule exceptions for SC2218 or SC2030/SC2031.
- First branch question: can the parser/AST identify Bats setup and test nodes early enough to construct per-test analysis roots without weakening ordinary subshell warnings?

### Meson map

- Source-only introspection: `mesonbuild/ast/introspection.py` and `mesonbuild/ast/interpreter.py`.
- Windows executable environment and DLL search paths: `mesonbuild/backend/backends.py`.
- Compiler/dependency sanity checks: compiler language modules and dependency factories.
- Cross-build candidates must prove host paths never reach target compiler arguments.

### uv map

- Tool environment creation and command launch: `crates/uv/src/commands/tool/run.rs`.
- Native tool integration tests: `crates/uv/tests/tool/tool_run.rs`.
- Resolver/source candidates: project settings, source lowering, index name resolution, and lock serialization.
- Windows managed Python: Python installation/discovery and minor-version-link lifecycle.

### Cargo map

- Patch/source candidate resolution: `src/workspace/registry.rs`.
- Tests: `tests/testsuite/patch.rs` and Git-source/config suites.
- Warning policy: compiler message handling and `build.warnings` configuration tests.

## Negative results and dead ends

- Generic searches for “bug” surfaced many trackers, feature requests, and already-owned work. They are not contribution candidates merely because they are open.
- pytest #14800 looked ideal but was immediately stopped after finding exact PR #14801.
- pytest #14737 had not one but two equivalent PRs; a third branch would add noise.
- Meson #16010 already has a focused replacement PR #16039.
- uv #20477 already has PR #20631.
- Meson #15740 is assigned to a maintainer and tied to a release milestone.
- Cargo #16574 is not a simple “skip the network” patch: source comparison and feature fallback are part of the current contract.
- ShellCheck #3509 is consequential but not yet a good branch because the supplied reproduction depends on a large external library and a small synthetic library did not reproduce.
- No CMake candidate from the sampled scan beat the top Meson, uv, Cargo, or ShellCheck probes on consequence plus reduction quality.

## Recommended execution order

1. **uv #20871 local isolation fixture** — current CI, no public services, strongest silent-correctness consequence.
2. **Meson #16046 source introspection fixture** — very small tree and direct downstream packaging consequence; test first, contract discussion second.
3. **Cargo #16574 current-head matrix** — clarify whether there is a narrow regression before discussing broader patch semantics.
4. **ShellCheck #3263 Bats sibling-root property** — minimal and likely reveals a reusable execution-model boundary.
5. **ShellCheck #3509 delta reduction** — preserve as a research task until the external library trigger is understood.

Keep at most three new implementation branches awaiting first review. These are probes, not reservations. Refresh ownership immediately before any branch.

## Current disposition

- Round disposition: **INVESTIGATE**
- First executable probes: **uv #20871**, **Meson #16046**, **Cargo #16574**
- Immediate independent implementation authorized by this report: **none**
- Public issue comments or pull requests: **not authorized**
- Required next record: exact probe commands, current-head result, environment, minimized fixture, ownership refresh, and promote/hold/stop decision for each of the first three probes.
