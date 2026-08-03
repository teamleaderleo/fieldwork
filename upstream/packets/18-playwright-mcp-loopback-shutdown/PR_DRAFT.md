# Suggested pull request title

fix(mcp): scope HTTP test shutdown to parent stdin

# Pull request draft

## Summary

- remove the test-only `/killkillkill` HTTP shutdown route;
- after HTTP mode is selected, translate the owning test parent's stdin EOF into the existing SIGINT cleanup path;
- leave MCP stdio input ownership unchanged;
- replace the route-driven lifecycle test and add controls for production scope and immediate stdio startup.

## Background

`/killkillkill` was introduced on September 19, 2025 by [microsoft/playwright#37484](https://github.com/microsoft/playwright/pull/37484) to let the HTTP and SSE lifecycle tests exercise graceful `SIGINT` cleanup on Windows. On that platform, `child.kill('SIGTERM')` terminates the process without running the graceful shutdown handlers. The endpoint was therefore a cross-platform test workaround, not a documented remote-administration feature.

The original route was an unauthenticated `GET` and shipped in [Playwright v1.56.0](https://github.com/microsoft/playwright/blob/v1.56.0/packages/playwright/src/mcp/sdk/http.ts). [microsoft/playwright#40551](https://github.com/microsoft/playwright/pull/40551) later changed it to `POST` plus `x-pw-mcp-kill: 1` to prevent browser-coerced cross-origin requests. The header is a fixed public value, so this hardening prevents that CSRF path but does not distinguish the spawning parent from another programmatic HTTP client.

At the current base, the route appears in the [HTTP implementation](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/packages/playwright-core/src/tools/utils/mcp/http.ts) and is called by the [`http transport browser sigint` test](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/tests/mcp/http.spec.ts). I did not find a documented supported workflow that uses it for agent or server administration.

## Why

The HTTP route gives a programmatic network client process-shutdown authority that is only needed by the parent process that spawned the test server. Parent stdin is already an ownership channel and does not require a private message protocol or retain a network process-control endpoint.

The stdin listener is installed only in HTTP mode and only when Playwright's existing test marker is true. The stdio branch returns first, so `StdioServerTransport` remains the sole reader of MCP stdio input.

This change does not prevent a process owner or supervisor from using `SIGINT`, `SIGTERM`, or forced termination. If remote administrative shutdown becomes a supported requirement, it should be introduced separately with an explicit authentication and authorization model.

## Tests

- the former `/killkillkill` request does not stop the server;
- MCP remains responsive before parent stdin EOF;
- parent EOF produces one graceful close and exit code 0;
- `PWTEST_UNDER_TEST=0` leaves the HTTP server responsive after EOF;
- immediate MCP stdio startup and ping remain intact;
- `npm ci`;
- `npm run build`;
- full `tests/mcp/http.spec.ts` with Chromium on Ubuntu, macOS, and Windows;
- focused ESLint for the three changed files;
- clean working tree and exact three-file diff checks.

Fixes #<approved-and-assigned-issue>
