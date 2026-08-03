# Unit 18 working notes

Last checked: 2026-08-03

## What this is

This is work in the Playwright repository, specifically Playwright's built-in MCP server and its tests. It is not an implementation of the MCP protocol itself.

The narrow question is how Playwright's own tests request graceful shutdown of the MCP child process without giving ordinary HTTP clients that same process-control path.

## Routes considered

1. Keep the HTTP test hook but restrict it to loopback. A local proxy showed that the final TCP peer is not necessarily the original caller.
2. Hide the HTTP test hook behind an environment variable. This hides it by default but retains an opt-in HTTP process-control path.
3. Remove the HTTP hook and use strict parent Node IPC. This candidate passed the complete focused gate and independent review on Ubuntu, macOS, and Windows.
4. Remove the HTTP hook and use parent stdin EOF globally. HTTP shutdown worked, but consuming stdin before transport selection could race the stdio MCP protocol.
5. Remove the HTTP hook and consume stdin only after HTTP mode is selected and only under `PWTEST_UNDER_TEST`. This mode-aware design passed cross-platform and avoids the stdio race.

## Stable fallback

Strict parent IPC remains the polished fallback:

```text
teamleaderleo/playwright#40
fix/mcp-parent-ipc-shutdown
e99e97da2acfc6c1a67749bc749e1d0cb71b5607
```

It passed exact identity/fence, locked install, complete build, Chromium, all 18 native HTTP tests, focused ESLint, clean tree, and exact diff on Ubuntu 24.04, macOS 15, and Windows Server 2025. Independent review `4834404331` records `ACCEPT`.

## Preferred design direction

Mode-aware parent stdin is now the preferred issue-first design direction:

```text
teamleaderleo/playwright#42
research/mcp-mode-aware-stdin-shutdown
aa591123067b1a2cbe548e87cfc542de4bfeb98b
```

Exact source fence:

- `packages/playwright-core/src/tools/utils/mcp/http.ts`
- `packages/playwright-core/src/tools/utils/mcp/server.ts`
- `tests/mcp/fieldwork-stdin-close.spec.ts`

The design removes `/killkillkill`, leaves the stdio branch unchanged, and installs readable-EOF ownership only after HTTP mode is selected and only when Playwright's existing test marker is true. Parent EOF reuses the existing SIGINT cleanup path.

### Exact-current execution

Carrier `teamleaderleo/fieldwork#563@d26b0afbc9f0af37f86f0aa7d0bfe4fb7e9e15cd`, workflow `30759441716`, passed every declared gate on all three platforms:

- Ubuntu 24.04, job `91527222085`: 18/18 in 23.9s; artifact `8838780975`; digest `sha256:e416022f0fde3220246e43790793383e55335ab64310019a24f55bb5024429e7`;
- macOS 15, job `91527222089`: 18/18 and all declared gates; artifact `8837054976`; digest `sha256:35e7fe49da3b13f2b1686a39d7a5c0241b1e2ba80e368b8045ce56f8e73e096d`;
- Windows Server 2025, job `91527222072`: 18/18 in 33.6s; artifact `8836997607`; digest `sha256:ff84da9f486c43f2e4d7ba20d7ad5e20bb5aece418c748171fe058c8bffc22f9`.

Each job passed exact source/base identity, the exact three-file fence, locked install, complete build, Chromium setup, selected HTTP controls, HTTP parent-EOF graceful shutdown, immediate stdio initialization and ping, focused ESLint, clean tree, and exact diff.

Independent review `4842216872` records `ACCEPT DESIGN / REPAIR NATIVE INTEGRATION`.

## First-principles judgment

Parent stdin is already a process-ownership capability. HTTP clients and reverse proxies cannot acquire the writable end of that pipe. EOF uses an existing lifetime channel and avoids adding a private IPC message schema, parser, version, duplicate-delivery rule, and fourth file descriptor.

Transport separation is the key constraint. The rejected global experiment consumed stdin before Playwright knew whether stdin carried MCP protocol bytes. The accepted design waits until the stdio branch has returned, so `StdioServerTransport` retains exclusive ownership of stdio-mode input.

Production behavior is narrower than the IPC alternative. Ordinary launches do not enable `PWTEST_UNDER_TEST`; Playwright's boolean parser explicitly treats `false` and `0` as false. The only ordinary production change is removal of the network shutdown route.

## Why it is not ready for final review yet

The research head proves the mechanism but is not the final Playwright-native patch:

1. the test is still in `tests/mcp/fieldwork-stdin-close.spec.ts`;
2. the old native `http transport browser sigint` case is excluded rather than replaced;
3. no explicit test proves `PWTEST_UNDER_TEST=0` leaves HTTP alive after stdin EOF;
4. the final native test should assert process exit code 0;
5. the full native HTTP file must run without a grep exclusion on Ubuntu, macOS, and Windows;
6. the resulting complete diff needs independent final review.

The next source generation should integrate the mechanism into `tests/mcp/http.spec.ts`, retain immediate stdio startup coverage, add the non-test negative control, and rerun the full matrix. Until that settles, PR #40 remains the clean reviewable fallback.

## Repository coordination

Fieldwork issue #404 and PRs #410/#416 retain the older environment-capability comparison. This packet retains the later route-removal work. Preserve both by chronology and scope; do not silently overwrite either record.

Public `microsoft/playwright:main` remains exactly `15b1aec478d90f0293dae7b7b6dafd494d9f0154`, the base used by these candidates.

Public upstream interaction performed: none.
