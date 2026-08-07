# Fieldwork upstream PR draft — retired

Status: `not needed`

Issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

## Why this draft is retired

Fieldwork prepared and fully tested a parent-stdin implementation that removed `/killkillkill` entirely. After the issue was filed, Simon Knott self-assigned it and opened a smaller maintainer-owned fix. Pavel Feldman approved that pull request.

Opening the Fieldwork draft now would create a competing implementation after the maintainers already selected their preferred fix.

## Retained alternate

The prepared source remains at:

```text
teamleaderleo/playwright#48
10e28dfdd7758d92aeed50922fd9c7ce9596c21c
```

Run `30855503566` passed 21/21 plus all declared gates on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

Keep the draft and source only as research evidence. Reopen this path only if maintainers explicitly request the alternate design.
