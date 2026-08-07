# Developer tools and build systems scout — Round 006

Updated: 2026-08-08

Authority boundary: owned repositories and forks only. No upstream comments, reactions, claims, branches, or pull requests were created.

## Final dispositions

### 1. Meson #15998 — CMake CUDA standard normalization

Status: `FOCUSED MODEL GREEN / DEFERRED-SETTLEMENT BOUNDARY SELECTED / IMPLEMENTATION UNEXECUTED`.

Owned investigation: `teamleaderleo/meson#3@e44c4547bd3a9b1d3dce9956c876908f657aeef4`.

The CMake converter maps CMake `CUDA` file groups to Meson language `cuda`, but the original standard-normalization pass visited only C and C++. The first candidate included CUDA in that existing pass.

Execution-only carrier `teamleaderleo/meson#4` completed successfully:

- focused workflow run `30858277753`: success;
- baseline synthetic File API control failed as expected;
- candidate control passed;
- `-std=c++17` became `cuda_std=c++17`;
- the raw duplicate was removed;
- an unrelated NVCC generate-code flag survived;
- Python compilation and diff hygiene passed.

This is valid compiler-free target evidence for language classification and raw-flag deduplication only.

Two complete-fix policies remain rejected:

1. unconditional normalization, because a generated target `cuda_std` override defeats an ordinary parent-project default;
2. provenance-only suppression, because an unexplained effective standard would be dropped when Meson supplied no replacement authority.

Execution PR #6 and queued run `31019630325` were retired as non-evidence; the temporary workflow was removed.

Static architecture review now identifies a narrower next boundary. `ConverterTarget.postprocess()` is too early to settle an unexplained File API standard. During later target AST generation the interpreter can see both replacement authorities:

- the surrounding Meson option store for effective `cuda_std`;
- global and target-specific `cmake.subproject_options()` state through `TargetOptions`.

The selected next experiment is deferred settlement:

1. explicit target CMake provenance becomes a generated target `cuda_std` override;
2. explicit `cmake.subproject_options()` replacement suppresses an unexplained fallback;
3. effective Meson `cuda_std != none` suppresses the unexplained fallback without creating a target override, allowing the project/subproject standard to win;
4. with no replacement authority, retain the effective CMake `-std=` as a raw CUDA fallback.

This preserves both the reporter case and the previously blocking no-authority case. A small `TargetOptions.has_override_option(...)`-style query is the preferred interface boundary.

Directory/global `CMAKE_CUDA_STANDARD` remains explicitly unresolved because final trace-variable state does not reliably identify the value that initialized a particular target. No production claim should include that case until creation-time provenance or intended precedence is explicit.

The mandatory next negative control is: unexplained effective CUDA standard + Meson `cuda_std=none` + no CMake-module override must retain the effective standard after AST settlement.

### 2. ShellCheck #3263 — two separate owners

#### Synthetic export references

Status: `TECHNICALLY ACCEPTED / READY FOR OWNER REFINEMENT / ORDINARY PACKAGING WORKFLOW BLOCKED`.

Clean source review: `teamleaderleo/shellcheck#11@83316fa272e4fc1caeffdfe39f946819bc723353`.

The final command-owned adjacency repair skips a reference only when the assignment-token reference is immediately followed by the matching assignment event with identical token identity and variable name, and that assignment belongs to the enclosing simple command. This preserves append, bare-export, RHS, and ordinary later reads.

Read-only run `30959236798`, job `92159247440`, completed successfully on Ubuntu 24.04 with GHC 9.6.6:

- complete `cabal v2-test test-shellcheck --test-show-details=direct` passed;
- `exe:shellcheck` built;
- literal replacement emitted no SC2030/SC2031;
- append and bare-export controls retained both diagnostics;
- explicit RHS and ordinary later reads retained warnings;
- only `src/ShellCheck/Analytics.hs` changed locally;
- `git diff --check` passed.

Source materialization run `31010993427` succeeded. Independent complete-diff review accepted the exact one-commit, one-file source head.

Current-head ordinary workflow runs `31016803810` and `31014496631` both failed in `Package Source Code` before tests. Their merge checkout has no reachable tags, so `git describe` fails inside `setgitversion`; test, build, binary-package, and deployment jobs were skipped. This is fork packaging/tag-topology evidence, not a source regression.

The focused complete-suite receipt remains the product authority. The item is visible on Human Review Desk #387 for owner refinement. No temporary workflow is part of source PR #11.

#### Sourced-function flow

Status: `FOCUSED FALSE POSITIVE CONFIRMED / DISCRIMINATOR MATRIX PREPARED / PRODUCTION FIX NOT SELECTED`.

Owned investigation: `teamleaderleo/shellcheck#3@74c524d8ad7262983d192150927562331c098d9a`.

Focused Fieldwork run `30839352175`, job `91772318148`, executed the primary fixture from its directory:

- the sourced file resolved;
- SC1091 was absent;
- SC2031 remained at the later `COMPREPLY` read.

A fixture-only matrix now separates setup-only sourcing, independent per-test sourcing, same-test execution, same content through different paths, a real top-level sourced assignment, and cross-test definition isolation. The matrix is prepared but unexecuted and carries no behavior claim.

The likely owner remains function/include invocation modeling or a CFG-backed analysis. Simply skipping function bodies remains rejected. Generic fork packaging CI is not a useful substitute for this matrix.

### 3. Cargo #16574 — patch source fetch semantics

Status: `DESIGN HOLD WITH EXECUTED NEGATIVE EVIDENCE`.

Owned fork draft: `teamleaderleo/cargo#1@868c4450a5c5a3bf78ef942cbafe326952373842`.

