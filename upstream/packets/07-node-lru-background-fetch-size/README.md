# Unit 07 — snapshot `backgroundFetchSize` before invoking user code

## Disposition

`SUBMITTED`

The owner submitted the reviewed source upstream as [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410).

The source validates `backgroundFetchSize`, snapshots the missing-key provisional size before synchronous user `fetchMethod` code runs, and uses that stored value for the in-flight fetch's accounting.

## Exact submitted source

- public/owned-fork base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical source PR: `teamleaderleo/node-lru-cache#2`;
- exact submitted head: `364a8c1c07c9f6281fbe19943eacd261bd410fc4`;
- relation: ahead 1, behind 0;
- changed files: exactly `src/index.ts` and `test/background-fetch-size.ts`;
- diff: +193 / -1;
- source blob: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- test blob: `a83968f5110bfe42cfe32aae55cb6018aba6aebd`;
- no dependency, lockfile, workflow, generated-output, or Fieldwork file.

## Accepted contract

- constructor values must be primitive finite nonnegative integers;
- mutated invalid values reject before provider dispatch when missing-key size accounting is active;
- zero remains valid and same-key callers remain coalesced;
- synchronous callback mutation affects later operations, not the fetch already in progress;
- stale refresh continues to use the existing entry size;
- caches without size tracking ignore irrelevant later mutation.

## Regression scope

The submitted tests cover supported behavior rather than deliberately corrupted private state. A previous `unsafeExposeInternals()` test that changed a hidden background-fetch receipt and reinserted it was removed; upstream explicitly warns that mutating exposed internals may cause strange breakage.

The small accounting-boundary receipt check remains as defensive code, but malformed private state is not presented as part of the public regression contract.

## Evidence boundary

Previous executions on the unchanged production logic established passing focused behavior/build/lint/format, Ubuntu/macOS native CI, and benchmarks. Windows stopped before product test discovery on the unchanged-base missing `@tapjs/clock` TAP configuration.

Fresh exact-head fork runs remain queued at this record update:

- CI `31231433021`;
- Benchmarks `31231433009`.

That execution limit is recorded but does not change the submission disposition.

## Public interaction boundary

The owner performed the upstream submission manually. The assistant did not create the upstream PR. No additional upstream comment, review, reaction, merge, release, or other public interaction is authorized without explicit owner direction for that exact action.
