# Suggested pull request title

fix(mcp): scope HTTP test shutdown to parent stdin

# Pull request draft

## Summary

- remove the test-only `/killkillkill` HTTP shutdown route;
- after HTTP mode is selected, translate the owning test parent's stdin EOF into the existing SIGINT cleanup path;
- leave MCP stdio input ownership unchanged;
- replace the route-driven lifecycle test and add controls for production scope and immediate stdio startup.

## Why

The HTTP route gives an accepted network client process-shutdown authority that is only needed by the parent process that spawned the test server. Parent stdin is already an ownership channel and does not require a private message protocol or retain a network process-control endpoint.

The stdin listener is installed only in HTTP mode and only when Playwright's existing test marker is true. The stdio branch returns first, so `StdioServerTransport` remains the sole reader of MCP stdio input.

## Tests

- `npm ci`
- `npm run build`
- full `tests/mcp/http.spec.ts` with Chromium on Ubuntu, macOS, and Windows
- focused ESLint for the three changed files
- clean working tree and exact three-file diff checks

Fixes #<approved-and-assigned-issue>
