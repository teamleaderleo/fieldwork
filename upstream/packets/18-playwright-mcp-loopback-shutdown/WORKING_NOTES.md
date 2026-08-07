# Unit 18 working notes

Last checked: 2026-08-07

## Question

How can Playwright's lifecycle test exercise graceful MCP HTTP shutdown without exposing process-control behavior in ordinary HTTP launches?

## Issue contribution

Upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Simon Knott self-assigned the issue, added `v1.63`, and opened the linked maintainer fix. Pavel Feldman approved it.

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

## Maintainer-selected fix

The selected implementation is smaller than Fieldwork's parent-stdin proposal:

- keep `/killkillkill` for the graceful-SIGINT lifecycle test;
- gate the route with `isUnderTest()`;
- remove the fixed POST/header requirement from that test-only path;
- leave ordinary MCP HTTP servers without the route.

This means the maintainers accepted the production-exposure problem but did not consider a shutdown endpoint inside Playwright's own test environment objectionable.

## Fieldwork research source

```text
teamleaderleo/playwright#48
fix/mcp-http-parent-stdin-review
base 2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2
head 10e28dfdd7758d92aeed50922fd9c7ce9596c21c
```

That alternate removes the route entirely and uses parent stdin EOF only after HTTP mode is selected. Run `30855503566` passed 21/21 and every declared gate on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

Keep it as research evidence. Do not open it upstream as a competing pull request unless maintainers request the alternate.

## Contribution judgment

`ISSUE CONTRIBUTION ACCEPTED / MAINTAINER FIX APPROVED`

This counts as the upstream contribution for Unit 18: the report identified a real issue, supplied enough evidence to reproduce and understand it, and directly triggered maintainer-owned corrective work.

## Finalization

The upstream pull request is approved but currently open and not yet merged. Final packet update after merge should record the merge commit, issue closure, and release status if available.
