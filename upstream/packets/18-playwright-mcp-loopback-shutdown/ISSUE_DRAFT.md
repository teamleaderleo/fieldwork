# Suggested issue title

MCP HTTP test shutdown route gives network clients process-control authority

# Issue draft

## Description

Playwright's built-in MCP HTTP server currently exposes a `/killkillkill` route used by the HTTP lifecycle test to simulate Ctrl+C. A POST request with the fixed `x-pw-mcp-kill: 1` header emits `SIGINT` in the server process.

That gives a programmatic HTTP client that can reach the server a process-shutdown capability that is only needed by the spawning test parent. Host and CORS checks reduce browser-origin attacks, but they do not establish process ownership or authorize a non-browser client.

This is an authority-boundary issue rather than a claim of a broadly exploitable production vulnerability: a client must still be able to reach an MCP HTTP server where the route is present.

## History and current use

The route was introduced on September 19, 2025 in [microsoft/playwright#37484](https://github.com/microsoft/playwright/pull/37484), merged as [83cd5af](https://github.com/microsoft/playwright/commit/83cd5af5b5d0b8faeb1ea14e15c6ca8b1c59e0e5). The PR explains that Windows `child.kill('SIGTERM')` terminates the child without exercising graceful shutdown handlers, while a Ctrl+C-derived `SIGINT` enters Playwright's watchdog cleanup path. The endpoint was added so the HTTP and SSE lifecycle tests could simulate that path on Windows.

The route was included in [Playwright v1.56.0](https://github.com/microsoft/playwright/blob/v1.56.0/packages/playwright/src/mcp/sdk/http.ts) as an unauthenticated `GET` endpoint.

On April 30, 2026, [microsoft/playwright#40551](https://github.com/microsoft/playwright/pull/40551), merged as [4a80eed](https://github.com/microsoft/playwright/commit/4a80eed396071d6ed15a74c32723f2bc66849988), changed it to `POST` plus the fixed header to prevent browser-coerced cross-origin requests. That is useful CSRF hardening, but the header is a public constant rather than an authentication secret, so an ordinary script or agent that can reach the port can still reproduce the request.

At the current public base, the string appears in the [HTTP server implementation](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/packages/playwright-core/src/tools/utils/mcp/http.ts) and the [`http transport browser sigint` test](https://github.com/microsoft/playwright/blob/2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2/tests/mcp/http.spec.ts). I did not find a documented Playwright workflow that presents it as an agent-management or remote-administration API.

## Proposed direction

Remove the HTTP shutdown route and let the test parent request graceful shutdown through the child stdin pipe it already owns.

The stdin listener should be installed only after HTTP mode has been selected and only under Playwright's existing test marker. The stdio transport branch must return before any new stdin reader is installed, so MCP protocol bytes remain exclusively owned by `StdioServerTransport`.

Readable EOF can then reuse the existing SIGINT watchdog and graceful cleanup path. Ordinary launches would lose the network shutdown route but would not gain stdin-driven shutdown behavior.

This does not remove administrative cleanup options. A process owner or supervisor can still use normal operating-system controls, including `SIGINT`, `SIGTERM`, and forced termination if graceful shutdown does not complete. A future requirement for remote administrative shutdown would be better handled as an explicit authenticated management interface rather than a hidden test route.

## Expected coverage

- the former HTTP route is inert;
- the MCP HTTP session remains responsive before parent EOF;
- closing the owning stdin produces one graceful shutdown and exit code 0;
- `PWTEST_UNDER_TEST=0` leaves the HTTP server alive after stdin EOF;
- immediate MCP stdio startup and ping still work;
- the full native MCP HTTP test file passes on Linux, macOS, and Windows.

I have a small implementation and test change prepared. I would like to work on this if maintainers agree with the direction. Per the contribution policy, I will not submit the pull request unless this issue is approved for community contribution and assigned to me.
