# Upstream pull-request outcome

Fieldwork-authored upstream PR status: `not needed`

Issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

## Outcome

Simon Knott took the issue and opened the linked fix. Pavel Feldman approved it. The upstream pull request is currently open and not yet merged.

The maintainer implementation keeps `/killkillkill` only under `isUnderTest()` instead of replacing it with parent stdin EOF. That directly removes the route from ordinary production MCP HTTP servers with a two-file change.

## Fieldwork source

The prepared parent-stdin source remains at:

```text
teamleaderleo/playwright#48
10e28dfdd7758d92aeed50922fd9c7ce9596c21c
```

Run `30855503566` passed its complete focused matrix on Ubuntu, macOS, and Windows. Keep it as research evidence and an alternate design record.

## Submission decision

Do not open a competing Fieldwork pull request upstream. The contribution goal for this unit has been met by the issue report leading to maintainer-owned corrective work.

Only reopen the Fieldwork PR path if maintainers explicitly request the alternate implementation.
