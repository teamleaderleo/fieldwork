# Scout report: Meson GNU ld.bfd `-rpath-link` regression

- Date: 2026-09-01
- Programme: high-leverage-open-source
- Worker: ChatGPT
- Claim scope: build/link correctness
- Upstream contact authorized: false
- Upstream writes performed: none
- Winner implementation surface: owned fork `teamleaderleo/meson`

## Question

Can we find a foundational-tooling bug where a small source change prevents a high-consequence deterministic correctness failure, and where the regression can be proved with a stable assertion from the exact current upstream revision?

## Finalists

| Rank | Candidate | Consequence | Proofability | Decision |
| --- | --- | ---: | ---: | --- |
| 1 | Meson #16087: modern GNU ld.bfd loses absolute `-rpath-link` search paths | 5/5 | 5/5 | Winner; implemented on owned fork |
| 2 | Ghostty #11935: tmux control parser rejects an exact-`max_bytes` line terminator | 4/5 | 5/5 | Rescue lane; an existing focused PR already carries the fix/test |
| 3 | Meson #15865: dependency introspection silently drops `declare_dependency()` objects | 4/5 | 5/5 | Scout-only; proof is crisp, but intended introspection semantics are still under upstream discussion |

## Winner: Meson #16087

Third-party issue: https://redirect.github.com/mesonbuild/meson/issues/16087

### Why it crosses the bar

**[observed: issue]** The open regression report shows that Meson stopped emitting `-rpath-link` for GNU ld.bfd at version 2.28+, relying on `$ORIGIN` entries in `-rpath`. GNU ld.bfd expands `$ORIGIN` for secondary-dependency lookup relative to the shared object carrying `DT_NEEDED`, which can differ from the directory of the output being linked. In a multi-directory build, the generated relative search entries can therefore point at the wrong place.

**[observed: source]** At the exact upstream head used here, `GnuLikeDynamicLinkerMixin.build_rpath_args()` still gates both `ld.bfd` and `ld.gold` behind `version < 2.28` before emitting absolute `-rpath-link` arguments.

**[observed: history]** The gate came from https://redirect.github.com/mesonbuild/meson/pull/14349. Its source comment says modern `$ORIGIN` support makes a duplicate `-rpath-link` unnecessary. Current upstream discussion has disproved that premise for ld.bfd and called for a partial rollback.

**[interpretation]** Consequence is 5/5 because the link can succeed after resolving a transitive dependency from an unrelated installed/system copy. That is wrong generated linker input leading to the wrong DSO selection, with a successful build masking the error.

**[interpretation]** Proofability is 5/5 because the faulty behavior reduces to one deterministic textual invariant in linker arguments. No installed library, timing, process tracing, network access, or human visual judgment is needed for the regression.

### Narrow invariant

For GNU ld.bfd, every build-tree rpath directory supplied to `build_rpath_args()` must also produce an absolute `-rpath-link` argument, regardless of the bfd version. GNU gold keeps the pre-2.28 version gate.

Stable discriminator for the fixture:

- fake build directory: `/build`
- target rpath directory: `lib`
- linker: `GnuBFDDynamicLinker`, version `2.40`
- required emitted argument: `-Wl,-rpath-link,/build/lib`

Before the fix, the generated args contain only `-Wl,-rpath,$ORIGIN/../lib` and the assertion fails. After the fix, the required absolute `-rpath-link` is present.

## Exact state and source/test map

- Upstream repository: `mesonbuild/meson`
- Upstream branch: `master`
- Exact upstream head at selection and post-implementation recheck: `cb59331b47aa1e502d5b49d92e7c75bdf7829e61`
- Source: `mesonbuild/linkers/linkers.py`
- Function: `GnuLikeDynamicLinkerMixin.build_rpath_args()`
- Regression: `unittests/linkerstests.py::LinkerTests.test_gnuld_rpath_link_modern_bfd`
- Test discovery: `run_unittests.py` discovers `unittests/*tests.py`

## Overlap check

Checked current open Meson PRs on 2026-09-01 for `16087`, `rpath-link`, and `$ORIGIN`. There is no open PR directly fixing #16087. Nearby open RPATH/linker PRs concern different failure modes.

The issue is assigned and has a confirmed diagnosis, yet no implementation PR currently occupies the lane.

## Patch

Owned fork branch: https://github.com/teamleaderleo/meson/tree/fieldwork/16087-bfd-rpath-link

Exact two-commit patch stack on the exact upstream base:

1. Test-only commit `7d1b961786eb94fd5e8d5aa3aee68235b3459a25` — `tests: cover modern ld.bfd rpath-link`
2. Fix commit `84d6a54d0794c08f5cd6767ffa611d3019738075` — `linkers: keep rpath-link for modern ld.bfd`

Comparison from upstream base to patch head:

- ahead by: 2
- behind by: 0
- changed files: 2
- `unittests/linkerstests.py`: +26
- `mesonbuild/linkers/linkers.py`: +6 / -5

The source edit changes the version condition to emit `-rpath-link` for all `ld.bfd` versions while preserving the `<2.28` gate for `ld.gold`, and corrects the adjacent comment to describe the ld.bfd `$ORIGIN` behavior.

