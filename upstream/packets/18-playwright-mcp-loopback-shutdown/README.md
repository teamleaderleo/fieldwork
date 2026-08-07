# Unit 18 — Playwright MCP shutdown authority

## Summary

Playwright MCP's HTTP server exposed `/killkillkill`, a test route that emits `SIGINT`, to ordinary HTTP launches. Fieldwork reproduced the behavior, traced the route's history, and filed the bug report.

The report was accepted into active maintainer work: Simon Knott self-assigned it, tagged it for `v1.63`, and opened a linked fix. Pavel Feldman approved that fix.

## Current disposition

`ISSUE CONTRIBUTION ACCEPTED / MAINTAINER FIX APPROVED / NO FIELDWORK PR NEEDED`

- upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)
- maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)
- packet PR: `teamleaderleo/fieldwork#451`
- Fieldwork research source: `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- exact Fieldwork execution: run `30855503566`

## Maintainer-selected fix

The upstream change keeps `/killkillkill` as Playwright test machinery but gates it with `isUnderTest()`. The test no longer needs the POST/custom-header check because production MCP HTTP servers do not expose the route at all.

That is narrower than the Fieldwork parent-stdin candidate and matches the maintainers' chosen boundary: the endpoint may exist under Playwright's own test marker, but not in ordinary MCP HTTP servers.

## Fieldwork research retained

The parent-stdin candidate removed the route entirely and passed the full 21-test native MCP HTTP file, complete build, focused ESLint, clean tree, and exact three-file diff on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

Keep that work as supporting research, not as a competing upstream submission.

## Next action

Watch the maintainer fix through merge and issue closure. No Fieldwork-authored upstream pull request is planned unless maintainers explicitly request an alternative.

## Packet navigation

- [Current source and upstream choice](./CURRENT_SOURCE.md)
- [Current execution](./CURRENT_EXECUTION.md)
- [Technical explanation](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests](./TESTS.md)
- [Review](./REVIEW.md)
- [Submitted issue record](./UPSTREAM_ISSUE.md)
- [Upstream PR outcome](./UPSTREAM_PR.md)
- [Handoff](./HANDOFF.md)
