# Approaches — Unit 18 Playwright MCP shutdown authority

## In simple words

Three repairs reached target execution. Direct loopback-peer checks were defeated by a local proxy. An explicit process capability removed accidental default exposure but retained a deliberately enabled network shutdown route. Parent-owned IPC removes network shutdown authority entirely while preserving the original cross-platform lifecycle-test purpose, so it leads.

## Decision criteria

1. Ordinary MCP network reachability must not grant process-shutdown authority.
2. The real-browser graceful SIGINT lifecycle test must continue on Linux, macOS, and Windows.
3. Wrong, repeated, or disconnected control messages must not replace or duplicate cleanup.
4. The source change should stay inside a small, reviewable target-native fence.
5. The mechanism should avoid a new public option, token lifecycle, proxy identity assumption, or hidden deployment contract.

## Selected approach

### One-shot parent-owned IPC

- Design: remove `/killkillkill`; spawn the MCP test child with an IPC fd; accept one exact internal message from the spawning parent; remove the listener before SIGINT.
- Owning boundary: MCP CLI entrypoint plus the test fixture that creates the child.
- Evidence: Linux 18/18 at PR #430; unchanged hardened patch 18/18 on Ubuntu/macOS/Windows at PR #432.
- Advantages: no HTTP route, no network credential, no proxy identity problem, no operator capability, parent already owns the process.
- Costs and risks: test-only listener lives in the CLI entrypoint when any parent supplies IPC; strict message validation adds a small private protocol.
- Remaining controls: exact current-head build/test/lint/diff execution for the extra-field and inherited-property rejection increment.

## Viable alternatives

### Explicit process capability

- Design: expose the route only when `PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN=1` is present.
- Why it remains plausible: passed direct and local-proxy controls; default process hides the route with 404.
- What it would improve: makes route exposure an explicit operator decision.
- What it would widen or complicate: retains a network shutdown route, adds configuration/help/deployment semantics, and allows inherited environment to re-enable it.
- Exact discriminator: parent-owned IPC works across every supported platform without a route.
- Reopening trigger: a supported runtime or test harness cannot provide reliable parent IPC.

### Keep route and document trusted deployment

- Design: retain POST/header and explain that remote HTTP requires a trusted authenticated boundary.
- Why it remains plausible: smallest source change and consistent with operator responsibility.
- What it would improve: documentation clarity only.
- What it would widen or complicate: leaves the test-only termination primitive reachable by accepted network clients.
- Exact discriminator: parent IPC removes the primitive without losing the test.
- Reopening trigger: route is confirmed as a supported external API rather than test machinery.

## Executed losing approaches

### Direct loopback peer

- Exact branch, patch, or commit: `teamleaderleo/playwright#37@a834222d585371636eea7fd013e551fb819d9f7d`; retained comparison PR #410.
- What ran: complete native HTTP suite, direct remote/loopback controls, build, lint, diff hygiene; later local-proxy discriminator.
- Result: direct remote caller received 403, but a local proxy relayed the request over loopback and MCP returned 200, gracefully closed the browser, and exited.
- Why it lost: socket peer describes the final transport hop, not the originating client.
- Useful evidence retained: direct-peer address classification and explicit proxy counterexample.

### Explicit environment capability

- Exact branch, patch, or commit: retained candidate in PR #410 and proxy execution in PR #416.
- What ran: 17 upstream controls under enabled capability, 2 capability controls, and 1 proxy control.
- Result: ordinary process returned 404 and stayed responsive; enabled process retained shutdown behavior.
- Why it lost: parent IPC removed the route entirely and therefore granted less authority.
- Useful evidence retained: viable fallback if IPC becomes unavailable.

### Bare-string parent IPC

- Exact branch, patch, or commit: PR #423 head `bcceeadc2c806ab6e60e013d2278b7515339036d`.
- What ran: 17/17 native suite on Ubuntu/macOS/Windows.
- Result: removed network route and preserved graceful lifecycle.
- Why it lost: public-looking bare string and persistent listener were weaker than a one-shot structured/versioned message.
- Useful evidence retained: decisive cross-platform feasibility proof.

### Matching type/version object

- Exact branch, patch, or commit: PR #430 head `59899a28503cbe9d97811cbed103b6fc831e6663`.
- What ran: 18/18 on Ubuntu/macOS/Windows.
- Result: one-shot ordering, duplicate handling, wrong string/version, disconnect, and lifecycle all passed.
- Why it needs one increment: validator accepted extra fields and inherited properties while the record claimed one exact message.
- Useful evidence retained: all hardened behavior except exact-own-property discrimination.

## Rejected easy answers

### Trust the custom header

- Temptation: treat the fixed non-simple header as authorization.
- Why it is incomplete: it is browser-CSRF resistance; a non-browser client can set it.
- Negative control or source fact: exact non-loopback request with the fixed header returned 200 and terminated MCP.

### Trust Host validation

- Temptation: accepted Host implies an authorized client.
- Why it is incomplete: Host validation protects against DNS rebinding; wildcard or explicit accepted hosts intentionally widen reachability.
- Negative control or source fact: default Host rejected the request, while wildcard Host accepted it.

### Trust loopback

- Temptation: direct peer locality represents local authority.
- Why it is incomplete: a local proxy terminates the remote connection and creates a loopback connection to MCP.
- Negative control or source fact: PR #416 executed this exact topology.

### Use a reusable secret in the URL or header

- Temptation: authenticate shutdown with a random token.
- Why it is incomplete: introduces generation, distribution, redaction, lifetime, and accidental exposure concerns for a primitive required only by the spawning test parent.
- Negative control or source fact: parent already owns the child and needs no new transferable credential.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`microsoft/playwright#40551`](https://github.com/microsoft/playwright/pull/40551) | require POST plus custom header | merged | complementary browser-CSRF hardening; does not establish client authority |
| [`4a80eed`](https://github.com/microsoft/playwright/commit/4a80eed396071d6ed15a74c32723f2bc66849988) | implementation of the POST/header repair | merged | exact historical source predecessor |

## Deferred adjacent work

- MCP client authentication — separate product and protocol decision
- proxy trust and forwarded identity — separate deployment design
- shared browser-context authority — adjacent Fieldwork finding, separate unit
- public security reporting — requires impact and authorization decisions

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | PR #410 direct comparison | provisional loopback selection | preserved test behavior with no hidden capability | realistic relay topology |
| 2026-07-31 | PR #416 proxy run `30656319708` | select explicit capability | proxy defeats direct-peer identity | route can be removed entirely |
| 2026-07-31 | PR #425 run `30657930500` | select parent IPC | cross-platform lifecycle preserved with no route | source hardening failure |
| 2026-07-31 | PR #432 run `30659762667` | select one-shot structured IPC | hardened generation passed three platforms | exact-message claim mismatch |
| 2026-08-01 | source head `c4c5e2d...` on public base `15b1aec...` | execute exact-message increment | rejects extra fields and inherited properties on a disjoint current base | exact-head test failure or maintainer contract |
