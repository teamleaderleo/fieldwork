# Owned source branch record

## Fieldwork research source

- repository: `teamleaderleo/playwright`
- owned source PR: `teamleaderleo/playwright#48`
- base branch: `fieldwork/435-unit-18-base-current`
- exact base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- candidate branch: `fix/mcp-http-parent-stdin-review`
- exact candidate head: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- commits: one
- additions/deletions at review: 66/19
- exact changed-file fence:
  - `packages/playwright-core/src/tools/utils/mcp/http.ts`
  - `packages/playwright-core/src/tools/utils/mcp/server.ts`
  - `tests/mcp/http.spec.ts`
- temporary workflow or evidence files in target diff: none

Run `30855503566` passed the complete focused matrix on Ubuntu, macOS, and Windows.

## Upstream outcome

Issue: [submitted bug report](https://redirect.github.com/microsoft/playwright/issues/42129)

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

The maintainer-owned fix is approved and uses a smaller `isUnderTest()` gate. PR #48 is therefore retained as research evidence, not an upstream submission candidate.

Strict parent IPC PR `teamleaderleo/playwright#40` remains another executed research fallback.
