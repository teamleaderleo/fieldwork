# Meson GNU ld.bfd `-rpath-link` PR draft

- Prepared: 2026-09-01
- Upstream contact authorized: false
- Upstream repository: `mesonbuild/meson`
- Candidate repository: `teamleaderleo/meson`
- Candidate branch: `fieldwork/16087-bfd-rpath-link`
- Exact upstream base: `cb59331b47aa1e502d5b49d92e7c75bdf7829e61`
- Candidate head: `f922ee286cebde91dbaf948d06eb14be226a3f8e`
- Candidate stack: one commit

## Title

`linkers: keep rpath-link for ld.bfd >= 2.28`

## Body

GNU ld.bfd expands `$ORIGIN` in `-rpath` relative to the DSO carrying the `DT_NEEDED` entry. When the output and a transitive dependency are in different build directories, those link-time search paths can therefore resolve from the wrong directory and allow another library earlier in the search order to win.

This change restores absolute `-rpath-link` arguments for ld.bfd regardless of version, while leaving the existing version handling for ld.gold unchanged.

The regression coverage checks the ld.bfd/ld.gold behavior at the 2.28 boundary and reproduces the transitive-dependency failure with a real ld.bfd link.

## Submission audit

- The production change remains the narrow conditional split: all ld.bfd versions receive absolute `-rpath-link`; ld.gold retains the existing `<2.28` gate.
- `LinkerTests.test_gnuld_rpath_link_version_gate` covers the complete changed boundary: bfd 2.27 yes, bfd 2.28 yes, gold 2.27 yes, gold 2.28 no.
- The synthetic fixture uses a tuple for `determine_rpath_dirs()` and builds expected paths with `os.path.join`.
- `BfdLinkerTests.test_rpath_link_transitive_dependency` uses a real Linux ld.bfd link with `A <- B <- executable` across different build directories and an incompatible same-SONAME `liba.so.1` earlier in `LD_LIBRARY_PATH`.
- The real-link test verifies that Meson is actually configured with linker id `ld.bfd` before building.
- The integration fixture lives under `test cases/unit/140 rpath link bfd`, the existing home for unit-test-driven Meson projects.
- The source condition remains within Meson's 120-column limit.
- The branch remains one commit directly on the exact upstream base as of the latest recheck.
- No issue number or outbound GitHub reference is included in this internal draft.
