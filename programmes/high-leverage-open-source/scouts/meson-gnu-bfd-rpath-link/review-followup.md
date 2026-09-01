# Meson GNU ld.bfd review follow-up

- Date: 2026-09-01
- Upstream contact authorized: false
- Upstream writes performed: none
- Exact upstream base: `cb59331b47aa1e502d5b49d92e7c75bdf7829e61`
- Candidate branch: `teamleaderleo/meson:fieldwork/16087-bfd-rpath-link`
- Candidate head: `f922ee286cebde91dbaf948d06eb14be226a3f8e`

## Review changes

The production change remains the same narrow conditional split: GNU ld.bfd always receives the absolute build-tree `-rpath-link` entries, while GNU gold retains the existing `<2.28` gate.

The regression coverage was strengthened after review:

- `LinkerTests.test_gnuld_rpath_link_version_gate` now pins the complete boundary table: bfd 2.27 yes, bfd 2.28 yes, gold 2.27 yes, gold 2.28 no.
- `BfdLinkerTests.test_rpath_link_transitive_dependency` now drives a real Meson project through GNU ld.bfd.
- The real fixture builds `liba` in `src`, `libb` in `mid`, and the final executable in `mid/tests`; the executable links only `libb`.
- An incompatible same-SONAME `liba.so.1` is placed earlier in `LD_LIBRARY_PATH`, so the unfixed link demonstrates the real transitive-dependency search failure rather than merely checking generated argument text.
- The fixture lives under `test cases/unit/140 rpath link bfd`.

## Fork execution proof

Fork-owned verifier run: https://github.com/teamleaderleo/meson/actions/runs/33538417444

Job: `99958329173`

Runner: Ubuntu 24.04

Result: success

**[observed: red synthetic]** On the unfixed source, the boundary test failed specifically for ld.bfd 2.28:

`AssertionError: '-Wl,-rpath-link,/build/lib' not found in ['-Wl,-rpath,$ORIGIN/../lib']`

**[observed: red integration]** Meson configured the fixture with `C linker for the host machine: cc ld.bfd 2.42`. The final executable link line contained only the `$ORIGIN` rpath and `mid/libb.so.1`; it did not contain the absolute build-tree `-rpath-link`. GNU ld.bfd then failed with:

`mid/libb.so.1: undefined reference to 'a_good'`

This is the intended real failure discriminator: the incompatible same-SONAME library won before ld.bfd could reach the correct transitive dependency through `libb`'s runtime path.

**[observed: green]** After applying the candidate source edit, all of the following passed in the same job:

- `LinkerTests.test_gnuld_rpath_link_version_gate`
- `BfdLinkerTests.test_rpath_link_transitive_dependency`
- `InternalTests.test_compiler_args_class_gnuld`
- Python `compileall` for the touched Python files
- `git diff --check`

The integration test completed normally rather than skipping.

## Carrier audit

The temporary review workflow was kept outside the upstream-facing candidate commit. It was removed from the fork default branch after the run was queued, and the disposable review refs were reset after the proof completed.

The upstream-facing compare remains one commit directly on the exact upstream base. No upstream interaction was performed.
