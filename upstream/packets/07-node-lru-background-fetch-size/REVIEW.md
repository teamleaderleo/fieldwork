# Review — Unit 07 `backgroundFetchSize` snapshot

## Review subject

- source PR: `teamleaderleo/node-lru-cache#2`;
- base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- submitted head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- upstream submission: [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410);
- fence: `src/index.ts`, `test/background-fetch-size.ts`;
- relation: ahead 1, behind 0;
- total diff: +193 / -1;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`.

## Source findings

No blocking production-source defect was found before submission.

- `isNonNegativeInt()` checks primitive number type before the existing positive-integer helper, so symbols, objects, and hostile conversion hooks are not coerced;
- zero and positive integers remain valid;
- the missing-key receipt is captured before the Promise executor invokes user `fetchMethod` synchronously;
- stale refresh continues to use the existing entry size;
- caches without size tracking remain insensitive to irrelevant later field mutation;
- `BackgroundFetch.__size` remains optional in the exported type for source compatibility;
- the accounting boundary retains a defensive validity check for the stored receipt;
- no workflow, dependency, lockfile, generated output, or unrelated source change is present.

## Test review

The submitted test placement and scope are accepted.

All `backgroundFetchSize` regressions remain in the dedicated feature test created upstream for this option. The suite covers representative invalid values, hostile non-coercion, zero support, pre-dispatch validation, the synchronous mutation race, later-operation behavior/coalescing, and stale/no-size compatibility boundaries.

A previous test deliberately corrupted the hidden receipt via `unsafeExposeInternals()` and reinserted it. That test and its test-only `BackgroundFetch` type import were removed. Upstream explicitly warns that modifying exposed internals may cause strange breakage, so that manufactured state is not a public behavior the regression suite should promise.

## Execution reviewed

The production source blob is unchanged from the previously reviewed candidate. Prior executions established passing focused behavior/build/lint/format, Ubuntu/macOS native CI, and benchmarks for that production logic. Windows native lanes stopped before product test discovery because the unchanged repository configuration requests missing `@tapjs/clock`.

Fresh submitted-head fork runs remain queued at this record update:

- CI `31231433021`;
- Benchmarks `31231433009`.

## Evidence limits

- no exact submitted-head green claim is made from those queued runs;
- no green native Windows coverage suite is claimed;
- production prevalence remains unknown;
- constructor-wide eager validation remains a public-contract choice the upstream maintainer may choose to narrow.

## Disposition

`SUBMITTED`

The owner manually opened upstream PR #410 from the reviewed exact head. Fieldwork should now preserve evidence and avoid additional upstream interaction unless the owner explicitly directs that exact action.
