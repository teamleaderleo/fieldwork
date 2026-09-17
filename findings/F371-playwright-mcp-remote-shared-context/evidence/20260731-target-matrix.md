# Playwright MCP remote/shared-context target matrix

Date: 2026-07-31  
Parent finding: `F371-playwright-mcp-remote-shared-context`  
Evidence class: `target-executed`

## Exact identities

- Fieldwork carrier PR: `#375`;
- exact carrier head: `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`;
- exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`;
- target project: Chromium on Ubuntu 24.04, Node 22;
- target run: `30633739476`;
- target job: `91166043729`;
- Fieldwork integrity: `30633739423`;
- artifact: `8794430468`;
- artifact digest: `sha256:e53fc07dbfb1dfecd98e5e4a4227c50e8774fe5fb4bc05f880f3f56c73403235`.

The first carrier run `30633035608` stopped before target installation because GitHub checked out the synthetic PR merge commit while the carrier verified the branch head. Head `2a7b6c4...` pins the Fieldwork checkout to the exact PR head. That first run is carrier-failure evidence only.

## Executed gate

The successful run:

- verified exact Fieldwork and Playwright heads;
- installed 638 exact target dependencies;
- built exact Playwright source;
- installed Chromium plus runner dependencies;
- ran the complete target `tests/mcp/http.spec.ts` suite;
- ran two Fieldwork controls through the same MCP fixtures;
- assembled and uploaded the exact-head receipt.

Result:

```text
Running 19 tests using 1 worker
19 passed (30.4s)
```

The 19 tests are the 17 target HTTP controls plus two Fieldwork composition controls.

## Fieldwork control: isolated mode

Configuration:

- `--port=0`;
- `--host=0.0.0.0`;
- `--allowed-hosts=*`;
- `--isolated`;
- headless Chromium;
- two independent streamable-HTTP MCP clients;
- connection through the runner's non-loopback IPv4 address;
- disposable local test page only.

Result:

- client 1 navigated to the disposable local page;
- client 2's tab list did not contain client 1's page;
- two HTTP sessions were deleted;
- the browser closed after the final client.

Evidence class: `target-executed / isolated client state`.

## Fieldwork control: shared browser context

Configuration matched the isolated control except it used `--shared-browser-context` rather than `--isolated`.

Result:

- client 1 navigated to the disposable local page;
- client 2's tab list contained client 1's page;
- client 1 disconnected;
- client 2 continued to take a browser snapshot successfully;
- two HTTP sessions were deleted;
- the shared browser closed after the final client.

Evidence class: `target-executed / shared browser authority and bounded final cleanup`.

## Interpretation

The composition is intentional and internally consistent:

- loopback remains the default;
- all-interface access and wildcard Host acceptance require explicit operator choices;
- isolated mode keeps browser state separate;
- shared mode creates one browser authority domain across accepted HTTP sessions;
- first-client disconnect does not revoke the remaining client's shared browser authority;
- final-client disconnect closes the shared browser.

Host validation and client authentication remain separate. No bearer token, client certificate, user identity, or equivalent authentication decision was used by the executed HTTP sessions.

The result supports a documentation/help repair rather than an automatic transport or behavior change. Current option text describes Host validation as DNS-rebinding protection and describes shared context across clients, but it does not state plainly that Host validation does not authenticate clients or that every accepted client shares tabs, cookies, storage, and page authority.

## Boundaries

Not established:

- public exploitability;
- production deployment prevalence;
- behavior behind an authenticated reverse proxy;
- real logged-in browser risk;
- behavior on other operating systems or browsers;
- correct credential protocol;
- need for a built-in authentication feature.

No external site, account, credential, private page, merge, deployment, spending, or public upstream interaction was used.
