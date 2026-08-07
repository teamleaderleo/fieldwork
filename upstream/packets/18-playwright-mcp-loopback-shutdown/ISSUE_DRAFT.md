# Submitted upstream issue record

## Issue

[MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Current status: open, assigned to Simon Knott, labeled `v1.63`, with an approved linked maintainer fix.

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

## Filed title

`[Bug]: MCP HTTP clients can terminate the server through /killkillkill`

## Reported behavior

A programmatic HTTP client that can reach an accepted MCP host could send the fixed `/killkillkill` request and cause the server to emit `SIGINT`.

The report explained that the fixed header reduced browser-CSRF exposure but did not distinguish the test harness from another programmatic client.

## Proposed direction in the report

Fieldwork proposed removing the HTTP route and using parent stdin EOF in HTTP test mode. That implementation was fully validated across Ubuntu, macOS, and Windows.

## Maintainer-selected direction

The maintainers chose a smaller fix: keep the route only while `isUnderTest()` is true. Ordinary MCP HTTP servers therefore no longer expose it. Pavel Feldman approved that implementation.

## Contribution result

The report produced a direct maintainer-owned fix, so the issue itself is the upstream contribution for this unit. No competing Fieldwork pull request is planned.
