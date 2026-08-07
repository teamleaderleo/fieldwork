# Approaches — Unit 18 Playwright MCP shutdown authority

## Maintainer-selected approach

### Gate `/killkillkill` with `isUnderTest()`

Upstream fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

The maintainers chose the smallest boundary change:

- keep `/killkillkill` for Playwright's own graceful-SIGINT lifecycle test;
- expose it only when `isUnderTest()` is true;
- remove the POST/custom-header check from that test-only path;
- leave ordinary MCP HTTP launches without the shutdown route.

This directly addresses the filed issue without adding a new parent-lifecycle mechanism. Pavel Feldman approved the implementation.

## Fieldwork alternate: mode-aware parent stdin EOF

Fieldwork's fully executed candidate removes `/killkillkill` entirely and translates parent stdin EOF into the existing `SIGINT` cleanup path only after HTTP mode is selected.

Exact source: `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`.

Run `30855503566` passed the full 21-test file and all declared gates on Ubuntu 24.04, macOS 15, and Windows Server 2025.

It is no longer a submission candidate because the maintainers selected and approved the smaller test-gating change. Keep it as research evidence.

## Earlier alternatives

### Strict parent IPC

`teamleaderleo/playwright#40@e99e97da2acfc6c1a67749bc749e1d0cb71b5607` also removes network shutdown authority and is fully executed. It adds a private parent message format and remains research only.

### Fixed public header

The fixed header reduces browser-CSRF exposure but doesn't authenticate a programmatic client. The maintainer fix makes that distinction irrelevant in ordinary launches by hiding the route outside tests.

### Loopback or Host restrictions

Those checks constrain reachability but don't establish process ownership. They were not selected.

### Authenticated remote shutdown

Reasonable only if Playwright later wants a real remote-administration API. It is unnecessary for the lifecycle test.

## Outcome

Issue: [submitted bug report](https://redirect.github.com/microsoft/playwright/issues/42129)

The issue contribution succeeded. No Fieldwork-authored upstream pull request is needed unless maintainers ask for another design.
