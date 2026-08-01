# Direct source materialization receipt — unit 21

## In simple words

The owned Jotai fork now exists. Unit 20 was materialized as the clean prerequisite branch, then unit 21 was created as a clean child branch with only the generation fence and the expanded target-native regression file.

## Exact identities

- inspected public and fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- owned fork: `teamleaderleo/jotai`
- unit 20 branch: `fix/utils-key-scoped-json-cache`
- unit 20 exact head: `b2f84273b53bbed9df073354dac503e520be7101`
- unit 20 fork-local draft PR: `teamleaderleo/jotai#2`
- unit 21 branch: `fix/utils-async-read-generation`
- unit 21 exact head: `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`
- unit 21 fork-local draft PR: `teamleaderleo/jotai#3`
- unit 21 merge base: `b2f84273b53bbed9df073354dac503e520be7101`
- materialization date: `2026-08-01`

## Unit 21 changed-file fence

Comparison `b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531` is exactly:

1. `src/vanilla/utils/atomWithStorage.ts` — 15 additions, 2 deletions;
2. `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` — 280 additions.

No workflow, dependency, lockfile, generated output, Fieldwork file, publisher, receipt, or unrelated formatting is present in the target diff.

## Commit shape

Unit 21 is two conventional commits on the exact unit-20 head:

1. `fix(utils): fence stale async JSON reads by per-key generation`;
2. `test(utils): cover stale async JSON read fencing`.

The branch was force-rewritten after a filename-only cleanup so the canonical head contains no rename or execution-history noise.

## Fork-local target execution

Opening the owned-fork draft PR triggered the repository's existing pull-request workflows at exact head `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`:

- Test Multiple Versions: run `30690923560`;
- Test Old TypeScript: run `30690923561`;
- Test: run `30690923575`;
- Compressed Size: run `30690923562`;
- Test Multiple Builds: run `30690923564`;
- Preview Release: run `30690923558`.

Status when this receipt was first written: queued. Final conclusions must be added before changing the unit disposition.

## Review result so far

- stack relation: exact; unit 21 is ahead of unit 20 and behind by zero;
- changed files: exact two-file fence;
- source patch: byte-for-byte equivalent to the retained unit-21 packet patch over the materialized unit-20 source;
- target-native test: byte-for-byte equivalent to the packet's expanded eleven-case fixture;
- temporary source machinery: absent;
- public upstream interaction: none.

## Remaining gates

1. record final fork-local workflow conclusions and inspect the primary Test job;
2. confirm the exact focused regression count and ordinary build/test coverage provided by current workflows;
3. update `README.md`, `TESTS.md`, `REVIEW.md`, packet PR #450, and issue #435;
4. obtain independent complete-diff review;
5. repeat public duplicate/policy checks immediately before any authorized filing.
