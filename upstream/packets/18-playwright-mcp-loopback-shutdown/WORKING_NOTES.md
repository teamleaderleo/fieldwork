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
5. Scope stdin EOF ownership to HTTP tests only. This experiment leaves stdio startup untouched, consumes stdin only after HTTP mode is selected and only under `PWTEST_UNDER_TEST`, and adds an immediate stdio-connect control.

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

- source PR: `teamleaderleo/playwright#42`
- current exact source: `aa591123067b1a2cbe548e87cfc542de4bfeb98b`
- exact three-file fence: `http.ts`, `server.ts`, and `fieldwork-stdin-close.spec.ts`
- current execution carrier: `teamleaderleo/fieldwork#563@d26b0afbc9f0af37f86f0aa7d0bfe4fb7e9e15cd`
- current workflow: `30759441716`

### Generation 1

Source `679e93190efd422727cb073bf0ceb9eee1611779`, workflow `30759098346`:

- macOS and Windows each passed exact identity, locked install, complete build, Chromium, and all 18 selected HTTP/stdin tests;
- focused ESLint then failed on the same single `curly` rule in `server.ts`;
- no behavior or transport failure was observed;
- macOS artifact `8836952814`, digest `sha256:473c0f97dbd2e7f1e86fe92b621ae86b53eb1753816dd58ff2c9c2d20e6b34ac`;
- Windows artifact `8836968509`, digest `sha256:52feb9ffa452d8e2f9bd432af5f76fbb568461a7f368f042941b22fd417c74ca`.

The repair added only the required braces.

### Generation 2

Source `aa591123067b1a2cbe548e87cfc542de4bfeb98b`, workflow `30759441716`:

- Windows passed exact identity/fence, locked install, complete build, Chromium, 18/18 tests in 33.6s, focused ESLint, clean tree, and exact diff;
- Windows artifact `8836997607`, digest `sha256:ff84da9f486c43f2e4d7ba20d7ad5e20bb5aece418c748171fe058c8bffc22f9`;
- exact-current macOS and Ubuntu remained queued at this note.

The mode-aware branch is not canonical yet. It needs exact-current macOS and Ubuntu completion plus independent comparison before it can displace the strict IPC candidate.

## Repository divergence found today

The unit-18 packet and owned source retain `ISSUE FIRST` with strict parent IPC as the leading fully executed candidate.

Fieldwork issue #404 was edited on 2026-08-02 back to the older explicit-environment-capability direction and `state:execute`. PR #416 is validating corrections to that older evidence record.

This is a coordination conflict between two Fieldwork records. It is not new Playwright behavior and does not invalidate the later three-platform IPC result.

Public Playwright `main` is still exactly:

```text
15b1aec478d90f0293dae7b7b6dafd494d9f0154
```

That remains the exact base used by the unit-18 packet and source candidates.

## Current judgment

Do not silently overwrite either lane again. Preserve both, treat the capability work as the older proxy-topology comparison, and keep the unit-18 packet as the record of the later current-base route-removal work.

The strict IPC candidate remains the strongest fully executed implementation. Mode-aware stdin is now a credible comparison rather than a speculative idea: it has behavior-positive macOS and Windows evidence, and an exact-current complete Windows result. It still needs the remaining exact-current platforms and review of the `PWTEST_UNDER_TEST` dependency.

Public upstream interaction performed: none.
