# F371-playwright-mcp-remote-shared-context: remote reachability and shared browser authority are separate controls

Finding state: `delivery-gate-ready`

Canonical issue: `#371`  
Initiative: `#254`  
Workstream: `B/C — browser runtime and MCP authority boundaries`  
Exact package source: `microsoft/playwright-mcp@55679f5f3d4b4f3e2534ec0ce2fc5683ba2eaf3f`  
Exact shared core source: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
Behavior carrier: closed Fieldwork PR `#375` at `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`  
Behavior run: `30633739476`, job `91166043729`, success  
Behavior artifact: `8794430468`, digest `sha256:e53fc07dbfb1dfecd98e5e4a4227c50e8774fe5fb4bc05f880f3f56c73403235`  
Help carrier: closed Fieldwork PR `#377` at `204b96c94dfd2fef3ea4981796b2cb98ceae09a9`  
Help run: `30634831167`, job `91169666445`, success  
Help artifact: `8794842941`, digest `sha256:d0347ff4a0ed8408f9c5d01b36b703d931bc5bab8e6ac79da373a6bfcb2d0683`  
Canonical implementation: `evidence/0001-document-http-client-authority.patch`  
Strongest evidence class: `target-executed`  
Current disposition: `REVIEW READY — documentation/runtime-help candidate`  
Upstream contact authorized: `no`

## In simple words

Playwright MCP already has strong network defaults:

- standard input/output is the default transport;
- HTTP is optional;
- HTTP binds to localhost by default;
- all-interface binding requires an explicit host option;
- accepted requests must pass a Host-header check.

When an operator deliberately enables non-loopback HTTP and `--shared-browser-context`, another authority boundary appears. Host validation prevents DNS rebinding; it does not authenticate a client. Every accepted HTTP session shares one browser context and can observe and control the same tabs, cookies, storage, and page state.

Exact target execution confirms that composition and confirms bounded final cleanup. The selected repair changes help text only.

## Five separate controls

1. **Bind authority** — which interfaces accept connections.
2. **Host validation** — which Host values pass DNS-rebinding defense.
3. **Client authentication** — which principal may create a session.
4. **Session identity** — which actions and resources belong to one client.
5. **Browser-context sharing** — whether separate sessions intentionally share browser state.

One passing control does not establish the others.

## Exact source result

At shared core head `3689414...`:

- `--port` enables HTTP/SSE transport;
- `--host` defaults to localhost;
- `--host=0.0.0.0` explicitly requests all-interface binding;
- `--allowed-hosts` defaults to the normalized listener Host;
- `--allowed-hosts=*` disables the Host check;
- accepted requests can create streamable HTTP or legacy SSE sessions;
- no bearer token, client certificate, user identity, or equivalent authentication decision is visible in the inspected HTTP handler;
- `--shared-browser-context` reuses one browser context across clients.

The complete source map and target paths are retained in `evidence/20260731-source-map.md`.

## Exact behavior matrix

Fieldwork PR #375 ran exact Playwright source on Ubuntu 24.04, Node 22, and Chromium.

The successful job:

- verified exact Fieldwork and target heads;
- installed 638 target dependencies;
- built exact source;
- installed Chromium and runner dependencies;
- ran the complete target `tests/mcp/http.spec.ts` file;
- ran two target-native Fieldwork controls through the same fixtures;
- uploaded logs, target report, and exact-head receipt.

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

With the same transport plus `--shared-browser-context`:

- client 1 opened the disposable page;
- client 2 saw that page in its own tab list;
- client 1 disconnected;
- client 2 continued using the shared browser successfully;
- both HTTP sessions were deleted;
- the shared browser closed after the final client.

No credential, account, private page, or external website was used. The complete receipt is retained in `evidence/20260731-target-matrix.md`.

## Current conclusion

The behavior is intentional and internally coherent:

- safe local defaults remain intact;
- explicit remote and wildcard-Host choices are required;
- isolated mode preserves per-client browser state;
- shared mode intentionally creates one browser authority domain;
- first-client disconnect does not revoke the remaining client's shared authority;
- final-client disconnect closes the shared browser.

The actionable gap is guidance. Current help describes Host validation as DNS-rebinding defense and says the browser context is reused across clients. It does not state plainly that Host validation is not authentication or name the browser authority shared by every accepted client.

## Selected repair

Retained patch:

`evidence/0001-document-http-client-authority.patch`

It changes three CLI descriptions only:

- `--allowed-hosts`: states that the check does not authenticate clients;
- `--host`: recommends a trusted authenticated network boundary or reverse proxy for non-loopback HTTP;
- `--shared-browser-context`: names shared tabs, cookies, storage, and page control.

No transport, session, authentication, browser, or default behavior changes.

## Exact help-candidate receipt

Fieldwork PR #377 applied the retained patch to exact shared-core source.

Final run `30634831167`, job `91169666445`, passed:

- exact Fieldwork and target-head verification;
- ordinary zero-fuzz, whitespace-clean patch application;
- one-file target diff enforcement;
- exact dependency installation;
- complete target build;
- generated `Playwright MCP --help` execution;
- semantic assertions for all three authority statements after whitespace normalization;
- `git diff --check`;
- JSON receipt and raw-help artifact upload;
- Fieldwork integrity `30634831152`, job `91169666324`.

Generated help contains:

```text
This is DNS-rebinding protection and does not authenticate clients.
```

```text
Non-loopback HTTP should be protected by a trusted authenticated network boundary or reverse proxy.
```

```text
Every accepted client can observe and control the shared tabs, cookies, storage, and page state.
```

The complete carrier history and claim boundary are retained in `evidence/20260731-help-candidate-receipt.md`.

## Alternatives

### Built-in token gate — deferred

The target matrix does not establish that Playwright MCP should own a credential protocol rather than rely on deployment infrastructure.

### Fail closed for remote shared mode — rejected for now

Remote binding and shared context are explicit operator choices. The executed behavior matches those choices and cleans up correctly.

### External authenticated proxy contract — compatible

The selected wording recommends this boundary without hard-coding one authentication mechanism.

## Evidence table

| Claim | Evidence class | Limit |
| --- | --- | --- |
| Stdio and loopback HTTP are the defaults. | `source-read / upstream-test-executed` | exact pinned source and suite |
| Default Host validation rejects unlisted address forms. | `target-executed` | upstream HTTP suite on one Linux/Chromium runner |
| Explicit remote-equivalent isolated clients keep browser state separate. | `target-executed` | runner non-loopback IPv4, wildcard Host opt-in |
| Explicit remote-equivalent shared clients use one browser authority domain. | `target-executed` | same runner and disposable local page |
| Remaining client keeps shared authority after first-client disconnect. | `target-executed` | streamable HTTP sessions |
| Final-client disconnect closes the shared browser. | `target-executed` | target debug lifecycle counters |
| Three-string help patch applies, builds, and appears in runtime help. | `target-executed` | exact pinned target and generated-help surface |
| Public exploitability or deployment prevalence. | `not established` | no production deployment or external target |
| Built-in authentication is the correct repair. | `not established` | deployment architecture comparison pending |
| Public upstream acceptance. | `not established` | no upstream contact authorized |

## Exact next transition

1. let Fieldwork integrity settle on this workflow-free exact head;
2. obtain one eligible complete-diff review of the five-file finding package;
3. only separate public-upstream authority may permit submission.

No merge, release, deployment, real credential, private browser data, spending, or public upstream interaction is authorized.
