# Suggested issue title

MCP HTTP test shutdown route gives network clients process-control authority

# Issue draft

## Description

Playwright's built-in MCP HTTP server currently exposes a `/killkillkill` route used by the HTTP lifecycle test to simulate Ctrl+C. A POST request with the expected header emits `SIGINT` in the server process.

That gives an accepted HTTP client a process-shutdown capability that is only needed by the spawning test parent. Restricting the route by host, origin, or loopback peer does not make the authority parent-only; a local proxy can still be the final TCP peer.

## Proposed direction

Remove the HTTP shutdown route and let the test parent request graceful shutdown through the child stdin pipe it already owns.

The stdin listener should be installed only after HTTP mode has been selected and only under Playwright's existing test marker. The stdio transport branch must return before any new stdin reader is installed, so MCP protocol bytes remain exclusively owned by `StdioServerTransport`.

Readable EOF can then reuse the existing SIGINT watchdog and graceful cleanup path. Ordinary launches would only lose the network shutdown route; they would not gain stdin-driven shutdown behavior.

## Expected coverage

- the former HTTP route is inert;
- the MCP HTTP session remains responsive before parent EOF;
- closing the owning stdin produces one graceful shutdown and exit code 0;
- `PWTEST_UNDER_TEST=0` leaves the HTTP server alive after stdin EOF;
- immediate MCP stdio startup and ping still work;
- the full native MCP HTTP test file passes on Linux, macOS, and Windows.

I have a small implementation and test change prepared. I would like to work on this if maintainers agree with the direction. Per the contribution policy, I will not submit the pull request unless this issue is approved for community contribution and assigned to me.
