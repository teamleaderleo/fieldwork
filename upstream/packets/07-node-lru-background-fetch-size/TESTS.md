# Tests and receipts — Unit 07 `backgroundFetchSize` snapshot

## Exact identity

- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical one-commit candidate: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- changed files: `src/index.ts`, `test/background-fetch-size.ts`;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`.

## Baseline characterization

Released `lru-cache@11.5.2` probes established that invalid `backgroundFetchSize` values can enter provisional accounting: `NaN` poisons calculated size, negative/fractional values are accepted, infinity disrupts provisional caching/coalescing, and runtime strings can reach coercive arithmetic. Zero remains coherent and coalesced.

## Final regression coverage

The feature test preserves the upstream `t.clock` setup and keeps one case for each distinct supported behavior boundary:

- constructor rejection for representative invalid numeric and runtime non-number values, including a hostile coercion object;
- zero and positive integer acceptance;
- invalid post-construction mutation rejected before provider dispatch;
- synchronous callback mutation not changing the current fetch's captured charge;
- later operations observing later valid mutation, with same-key in-flight coalescing preserved;
- no-size caches ignoring irrelevant mutation;
- stale refresh using the existing entry size;
- zero-size same-key coalescing.

A previous test deliberately modified a hidden background-fetch receipt through `unsafeExposeInternals()` and reinserted it. It was removed because upstream documents mutation of exposed internals as unsupported and potentially breakage-inducing. The test suite no longer treats malformed private state as a regression contract.

## Prior execution evidence

Earlier executions on the unchanged production blob established:

- focused behavior/build/OXLint/Prettier/diff hygiene success;
- Ubuntu Node 24/25 success;
- macOS Node 24/25 success;
- benchmark success;
- Windows Node 24/25 Bash/PowerShell stopping before product test discovery because the unchanged repository TAP configuration could not load `@tapjs/clock`.

The Windows condition is an unchanged-base harness limit; this contribution doesn't modify `.taprc`, package dependencies, or the lockfile.

## Final exact-head execution

Because `test/background-fetch-size.ts` changed, previous test-tree receipts are historical support only. Fresh final-head runs are the source of truth:

- CI `31231433021`: queued at this record update;
- Benchmarks `31231433009`: queued at this record update.

Do not claim final exact-head success until those runs execute.

## Final judgment

`OWNER REVIEW / EXACT-HEAD EXECUTION PENDING`.

The final suite focuses on plausible regressions of the public option and fetch behavior, not exhaustive or deliberately corrupted internal states. No public upstream interaction occurred.
