# Developer tools and build systems scout — Round 006

Updated: 2026-08-05

Authority boundary: owned repositories and forks only. No upstream comments, reactions, claims, branches, or pull requests were created.

## Final dispositions

### 1. Meson #15998 — CMake CUDA standard normalization

Status: `FOCUSED MODEL GREEN / PRECEDENCE HOLD`.

Owned source: `teamleaderleo/meson#3@8418a967ba268d323477752fe4fc17e8cf8f8256`.

The CMake converter maps CMake `CUDA` file groups to Meson language `cuda`, but the standard-normalization pass visited only C and C++. The candidate includes CUDA in that existing pass.

Execution-only carrier `teamleaderleo/meson#4` completed successfully:

- focused workflow run `30858277753`: success;
- baseline synthetic File API control failed as expected;
- candidate control passed;
- `-std=c++17` became `cuda_std=c++17`;
- the raw duplicate was removed;
- an unrelated NVCC generate-code flag survived;
- Python compilation and diff hygiene passed.

The carrier receipt and before/after outputs are retained on source PR #3. Carrier PR #4 closed without merge.

Evidence class: `compiler-free-target-executed` for language classification and raw-flag deduplication.

The candidate is not ready because precedence remains unproved among:

- a standard reported by CMake File API compile flags;
- a traced explicit `CUDA_STANDARD` target property or CMake global;
- the top-level Meson `cuda_std` project default;
- an explicit CMake subproject override.

Next source work is a three-way or four-way precedence matrix, not another execution trigger for the already-green classification change.

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

Read-only run `30959236798`, job `92159247440`, against immutable source `a1716be3b847dc23761d35137b43cef7752b3c1d` completed successfully on Ubuntu 24.04 with GHC 9.6.6:

- complete `cabal v2-test test-shellcheck --test-show-details=direct` passed;
- `exe:shellcheck` built;
- literal replacement emitted no SC2030/SC2031;
- append export retained SC2030 and SC2031;
- bare export retained SC2030 and SC2031;
- only `src/ShellCheck/Analytics.hs` changed locally;
- `git diff --check` passed.

Source materialization run `31010993427` succeeded. The final review fence is one commit and one production file, with 27 additions and 4 deletions relative to public base `9af7ee28ce587baadd950b85dd6826a16b9c068d`.

Historical packet PR #1 is closed as superseded. Obsolete execution PR #2 and later carrier generations are retired without merge. No temporary workflow is part of source PR #11.

Evidence class: `target-executed` on one Linux/GHC configuration plus clean owned-fork source materialization; broader compiler and OS matrix not run.

#### Sourced-function flow

Status: `FOCUSED FALSE POSITIVE CONFIRMED / PRODUCTION FIX NOT SELECTED`.

Owned investigation: `teamleaderleo/shellcheck#3@898191ab5665e7c4ba01101a15e4c6a8776611f2`.

Focused Fieldwork run `30839352175`, job `91772318148`, executed the fixture from its directory:

- the sourced file resolved;
- SC1091 was absent;
- SC2031 remained at the later `COMPREPLY` read.

This is a separate function/include/Bats lifecycle defect. The likely owner is CFG-backed function execution or explicit definition-versus-invocation modeling. Simply skipping function bodies would hide legitimate diagnostics and remains rejected.

### 3. Cargo #16574 — patch source fetch semantics

Status: `DESIGN HOLD WITH EXECUTED NEGATIVE EVIDENCE`.

Owned fork draft: `teamleaderleo/cargo#1@868c4450a5c5a3bf78ef942cbafe326952373842`.

The broad no-fetch contract still reaches the original source. A separate exact `=0.1.0`, single-path-patch probe also reached the original git source, so the historical exact-version fast path is absent on the tested head.

The exact probe's product classification is valid: Cargo exited 101 after contacting the unreachable original source. The runner lacked `rg`, so its guarded auxiliary source-map capture was empty. Treat the product behavior as executed evidence and the source map as missing, not as a successful fallback map.

No production change is justified without an accepted semantic design for when a patched source may avoid fetching its original source while preserving registry, git, checksum, lockfile, and diagnostic behavior.

### 4. uv #13505 — Windows path-case duplicates in `uv python list`

Status: `SOURCE/HISTORY MAPPED / WINDOWS EXECUTION REQUIRED`.

Owned investigation: `teamleaderleo/uv#39@708fe0b557a9ac7a0fc98394477ba1771f52f977`.

Historical issue #9979 and PR #12628 intentionally changed `uv python list` to report the queried executable path instead of only `sys.executable`, preserving shim and search-path provenance. The current final listing then deduplicates with `FxHashSet<PathBuf>`, whose lexical equality remains case-sensitive. Windows case variants such as `C:\Python311\python.exe` and `c:\python311\python.exe` can therefore survive as duplicate rows.

The packet contains a candidate Windows-only case-folded key and unit controls, but no production source change is applied. A final implementation must first use or introduce a helper matching Windows ordinal case-insensitive path semantics without lossy string conversion.

Do not use file identity or canonicalization for this fix: intentional symlink, shim, and queried-path entries are part of the command's observable provenance and may need to remain distinct.

Next gate: Windows-targeted unit and integration execution proving case-only duplicates collapse while distinct queried paths remain visible.

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

1. Build Meson CUDA standard precedence controls on source PR #3.
2. Locate or design a Windows ordinal path-key helper for uv PR #39, then run Windows-specific controls before applying production source.
3. Keep the ShellCheck sourced-function case on investigation PR #3 until a current-base architecture is selected.
4. Keep Cargo held until a semantic design is accepted.
5. Refresh public ownership before opening any reserve lead.

## Evidence boundary

This report records owned-fork research, execution, and source-review state. It does not authorize or claim public upstream filing, review, reaction, release, or deployment.
