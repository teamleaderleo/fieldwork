# Review — Unit 07 `backgroundFetchSize` snapshot

## Review subject

- source PR: `teamleaderleo/node-lru-cache#2`;
- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical head: `4a80ff2cec44d259907e474336a64ec984a465a5`;
- fence: `src/index.ts`, `test/background-fetch-size.ts`;
- canonical relation: ahead 1, behind 0;
- total diff: +223 / -2.

Final blobs:

- `src/index.ts`: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- `test/background-fetch-size.ts`: `00b81ade21068c55c23623d95992acbe9f26ebb2`.

## Source findings

No blocking production-source defect remains.

- `isNonNegativeInt()` checks primitive number type before the existing positive-integer helper, so symbols, objects, and hostile conversion hooks are not coerced.
- zero and positive integers remain valid.
- the missing-key receipt is captured before the Promise executor invokes user `fetchMethod` synchronously.
- stale refresh continues to use the existing entry size and does not consume the provisional receipt.
- caches without size tracking remain insensitive to later irrelevant field mutation.
- `BackgroundFetch.__size` is optional in the exported type, while the accounting boundary rejects an absent or corrupt receipt.
- no workflow, dependency, lockfile, generated output, or unrelated source change is present.

## Test-style review

The final placement is accepted.

`test/basic.ts` contains broad constructor-option validation, but upstream introduced `test/background-fetch-size.ts` specifically with this option. Keeping its constructor and runtime regression cases together preserves feature ownership and avoids adding a third changed file for one closely coupled check.

The original candidate over-enumerated invalid JavaScript types. Final coverage uses representative cases for each distinct invariant instead:

- numeric-domain rejection;
- runtime non-number rejection;
- hostile non-coercion;
- zero support;
- pre-dispatch mutation validation;
- operation-local snapshotting and later-operation mutation;
- stale/no-size exceptions;
- zero coalescing;
- defensive receipt validation.

The repository's original TAP clock setup is preserved.

## Execution reviewed

The production source blob is unchanged from the previously reviewed candidate. Prior executions established passing focused behavior/build/lint/format, Ubuntu/macOS native CI, and benchmarks for that production logic. Windows native lanes stopped before product test discovery because the unchanged repository configuration requests missing `@tapjs/clock`.

The final test blob is new, so those prior receipts are not represented as exact final-tree execution. Fresh final-head runs are pending:

- CI `31227785209`;
- Benchmarks `31227785205`.

## Evidence limits

- no final exact-head green claim until the fresh runs execute;
- no green native Windows coverage suite is claimed;
- production prevalence remains unknown;
- constructor-wide eager validation remains a public-contract choice and can be narrowed if the maintainer prefers.

## Disposition

`SOURCE ACCEPTED / TEST STYLE ACCEPTED / FINAL EXACT-HEAD EXECUTION PENDING`

The candidate is appropriate for owner review. Public interaction remains owner-only and has not occurred.
