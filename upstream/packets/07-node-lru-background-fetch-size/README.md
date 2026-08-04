# Unit 07 — snapshot `backgroundFetchSize` before invoking user code

## Disposition

`TECHNICALLY READY — OWNER REVIEW / PUBLIC CONTACT HOLD`

The source candidate validates `backgroundFetchSize`, captures one immutable provisional-size receipt before synchronous user `fetchMethod` code runs, and consumes that receipt during missing-key accounting.

## Exact source

- public/owned-fork base: `16b3a916662ab449d496b7b4b4f04132565d1d28`;
- canonical source PR: `teamleaderleo/node-lru-cache#2`;
- exact source head: `47fef8068ab3e4a36b939e6d4c05b2ea085f6314`;
- changed files: exactly `src/index.ts` and `test/background-fetch-size.ts`;
- no dependency, lockfile, workflow, generated-output, or Fieldwork file.

## Accepted contract

- constructor values must be primitive finite nonnegative integers; explicit `undefined` retains omission/default behavior;
- mutated invalid values reject before provider dispatch when missing-key size accounting is active;
- zero remains valid and same-key callers remain coalesced;
- synchronous callback mutation affects later operations only;
- stale refresh continues to reuse the existing entry size;
- caches without size tracking ignore irrelevant later mutation;
- the internal receipt is optional on the exported type for source compatibility and required at the accounting boundary.

## Exact execution

Focused formatted-head run `30754588900`, job `91514469959`:

- install and repository build passed;
- 95/95 focused assertions passed;
- OXLint passed with zero warnings/errors;
- repository Prettier passed;
- diff and tracked-worktree hygiene passed.

Current-head native evidence:

- Benchmarks `30754536526`: success;
- CI `30754536472`:
  - Ubuntu Node 24/25: success;
  - macOS Node 24/25: success;
  - Windows Node 24/25 under Bash and PowerShell: repository harness failure before tests.

Every Windows failure has the same unchanged-base signature:

```text
'@tapjs/clock' does not appear to be a tap plugin.
Cannot find module '@tapjs/clock'
```

The source candidate does not modify `.taprc`, package dependencies, or the lockfile. A separate exact-version investigation established that injecting the matching TAP plugin lets unchanged base and candidate execute without coverage, while the coverage-enabled Windows command remains red for both. The Windows result is retained as a baseline harness limit, not presented as a green product suite.

## Review conclusion

Complete-diff review accepts the two-file source. The numeric guard avoids hostile coercion, the receipt is captured before the synchronous provider boundary, stale/no-size paths retain their existing ownership, and no unrelated repository repair enters the source diff.

The detailed mechanism, rejected approaches, historical executions, drafts, and exact current-head receipt remain in the adjacent packet files.

## Remaining gates

Immediately before any authorized filing:

1. refresh public main and duplicate/prior-art search;
2. read current contribution and AI-disclosure policy;
3. decide issue-first versus direct PR;
4. obtain explicit public-contact authorization.

No public upstream interaction occurred or is authorized.
