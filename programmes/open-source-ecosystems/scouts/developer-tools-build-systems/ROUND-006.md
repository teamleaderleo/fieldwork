# Developer tools and build systems scout — Round 006

Updated: 2026-08-05

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

The carrier receipt and before/after outputs are retained on source PR #3. Carrier PR #4 closed without merge.

Evidence class: `compiler-free-target-executed` for language classification and raw-flag deduplication only.

A later precedence control proved that the one-line model is not a complete fix: converting every effective CUDA standard into a generated target override defeats an ordinary parent-project `cuda_std`. Explicit `cmake.subproject_options()` overrides still replace the generated value, but the reporter's no-explicit-CMake-standard case remains wrong.

A provenance-gated second generation was prepared to remove unexplained raw standards and retain only traced explicit target `CUDA_STANDARD` or direct target `-std=` intent. Independent design review found a blocking compatibility case before execution:

- no explicit target CMake provenance;
- no Meson parent/subproject `cuda_std` replacement authority;
- File API reports the only effective CUDA standard.

That policy would silently drop the only standard and fall back to compiler defaults.

Execution PR `teamleaderleo/meson#6` and run `31019630325` were retired while queued. They are not behavior evidence. The temporary workflow was removed from `master` at `2f4ef1ae42ca3c47d189b06b91e601810dd68d4c`.

A production-safe repair needs both provenance and replacement authority. The next design must preserve:

- parent Meson `cuda_std` winning when it deliberately replaces an unexplained CMake effective flag;
- the effective CMake standard remaining when Meson supplies no replacement authority;
- explicit target `CUDA_STANDARD` and direct target compile options;
- explicit global/target CMake-module overrides;
- mixed CXX/CUDA and GNU-extension semantics.

The likely next boundary is passing effective Meson standard authority into conversion, deferring fallback resolution until AST generation, or moving Meson standard authority into the generated CMake toolchain.

### 2. ShellCheck #3263 — two separate owners

#### Synthetic export references

Status: `CLEAN SOURCE MATERIALIZED / OWNED-FORK DRAFT`.

Clean source review: `teamleaderleo/shellcheck#11@83316fa272e4fc1caeffdfe39f946819bc723353`.

Replacement forms such as `export foo=baz` contribute a command-owned synthetic reference immediately before the matching assignment. The first fork candidate ignored every same-name assignment-token reference. That fixed literal replacement but incorrectly suppressed the genuine read in `export foo+=baz`.

The final command-owned adjacency repair skips a reference only when:

1. the reference token is an assignment token;
2. the next flow event is the matching assignment;
3. token identity and variable name match;
4. the assignment belongs to a simple command.

This matches the exported/declaration-style synthetic-reference emitters (`export`, `declare`, `typeset`, and `local -x`) without keying the analysis to command-name strings.

Read-only run `30959236798`, job `92159247440`, against immutable source `a1716be3b847dc23761d35137b43cef7752b3c1d` completed successfully on Ubuntu 24.04 with GHC 9.6.6:

- complete `cabal v2-test test-shellcheck --test-show-details=direct` passed;
- `exe:shellcheck` built;
- literal replacement emitted no SC2030/SC2031;
- append export retained SC2030 and SC2031;
- bare export retained SC2030 and SC2031;
- only `src/ShellCheck/Analytics.hs` changed locally;
- `git diff --check` passed.

Source materialization run `31010993427` succeeded. Independent complete-diff review accepted the exact one-file source head. The final review fence is one commit and one production file, with 27 additions and 4 deletions relative to public base `9af7ee28ce587baadd950b85dd6826a16b9c068d`.

Historical packet PR #1 is closed as superseded. Obsolete execution PR #2 and later carrier generations are retired without merge. No temporary workflow is part of source PR #11.

Evidence class: `target-executed` on one Linux/GHC configuration plus clean owned-fork source materialization and complete-diff acceptance; current ordinary repository builds remain queued.

#### Sourced-function flow

Status: `FOCUSED FALSE POSITIVE CONFIRMED / DISCRIMINATOR MATRIX PREPARED / PRODUCTION FIX NOT SELECTED`.

Owned investigation: `teamleaderleo/shellcheck#3@74c524d8ad7262983d192150927562331c098d9a`.

Focused Fieldwork run `30839352175`, job `91772318148`, executed the primary fixture from its directory:

- the sourced file resolved;
- SC1091 was absent;
- SC2031 remained at the later `COMPREPLY` read.

This is a separate function/include/Bats lifecycle defect. The likely owner is CFG-backed function execution or explicit definition-versus-invocation modeling. Simply skipping function bodies would hide legitimate diagnostics and remains rejected.

A fixture-only matrix now separates:

- setup-only sourcing without the redundant first-test include;
- independent sourcing in each test;
- source, call, and read in one test;
- same content through different include paths;
- a real sourced top-level assignment that must retain warnings;
- a function defined only in the first isolated test.

The matrix is prepared but unexecuted. It carries no behavior claim until run from its own directory against an exact ShellCheck head.

### 3. Cargo #16574 — patch source fetch semantics

Status: `DESIGN HOLD WITH EXECUTED NEGATIVE EVIDENCE`.

Owned fork draft: `teamleaderleo/cargo#1@868c4450a5c5a3bf78ef942cbafe326952373842`.

The broad no-fetch contract still reaches the original source. A separate exact `=0.1.0`, single-path-patch probe also reached the original git source, so the historical exact-version fast path is absent on the tested head.

