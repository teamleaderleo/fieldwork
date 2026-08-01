# Approaches — Unit 18 Playwright MCP shutdown authority

## Decision criteria

1. Ordinary MCP network reachability must not grant process-shutdown authority.
2. The real-browser graceful shutdown lifecycle must remain target-native and cross-platform.
3. Wrong, repeated, or disconnected controls must not replace or duplicate cleanup.
4. The source change must remain small and reviewable.
5. The mechanism should avoid a new public token, option, proxy assumption, or accidental protocol surface.
6. A replacement ownership channel must not interfere with ordinary stdio MCP traffic.

## Selected approach

### One-shot strict parent-owned IPC

- Remove `/killkillkill` from the HTTP transport.
- Spawn the MCP test child with Node IPC.
- Accept one exact plain-object `{ type, version }` message from the spawning parent.
- Reject wrong strings, wrong versions, extension fields, inherited properties, and disconnect.
- Remove the listener before emitting SIGINT.

Exact source: `fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`.

Exact result: workflow `30690674059` passed all 18 native MCP HTTP tests plus locked install, complete build, Chromium, focused ESLint, clean tree, and exact diff on Ubuntu 24.04, macOS 15, and Windows 2025.

Why it remains selected: it is the smallest fully executed design that removes network authority without changing normal MCP stdio behavior.

## Newly executed alternative

### Mode-aware parent stdin EOF

#### Initial hypothesis

The HTTP test harness already owns the child's stdin pipe, and MCP already has an exit watchdog. Closing the parent writable side could reuse process ownership without adding a private IPC message.

#### First result

Source `1d6ec11b...` removed the route and closed `cp.stdin`, but all three platforms failed the graceful-close discriminator. Parent EOF arrives as readable `end`; the watchdog listened for `close`.

#### Repaired experiment

Source `86d32569b47fd9f6e98c11517d1699cea5a2465a` listens for stdin `end` and calls `process.stdin.resume()`. Workflow `30704592268` passed a 17-test matrix, complete build, Chromium, focused ESLint, clean tree, and exact diff on Ubuntu, macOS, and Windows.

#### Why it is held

The watchdog is installed before server mode is selected. Global `process.stdin.resume()` can put stdin into flowing mode before `StdioServerTransport` attaches and can discard early protocol input. Stdio mode already owns its EOF handling in `server.start()`.

Reopening condition: a mode-aware implementation consumes stdin only after HTTP mode is known and passes dedicated stdio early-message, disconnect, and ordinary protocol controls across all three platforms.

## Other viable alternatives

### Test-marker gate on the IPC listener

Require Playwright's standard under-test marker in addition to `process.send` before installing the private listener.

Benefit: embeddings with an IPC channel would not accept the test message outside Playwright's test environment.

Why not applied: the parent already owns the child, the message is exact and one-shot, and changing the fully executed source head would require another matrix. Keep as a maintainer-review hardening option.

### Explicit process capability

Expose the route only when `PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN=1` is present.

It passed direct and proxy controls, but retains a network termination primitive and adds configuration/deployment semantics. Reopen only if maintainers reject both private parent channels.

### Keep route and document trusted deployment

Smallest code delta, but leaves the test-only termination primitive reachable by accepted network clients. Reopen only if `/killkillkill` is confirmed as a supported external API.

## Executed losing approaches

### Direct loopback peer

PR #416 proved a local proxy presents a loopback peer and can relay the terminating request. Socket peer identity describes the last hop, not the originating caller.

### Bare-string persistent IPC

Cross-platform viable, but weaker than a one-shot structured/versioned message.

### Loose matching object

Cross-platform viable, but accepted extra fields and inherited matching properties. Superseded by the exact-own-property validator.

### Naïve stdin `close`

Failed identically on Ubuntu, macOS, and Windows because ordinary parent EOF did not trigger the watchdog's `close` listener.

### Global stdin `resume()` as final design

HTTP discriminator passed cross-platform, but the placement can race stdio protocol attachment. Useful proof, not a safe final design.

## Rejected easy answers

- Treat fixed custom header as authorization: non-browser clients can set it.
- Treat Host validation as authorization: it controls accepted hostnames and DNS rebinding, not caller identity.
- Treat loopback as original-client identity: proxies break that assumption.
- Add a reusable URL/header secret: unnecessary token lifecycle for a parent-owned test action.
- Change signal exit codes in this unit: separate lifecycle-policy question.
- Repair every stdin-close server surface here: separate bounded investigations.

## Nearby leads kept separate

- `packages/playwright-core/src/cli/driver.ts` foreground server stdin ownership
- `packages/playwright/src/runner/testServer.ts` stdin ownership
- dashboard/trace-viewer stdin-close patterns
- MCP SIGINT/SIGTERM exit-code semantics versus the general process launcher

These are source-read leads, not unit 18 defect claims. See `ADJACENT_RESEARCH.md`.

## Decision history

| Date | Evidence | Decision |
| --- | --- | --- |
| 2026-07-31 | direct loopback controls | provisional loopback repair |
| 2026-07-31 | local-proxy discriminator | reject loopback; select explicit capability |
| 2026-07-31 | bare IPC three-platform execution | select parent ownership; remove route |
| 2026-07-31 | one-shot structured IPC three-platform execution | select hardened IPC |
| 2026-08-01 | exact strict validator run `30690674059` | exact current candidate clears execution gate |
| 2026-08-01 | stdin runs `30704410449` and `30704592268` | retain mode-aware stdin EOF as issue-first alternative; do not replace IPC yet |

Current contribution route: `ISSUE FIRST`.
