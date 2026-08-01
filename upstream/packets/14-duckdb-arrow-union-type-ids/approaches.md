# Approaches

## 1. Characterize before changing source

Use sparse logical IDs `{3, 7}` so positional-index behavior fails deterministically, then repeat with parent offsets. Result: successful expected-failure characterization in `teamleaderleo/duckdb#12` at `ed05ac593498fb4f95546ec591824ee23429088d`.

## 2. Minimal logical-ID mapping

Parse the sparse union schema codes once, retain a logical-ID to child-index map in union-specific Arrow type information, and resolve row tags through that map. Result: targeted candidate and `Main` passed in `teamleaderleo/duckdb#14` at `c962ece64c1356015aef15a37c0cc636f63b376b`.

## 3. Harden malformed input

Add duplicate-ID rejection, type-ID storage validation, validity checks, explicit byte reads, and malformed `int16` coverage. Result: `Main` passed in `teamleaderleo/duckdb#16` at `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`; targeted positive mapping tests failed after a successful debug build.

## 4. Materialize a clean source branch

Planned branch: `fix/arrow-sparse-union-type-id-map` from exact base `2c9e51aa33dd07e928edae66304430aeb038edd7`.

Required content:

- product source changes only;
- focused C++ regression tests;
- no Fieldwork workflows or patch-generation scripts;
- no unrelated formatter churn;
- one readable source commit or a small source/test sequence.

This approach remains pending because the passing minimal patch exists as CI-generated material and the hardening run lacks an exposed failed assertion. An empty branch or a copy of carrier commits would misrepresent review state.

## Recommended continuation

1. Download the retained artifact from run `30659465467` and inspect the complete test output from GitHub Actions UI or rerun the targeted command locally.
2. Identify whether the hardening failure comes from `int8` buffer interpretation, offset handling, duplicate detection, or test construction.
3. Apply the verified implementation to a branch from `2c9e51aa33dd07e928edae66304430aeb038edd7`.
4. Strip the five unrelated formatting-only files from the generated patch.
5. Add the focused test as source, run the targeted test, formatter/lint checks, and the relevant DuckDB test suite.
6. Update this packet and #435 with the resulting exact head.