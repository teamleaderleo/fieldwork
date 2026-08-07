# Review — Unit 18 Playwright MCP shutdown authority

## Upstream review outcome

Issue: [submitted bug report](https://redirect.github.com/microsoft/playwright/issues/42129)

Maintainer fix: [only enable `/killkillkill` under test](https://redirect.github.com/microsoft/playwright/pull/42133)

Simon Knott self-assigned the issue and opened the linked fix. Pavel Feldman approved that pull request.

## Maintainer-selected diff

The upstream source changes two files:

- `packages/playwright-core/src/tools/utils/mcp/http.ts`
- `tests/mcp/http.spec.ts`

The HTTP handler now serves `/killkillkill` only when `isUnderTest()` is true. The lifecycle test uses the test-only route directly. The fixed POST/custom-header check is removed because ordinary MCP HTTP launches no longer expose the endpoint.

This is a smaller fix than the Fieldwork parent-stdin candidate and directly addresses the reported production exposure.

## CI state

The linked upstream CI reported one unrelated Firefox annotate/screencast failure. Playwright's CI triage classified it as a pre-existing flake and stated that the pull request itself was clear.

The upstream pull request remains open and not yet merged.

## Fieldwork source review

Fieldwork's alternate source remains `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`. Run `30855503566` passed 21/21 and every declared focused gate on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

No defect was found in that alternate, but it no longer needs upstream review because maintainers selected their own smaller implementation.

## Disposition

`ISSUE CONTRIBUTION SUCCEEDED / MAINTAINER FIX APPROVED / NO COMPETING PR`

Count the issue report as the upstream contribution for this unit. Retain the Fieldwork source as research only unless maintainers request it.
