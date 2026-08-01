# Upstream pull-request draft — fix(mcp): replace HTTP shutdown route with parent IPC

Draft status: `issue first`  
Proposed head: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown`  
Proposed base: `microsoft/playwright:main` from exact base `15b1aec478d90f0293dae7b7b6dafd494d9f0154`  
Public interaction authorized: `no`

---

## Summary

- Remove the test-only `/killkillkill` route from the MCP HTTP transport.
- Exercise the existing graceful SIGINT path through the spawning test parent's private Node IPC channel.
- Accept one exact versioned message once and keep malformed, duplicate, and disconnected IPC behavior inert.

## Problem

The MCP HTTP server exposes a special shutdown route used by one native lifecycle test. The route follows the configured listener and Host policy, so an accepted non-browser HTTP caller can request graceful process termination with a fixed POST and header.

The route is test machinery. Ordinary MCP network reachability should not grant process-shutdown authority.

## Change

`packages/playwright-core/src/tools/utils/mcp/http.ts` removes the shutdown branch.

`packages/playwright-core/src/entry/mcp.ts` installs a test-parent message listener only when the child has an IPC channel. It accepts one plain object with exactly the own keys `type` and `version`, exact values, and the ordinary object prototype. The listener is removed before emitting SIGINT.

`tests/mcp/http.spec.ts` spawns the child with an IPC fd and verifies the old HTTP request, wrong string, wrong version, extra-field object, inherited-property object, duplicate valid delivery, IPC disconnect, and the existing real-browser graceful cleanup path.

## Tests

Planned exact-head commands:

- `npm ci`
- `npm run build`
- `npx playwright install chromium` (plus platform dependencies where required)
- `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`
- `npx eslint packages/playwright-core/src/entry/mcp.ts packages/playwright-core/src/tools/utils/mcp/http.ts tests/mcp/http.spec.ts`
- `git diff --check`

Retained predecessor evidence:

- hardened one-shot generation: 18/18 native MCP HTTP tests on Ubuntu 24.04, macOS 15, and Windows 2025 under Node 22 / Chromium
- complete Playwright build, focused ESLint, and exact three-file diff passed on each platform

## Compatibility

- public API: unchanged
- existing behavior retained: ordinary MCP HTTP/SSE behavior and graceful SIGINT cleanup
- platform or runtime notes: parent IPC predecessor passed Linux, macOS, and Windows with Node 22
- performance or allocation notes: one process message listener only when an IPC channel exists
- migration or rollback: none; revert the three-file commit

## Alternatives considered

- Direct loopback-peer restriction passed direct controls but failed through a local reverse proxy because the proxy's connection appears loopback.
- An explicit environment capability hid the route by default but retained an operator-enabled network shutdown primitive.
- A reusable secret would add generation, distribution, lifetime, and redaction work for an action required only by the process that already owns the child.

## Limits

- Exact current-head execution for the strict extra-field/inherited-property controls is pending.
- Full Playwright repository CI has not run for the candidate.
- This change does not add MCP client authentication or change shared-browser authority.

## Related work

- [Require POST plus a custom header on `/killkillkill`](https://github.com/microsoft/playwright/pull/40551)

---

## Submission checklist

- [ ] A corresponding upstream issue is triaged and the contribution is approved or assigned.
- [ ] Branch is a direct child or clean rebase of a recent upstream head.
- [ ] Diff contains only the two product files and one target-native test file.
- [ ] Fieldwork wording, temporary workflows, publishers, receipts, and evidence-only files are absent.
- [ ] Transient source-branch commits are squashed into a clean semantic commit.
- [ ] Every changed file was reviewed at the exact proposed head.
- [ ] Focused regression relationship is clear: baseline HTTP request terminates; candidate request stays inert.
- [ ] Current exact-head build, native suite, lint, diff, and platform result are recorded.
- [ ] Current duplicate and overlap search is repeated.
- [ ] Commit title follows Playwright semantic commit conventions.
- [ ] Current contribution and AI-disclosure policies are checked at filing time.
- [ ] Exact user authorization to open the pull request is recorded.
