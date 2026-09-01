# Meson GNU ld.bfd `-rpath-link` PR draft

- Prepared: 2026-09-01
- Upstream contact authorized: false
- Upstream repository: `mesonbuild/meson`
- Candidate repository: `teamleaderleo/meson`
- Candidate branch: `fieldwork/16087-bfd-rpath-link`
- Exact upstream base: `cb59331b47aa1e502d5b49d92e7c75bdf7829e61`
- Candidate head: `01ce61839a638953bf852edff30ce920eeebc98b`
- Candidate stack: one commit, two files

## Title

`linkers: keep rpath-link for modern ld.bfd`

## Body

GNU ld.bfd expands `$ORIGIN` in `-rpath` relative to the DSO carrying the `DT_NEEDED` entry. When the output and a transitive dependency are in different build directories, those link-time search paths can therefore resolve from the wrong directory and allow another library earlier in the search order to win.

This change restores absolute `-rpath-link` arguments for ld.bfd regardless of version. The existing version handling for ld.gold is unchanged.

The regression test covers a modern ld.bfd and verifies that build-tree rpath directories are also included through `-rpath-link`.

## Submission audit

- The source change is the narrow conditional split: modern ld.bfd receives absolute `-rpath-link`; modern ld.gold retains the existing behavior.
- The regression lives in `unittests/linkertests.py`, matching Meson's `*tests.py` unit-test discovery convention and providing a dedicated home for linker-unit coverage.
- The test class is `LinkerTests`; the method is `test_gnuld_rpath_link_modern_bfd`, consistent with existing Meson `gnuld` test naming.
- The fixture forces the fake host machine to Linux so the test exercises RPATH behavior independently of the CI runner platform.
- Expected paths are built with `os.path.join`, avoiding a Linux-only path literal in cross-platform unit runs.
- The branch is expected to remain a single commit directly on the exact upstream base. Recheck upstream head before opening the PR and rebase if it has moved.
- No issue number or outbound GitHub reference is included in this draft.
