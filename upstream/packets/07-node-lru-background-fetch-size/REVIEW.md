# Review — Unit 07 `backgroundFetchSize` snapshot

## Review subject

- source PR: `teamleaderleo/node-lru-cache#2`;
- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- fence: `src/index.ts`, `test/background-fetch-size.ts`;
- relation: ahead 1, behind 0;
- total diff: +193 / -1;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`.

## Source findings

No blocking production-source defect remains.

- `isNonNegativeInt()` checks primitive number type before the existing positive-integer helper, so symbols, objects, and hostile conversion hooks aren't coerced;
- zero and positive integers remain valid;
- the missing-key receipt is captured before the Promise executor invokes user `fetchMethod` synchronously;
- stale refresh continues to use the existing entry size;
- caches without size tracking remain insensitive to irrelevant later field mutation;
- `BackgroundFetch.__size` remains optional in the exported type for source compatibility;
- the accounting boundary retains a defensive validity check for the stored receipt;
- no workflow, dependency, lockfile, generated output, or unrelated source change is present.

## Test review

The final test placement and scope are accepted.

All `backgroundFetchSize` regressions remain in the dedicated feature test created upstream for this option. The suite now covers representative invalid values, hostile non-coercion, zero support, pre-dispatch validation, the synchronous mutation race, later-operation behavior/coalescing, and the stale/no-size compatibility boundaries.

A previous test deliberately corrupted the hidden receipt via `unsafeExposeInternals()` and reinserted it. That test and its test-only `BackgroundFetch` type import were removed. Upstream explicitly warns that modifying exposed internals may cause strange breakage, so that manufactured state isn't a public behavior the regression suite should promise.

The existing TAP clock setup is preserved.

## Execution reviewed

The production source blob is unchanged from the previously reviewed candidate. Prior executions established passing focused behavior/build/lint/format, Ubuntu/macOS native CI, and benchmarks for that production logic. Windows native lanes stopped before product test discovery because the unchanged repository configuration requests missing `@tapjs/clock`.

The final test blob is new, so those prior receipts aren't represented as exact final-tree execution. Fresh final-head runs are pending:

- CI `31231433021`;
- Benchmarks `31231433009`.

## Evidence limits

- no final exact-head green claim until the fresh runs execute;
- no green native Windows coverage suite is claimed;
- production prevalence remains unknown;
- constructor-wide eager validation remains a public-contract choice and can be narrowed if the maintainer prefers.

## Disposition

`SOURCE ACCEPTED / REGRESSION SCOPE ACCEPTED / FINAL EXACT-HEAD EXECUTION PENDING`

The candidate is appropriate for owner review. Public interaction remains owner-only and hasn't occurred.
