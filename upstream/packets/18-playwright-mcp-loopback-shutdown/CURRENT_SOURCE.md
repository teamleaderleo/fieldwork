# Current source generation

## Upstream-selected source

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

Current upstream head: `5074f70234d518b04400227c616ca682f6f0c309`

The upstream pull request changes two files with 3 additions and 9 deletions:

1. `packages/playwright-core/src/tools/utils/mcp/http.ts`
2. `tests/mcp/http.spec.ts`

Behavior:

- import and use `isUnderTest()` in the HTTP dispatcher;
- serve `/killkillkill` only while Playwright is running under its test marker;
- keep the existing `SIGINT` simulation for the lifecycle test;
- simplify the test request because the route is no longer exposed in ordinary MCP HTTP launches.

Pavel Feldman approved this source. It is currently open and not yet merged.

## Fieldwork research source

The previously preferred alternate remains:

- repository: `teamleaderleo/playwright`
- owned source PR: `teamleaderleo/playwright#48`
- branch: `fix/mcp-http-parent-stdin-review`
- exact base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact head: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- exact fence: `http.ts`, `server.ts`, `http.spec.ts`

That source removes the route entirely and uses parent stdin EOF only in HTTP test mode. Run `30855503566` passed the full 21-test file and all declared gates on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

## Decision

The upstream-selected `isUnderTest()` gate supersedes the need to submit the Fieldwork alternate. Retain PR #48 as research evidence only unless maintainers request it.
