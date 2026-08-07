# Packet status

Current disposition: `ISSUE CONTRIBUTION ACCEPTED / MAINTAINER FIX APPROVED / NO FIELDWORK PR NEEDED`

Upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

## Upstream outcome

Simon Knott self-assigned the issue, added the `v1.63` label, and opened the linked fix. Pavel Feldman approved that pull request. It is currently open and not yet merged.

The upstream fix takes a smaller route than the Fieldwork candidate: it keeps `/killkillkill` for Playwright's own tests, gates it with `isUnderTest()`, and removes the fixed POST/header requirement from the test-only path. Production MCP HTTP servers therefore no longer expose the shutdown route.

## Fieldwork contribution result

The issue report is the contribution outcome for this unit. It identified the production exposure, supplied a reproduction and history, and led directly to a maintainer-owned fix. Fieldwork should not open a competing upstream pull request unless maintainers specifically ask for an alternative.

The fully executed parent-stdin source remains retained as research evidence:

- owned source PR: `teamleaderleo/playwright#48`
- exact base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- exact source: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- run `30855503566`: 21/21 plus all declared gates on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

Packet integrity for the previous packet head passed in run `30972618158`.

## Next gate

Watch the maintainer pull request through merge and issue closure. No Fieldwork-authored upstream PR is planned.