Both the broad no-fetch contract and an exact `=0.1.0`, single-path-patch probe reached the unreachable original git source. The exact-version fast path is absent on the tested head.

Cargo exited 101 after contacting the original source. The runner lacked `rg`, so its guarded auxiliary source-map capture was empty. Treat the product behavior as valid executed evidence and the source map as missing.

No production change is justified without an accepted semantic design preserving source identity, version and feature selection, lockfiles, checksums, registries, git sources, and diagnostics.

### 4. uv #13505 — Windows path-case duplicates in `uv python list`

Status: `SOURCE/HISTORY MAPPED / DUPLICATED-PATH REPRODUCER ABSENT / CANDIDATE UNEXECUTED`.

Owned investigation: `teamleaderleo/uv#39@0bd5bb057a4df542951fb6c69018e5509a5445a0`.

Historical issue #9979 and PR #12628 intentionally changed `uv python list` to report queried executable paths, preserving shim and search-path provenance. The final list still uses case-sensitive Rust path equality, so Windows ordinal comparison remains a plausible boundary.

Read-only Windows run `31047448111`, job `92446355170`, applied the UTF-16 case-variant integration control and candidate transformer cleanly, compiled the immutable baseline, and ran exactly one focused `python_list_duplicate_path_entries` test.

The baseline passed and listed each Python once. Therefore case-varied copies of the same `UV_PYTHON_SEARCH_PATH` directories do not reproduce the public report on the tested head. An earlier discovery layer already collapses or avoids those duplicates.

The candidate stage was skipped. The result is not candidate evidence and does not establish that the public issue is fixed.

Transcript artifact: `8948402487`; SHA-256 `a136314c4f7d4b21c7d29fdd105de187fb6faccedfd1d01815485964ea37aabc`.

Execution PR #48 was retired, its branch reset to cleaned `main`, and the temporary workflow removed at `fb6f822820fb2234035610066527b749d3a153cf`.

The retained ordinal-comparison design remains unexecuted. A renewed experiment must either:

1. reproduce one interpreter through distinct discovery routes such as PATH plus registry or shim;
2. directly isolate the final-list inclusion boundary with case-varied queried paths;
3. preserve a negative control for genuinely distinct shim/search-path locations.

No new Windows carrier should run until its baseline control distinguishes current behavior.

### 5. uv tool upgrade inventory errors

Status: `CURRENT-MAIN SOURCE ACCEPTED / FOCUSED ASSERTIONS RESTORED / EXACT-HEAD CI PENDING`.

Canonical current source: `teamleaderleo/uv#57@96170fa4d0b540e698d845258549e44b9f280762`, based on uv source `507230998c9541d67814b57463ac00e454ff6991`.

The earlier source PR #47 and execution PR #52 are closed as superseded. Historical focused run `31043690842` proved the reversing behavior on the older source generation but is not current-head evidence.

The production repair remains one line:

- `installed_tools.tools().unwrap_or_default()` -> `installed_tools.tools()?`.

That preserves the intended semantic boundary: top-level inventory enumeration/parsing failure stops `uv tool upgrade --all`; per-tool receipt failures remain per-tool values after successful enumeration; genuine empty inventory still reaches the existing `Nothing to upgrade` success path.

Re-review of the first current-main rebase found that its invalid-directory regression had weakened to generic `.failure()`. That review defect is now repaired on the current head with a dedicated `tool_upgrade_inventory` test module:

- gated by `test-python` only rather than the broad module's unrelated `test-pypi` gate;
- creates an invalid tool-directory package name deterministically;
- requires command failure;
- requires stderr to contain `Not a valid package`;
- requires stderr not to contain `Nothing to upgrade`.

The older generic failure test remains as redundant coverage. The focused module restores the accepted user-visible regression contract.

Current fence is four paths: one product source file plus three test/plumbing files. Only `crates/uv/src/commands/tool/upgrade.rs` changes product behavior.

Fresh exact-head CI run `31201691790` is pending. Pending state is not execution evidence. Superseded run `31200368519` belongs to the weaker pre-repair head and must not be promoted.

Durable coordination issue #627 now records the current source and source-review acceptance pending execution.

## Occupied stops

The following reports were not entered because active implementation or explicit intent already existed at intake:

- Meson #15989 and #16024;
- ripgrep #3477;
- fd #2067;
- Vite #23032, #23146, #22957, and #23108;
- Biome #10838;
- uv #20949, #20744, #20678, and #16209.

These checks are dated intake evidence and must be refreshed before future entry.

## Reserve leads

- Biome #11174 — potentially valid type-flow false positive, but wider analyzer semantics;
- just #3684 — bounded completion defect with historical overlap requiring refresh;
- fd #2033 — ordering behavior worth characterization after ownership and fork refresh.

## Work order

1. Classify uv PR #57 exact-head CI `31201691790`; do not promote the superseded pre-repair run.
2. Implement the Meson deferred-settlement probe in source form with the mandatory `cuda_std=none` no-authority fallback control; do not create a runner before that source boundary is reviewable.
3. Design a uv #13505 baseline that uses distinct discovery sources or directly owns final-list inclusion; do not rerun the retired PATH-only carrier.
4. Execute the ShellCheck sourced-function matrix through a dedicated exact-head read-only carrier rather than generic packaging CI.
5. Keep Cargo held until a semantic design is accepted.
6. Refresh public overlap before opening reserve leads.

## Evidence boundary

This report records owned-fork research, execution, source review, and owner visibility. It does not authorize or claim public upstream filing, review, reaction, release, or deployment.
