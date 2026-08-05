# Suggested pull request title

fix(mcp): scope HTTP test shutdown to parent stdin

# Pull request draft

Upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

## Summary

- remove the test-only `/killkillkill` HTTP shutdown route;
- in HTTP test mode, translate the owning parent's stdin EOF into the existing `SIGINT` cleanup path;
- leave MCP stdio input ownership unchanged;
- replace the route-driven lifecycle test and add production-scope and stdio-startup controls.

## Background

The endpoint was added so HTTP and SSE lifecycle tests could exercise graceful `SIGINT` cleanup on Windows. It later changed to `POST` plus the fixed `x-pw-mcp-kill: 1` header. That reduces browser-CSRF exposure, but it doesn't distinguish the spawning parent from another programmatic HTTP client.

## Change

The test parent already owns the child stdin pipe. After HTTP mode is selected, and only under Playwright's test marker, readable EOF requests graceful shutdown through the existing `SIGINT` path.

The stdio branch returns first, so `StdioServerTransport` remains the sole reader of MCP protocol input.

This doesn't remove process supervision. Owners can still use `SIGINT`, `SIGTERM`, or forced termination.

## Tests

- former route is inert;
- MCP remains responsive before parent EOF;
- parent EOF produces one graceful close and exit code 0;
- `PWTEST_UNDER_TEST=0` leaves HTTP responsive after EOF;
- immediate MCP stdio startup and ping remain intact;
- full `tests/mcp/http.spec.ts`, build, and focused ESLint pass on Ubuntu 24.04, macOS 15, and Windows Server 2025.

When an upstream PR is authorized, add the closing line shown below with the real upstream issue number:

```text
Fixes #42129
```
