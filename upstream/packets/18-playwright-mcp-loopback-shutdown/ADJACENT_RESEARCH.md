# Adjacent research — Unit 18

## Purpose

This file records new approaches and nearby lifecycle findings discovered after the canonical parent-IPC candidate completed exact-head execution. These findings do not silently replace the canonical source branch.

## Canonical candidate remains selected

- source: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- exact-current execution: run `30690674059`
- result: complete success on Ubuntu 24.04, macOS 15, and Windows 2025
- current route: `ISSUE FIRST`

The candidate is the smallest fully executed design that removes the HTTP shutdown authority while retaining an explicit target-native graceful-SIGINT control across all three platforms.

## Alternative A — parent stdin EOF

### Why it looked promising

MCP already calls `setupExitWatchdog()`. The watchdog owns graceful browser closure for SIGINT/SIGTERM and also registered a handler for `process.stdin` `close`. The HTTP test harness already spawns the MCP child with piped stdin, so closing the parent's writable side appeared able to reuse an existing ownership channel without adding a private IPC message protocol.

### First discriminator

- source branch: `teamleaderleo/playwright:research/mcp-stdin-close-shutdown`
- first source head: `1d6ec11b5f06df32ce5b4fa0346af7631216e79c`
- source PR: `teamleaderleo/playwright#41`
- execution carrier: `teamleaderleo/fieldwork#494`
- first workflow: `30704410449`

The experiment removed `/killkillkill`, kept MCP responsive after the old request, then called `cp.stdin.end()` from the spawning test. Ubuntu, macOS, and Windows all reached the same negative result: no graceful-close receipt appeared.

### Root cause

Parent EOF is reported to a readable stream as `end`; `close` means the underlying resource was destroyed or closed. Also, `end` is emitted only while the readable stream is consumed. The existing watchdog's `close` listener therefore does not observe ordinary parent-side EOF in HTTP mode.

### Repaired experiment

- exact source head: `86d32569b47fd9f6e98c11517d1699cea5a2465a`
- exact carrier head: `2e32e643cdc6af0a322d49499b0cece3ee9e0699`
- workflow: `30704592268`
- change: watchdog listens for `end` and calls `process.stdin.resume()` so EOF becomes observable
- experiment fence:
  1. `packages/playwright-core/src/tools/mcp/watchdog.ts`
  2. `packages/playwright-core/src/tools/utils/mcp/http.ts`
  3. `tests/mcp/fieldwork-stdin-close.spec.ts`

All three platforms passed exact identity, locked install, complete build, Chromium, the ordinary MCP HTTP controls excluding the superseded route-based SIGINT test, the stdin-EOF discriminator, focused ESLint, clean tree, and exact diff.

| Platform | Result | Artifact | Digest |
| --- | --- | --- | --- |
| Ubuntu 24.04 | 17/17 passed in 21.5s and all declared gates passed | `8819925107` | `sha256:e05bcd01a8f7d1d43eb516fbc7891cdb310245c68d9d8450420a85f4a9454307` |
| macOS 15 | complete success | `8819927910` | `sha256:b1099fc064a80e1a8db32c6a17e298f0c9018419ed26cb2823a43214e8fc29f9` |
| Windows 2025 | complete success | `8819934140` | `sha256:6833261278e27a3a8b1670bffdc58b2fa9eeaf4f3a03582efe4537fe32600f99` |

### Why it is not promoted

The watchdog runs before server mode is resolved. In stdio mode, `server.start()` creates `StdioServerTransport` and already listens for stdin `end` to close that transport. Calling `process.stdin.resume()` globally before the transport attaches can put stdin into flowing mode and discard early MCP protocol bytes.

A safe stdin-owned design must therefore be mode-aware. It could consume stdin only after HTTP mode is selected while preserving the stdio transport's existing EOF handling. That is a broader lifecycle change with a new compatibility surface and requires dedicated stdio controls. It does not currently outrank the fully executed parent-IPC candidate.

## Alternative B — test-only IPC gating

The canonical listener is installed whenever `process.send` exists. MCP tests set Playwright's standard `PWTEST_UNDER_TEST=1` marker, so the listener could additionally require `isUnderTest()`.

Potential benefit: embeddings that provide a Node IPC channel would not expose the private test message outside Playwright's test environment.

Reason not applied now: the parent already owns the child process, the protocol is exact and one-shot, and changing the fully executed head would require another complete matrix. This remains a small hardening option for maintainer discussion.

## Nearby actionable leads

### 1. Other foreground servers use stdin `close`

Source search found the same ownership pattern outside MCP:

- `packages/playwright-core/src/cli/driver.ts` — `runServer()` exits on `process.stdin.on('close')`
- `packages/playwright/src/runner/testServer.ts` — `innerRunTestServer()` exits on `process.stdin.on('close')`
- additional dashboard and trace-viewer surfaces contain stdin-close ownership logic

The MCP experiment proves that parent `Writable.end()` does not by itself trigger the current MCP `close` listener. The other surfaces are source-read leads only; each needs a focused parent-EOF reproduction before any defect claim.

### 2. Signal exit-code semantics differ

MCP's watchdog exits with code `0` after SIGINT or SIGTERM. Playwright's general process launcher uses conventional SIGINT exit code `130` and includes repeated-interrupt escalation behavior. Whether MCP intentionally treats signals as a clean service stop is a maintainer-policy question. It should be investigated separately from removing the HTTP route.

### 3. Stdio SDK disconnect handling is already custom

`server.start()` notes that the MCP SDK's `StdioServerTransport` does not detect peer disconnect by itself and adds a local stdin `end` hook. This is the correct nearby owner for stdio EOF and reinforces that any HTTP stdin ownership should be installed only after transport mode is known.

## Recommended order

1. Keep `e99e97da...` as the canonical issue-first candidate.
2. Present stdin EOF as an alternative during upstream design discussion, including the positive cross-platform result and stdio-race limitation.
3. Only reopen implementation selection if maintainers prefer owner-pipe lifetime over a private test IPC message.
4. If reopened, build a mode-aware prototype and run both HTTP EOF and stdio early-message/disconnect controls on all three platforms.
5. Track the other stdin-close server surfaces and signal exit-code semantics as separate bounded findings.

Public upstream interaction remains unauthorized and none was performed.
