# Upstream issue record

Status: `accepted into maintainer work / assigned / v1.63 / linked fix approved`

Issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

## Filed report

The issue reported that an ordinary programmatic HTTP client that could reach an accepted MCP host could reproduce the fixed `/killkillkill` request and cause the server to emit `SIGINT`.

The report included the route history, the later POST/custom-header hardening, a command-line reproduction, current source references, and the completed parent-stdin research implementation.

## Maintainer response

Simon Knott self-assigned the issue and added the `v1.63` label. He opened the linked pull request that closes the issue. Pavel Feldman approved that pull request.

The chosen fix is smaller than the proposed parent-stdin replacement: `/killkillkill` remains available only under Playwright's own `isUnderTest()` marker. Ordinary MCP HTTP servers no longer expose it.

## Contribution outcome

Count this unit as a successful issue contribution. The report directly resulted in maintainer-owned corrective work. A Fieldwork-authored upstream pull request is not needed.

Current finalization gate: maintainer PR merge and issue closure.
