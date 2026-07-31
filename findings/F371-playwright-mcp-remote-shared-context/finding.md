# F371-playwright-mcp-remote-shared-context: remote reachability and shared browser authority are separate controls

Finding state: `research-active`

Canonical issue: `#371`  
Initiative: `#254`  
Workstream: `B/C — browser runtime and MCP authority boundaries`  
Exact package source: `microsoft/playwright-mcp@55679f5f3d4b4f3e2534ec0ce2fc5683ba2eaf3f`  
Exact shared core source: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
Exact executed carrier: Fieldwork PR `#375` at `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`  
Exact target run: `30633739476`, job `91166043729`, success  
Artifact: `8794430468`, digest `sha256:e53fc07dbfb1dfecd98e5e4a4227c50e8774fe5fb4bc05f880f3f56c73403235`  
Canonical implementation: documentation patch `evidence/0001-document-http-client-authority.patch`  
Strongest evidence class: `target-executed`  
Current disposition: `EXECUTE documentation candidate`  
Upstream contact authorized: `no`

## In simple words

Playwright MCP is careful about accidental HTTP exposure:

- standard input/output is the default;
- HTTP is optional;
- HTTP binds to localhost by default;
- all-interface binding requires an explicit host option;
- requests must pass a Host-header check.

Those are strong defaults.

When an operator deliberately enables remote-equivalent HTTP and `--shared-browser-context`, a separate authority boundary appears. Host validation prevents DNS rebinding; it does not authenticate a client. Every accepted HTTP session shares one browser context and can observe and control the same tabs, cookies, storage, and page state.

Exact target execution confirms that composition and also confirms bounded final cleanup.

## Five separate controls

1. **Bind authority** — which interfaces accept connections.
2. **Host validation** — which HTTP Host values pass DNS-rebinding defense.
3. **Client authentication** — which principal may create a session.
4. **Session identity** — which actions and resources belong to one client.
5. **Browser-context sharing** — whether separate sessions intentionally share browser state.

Passing one control does not establish the others.

## Source map

At shared core head `3689414...`:

- `--port` enables HTTP/SSE transport;
- `--host` defaults to localhost;
- `--host=0.0.0.0` explicitly requests all-interface binding;
- `--allowed-hosts` defaults to the normalized listener Host;
- `--allowed-hosts=*` disables the Host check;
- accepted requests can create streamable HTTP or legacy SSE sessions;
- no bearer token, client certificate, user identity, or equivalent client-authentication decision is visible in the inspected handler;
- `--shared-browser-context` reuses one browser context across clients.

The upstream suite already tests default Host rejection and loopback shared-context behavior. Fieldwork added the missing explicit remote-equivalent composition.

## Exact target matrix

Fieldwork PR #375 executed exact Playwright source on Ubuntu 24.04, Node 22, and Chromium.

The workflow:

- verified exact Fieldwork and target heads;
- installed 638 target dependencies;
- built exact Playwright source;
- installed Chromium and runner dependencies;
- ran the complete upstream `tests/mcp/http.spec.ts` file;
- ran two target-native Fieldwork controls through the same fixtures;
- uploaded logs, a target report, and an exact-head receipt.

Result:

```text
Running 19 tests using 1 worker
19 passed (30.4s)
```

### Isolated negative control

With explicit `--host=0.0.0.0`, `--allowed-hosts=*`, and connection through the runner's non-loopback IPv4:

- client 1 opened a disposable local page;
- client 2 did not see client 1's page;
- both HTTP sessions were deleted;
- the browser closed after the final client.

### Shared-context positive control

With the same remote-equivalent transport plus `--shared-browser-context`:

- client 1 opened a disposable local page;
- client 2 saw that page in its own tab list;
- client 1 disconnected;
- client 2 continued using the shared browser successfully;
- both HTTP sessions were deleted;
- the shared browser closed after the final client.

No credential, account, private page, or external website was used.

## Current conclusion

The behavior is intentional and internally coherent:

- safe local defaults remain intact;
- explicit remote and wildcard-Host choices are required;
- isolated mode preserves per-client browser state;
- shared mode intentionally creates one browser authority domain;
- first-client disconnect does not revoke the remaining client's shared authority;
- final-client disconnect closes the shared browser.

The actionable gap is guidance rather than transport behavior. Current help describes Host validation as DNS-rebinding defense and says shared context is reused across clients. It does not state plainly that Host validation is not authentication or that every accepted client shares browser authority.

## Selected repair

### Documentation/runtime-help boundary — selected

Retained patch:

`evidence/0001-document-http-client-authority.patch`

It changes only three CLI help strings:

- `--allowed-hosts`: explicitly says the check does not authenticate clients;
- `--host`: recommends a trusted authenticated network boundary or reverse proxy for non-loopback HTTP;
- `--shared-browser-context`: explicitly names shared tabs, cookies, storage, and page control.

This preserves current behavior and safe defaults while making the composed authority model difficult to mistake.

## Alternatives

### Built-in token gate — deferred

The target matrix does not establish that Playwright MCP should own a credential protocol rather than rely on deployment infrastructure.

### Fail closed for remote shared mode — rejected for now

Remote binding and shared context are both explicit operator choices. The executed behavior matches those choices and cleans up correctly.

### External authenticated proxy contract — compatible

The selected help wording can recommend this boundary without hard-coding a particular authentication mechanism.

## Evidence table

| Claim | Evidence class | Limit |
| --- | --- | --- |
| Stdio and loopback HTTP are the defaults. | `source-read / upstream-test-executed` | exact pinned source and suite |
| Default Host validation rejects unlisted address forms. | `target-executed` | upstream HTTP suite on one Linux/Chromium runner |
| Explicit remote-equivalent isolated clients keep browser state separate. | `target-executed` | runner non-loopback IPv4, wildcard Host opt-in |
| Explicit remote-equivalent shared clients use one browser authority domain. | `target-executed` | same runner and disposable local page |
| Remaining client keeps shared authority after first-client disconnect. | `target-executed` | streamable HTTP sessions |
| Final-client disconnect closes the shared browser. | `target-executed` | target debug lifecycle counters |
| Public exploitability or deployment prevalence. | `not established` | no production deployment or external target |
| Built-in authentication is the correct repair. | `not established` | deployment architecture comparison pending |

## Carrier history

The first execution run `30633035608` failed before target installation because the carrier checked the synthetic PR merge ref while expecting the branch head. Head `2a7b6c4...` pinned the checkout to the exact PR head. That first run is carrier-failure evidence only.

## Exact next transition

1. apply the retained documentation patch to exact shared core source;
2. require zero-fuzz application, build, generated CLI help, and focused help-text assertions;
3. transfer the receipt into this finding;
4. retire the temporary workflow carrier;
5. obtain one eligible review before any delivery or upstream-submission claim.

No merge, release, deployment, real credential, private browsing data, spending, or public upstream interaction is authorized.
