# Unit 18 continuation handoff

## Current state

This unit has a successful upstream issue contribution.

- issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)
- maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

Simon Knott self-assigned the issue, added `v1.63`, and opened the linked fix. Pavel Feldman approved it. The pull request is currently open and not yet merged.

## Maintainer decision

The maintainers chose a smaller fix than the Fieldwork parent-stdin candidate:

- retain `/killkillkill` for Playwright's own lifecycle test;
- expose it only when `isUnderTest()` is true;
- remove the POST/custom-header requirement from the test-only route.

This resolves the reported production exposure without adding new stdin lifecycle handling.

## Fieldwork research

The alternate parent-stdin source remains fully executed and useful as supporting evidence:

- owned PR: `teamleaderleo/playwright#48`
- base: `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`
- head: `10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- run `30855503566`: 21/21 on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025, plus build, focused lint, clean tree, and exact diff checks.

Do not open that source upstream as a competing pull request. Retain it as research unless a maintainer asks for an alternative.

## Next action

1. Watch the maintainer pull request for merge.
2. Watch the upstream issue for closure.
3. Record the final merged commit/release state in this packet when it lands.

No further upstream write is needed from Fieldwork for this unit unless a maintainer asks a question or the user explicitly authorizes a response.
