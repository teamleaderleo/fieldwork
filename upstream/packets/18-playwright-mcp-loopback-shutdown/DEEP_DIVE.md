# Deep dive — Unit 18 Playwright MCP shutdown authority

## In simple words

Playwright MCP's HTTP server contains a special route used by one cross-platform lifecycle test to simulate Ctrl+C. The route follows the same listener and Host reachability as ordinary MCP traffic. Exact execution showed that a caller accepted by those network controls can terminate the process by sending a fixed POST and header.

The selected correction removes the network route and moves the test-only action to the spawning parent's private Node IPC channel. That parent already owns the child process. The current candidate accepts one exact, versioned plain-object message once, removes the listener before emitting SIGINT, and keeps malformed messages, duplicate delivery, and IPC disconnect inert.

## Governing invariant

> An ordinary MCP client, accepted Host, reverse proxy, or inherited process configuration must never acquire process-shutdown authority solely through the MCP HTTP listener; the test harness may exercise graceful SIGINT only through authority already held by the spawning parent.

## Current behavior

- entrypoint: `packages/playwright-core/src/entry/mcp.ts`
- HTTP transport: `packages/playwright-core/src/tools/utils/mcp/http.ts`
- state owner: the MCP child process and its HTTP server
- caller-visible result: baseline exact POST/header to `/killkillkill` returns 200 `Killing process`
- side effects: emits process `SIGINT`, invokes the existing graceful browser cleanup path, and exits
- cleanup owner: Playwright's existing graceful process-exit machinery
- persistence or publication boundary: none; process-local lifecycle
- relevant ordering: HTTP response is ended before `SIGINT`; selected IPC listener is removed before `SIGINT`

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| MCP CLI entry | [`mcp.ts@c4c5e2d`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/packages/playwright-core/src/entry/mcp.ts) | parse CLI and install private test-parent message listener | `http transport browser sigint` |
| HTTP dispatch | [`http.ts@c4c5e2d`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/packages/playwright-core/src/tools/utils/mcp/http.ts) | Host checks and MCP HTTP/SSE request handling | complete `tests/mcp/http.spec.ts` |
| test child fixture | [`http.spec.ts@c4c5e2d`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/tests/mcp/http.spec.ts) | spawn MCP with an IPC fd and expose send/disconnect controls | lifecycle, malformed-message, duplicate, disconnect controls |
| historical route hardening | [`4a80eed`](https://github.com/microsoft/playwright/commit/4a80eed396071d6ed15a74c32723f2bc66849988) | changed GET shutdown to POST plus custom header | historical `http transport browser sigint` |

## Reproduction or characterization

### Setup

- exact executed upstream revision: `368941457a82da112aa8610107e25f4bde94339a`
- environment: Ubuntu 24.04, Node 22.23.1, Chromium
- listener: `--host=0.0.0.0 --allowed-hosts=* --isolated`
- request: `POST /killkillkill` with `x-pw-mcp-kill: 1`
- retained execution: Fieldwork PR #405, run `30649849111`, job `91220131763`

### Baseline result

- exact accepted non-loopback request returned HTTP 200 `Killing process`
- MCP exited code 0 after graceful cleanup
- wrong method, missing header, and wrong header returned 405 and left MCP responsive
- default Host policy rejected the non-loopback request before route handling
- loopback used the same route

### Candidate result

The hardened parent-IPC predecessor at Fieldwork PR #430 passed 18/18 native tests on Linux and the unchanged patch passed 18/18 on Ubuntu, macOS, and Windows through PR #432. It removed the HTTP route, preserved graceful real-browser SIGINT cleanup, ignored wrong string/wrong version, handled duplicate valid delivery once, and kept serving after IPC disconnect.

The current candidate adds the missing exact-message controls: an extra-field object and an object inheriting matching properties are sent before the valid message and must leave MCP responsive. Exact current-head execution remains pending.

## Failure model

1. The MCP process starts an HTTP listener and installs ordinary Host validation.
2. The test-only `/killkillkill` route lives inside the same request dispatcher.
3. Operator configuration may deliberately expose the listener and accept a remote Host.
4. A non-browser caller can send the fixed POST/header and reach the route.
5. The route emits `SIGINT`, transferring process-lifecycle authority from listener reachability to any accepted caller.
6. A loopback-only peer test fails to identify the original client after a local proxy creates a new loopback connection.

Steps 1–5 were target-executed. Step 6 was integration-executed through the local proxy discriminator.

## Consequence and claim boundary

### Established

- The route terminates MCP wherever listener and Host policy accept the caller under the executed configuration.
- Method plus custom header prevents simple browser-coerced requests but does not authenticate a caller.
- Direct socket-peer locality blocks direct remote peers yet permits a relayed remote-originated request through a local proxy.
- Parent-owned IPC preserves the tested cross-platform graceful lifecycle without an HTTP shutdown route.

### Inferred

- Removing the route is a narrower authority model than an environment capability because no network caller can present or inherit a route-enabling value.
- The current two-key exact-message validation is suitable for an internal test-only protocol with no extension compatibility burden.

### Unknown or unmeasured

- prevalence of deployments exposing MCP HTTP beyond loopback
- production impact or exploit frequency
- behavior behind authenticated or policy-enforcing proxies
- full Playwright repository gate at the current source head
- upstream maintainer preference

## Selected implementation

The spawning parent owns the test action:

- `mcp.ts` installs a message listener only when `process.send` exists.
- The accepted message is a plain object with prototype `Object.prototype`, exactly two own keys, exact type, and exact version.
- The listener is removed before `process.emit('SIGINT')`.
- `http.ts` contains no shutdown route.
- The native test fixture allocates the IPC fd and exposes `send` and `disconnect` only to the test process.
- The lifecycle test proves the former network request cannot shut down the process, malformed messages are inert, duplicate valid messages produce one graceful close, and the valid parent message retains the real-browser assertion.

## Compatibility analysis

- public API: unchanged
- source compatibility: internal test and MCP entrypoint changes only
- binary or wire compatibility: MCP protocol unchanged; one private parent-child test message added
- persistence or format compatibility: not applicable
- platform behavior: hardened predecessor passed Ubuntu 24.04, macOS 15, and Windows 2025 under Node 22/Chromium
- performance and allocation: one listener only when an IPC channel exists; negligible
- cancellation, retry, and recovery: duplicate message ignored after listener removal; IPC disconnect leaves HTTP live
- generated output: not applicable
- migration or rollback: revert the three-file change; no stored state

## Adversarial and edge controls

- re-entry: valid message sent twice; one graceful-close receipt
- malformed value: wrong string inert
- version mismatch: wrong-version object inert
- extension field: exact type/version plus extra field inert on current candidate
- prototype inheritance: inherited type/version inert on current candidate
- interruption: parent IPC disconnect leaves MCP responsive
- network relay: old HTTP route absent, avoiding proxy identity ambiguity
- platform boundary: prior hardened generation passed Linux, macOS, and Windows

## Review risks

- **Test-only production listener in CLI entrypoint:** reviewer should confirm `process.send` can exist in non-test embeddings and that accepting the exact internal message is acceptable when the embedding parent already owns the process.
- **Message validation complexity:** current implementation uses a strict plain-object/two-own-key rule; reviewer should confirm this is clearer than a shared test helper or constant.
- **Fixture-wide IPC fd:** every server spawned by this test fixture gains an IPC channel; disconnect and ordinary-suite controls show no observed behavior change, but current-head execution must repeat them.
- **Issue-first policy:** Playwright's contribution rules require an approved/assigned issue before a substantive PR.

## Reversing evidence

Reopen the conclusion if:

- current Playwright test machinery offers a simpler existing cross-platform parent-owned signal primitive
- an exact current-head run shows Node IPC or graceful SIGINT behavior differs on a supported platform
- maintainers state the HTTP route serves a supported external lifecycle contract beyond tests
- current main removes or replaces the route independently

## Adjacent work excluded

- built-in client authentication for MCP HTTP
- reverse-proxy authentication or forwarded-client identity
- shared-browser-context authorization
- process supervision outside the Playwright test harness
- public vulnerability classification or severity scoring
