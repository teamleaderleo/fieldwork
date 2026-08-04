# Developer tools and build systems scout — Round 006

Updated: 2026-08-04

Authority boundary: owned repositories and forks only. No upstream comments, reactions, claims, branches, or pull requests were created.

## Final dispositions

### 1. Meson #15998 — CMake CUDA standard normalization

Status: `FOCUSED MODEL GREEN / PRECEDENCE HOLD`.

Owned source: `teamleaderleo/meson#3@782f344a945e3824fe5dbe4327831eb33b77f46b`.

The CMake converter maps CMake `CUDA` file groups to Meson language `cuda`, but the standard-normalization pass visited only C and C++. The candidate includes CUDA in that existing pass.

Execution-only carrier `teamleaderleo/meson#4@586ffaf4fecb5f98b2a934013e5f39124f56c779` completed successfully:

- focused workflow run `30858277753`: success;
- file-format run `30858277637`: success;
- baseline synthetic File API control failed as expected;
- candidate control passed;
- `-std=c++17` became `cuda_std=c++17`;
- the raw duplicate was removed;
- unrelated NVCC flags survived;
- Python compilation and diff hygiene passed.

The carrier receipt and before/after outputs were transferred to source PR #3. Carrier PR #4 closed without merge.

The candidate is not ready because precedence remains unproved among:

- a CMake-discovered CUDA standard;
- top-level Meson `cuda_std`;
- an explicit CMake subproject override.

Next source work is a three-way precedence matrix, not another execution trigger.

### 2. ShellCheck #3263 — two separate owners

#### Synthetic export references

Status: `REPAIR / CURRENT SOURCE RECEIPT REQUIRED`.

Owned source PR `teamleaderleo/shellcheck#1` contains the literal-export repair and a later append-read self-review. The original candidate passed the full `test-shellcheck` suite, but token-only filtering could suppress a genuine read in `export foo+=bar`.

A later execution carrier attempted a broader structural transformation, but run `30857425997`, job `91831573714`, failed inside its own source transformer with:

```text
unexpected singleFn body
```

Exact-base verification passed at execution time. Haskell formatting, compilation, tests, lint, and source publication did not run.

The pinned base `269f6cf2dd42b1749004bdfaeee225c7c7fbc04d` and product branch `fieldwork/sourced-function-append-read` are no longer reachable, and the run retained no downloadable source artifact. Execution carrier `teamleaderleo/shellcheck#4` is therefore retired without merge as unreproducible.

Do not treat that carrier as evidence for or against the current source PR. Any renewed append-read repair must begin from a current reachable base with a new exact candidate and read-only carrier.

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

Owned fork draft: `teamleaderleo/cargo#1`.

The broad no-fetch contract still reaches the original source. A separate exact `=0.1.0`, single-path-patch probe also reached the original git source, so the historical exact-version fast path is absent on the tested head.

No production change is justified without an accepted semantic design for when a patched source may avoid fetching its original source while preserving registry, git, checksum, lockfile, and diagnostic behavior.

## Occupied stops

The following reports were not entered because an active implementation or explicit contributor claim already existed at intake:

- Meson #15989 — active PR #16003.
- Meson #16024 — active PR #16029.
- ripgrep #3477 — active PR #3478.
- fd #2067 — active PR #2068.
- Vite #23032 — active PR #23033.
- Vite #23146 — active PR #23147.
- Vite #22957 — active PR #22958.
- Vite #23108 — contributor reproduced the defect and stated intent to take it.
- Biome #10838 — active PRs #10976 and #10984.

These ownership checks are dated intake evidence and must be refreshed before any future entry.

## Reserve leads

- Biome #11174 — potentially valid type-flow false positive, but wider analyzer semantics than the completed scout round.
- just #3684 — bounded completion defect; no owned fork was available at intake.
- fd #2033 — ordering behavior worth characterization; no owned fork was available at intake.

## Work order

1. Build Meson CUDA standard precedence controls on source PR #3.
2. Keep the ShellCheck sourced-function case on investigation PR #3 until a current-base architecture is selected.
3. Revalidate the current ShellCheck synthetic-export source independently; do not reuse retired carrier #4.
4. Keep Cargo held until a semantic design is accepted.
5. Refresh public ownership before opening any reserve lead.

## Evidence boundary

This report records owned-fork research and execution state. It does not authorize or claim public upstream filing, review, reaction, release, or deployment.
