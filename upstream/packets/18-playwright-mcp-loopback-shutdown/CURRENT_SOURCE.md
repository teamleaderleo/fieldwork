# Current source generation

## Identity

- repository: `teamleaderleo/playwright`
- owned source PR: `teamleaderleo/playwright#48`
- branch: `fix/mcp-http-parent-stdin-review`
- exact public base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact source head: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- commits ahead: one

## Exact file fence

1. `packages/playwright-core/src/tools/utils/mcp/http.ts`
2. `packages/playwright-core/src/tools/utils/mcp/server.ts`
3. `tests/mcp/http.spec.ts`

## Behavior

- removes the `/killkillkill` HTTP branch;
- leaves MCP stdio input ownership unchanged;
- installs the stdin listener only after HTTP mode is selected;
- requires Playwright's existing test marker;
- translates readable parent EOF into the existing `SIGINT` cleanup path;
- handles stdin that already ended before listener setup.

The test proves the old route is inert, MCP remains responsive before EOF, closing the owning stdin produces one graceful close and exit code 0, disabling the test marker leaves HTTP alive after EOF, and immediate stdio startup still works.

## Upstream state

Issue filed: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

The source is ready for a linked upstream PR after explicit maintainer approval or assignment.
