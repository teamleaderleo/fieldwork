# Unit 18 working notes

Last checked: 2026-08-03

## What this is

This is work in the Playwright repository, specifically Playwright's built-in MCP server and its tests. It is not an implementation of the MCP protocol itself.

The narrow question is how Playwright's own tests request graceful shutdown of the MCP child process without giving ordinary HTTP clients that same process-control path.

## Main routes considered

1. Keep the HTTP test hook but restrict it to loopback. A local proxy showed that the final TCP peer is not necessarily the original caller.
2. Hide the HTTP test hook behind an environment variable. This works as an opt-in design but still retains the HTTP control path.
3. Remove the HTTP hook and let the spawning test parent request shutdown through private Node IPC. This exact candidate passed the full focused gate on Ubuntu, macOS, and Windows.
4. Remove the HTTP hook and use parent stdin EOF. The first HTTP experiment passed after listening for readable `end`, but it consumed stdin before transport selection and could interfere with stdio MCP startup.
5. Scope stdin EOF ownership to HTTP tests only. This new experiment leaves stdio startup untouched, consumes stdin only after HTTP mode is selected and only under `PWTEST_UNDER_TEST`, and adds an immediate stdio-connect control.

## Current source records

Canonical tested source:

```text
teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown
e99e97da2acfc6c1a67749bc749e1d0cb71b5607
```

Packet and source PRs:

- `teamleaderleo/fieldwork#451`
- `teamleaderleo/playwright#40`

First stdin research:

- `teamleaderleo/playwright#41`
- exact research head `86d32569b47fd9f6e98c11517d1699cea5a2465a`

Mode-aware stdin research:

- `teamleaderleo/playwright#42`
- exact source head `679e93190efd422727cb073bf0ceb9eee1611779`
- exact three-file fence: `http.ts`, `server.ts`, and `fieldwork-stdin-close.spec.ts`
- execution carrier: `teamleaderleo/fieldwork#563@d46b11c988cfeda87123d0538952bdc57b39e4f0`
- workflow `30759098346`: queued at the time of this note

The mode-aware branch is not canonical. It must pass exact three-platform execution and independent comparison before it can displace the strict IPC candidate.

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

The strict IPC candidate remains the strongest fully executed implementation. The mode-aware stdin branch is now the best bounded comparison because it may remove the network hook without adding a private message protocol while directly avoiding the stdio race found in the first stdin experiment.

Public upstream interaction performed: none.
