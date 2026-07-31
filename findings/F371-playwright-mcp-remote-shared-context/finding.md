# F371-playwright-mcp-remote-shared-context: remote reachability and shared browser authority are separate controls

Finding state: `research-active`

Canonical issue: `#371`  
Initiative: `#254`  
Workstream: `B/C — browser runtime and MCP authority boundaries`  
Exact package source: `microsoft/playwright-mcp@55679f5f3d4b4f3e2534ec0ce2fc5683ba2eaf3f`  
Exact shared core source: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
Canonical implementation: `none`  
Strongest evidence class: `source-read / upstream-test-read`  
Current disposition: `EXECUTE bounded local matrix`  
Upstream contact authorized: `no`

## In simple words

Playwright MCP is careful about accidental HTTP exposure. It uses standard input/output by default. HTTP requires a port. The default HTTP host is localhost. All-interface binding requires an explicit host option, and requests must pass a Host-header check.

That is stronger than a server that silently listens on every interface.

A different question appears when an operator deliberately enables remote HTTP and shared browser state. The Host check prevents DNS rebinding; it does not authenticate the client. `--shared-browser-context` intentionally lets several HTTP clients use one browser context.

The investigation asks whether that authority boundary is sufficiently explicit and whether disconnect/cleanup behavior can accidentally transfer control of sensitive shared state between unrelated clients.

## Current source map

### Package wrapper

`microsoft/playwright-mcp` delegates CLI and transport behavior to `playwright-core`:

- `cli.js` calls `tools.decorateMCPCommand()`;
- `index.js` exports the shared-core connection factory;
- the package adds no separate HTTP authorization layer.

### Listener policy

At shared core head `3689414...`:

- `--port` enables HTTP/SSE transport;
- `--host` defaults to localhost;
- `--host=0.0.0.0` explicitly requests all-interface binding;
- `--allowed-hosts` defaults to the normalized listener Host;
- `--allowed-hosts=*` disables the Host check;
- the HTTP request handler rejects missing or unlisted Host values before routing.

Current target tests retain a negative control in which a request addressed through localhost's resolved IP returns 403 under default allowed Hosts.

### Session policy

Requests that pass the Host check can create streamable HTTP or legacy SSE sessions. No bearer token, client certificate, user identity, or other client-authentication decision is visible in the inspected HTTP handler.

This is a source observation, not a claim that remote deployment is unsafe by default. Loopback remains the default.

### Shared browser state

`--shared-browser-context` makes the browser factory reuse one browser context across connected HTTP clients.

The target test suite demonstrates this intended composition:

1. client 1 connects and opens a page;
2. client 2 connects separately;
3. client 2 lists tabs and sees the page created by client 1;
4. client 1 disconnects;
5. client 2 continues using the shared context.

That test runs on loopback. It does not establish the remote-network or authentication boundary.

## Invariant

Five controls must remain distinct:

1. **Bind authority** — which interfaces accept connections.
2. **Host validation** — which HTTP Host values pass DNS-rebinding defense.
3. **Client authentication** — which remote principal may create a session.
4. **Session identity** — which actions and resources belong to one client.
5. **Browser-context sharing** — whether separate sessions intentionally share cookies, tabs, storage, and page authority.

Passing one control must not be described as passing the others.

## Current evidence table

| Claim | Evidence class | Limit |
| --- | --- | --- |
| Standard I/O is the default transport. | `source-read` | exact pinned package/core heads |
| HTTP bind defaults to localhost. | `source-read` | executable confirmation pending |
| All-interface bind requires explicit `--host=0.0.0.0`. | `source-read` | executable confirmation pending |
| Default Host validation rejects an IP-address request. | `upstream-test-read` | target test not rerun by Fieldwork |
| Allowed Hosts are checked before MCP/SSE routing. | `source-read` | no reverse-proxy execution |
| No client authentication check is visible in the inspected handler. | `source-read` | external auth layers remain possible |
| Shared mode lets client 2 observe/use client 1's tab. | `upstream-test-read` | loopback target test, not Fieldwork-executed |
| Remote unauthenticated clients can share real browser state. | `unproven` | requires bounded target-native matrix |

## Alternatives

### A — documentation-only boundary

Keep current behavior and state plainly that Host validation is not authentication. Warn that every reachable accepted client shares common browser authority in shared-context mode.

**Wins when:** executable behavior is intentional and the only defect is ambiguous operator guidance.

### B — optional built-in token gate

Allow a configured bearer or equivalent token before HTTP/SSE session creation.

**Wins when:** remote HTTP is a supported direct deployment and a small built-in gate composes cleanly with clients.

### C — fail closed for remote shared mode without authentication

Require an authentication option or explicit dangerous acknowledgement when non-loopback HTTP and shared context are combined.

**Wins when:** the composition is unusually easy to enable accidentally and shared state carries materially broader authority than ordinary isolated sessions.

### D — external authenticated proxy contract

Keep the server authentication-free and document an authenticated reverse proxy as the required remote deployment boundary.

**Wins when:** maintaining credential protocols in the MCP server would duplicate established infrastructure.

No alternative is selected yet.

## First executable matrix

Use exact current package/core source and disposable local pages only.

1. Start default HTTP mode and record the actual listener/startup URL.
2. Address the listener through the resolved non-loopback or alternate Host value; require default rejection.
3. Explicitly enable all-interface/accepted-Host access.
4. Create two independent MCP sessions without credentials.
5. Run isolated mode; require client 2 to lack client 1's browser state.
6. Run shared-context mode; determine whether client 2 sees and controls client 1's page.
7. Disconnect client 1; verify client 2 continuity and browser/context cleanup ownership.
8. Terminate the final client; require bounded browser and context cleanup.
9. Inspect emitted help/startup text for a clear statement that Host checks do not authenticate clients.

No external website, account, secret, private page, or usable credential is needed.

## Promotion and stop conditions

### Continue to comparison

Continue when the matrix proves that separately reachable clients share browser authority and current help/docs do not make that consequence explicit enough for a reasonable operator.

### Stop as no-action

Stop when current documentation already states the authentication boundary clearly and the executable matrix reveals no surprising cross-client authority or cleanup behavior beyond the explicitly selected shared mode.

### Reopen trigger

Reopen after any change to HTTP authentication, allowed-host semantics, shared-context defaults, session cleanup, or remote deployment guidance.

## Boundaries

This investigation does not claim:

- public exploitability;
- production deployment prevalence;
- behavior behind an authenticated reverse proxy;
- vulnerability of the default loopback configuration;
- isolation across operating-system users or containers;
- safety of real logged-in browser data;
- any right to contact Microsoft or publish upstream.

No merge, release, deployment, real credential, private browsing data, spending, or public upstream interaction is authorized.
