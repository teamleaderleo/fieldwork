# Deep dive — Unit 18 Playwright MCP shutdown authority

## Problem

The MCP HTTP dispatcher exposed `/killkillkill` in ordinary HTTP launches. A matching request emitted `SIGINT` in the server process. The route existed to exercise Playwright's graceful shutdown path in tests, but a programmatic client that could reach an accepted host could also invoke it.

The fixed POST/header requirement reduced browser-CSRF exposure. It didn't distinguish a test harness from another script or agent.

## Filed issue

[MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

The report included a self-contained reproduction, route history, current source references, and a fully tested alternate implementation.

## Maintainer-selected fix

[Only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

The selected change does not remove the endpoint. Instead it draws the boundary at Playwright's test marker:

- `http.ts` imports `isUnderTest()`;
- `/killkillkill` is handled only when `isUnderTest()` is true;
- ordinary MCP HTTP servers therefore don't expose the shutdown route;
- the lifecycle test can still simulate `SIGINT` directly;
- the test-only route no longer needs the fixed POST/custom-header check.

The upstream pull request is two files, 3 additions and 9 deletions. Pavel Feldman approved it. It is currently open and not yet merged.

## What the maintainer choice says about the boundary

The accepted issue was the route's availability in ordinary MCP HTTP servers. The maintainers did not treat the existence of a shutdown endpoint inside Playwright's own test environment as a problem.

That is narrower than Fieldwork's original design preference, which removed the endpoint entirely and moved lifecycle control to the spawning parent. Both prevent ordinary production HTTP clients from invoking shutdown; the maintainer change does so with less code and no new lifecycle handling.

## Fieldwork research evidence

Fieldwork's parent-stdin candidate remains at `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`.

Run `30855503566` passed the complete 21-test MCP HTTP file, full build, focused lint, clean tree, and exact three-file diff on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

That evidence made the issue report stronger, but it is not the upstream implementation and should not be submitted competitively.

## Contribution result

This unit succeeded at the issue level: the report was assigned, targeted for `v1.63`, linked to a maintainer-owned fix, and that fix received maintainer approval.

Next finalization step: record the merge and issue closure when they happen.
