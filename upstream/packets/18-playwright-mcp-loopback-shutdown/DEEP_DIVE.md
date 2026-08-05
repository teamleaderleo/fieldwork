# Deep dive — Unit 18 Playwright MCP shutdown authority

## Problem

The MCP HTTP dispatcher includes `/killkillkill`. A matching `POST` with `x-pw-mcp-kill: 1` returns success and emits `SIGINT` in the server process. The route was added for a cross-platform lifecycle test, but it is reachable through the same HTTP listener as ordinary MCP traffic.

The fixed header reduces browser-CSRF exposure. It doesn't authenticate a script or agent that can reach the accepted host.

## Invariant

> The spawning process may control the child lifecycle. Ordinary MCP HTTP clients may not gain that authority from listener reachability alone.

## Selected implementation

Source: `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`

- `http.ts` removes the shutdown route.
- `server.ts` returns from the stdio branch before installing any HTTP stdin handling.
- In HTTP mode, `isUnderTest()` gates a one-shot readable-EOF listener.
- If stdin already ended, the same shutdown path is requested immediately.
- EOF emits the existing `SIGINT` event, so browser and connection cleanup remains centralized.
- `http.spec.ts` proves route inertness, liveness before EOF, graceful close and exit code 0, production-scope gating, and immediate stdio startup.

## Why stdin is an ownership signal

The parent creates and owns the child's stdin pipe. Closing its writable side is available to the spawning test process without exposing a command through HTTP. If the child doesn't respond, the parent or supervisor still retains normal OS process controls.

## Transport safety

Stdio MCP mode already uses stdin for protocol bytes. Installing a global listener or calling `resume()` before transport selection could consume those bytes. The selected source installs the listener only after stdio mode has returned, so HTTP lifetime handling and stdio protocol handling don't compete.

## Compatibility

- MCP protocol: unchanged
- public CLI options: unchanged
- ordinary HTTP launches: no stdin-driven shutdown because the test marker is absent
- test HTTP launches: parent EOF requests graceful shutdown
- process supervision: unchanged
- persistent data or migration: none

## Evidence

Run `30855503566` passed the complete 21-test MCP HTTP file, full build, focused lint, clean tree, and exact three-file diff on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

Full repository CI and Node versions outside 22 weren't run.

## Upstream state

Issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

The next step is a linked PR after explicit maintainer approval or assignment.
