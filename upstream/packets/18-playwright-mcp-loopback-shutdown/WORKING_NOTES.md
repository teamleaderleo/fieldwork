# Unit 18 working notes

Last checked: 2026-08-03

## What this is

This is work in the Playwright repository, specifically Playwright's built-in MCP server and its tests. It is not an implementation of the MCP protocol itself.

The narrow question is how Playwright's own tests request graceful shutdown of the MCP child process without giving ordinary HTTP clients that same process-control path.

## Main routes considered

1. Keep the HTTP test hook but restrict it to loopback. A local proxy showed that the final TCP peer is not necessarily the original caller.
2. Hide the HTTP test hook behind an environment variable. This works as an opt-in design but still retains the HTTP control path.
3. Remove the HTTP hook and let the spawning test parent request shutdown through private Node IPC. This exact candidate passed the full focused gate on Ubuntu, macOS, and Windows.
4. Remove the HTTP hook and use parent stdin EOF. The HTTP experiment passed after listening for readable `end`, but the tested implementation consumed stdin before transport selection and could interfere with stdio MCP startup. It remains research only.

## Current source records

Canonical tested source:

```text
teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown
e99e97da2acfc6c1a67749bc749e1d0cb71b5607
```

Packet and source PRs:

- `teamleaderleo/fieldwork#451`
- `teamleaderleo/playwright#40`

Stdin research:

- `teamleaderleo/playwright#41`
- exact research head `86d32569b47fd9f6e98c11517d1699cea5a2465a`

## Repository divergence found today

The unit-18 packet and owned source still say `ISSUE FIRST` with strict parent IPC as the leading candidate.

Fieldwork issue #404 was edited on 2026-08-02 back to the older explicit-environment-capability direction and `state:execute`. PR #416 is validating corrections to that older evidence record.

This is a coordination conflict between two Fieldwork records. It is not new Playwright behavior and does not invalidate the later three-platform IPC result.

Public Playwright `main` is still exactly:

```text
15b1aec478d90f0293dae7b7b6dafd494d9f0154
```

That remains the exact base used by the unit-18 packet and source candidates.

## Current judgment

Do not silently overwrite either lane again. Preserve both, note that the capability work is the older comparison lane, and keep the unit-18 packet as the record of the later current-base route-removal work.

The next useful technical experiment, after the record split is acknowledged, is a transport-mode-aware stdin design with early stdio-message and disconnect controls. Until then, the strict IPC candidate is the strongest fully executed implementation.

Public upstream interaction performed: none.
