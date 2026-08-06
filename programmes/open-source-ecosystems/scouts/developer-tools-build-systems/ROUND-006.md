# Developer tools and build systems scout — Round 006

Updated: 2026-08-06

Authority boundary: owned repositories and forks only. No upstream comments, reactions, claims, branches, or pull requests were created.

## Final dispositions

### 1. Meson #15998 — CMake CUDA standard normalization

Status: `FOCUSED MODEL GREEN / PROVENANCE-ONLY POLICY REJECTED / REPLACEMENT-AUTHORITY HOLD`.

Owned investigation: `teamleaderleo/meson#3@3e43e0c7d70392b4f22de6838b85ce805b839a98`.

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

A later precedence control proved that unconditional normalization is not a complete fix: a generated target `cuda_std` override defeats an ordinary parent-project default in the reporter's no-explicit-CMake-standard case.

A provenance-gated second generation was then rejected before execution. It would remove an unexplained effective standard even when Meson supplied no replacement authority, silently falling back to compiler defaults. Execution PR #6 and queued run `31019630325` were retired as non-evidence; the temporary workflow was removed.

A safe repair needs both provenance and replacement authority. It must preserve:

- parent Meson `cuda_std` when it deliberately replaces an unexplained CMake effective flag;
- the effective CMake standard when Meson supplies no replacement;
- explicit target `CUDA_STANDARD` and direct target compile options;
- explicit global and target CMake-module overrides;
- mixed CXX/CUDA and GNU-extension semantics.

The next owning boundary is likely effective Meson option authority passed into conversion, deferred fallback resolution during AST generation, or propagation through the generated CMake toolchain.

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

The likely owner remains function/include invocation modeling or a CFG-backed analysis. Simply skipping function bodies remains rejected.

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

Status: `OWNED-FORK SOURCE ACCEPTED / CI QUEUED`.

Owned source: `teamleaderleo/uv#47@9e080cb2a92b35b01f42128902d7a6edfdc57481`.

`uv tool upgrade --all` previously converted a top-level `InstalledTools::tools()` error into an empty inventory with `unwrap_or_default()`, then printed `Nothing to upgrade` and exited successfully.

The production repair is one line: propagate `tools()?`. Complete-diff review confirmed that missing or malformed receipts remain per-tool values inside a successfully enumerated vector; only failure to enumerate or parse the inventory itself stops the command.

Review repaired two test-only defects before CI:

- the case-sensitive predicate now matches the actual `Not a valid package...` diagnostic;
- the deterministic invalid-directory regression requires only `test-python`, not the unrelated PyPI feature.

The existing `tool_upgrade_empty` integration test preserves the genuine empty/up-to-date success path. Current-head independent review accepted the source.

Repository CI run `31020821954` remains queued. Queue state is not execution evidence. The item is visible on Human Review Desk #387 as a watch, not yet as a final ready decision. Durable coordination remains Fieldwork issue #627.

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

1. Design a uv #13505 baseline that uses distinct discovery sources or directly owns final-list inclusion; do not rerun the retired PATH-only carrier.
2. Classify uv PR #47 CI when it moves and transfer any exact result to issue #627 and the owner desk.
3. Locate Meson's replacement-authority boundary and add the no-authority negative control before selecting another source candidate.
4. Execute the ShellCheck sourced-function matrix only through an exact current-base read-only carrier.
5. Keep Cargo held until a semantic design is accepted.
6. Refresh public overlap before opening reserve leads.

## Evidence boundary

This report records owned-fork research, execution, source review, and owner visibility. It does not authorize or claim public upstream filing, review, reaction, release, or deployment.
