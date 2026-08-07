# Tests and receipts — Unit 07 `backgroundFetchSize` snapshot

## Exact identity

- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical one-commit candidate: `4a80ff2cec44d259907e474336a64ec984a465a5`;
- changed files: `src/index.ts`, `test/background-fetch-size.ts`;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `00b81ade21068c55c23623d95992acbe9f26ebb2`.

## Baseline characterization

Released `lru-cache@11.5.2` probes established that invalid `backgroundFetchSize` values can enter provisional accounting: `NaN` poisons calculated size, negative/fractional values are accepted, infinity disrupts provisional caching/coalescing, and runtime strings can reach coercive arithmetic. Zero remains coherent and coalesced.

## Final focused coverage

The final feature test preserves the upstream `t.clock` setup and uses representative cases rather than an exhaustive type inventory.

It covers:

- constructor rejection for negative, fractional, `NaN`, infinity, string, symbol, and hostile-coercion-object values;
- zero and positive integer acceptance;
- invalid post-construction mutation rejected before provider dispatch;
- synchronous callback mutation not changing the current operation's captured charge;
- later operations observing later valid mutation;
- no-size caches ignoring irrelevant mutation;
- stale refresh using the existing entry size;
- zero-size same-key coalescing;
- corrupt internal provisional receipt rejection.

This reduces the feature-test addition from +269 lines to +190 while preserving every distinct behavioral invariant needed by the source change.

## Prior execution evidence

Earlier executions on the unchanged production blob established:

- focused behavior/build/OXLint/Prettier/diff hygiene success;
- Ubuntu Node 24/25 success;
- macOS Node 24/25 success;
- benchmark success;
- Windows Node 24/25 Bash/PowerShell stopping before product test discovery because the unchanged repository TAP configuration could not load `@tapjs/clock`.

The Windows condition is an unchanged-base harness limit; this contribution does not modify `.taprc`, package dependencies, or the lockfile.

## Final exact-head execution

Because `test/background-fetch-size.ts` was simplified, prior test-tree receipts are historical support only. Fresh final-head runs are the source of truth for the final tree:

- CI `31227785209`: queued at this record update;
- Benchmarks `31227785205`: queued at this record update.

Do not claim final exact-head success until those runs execute.

## Final judgment

`OWNER REVIEW / EXACT-HEAD EXECUTION PENDING`.

The test organization and coverage are now aligned with the repository's feature-focused style while keeping the source diff to the original two-file ownership boundary. No public upstream interaction occurred.
