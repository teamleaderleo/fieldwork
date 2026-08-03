# Developer tools and build systems scout — Round 006

Date: 2026-08-04

Authority boundary: owned repositories and forks only. No upstream comments, reactions, claims, branches, or pull requests were created.

## Active work

### 1. Meson #15998 — CMake CUDA standard normalization

Status: active fork probe.

Owned fork branch: `teamleaderleo/meson:fieldwork/15998-cmake-cuda-std`  
Owned fork draft: `teamleaderleo/meson#3`

The CMake converter maps CMake `CUDA` file groups to Meson language `cuda`, but the standard-normalization pass only visits C and C++. The prepared candidate includes CUDA in that existing pass. A compiler-free synthetic File API regression checks that `-std=c++17` becomes `cuda_std=c++17`, the raw duplicate is removed, and unrelated NVCC flags survive.

The candidate remains deliberately narrow. It does not yet settle precedence among a CMake-discovered standard, a top-level Meson `cuda_std`, and an explicit CMake subproject override.

Execution carrier: `teamleaderleo/meson#4`, run `30858277753`.

### 2. ShellCheck #3263 — synthetic export references

Status: structural repair executing.

The first narrow fix passed the full ShellCheck suite, but self-review found that token-only filtering could suppress a real append read in `export foo+=bar`. The next discriminator uses variable-flow order: a replacement export has one matching reference immediately before the assignment, while an append has an earlier duplicate genuine read.

Execution run: `teamleaderleo/shellcheck` run `30857425997`.

The separate sourced-function flow defect remains isolated on fork draft `teamleaderleo/shellcheck#3`.

### 3. Cargo #16574 — patch source fetch semantics

Status: design hold with executed negative evidence.

The broad no-fetch contract still reaches the original source. A separate exact `=0.1.0`, single-path-patch probe also reached the original git source, so the historical exact-version fast path is absent on the tested head. No production change is justified without an accepted semantic design.

Owned fork draft: `teamleaderleo/cargo#1`.

## Occupied stops

The following reports were not entered because an active implementation or explicit contributor claim already exists:

- Meson #15989 — active PR #16003.
- Meson #16024 — active PR #16029.
- ripgrep #3477 — active PR #3478.
- fd #2067 — active PR #2068.
- Vite #23032 — active PR #23033.
- Vite #23146 — active PR #23147.
- Vite #22957 — active PR #22958.
- Vite #23108 — contributor reproduced the defect and explicitly stated an intent to take it.
- Biome #10838 — active PRs #10976 and #10984.

## Reserve leads

- Biome #11174 — potentially valid type-flow false positive, but wider analyzer semantics than the current Meson lane.
- just #3684 — bounded completion defect, but no owned fork currently installed.
- fd #2033 — ordering behavior worth characterization, but no owned fork currently installed.

## Work order

1. Resolve ShellCheck structural repair at its exact canonical head.
2. Execute Meson #15998 before/after focused regression and retain the source commit only if green.
3. Build Meson precedence controls before any readiness claim.
4. Keep Cargo held for accepted design.
5. Recheck ownership immediately before opening any reserve lane.