The exact probe's product classification is valid: Cargo exited 101 after contacting the unreachable original source. The runner lacked `rg`, so its guarded auxiliary source-map capture was empty. Treat the product behavior as executed evidence and the source map as missing, not as a successful fallback map.

No production change is justified without an accepted semantic design for when a patched source may avoid fetching its original source while preserving registry, git, checksum, lockfile, and diagnostic behavior.

### 4. uv #13505 — Windows path-case duplicates in `uv python list`

Status: `ORDINAL-COMPARISON CANDIDATE ACCEPTED FOR EXECUTION / WINDOWS RUN PENDING`.

Owned investigation: `teamleaderleo/uv#39@89eb1dbac9aa018478ded480018faf999097a9ff`.

Historical issue #9979 and PR #12628 intentionally changed `uv python list` to report the queried executable path instead of only `sys.executable`, preserving shim and search-path provenance. The current final listing then deduplicates with case-sensitive Rust path equality. Windows case variants such as `C:\Python311\python.exe` and `c:\python311\python.exe` can therefore survive as duplicate rows.

The selected candidate uses the already-enabled `windows` 0.61 `Win32_Globalization` binding:

- add `uv_windows::path_eq_ignore_case` using `CompareStringOrdinal` over UTF-16 path slices;
- on Windows, scan the small set of already-seen queried paths with ordinal case-insensitive equality;
- on non-Windows platforms, retain the current exact hash-set behavior;
- add a direct Unicode/ASCII case control while preserving a distinct shim path;
- extend the existing duplicate-PATH integration test with case-varied spellings of the same interpreter directories.

The candidate deliberately avoids canonicalization, file identity, and lossy UTF-8 conversion. Intentional symlink, shim, and queried-path entries remain distinct unless their path strings differ only by Windows case semantics.

Independent design review accepted the exact transformer and test boundary for execution.

Read-only execution PR `teamleaderleo/uv#48` targets immutable source `1da26a68629be6ae5fd7f924a7d49ff54763a7df` on Windows Server 2022.

Current authoritative carrier state:

- workflow run `31020377730`;
- job `92355236199`;
- last observed state: `queued`;
- earlier queued generations are superseded harness runs;
- queue state is not source or behavior evidence.

The carrier requires a behavioral baseline failure, passing direct and integration controls for the candidate, rustfmt, diff hygiene, and an exact four-file source/test fence. No product source is published by the carrier.

### 5. uv tool upgrade inventory errors

Status: `OWNED-FORK SOURCE REPAIRED / CI PENDING`.

Owned source: `teamleaderleo/uv#47@9e080cb2a92b35b01f42128902d7a6edfdc57481`.

`uv tool upgrade --all` previously converted a top-level `InstalledTools::tools()` enumeration error into an empty inventory with `unwrap_or_default()`, then printed `Nothing to upgrade` and exited successfully.

The production repair is one line: propagate `tools()?`. Complete-diff review confirmed this preserves the existing per-tool receipt-error policy because missing or malformed receipts remain values inside the returned vector; only failure to enumerate or parse the inventory itself stops the command.

Review repaired two test-only defects before CI:

- the case-sensitive predicate now matches the actual `Not a valid package...` diagnostic;
- the deterministic invalid-directory regression requires only `test-python`, not the unrelated PyPI test feature.

The existing `tool_upgrade_empty` integration test already preserves the genuine empty/up-to-date success path.

Current repository CI run `31020821954` is pending. That state is not execution evidence. Durable coordination remains Fieldwork issue #627.

## Occupied stops

The following reports were not entered because an active implementation or explicit contributor claim already existed at intake:

- Meson #15989 — active implementation PR.
- Meson #16024 — active PR #16029.
- ripgrep #3477 — active PR #3478.
- fd #2067 — active implementation PR.
- Vite #23032 — active implementation PRs.
- Vite #23146 — active PR #23147.
- Vite #22957 — active PR #22958.
- Vite #23108 — explicit contributor claim and later implementation PR.
- Biome #10838 — active PRs #10976 and #10984.
- uv #20949 — active PR #20950.
- uv #20744 — active PR #20787.
- uv #20678 — active PR #20922.
- uv #16209 — active PR #20943.

These ownership checks are dated intake evidence and must be refreshed before any future entry.

## Reserve leads

- Biome #11174 — potentially valid type-flow false positive, but wider analyzer semantics than the completed scout round.
- just #3684 — bounded completion defect with historical overlap requiring a refreshed ownership check.
- fd #2033 — ordering behavior worth characterization after refreshing ownership and fork availability.

## Work order

1. Locate the Meson replacement-authority boundary and add the no-authority negative control before selecting another source candidate.
2. Classify uv Windows run `31020377730`; transfer the receipt, remove its temporary workflow, and materialize only a clean four-file source if the matrix is green.
3. Classify uv PR #47 CI after the reviewed test repairs; keep queue state separate from execution evidence.
4. Execute the ShellCheck sourced-function discriminator matrix only after selecting an exact current-base carrier; retain real top-level and definition-isolation controls.
5. Keep Cargo held until a semantic design is accepted.
6. Refresh public ownership before opening any reserve lead.

## Evidence boundary

This report records owned-fork research, execution, and source-review state. It does not authorize or claim public upstream filing, review, reaction, release, or deployment.
