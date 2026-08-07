# Unit 07 — snapshot `backgroundFetchSize` before invoking user code

## Disposition

`OWNER REVIEW — FINAL EXACT-HEAD RUNS PENDING`

The source candidate validates `backgroundFetchSize`, captures one immutable provisional-size receipt before synchronous user `fetchMethod` code runs, and consumes that receipt during missing-key accounting.

## Exact source

- public/owned-fork base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical source PR: `teamleaderleo/node-lru-cache#2`;
- exact source head: `4a80ff2cec44d259907e474336a64ec984a465a5`;
- relation: ahead 1, behind 0;
- changed files: exactly `src/index.ts` and `test/background-fetch-size.ts`;
- diff: +223 / -2;
- no dependency, lockfile, workflow, generated-output, or Fieldwork file.

Final changed-file blobs:

- `src/index.ts`: `c3549a638b84ce096b13ebd7e3f71496dbe5afd5`;
- `test/background-fetch-size.ts`: `00b81ade21068c55c23623d95992acbe9f26ebb2`.

The production source blob is unchanged from the previously reviewed candidate. The test file was simplified to match repository conventions and preserves the original TAP clock setup.

## Accepted contract

- constructor values must be primitive finite nonnegative integers;
- mutated invalid values reject before provider dispatch when missing-key size accounting is active;
- zero remains valid and same-key callers remain coalesced;
- synchronous callback mutation affects later operations only;
- stale refresh continues to reuse the existing entry size;
- caches without size tracking ignore irrelevant later mutation;
- the internal receipt is optional on the exported type for source compatibility and checked at the accounting boundary.

## Test placement and style

Upstream already created `test/background-fetch-size.ts` for this option. Broad constructor validation also exists in `test/basic.ts`, but moving one closely related option check there would expand this contribution to a third file. The final candidate keeps all `backgroundFetchSize` regressions in the dedicated feature test.

The invalid-value coverage was reduced from an exhaustive JavaScript type inventory to representative cases proving distinct invariants: numeric-domain rejection, runtime non-number rejection, non-coercion, zero support, pre-dispatch mutation validation, operation-local snapshotting, stale/no-size exceptions, zero coalescing, and defensive receipt validation.

## Execution boundary

Previous executions on the unchanged production logic established passing focused behavior/build/lint/format, Ubuntu/macOS native CI, and benchmarks. Windows stopped before product test discovery on the unchanged-base missing `@tapjs/clock` TAP configuration.

Because the final test file changed, exact-head success is not carried forward by blob identity. Fresh runs for `4a80ff2cec44d259907e474336a64ec984a465a5` are pending:

- CI `31227785209`;
- Benchmarks `31227785205`.

No green exact-head claim is made until those runs execute.

## Remaining boundary

The public-facing draft is ready for owner review. No public upstream interaction occurred or is authorized; the repository owner will perform any eventual submission manually.