## Red/green proof and CI

Fork-only GitHub Actions run: https://github.com/teamleaderleo/meson/actions/runs/33530190873

- workflow run: `33530190873`
- job: `99931095415`
- runner: Ubuntu 24.04
- result: success

**[observed: red]** The verifier checked out the test-only commit exactly and ran:

`python3 run_unittests.py LinkerTests.test_gnuld_rpath_link_modern_bfd`

The test failed deterministically with:

`AssertionError: '-Wl,-rpath-link,/build/lib' not found in ['-Wl,-rpath,$ORIGIN/../lib']`

**[observed: green]** After the single source edit, the same focused regression passed. The nearby existing GNU linker argument unit `InternalTests.test_compiler_args_class_gnuld` also passed. `compileall` for the touched Python files and `git diff --check` passed.

The verifier then committed and pushed the fix commit to the owned candidate branch.

## CI carrier audit

Canonical upstream CI is read-only from this worker, so the proof used a fork-owned temporary carrier. The carrier lived only on the owned fork default branch and remained outside the upstream-facing two-commit candidate stack.

Two early carrier-harness attempts failed before any candidate source mutation. They were treated as harness failures, and the candidate stayed pinned to the exact upstream base until the test-only commit was created. The successful verifier performed the final red/green proof and pushed the fix.

Carrier retirement commit: `9707672782266c32aee4a462d77b9dffda10e8e4` — `Retire Meson 16087 verifier`.

Post-run check: `.github/workflows/fieldwork-16087-verify.yml` is absent from fork `master`. The disposable trigger ref was reset to that post-retirement fork tip. The internal fork PR used to trigger execution was closed unmerged. Upstream remained untouched throughout.

## Fork receipts

- owned fork: `teamleaderleo/meson`
- candidate branch: `fieldwork/16087-bfd-rpath-link`
- exact upstream base: `cb59331b47aa1e502d5b49d92e7c75bdf7829e61`
- test commit: `7d1b961786eb94fd5e8d5aa3aee68235b3459a25`
- fix commit: `84d6a54d0794c08f5cd6767ffa611d3019738075`
- verifier run: `33530190873`
- verifier job: `99931095415`
- carrier retirement: `9707672782266c32aee4a462d77b9dffda10e8e4`
- upstream contact authorized: false
- upstream interaction: none

## Finalist 2: Ghostty #11935

Third-party issue: https://redirect.github.com/ghostty-org/ghostty/issues/11935

Existing fix PR: https://redirect.github.com/ghostty-org/ghostty/pull/12866

- Score: Consequence 4/5; Proofability 5/5.
- Current upstream `main` inspected during the scout still has the buffer-limit check before parser-state handling.
- Exact failure boundary: payload length equals `max_bytes`; the following newline is a terminator that would not be stored, yet the early guard returns `OutOfMemory`, silently drops the notification, and places the parser in `.broken`.
- The fixture is a tiny byte sequence with a direct parser-result assertion.
- PR #12866 is open, mergeable, one commit, one changed file, with the exact regression test and the narrow guard relocation. It was opened 2026-05-31 and has seen no update since that date.

Decision: strong rescue/refresh lane; duplicating the patch would add little value while the focused existing PR remains viable.

## Finalist 3: Meson #15865

Third-party issue: https://redirect.github.com/mesonbuild/meson/issues/15865

- Score: Consequence 4/5; Proofability 5/5.
- Regression: `meson introspect --dependencies` returns `[]` for a variable holding `declare_dependency()` where Meson 1.9.2 returned an internal dependency record with `meson_variables`.
- Current source inspection shows introspection serializing dependency fields including `ext_deps` and `meson_variables`, while internal dependencies themselves carry `ext_deps`; other Meson paths already recurse through those wrapped external dependencies.
- A downstream SciPy use case depends on mapping targets to wrapped external dependency metadata for packaging.
- Current open-PR search found no direct fix.

Decision: crisp JSON proof and meaningful package-metadata consequence, but upstream is still discussing intended introspection semantics. That makes #16087 the cleaner correctness patch.

## Rejected lanes

- Meson NVHPC depfile omission: high consequence and excellent proof, but an active focused upstream PR already owns the fix.
- jj head-removal error path: serious loss mode, but an active PR already owns the fix.
- jj trailing-CR conflict loss: strong deterministic data-loss bug, already fixed on current upstream.
- Helix exit panic: deterministic, but an active tested PR already owns the lane.
- deep nested jj revset stack overflow: reproducible, yet lower real-world consequence than the winner.
- concurrency/performance and environment-sensitive reports: rejected where the regression proof would depend on scheduling, installed state, or flaky external conditions.

## Recommendation

Keep the Meson #16087 patch as the prepared candidate. It has the strongest combination found in this scout: wrong-library selection behind a successful link, a single stable emitted-argument discriminator, a one-condition implementation change, exact-current-head provenance, separable test/fix commits, and a successful fork-owned red/green verifier.

Any upstream issue comment or PR remains outside this worker's authorization boundary until a fresh bounded greenlight is recorded.
