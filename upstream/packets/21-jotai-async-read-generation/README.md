# Unit 21 — fix(utils): fence stale async JSON reads by per-key generation

## Disposition

`READY — public contact unauthorized`

Last verified: `2026-08-02`  
Review class: owner-authorized AI complete-diff review; human review not claimed  
Public upstream interaction: none

## Contribution

Jotai's JSON storage adapter preserves parsed object identity. Unit 20 makes that cache key-scoped. Unit 21 adds one read generation per key so an older asynchronous read cannot replace or delete shared cache authority after a newer read or a completed removal. Every caller still receives its own result or rejection.

- proposed target: Jotai `main`, stacked after unit 20 unless the prerequisite has merged;
- proposed title: `fix(utils): fence stale async JSON reads by per-key generation`;
- public API, stored bytes, and backend error propagation: unchanged.

## Exact identities

- public/fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- unit 20 branch/head: `teamleaderleo/jotai:fix/utils-key-scoped-json-cache` at `b2f84273b53bbed9df073354dac503e520be7101`
- unit 20 fork-local draft PR: `teamleaderleo/jotai#2`
- unit 21 branch/head: `teamleaderleo/jotai:fix/utils-async-read-generation` at `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`
- unit 21 fork-local draft PR: `teamleaderleo/jotai#3`
- packet PR: `teamleaderleo/fieldwork#450`

## Exact target diff

Comparison `b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531` is ahead by two commits, behind by zero, and changes only:

| Path | Diff | Purpose |
| --- | ---: | --- |
| `src/vanilla/utils/atomWithStorage.ts` | +15/-2 | per-key read generation and guarded cache publication/invalidation |
| `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` | +280 | eleven deterministic regressions |

Commits:

1. `fix(utils): fence stale async JSON reads by per-key generation`;
2. `test(utils): cover stale async JSON read fencing`.

No workflow, dependency, lockfile, generated output, Fieldwork file, publisher, receipt, snapshot, or unrelated formatting is present.

## Exact-head execution

At source head `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`:

| Workflow | Run | Result |
| --- | ---: | --- |
| Test | `30690923575` | success |
| Test Multiple Versions | `30690923560` | success |
| Test Old TypeScript | `30690923561` | success |
| Test Multiple Builds | `30690923564` | success |
| Compressed Size | `30690923562` | success |
| Preview Release | `30690923558` | fork-infrastructure failure after successful build |

Primary Test job `91345378689` succeeded for formatting, TypeScript, lint, complete specs, and build.

Preview job `91345378639` built successfully, then `pkg-pr-new` returned 404 because its GitHub App is not installed on the owned fork. This is not a product-source, test, lint, type, format, size, compatibility, or build failure.

Historical focused execution also passed the repair on Node 22, 24, and 26.

## Review result

Owner-authorized AI complete-diff review: `ACCEPT` at exact heads `b2f84273...dfe607d7`.

The review accepted:

- generation ownership inside `createJSONStorage()`;
- initiation-order authority for valid and malformed completions;
- caller-visible backend rejection without stale cache mutation;
- same-string identity reuse;
- removal-time authority advance in the terminal invalidation path;
- the unit-20 stack dependency and exact two-file fence.

Human review is not claimed. Write ordering and subscription-event authority remain separate work.

## Duplicate and compatibility state

The latest recorded search found no equivalent current implementation. Earlier same-key cache work is complementary rather than duplicative. Repeat the duplicate search and contribution/AI-disclosure policy checks immediately before filing because upstream may move.

Known limits:

- dynamic key generation entries retain adapter-lifetime scope, matching the prerequisite cache lifetime;
- application prevalence and key cardinality are unmeasured;
- public filing remains separately unauthorized;
- eventual delivery may need rebasing if unit 20 lands first.

## Packet contents

- `DEEP_DIVE.md` — mechanism and compatibility analysis;
- `APPROACHES.md` — alternatives and rejected widening;
- `TESTS.md` — test inventory;
- `REVIEW.md` — exact complete-diff review;
- `UPSTREAM_ISSUE.md` and `UPSTREAM_PR.md` — filing drafts;
- `patches/0001-fix-utils-fence-stale-async-json-reads.patch` — unit-only patch;
- `fixtures/atomWithStorageAsyncReadGenerationRepair.test.ts` — eleven-case native test;
- `receipts/20260801-direct-source-materialization.md` — canonical exact-head execution receipt.

## Remaining actions

1. repeat current-upstream duplicate and policy checks immediately before filing;
2. obtain explicit user authority for any public upstream interaction;
3. file stacked after unit 20, or rebase onto its merged result.
