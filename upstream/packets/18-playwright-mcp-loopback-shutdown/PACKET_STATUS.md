# Packet status

Current disposition: `ISSUE FILED / WAITING FOR MAINTAINER APPROVAL OR ASSIGNMENT`

Upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

## Preferred source

- owned source PR: `teamleaderleo/playwright#48`
- public base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact source: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- exact file fence:
  - `packages/playwright-core/src/tools/utils/mcp/http.ts`
  - `packages/playwright-core/src/tools/utils/mcp/server.ts`
  - `tests/mcp/http.spec.ts`

The source removes `/killkillkill`. In HTTP mode under Playwright's test marker, parent stdin EOF enters the existing `SIGINT` cleanup path. The stdio branch returns before the HTTP-only stdin listener is installed.

## Exact-head execution

Run `30855503566` passed the full 21-test native MCP HTTP file, build, focused ESLint, clean-tree check, and exact three-file fence on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

## Next gate

Wait for an explicit maintainer approval for community contribution or assignment of the upstream issue. Open the linked upstream PR only after that response and separate user authorization.

Strict parent IPC at `teamleaderleo/playwright#40@e99e97da2acfc6c1a67749bc749e1d0cb71b5607` remains the executed fallback.
