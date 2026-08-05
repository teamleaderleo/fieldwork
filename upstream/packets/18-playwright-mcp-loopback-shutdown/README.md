# Unit 18 — Remove Playwright MCP network shutdown authority

## Summary

Playwright MCP's HTTP server exposes `/killkillkill`, a test route that emits `SIGINT`. A reachable programmatic client can reproduce the fixed request. The selected source removes the route and lets the spawning test parent request graceful shutdown by closing the child stdin pipe it already owns.

## Current disposition

`ISSUE FILED / WAITING FOR MAINTAINER APPROVAL OR ASSIGNMENT`

- upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)
- packet PR: `teamleaderleo/fieldwork#451`
- preferred source PR: `teamleaderleo/playwright#48`
- exact base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact source: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- exact execution: run `30855503566`

## Source behavior

- remove `/killkillkill` from ordinary HTTP;
- install the stdin listener only after HTTP mode is selected;
- require Playwright's existing test marker;
- translate readable parent EOF into the existing graceful `SIGINT` path;
- leave MCP stdio input ownership unchanged.

## Validation

The full 21-test native MCP HTTP file, complete build, focused ESLint, clean tree, and exact three-file diff passed on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

## Next action

Wait for explicit maintainer approval for community contribution or assignment. A linked upstream PR may follow only after that response and separate user authorization.

## Packet navigation

- [Current source](./CURRENT_SOURCE.md)
- [Current execution](./CURRENT_EXECUTION.md)
- [Technical explanation](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests](./TESTS.md)
- [Review](./REVIEW.md)
- [Submitted issue record](./UPSTREAM_ISSUE.md)
- [Pull-request draft](./UPSTREAM_PR.md)
- [Handoff](./HANDOFF.md)
