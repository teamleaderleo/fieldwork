# Direct source and execution receipt — unit 21

## Disposition

`READY — public contact unauthorized`

The exact clean Jotai source head passed the repository's product, compatibility, and build gates. The only failed workflow was preview publication, after its build succeeded, because the `pkg-pr-new` GitHub App is not installed on the owned fork.

## Exact identities

- inspected public and fork base: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- owned fork: `teamleaderleo/jotai`
- unit 20 branch/head: `fix/utils-key-scoped-json-cache` at `b2f84273b53bbed9df073354dac503e520be7101`
- unit 20 fork-local draft PR: `teamleaderleo/jotai#2`
- unit 21 branch/head: `fix/utils-async-read-generation` at `dfe607d7637fbcf61ae41c39f4f470f61fa7c531`
- unit 21 fork-local draft PR: `teamleaderleo/jotai#3`
- unit 21 merge base: `b2f84273b53bbed9df073354dac503e520be7101`
- execution inspected: `2026-08-02`

## Exact changed-file fence

Comparison `b2f84273b53bbed9df073354dac503e520be7101...dfe607d7637fbcf61ae41c39f4f470f61fa7c531` is ahead by two commits, behind by zero, and changes only:

1. `src/vanilla/utils/atomWithStorage.ts` — 15 additions, 2 deletions;
2. `tests/react/vanilla-utils/atomWithStorageAsyncReadGenerationRepair.test.ts` — 280 additions.

No workflow, dependency, lockfile, generated output, Fieldwork file, publisher, receipt, or unrelated formatting is present.

## Exact-head workflow conclusions

| Workflow | Run | Conclusion | Evidence |
| --- | ---: | --- | --- |
| Test | `30690923575` | success | format, types, lint, complete spec command, and build all succeeded |
| Test Multiple Versions | `30690923560` | success | repository compatibility matrix succeeded |
| Test Old TypeScript | `30690923561` | success | supported old TypeScript gate succeeded |
| Test Multiple Builds | `30690923564` | success | build matrix succeeded |
| Compressed Size | `30690923562` | success | size gate succeeded |
| Preview Release | `30690923558` | infrastructure failure after successful build | `pkg-pr-new` returned 404 because its GitHub App is not installed on `teamleaderleo/jotai` |

Primary Test job: `91345378689`.

Successful steps in that job:

- `pnpm install`;
- `pnpm run test:format`;
- `pnpm run test:types`;
- `pnpm run test:lint`;
- `pnpm run test:spec`;
- `pnpm run build`.

Preview job: `91345378639`. Its `pnpm run build` step succeeded. The later publication command failed before publication with: `The app https://github.com/apps/pkg-pr-new is not installed on teamleaderleo/jotai.` This is not a source, test, type, lint, format, or build failure.

## Review

- owner-authorized AI complete-diff review: `ACCEPT` at the exact source/base heads;
- human review: not claimed;
- target diff cleanliness: accepted;
- stack dependency on unit 20: accepted;
- write and subscription-event ordering: explicitly outside this unit;
- public upstream interaction: none.

## Remaining actions

1. repeat duplicate/prior-art, contribution-policy, and AI-disclosure checks immediately before filing;
2. obtain explicit user authority before any public upstream discussion or pull request;
3. decide at filing time whether unit 21 should remain stacked or be rebased after unit 20 merges.
