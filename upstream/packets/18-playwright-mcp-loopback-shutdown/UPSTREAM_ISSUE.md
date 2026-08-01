# Upstream issue draft — Remove the MCP HTTP shutdown route from ordinary server reachability

Draft status: `ready after current-head execution`  
Public interaction authorized: `no`

---

## Summary

Playwright MCP's HTTP transport includes a special `/killkillkill` route used by the native cross-platform lifecycle test to simulate Ctrl+C. The route is available wherever the configured listener and Host policy accept the request. A non-browser client can send the fixed POST and custom header and request graceful process termination.

Could the lifecycle test move this action to the spawning parent's private process channel and remove the network route?

## Reproduction

1. Start Playwright MCP with a non-loopback listener and an accepted Host policy.
2. Connect an MCP client and open a disposable page.
3. Send `POST /killkillkill` with `x-pw-mcp-kill: 1` through the accepted HTTP endpoint.

Minimal request:

```text
POST /killkillkill
x-pw-mcp-kill: 1
```

## Observed behavior

On exact source revision `368941457a82da112aa8610107e25f4bde94339a` under Ubuntu 24.04 / Node 22 / Chromium, the request returned HTTP 200 `Killing process`, the server gracefully closed the tracked browser work, and the process exited code 0.

Wrong method, missing header, and wrong header returned 405 and left the server responsive. The default Host policy rejected the same non-loopback request before route handling.

## Expected behavior

Ordinary MCP HTTP reachability should not include process-shutdown authority for a route required only by the spawning lifecycle test.

## Current source observation

The route is dispatched inside `packages/playwright-core/src/tools/utils/mcp/http.ts` after Host validation. It requires POST plus a custom header, which protects against simple browser-coerced requests. A non-browser caller can supply both values.

The native `http transport browser sigint` test uses this route only to reach the existing graceful SIGINT cleanup path in a cross-platform way.

## Candidate direction

Remove the special HTTP branch and spawn the test child with a Node IPC fd. When an IPC channel exists, the MCP entrypoint can accept one exact internal versioned message from its parent, remove the listener, and emit the same SIGINT event. The native test can preserve the real-browser graceful cleanup assertion while proving:

- the old HTTP request stays inert;
- malformed and wrong-version messages stay inert;
- extra-field and inherited-property variants stay inert;
- duplicate valid delivery triggers one cleanup;
- IPC disconnect leaves the HTTP server responsive.

## Compatibility and risks

- The MCP network protocol and public CLI remain unchanged.
- The listener exists only when a parent process provides an IPC channel.
- The spawning parent already owns the child process and can terminate it independently.
- The test fixture adds an IPC fd to children spawned within this native suite.
- The strict private message format has no intended extension compatibility.

## Evidence limits

- Current exact-head execution is pending for the strict extra-field/inherited-property controls.
- No production deployment prevalence or impact claim is made.
- Full Playwright repository CI has not run for the candidate.
- Maintainer preference for test-fixture placement remains unknown.

## Versions and environment

- characterized commit: `368941457a82da112aa8610107e25f4bde94339a`
- current inspected commit: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- platforms already exercised by the hardened predecessor: Ubuntu 24.04, macOS 15, Windows 2025
- runtime: Node 22
- browser: Chromium
- relevant configuration: `--host=0.0.0.0 --allowed-hosts=* --isolated` for characterization

## Additional context

The existing POST plus custom-header behavior was introduced in merged PR [#40551](https://github.com/microsoft/playwright/pull/40551) to prevent browser-CSRF-style requests. This proposal addresses the separate question of whether an accepted non-browser HTTP client should have access to a test-only process termination route.

---

## Filing checklist

- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Reproduction works on a current public revision.
- [ ] Current strict-validator candidate passes exact-head tests.
- [ ] Severity and prevalence wording stays within evidence.
- [ ] Private, internal, or evidence-only links removed.
- [ ] Target issue template and contribution policy followed.
- [ ] AI disclosure handled according to current project policy.
- [ ] Exact user authorization to file this issue recorded.
