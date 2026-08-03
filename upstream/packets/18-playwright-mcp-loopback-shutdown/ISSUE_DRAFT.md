# Suggested issue title

MCP HTTP test shutdown route gives network clients process-control authority

# Issue draft

## Problem

Playwright's built-in MCP HTTP server exposes a `/killkillkill` route used by the HTTP lifecycle test to simulate Ctrl+C. A `POST` request with the fixed `x-pw-mcp-kill: 1` header emits `SIGINT` in the server process.

The test parent needs a way to exercise graceful shutdown. An ordinary HTTP client doesn't need process-shutdown authority. Today, any programmatic client that can reach the server can reproduce the request.

Host checks and the custom header reduce cross-site request forgery exposure, but they don't authenticate the caller or show that it owns the process.

## History and current use

The route was introduced on September 19, 2025 in [microsoft/playwright#37484](https://github.com/microsoft/playwright/pull/37484), merged as [83cd5af](https://github.com/microsoft/playwright/commit/83cd5af5b5d0b8faeb1ea14e15c6ca8b1c59e0e5). On Windows, `child.kill('SIGTERM')` terminates the child without running Playwright's graceful shutdown handlers. The endpoint let the HTTP and SSE lifecycle tests trigger the existing `SIGINT` cleanup path instead.

It shipped in [Playwright v1.56.0](https://github.com/microsoft/playwright/blob/v1.56.0/packages/playwright/src/mcp/sdk/http.ts) as an unauthenticated `GET` endpoint.

On April 30, 2026, [microsoft/playwright#40551](https://github.com/microsoft/playwright/pull/40551), merged as [4a80eed](https://github.com/microsoft/playwright/commit/4a80eed396071d6ed15a74c32723f2bc66849988), changed it to `POST` plus the fixed header. That reduces the CSRF risk, but the header is public and doesn't distinguish the spawning parent from another script or agent that can reach the port.

At the current public base, the string appears in the [HTTP server implementation](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/packages/playwright-core/src/tools/utils/mcp/http.ts) and the [`http transport browser sigint` test](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/tests/mcp/http.spec.ts). I couldn't find a documented Playwright workflow that uses it for agent or server administration.

## Proposed change

Remove the HTTP shutdown route. In HTTP mode under Playwright's existing test marker, let the spawning test parent request graceful shutdown by closing the child stdin pipe it already owns.

The HTTP-only listener would translate readable stdin EOF into the existing `SIGINT` cleanup path. The stdio branch would return before that listener is installed, so `StdioServerTransport` remains the sole reader of MCP protocol input.

This approach doesn't remove cleanup options. A process owner or supervisor can still use `SIGINT`, `SIGTERM`, or forced termination. If Playwright later needs remote administrative shutdown, that should be a separate authenticated interface.

## Coverage

- the former route doesn't stop the server;
- MCP remains responsive before parent EOF;
- closing the owning stdin produces one graceful shutdown and exit code 0;
- `PWTEST_UNDER_TEST=0` leaves the HTTP server alive after stdin EOF;
- immediate MCP stdio startup and ping still work;
- the full MCP HTTP test file passes on Linux, macOS, and Windows.

I've prepared the implementation and tests. Once this issue is approved or assigned, I'll send the linked PR.
