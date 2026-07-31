# Playwright MCP remote shutdown authority probe

Owning issue: #404  
Parent finding: `F371-playwright-mcp-remote-shared-context`  
Exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
Evidence state: `target-test-prepared`  
Upstream contact authorized: `no`

## Question

When an operator explicitly enables Playwright MCP HTTP on a non-loopback interface, which client owns process-shutdown authority?

The exact ordinary HTTP handler accepts:

```text
POST /killkillkill
x-pw-mcp-kill: 1
```

and emits `SIGINT`. The normal MCP watchdog then gracefully closes tracked browser work and exits. Source describes the custom header as browser-CSRF protection and Host validation as DNS-rebinding protection. The prepared probe asks whether a remote non-browser client that passes Host validation can exercise that shutdown path.

This is not a vulnerability claim and does not infer deployment prevalence or public exploitability.

## Exact controls

The target-native spec uses only one disposable GitHub runner, exact public source, one local test page, and runner-local IPv4.

1. Start HTTP with `--host=0.0.0.0`, `--allowed-hosts=*`, and `--isolated`.
2. Connect through the runner's non-loopback IPv4 and create one live disposable browser session.
3. Prove these requests do not terminate the process and the MCP client still answers `ping`:
   - GET with the exact shutdown header;
   - POST without the header;
   - POST with the wrong header.
4. Send the exact POST/header through the non-loopback address and record:
   - HTTP status/body;
   - process exit code/signal;
   - `create http session` and `gracefully closing` debug receipts.
5. Start a second all-interface server without wildcard Host permission and prove a non-loopback request is rejected before shutdown handling.
6. Repeat the accepted shutdown through loopback to distinguish route behavior from network reachability.

## Reversing outcomes

The source-read lead is reversed or narrowed if:

- the non-loopback exact request is rejected by another target-owned admission layer;
- the process remains live after the accepted response;
- cleanup receipt differs from the existing upstream SIGINT contract;
- only loopback can exercise the route despite all-interface binding;
- target source or tests identify a separate authenticated shutdown capability.

## Evidence boundary

A green run would establish only exact target behavior on Ubuntu 24.04, Node 22, Chromium, and runner-local networking. It would not establish real deployment prevalence, external reachability, malicious exploitation, other operating systems, reverse-proxy behavior, the correct repair family, or public upstream acceptance.

No external website, account, usable credential, private browser state, source repair, merge, deployment, spending, or public-upstream interaction is included.