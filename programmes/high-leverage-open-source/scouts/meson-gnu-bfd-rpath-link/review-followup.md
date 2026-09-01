# Meson GNU ld.bfd review follow-up

- Date: 2026-09-01
- Upstream contact authorized: false
- Upstream writes performed: none
- Exact upstream base: `be6841aab8318b61b620c6c9375137570a01b89d`
- Candidate branch: `teamleaderleo/meson:fieldwork/16087-bfd-rpath-link`
- Candidate head: `ed3d0bcccfb713e369ee4fddb95da23e825b72b1`

## Review changes

The production change remains the same narrow conditional split: GNU ld.bfd always receives the absolute build-tree `-rpath-link` entries, while GNU gold retains the existing `<2.28` gate.

The regression coverage was strengthened after review:

- `LinkerTests.test_gnuld_rpath_link_version_gate` pins the complete boundary table: bfd 2.27 yes, bfd 2.28 yes, gold 2.27 yes, gold 2.28 no.
- `BfdLinkerTests.test_rpath_link_transitive_dependency` drives a real Meson project through GNU ld.bfd.
- The real fixture builds `liba` in `src`, `libb` in `mid`, and the final executable in `mid/tests`; the executable links only `libb`.
- An incompatible same-SONAME `liba.so.1` is placed earlier in `LD_LIBRARY_PATH`, so the unfixed link demonstrates the real transitive-dependency search failure rather than merely checking generated argument text.
- The fixture lives under `test cases/unit/140 rpath link bfd`.

The final external review considered the real reproducer valid, the build-only assertion correct, the four-case boundary test appropriate, the dedicated linker test module justified, and the production condition correctly scoped. Suggested environment refinements were explicitly non-blocking polish rather than submission requirements.

## Fork execution proof

Fork-owned verifier run: `33538417444`

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

## Final rebase audit

Upstream advanced by one unrelated interpreter-array commit after review. The candidate was rebased onto the exact current upstream head without changing the reviewed patch blobs. The final compare is one commit ahead and zero commits behind.

The final commit retains the reviewed title and message. Its parent is the exact upstream base above, and its diff contains the same production edit plus the same eight test-fixture paths as the reviewed candidate.

A duplicate post-rebase hosted-runner carrier was prepared, but GitHub had not assigned a runner while the final audit was being completed. Submission is not conditioned on that redundant run because the substantive real-link red/green proof already passed and the rebase preserved the reviewed patch byte-for-byte.

## Carrier audit

Temporary fork-only workflow files were removed from the fork default branch. Disposable import, rebase, and verifier refs were reset after use. A temporary fork-only PR was used solely to import the exact new upstream Git object into the fork; it did not create an upstream pull request or upstream review interaction.

The upstream-facing candidate is one commit directly on the exact current upstream base. No upstream interaction was performed.
