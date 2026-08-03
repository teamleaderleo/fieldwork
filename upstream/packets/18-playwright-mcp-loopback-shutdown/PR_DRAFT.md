# Suggested pull request title

fix(mcp): scope HTTP test shutdown to parent stdin

# Pull request draft

## Summary

- remove the test-only `/killkillkill` HTTP shutdown route;
- in HTTP test mode, translate the owning parent's stdin EOF into the existing `SIGINT` cleanup path;
- leave MCP stdio input ownership unchanged;
- replace the route-driven lifecycle test and add production-scope and stdio-startup controls.

## Background

`/killkillkill` was introduced on September 19, 2025 by [microsoft/playwright#37484](https://github.com/microsoft/playwright/pull/37484). On Windows, `child.kill('SIGTERM')` terminates the process without running Playwright's graceful shutdown handlers, so the HTTP and SSE lifecycle tests needed another way to exercise the existing `SIGINT` cleanup path.

The route shipped in [Playwright v1.56.0](https://github.com/microsoft/playwright/blob/v1.56.0/packages/playwright/src/mcp/sdk/http.ts) as an unauthenticated `GET`. [microsoft/playwright#40551](https://github.com/microsoft/playwright/pull/40551) later changed it to `POST` plus `x-pw-mcp-kill: 1`. That reduces the CSRF risk, but the fixed public header doesn't authenticate the caller or prove that it owns the process.

At the current base, the route appears in the [HTTP implementation](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/packages/playwright-core/src/tools/utils/mcp/http.ts) and is called by the [`http transport browser sigint` test](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/tests/mcp/http.spec.ts). I couldn't find a documented workflow that uses it for agent or server administration.

## Change

The test parent already owns the child stdin pipe. In HTTP mode under Playwright's test marker, closing that pipe now requests graceful shutdown through the existing `SIGINT` path.

The stdio branch returns before the HTTP-only stdin listener is installed, so `StdioServerTransport` remains the sole reader of MCP protocol input.

This approach doesn't remove process supervision. Owners can still use `SIGINT`, `SIGTERM`, or forced termination. A future remote shutdown feature can be introduced separately with authentication and authorization.

## Tests

- the former `/killkillkill` request doesn't stop the server;
- MCP remains responsive before parent stdin EOF;
- parent EOF produces one graceful close and exit code 0;
- `PWTEST_UNDER_TEST=0` leaves the HTTP server responsive after EOF;
- immediate MCP stdio startup and ping remain intact;
- `npm ci`;
- `npm run build`;
- full `tests/mcp/http.spec.ts` with Chromium on Ubuntu, macOS, and Windows;
- focused ESLint for the three changed files;
- clean working tree and exact three-file diff checks.

Fixes #<linked-issue>
