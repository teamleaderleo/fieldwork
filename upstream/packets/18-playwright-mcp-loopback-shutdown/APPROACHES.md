# Approaches — Unit 18 Playwright MCP shutdown authority

## Decision criteria

1. Ordinary HTTP reachability must not grant process-shutdown authority.
2. The existing graceful browser cleanup path must remain covered on Linux, macOS, and Windows.
3. MCP stdio input must keep a single owner.
4. The replacement should stay small and test-only.

## Selected: mode-aware parent stdin EOF

- Remove `/killkillkill` from the HTTP dispatcher.
- Leave the stdio branch unchanged and return before installing any new stdin listener.
- In HTTP mode, only under Playwright's test marker, consume readable stdin EOF.
- Reuse the existing `SIGINT` cleanup path.

Exact source: `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`.

Why selected: the parent already owns the pipe, so the mechanism needs no HTTP credential and no private IPC message format. Run `30855503566` passed the full 21-test file and all declared gates on Ubuntu 24.04, macOS 15, and Windows Server 2025.

## Fallback: strict parent IPC

`teamleaderleo/playwright#40@e99e97da2acfc6c1a67749bc749e1d0cb71b5607` removes the route and accepts one exact parent message. It is fully executed and remains a safe fallback if maintainers prefer an explicit command over pipe lifetime.

## Rejected

### Keep the endpoint with the fixed header

The fixed value reduces browser-CSRF exposure but doesn't authenticate a programmatic client or prove process ownership.

### Restrict the endpoint to loopback or accepted Hosts

Those checks constrain reachability. They don't distinguish the spawning parent from another local client or proxy.

### Add an endpoint secret

This would preserve a remote process-control API and add token generation and handling for a test action already available through a parent-owned pipe.

### Consume stdin before transport selection

The HTTP mechanism works, but early `resume()` can race the stdio transport and discard protocol bytes. The final source avoids this placement.

## Current route

The issue is filed at [the Playwright bug report](https://redirect.github.com/microsoft/playwright/issues/42129). Wait for explicit approval or assignment before opening the upstream PR.
