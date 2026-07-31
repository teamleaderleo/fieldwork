# Playwright MCP remote shutdown authority execution receipt

Owning issue: #404  
Carrier PR: #405  
Evidence class: `target-executed` for the named controls  
Upstream contact authorized: `no`

## Exact identities

- Fieldwork target-executed head: `69b8390fe4db742043de2615e4a06c0760415963`;
- exact public target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`;
- runner: Ubuntu 24.04;
- Node: 22.23.1;
- browser project: Chromium;
- focused workflow: `30649849111`;
- exact job: `91220131763`;
- Fieldwork integrity: `30649849265`, success;
- artifact: `8800945684`;
- artifact digest: `sha256:ce7c9a2d02affa71367c2f1fdc56a0a338b2afcb5d50d72d72a0f6a50310cf8b`;
- receipt generated: `2026-07-31T17:07:31.425Z`.

## Exact gate

Every recorded workflow step succeeded:

- exact Fieldwork and target verification;
- `npm ci` with 638 target packages;
- complete Playwright source build;
- Chromium and runner dependency installation;
- focused target-native shutdown test;
- receipt assembly;
- artifact upload.

The receipt records `reusableTargetEvidence: true`.

Focused result:

```text
Running 3 tests using 1 worker
3 passed (8.9s)
```

The executed tests were:

1. `non-loopback accepted shutdown header owns process termination`;
2. `Host rejection happens before shutdown handling`;
3. `loopback accepted shutdown uses the same ordinary route`.

## Target-executed result

### Non-loopback accepted path

With `--port=0`, `--host=0.0.0.0`, `--allowed-hosts=*`, `--isolated`, and connection through the runner's non-loopback IPv4:

- one MCP session connected and created one isolated browser;
- GET with the exact header returned 405 and the MCP client still answered ping;
- POST without the header returned 405 and the MCP client still answered ping;
- POST with the wrong header returned 405 and the MCP client still answered ping;
- POST with `x-pw-mcp-kill: 1` returned HTTP 200 with body `Killing process`;
- the MCP process exited with code 0 and no terminating signal;
- debug receipts contained one HTTP session, one isolated browser, and `gracefully closing 1`.

### Host reversing control

With all-interface binding and the default Host policy:

- the same non-loopback POST/header request returned HTTP 403;
- the response named the allowed Host boundary;
- an accepted loopback request with the wrong header still returned 405;
- the process remained live until fixture teardown.

Host validation therefore runs before shutdown handling, while wildcard or otherwise accepted Host policy does not authenticate the shutdown caller.

### Loopback comparison

Through the presented loopback URL:

- the same POST/header returned HTTP 200 `Killing process`;
- the process exited with code 0;
- the no-browser case logged `gracefully closing 0`.

The shutdown route is one ordinary HTTP route whose reachability follows the configured listener and Host policy.

## Interpretation

The source-read prediction survived exact target execution. After explicit non-loopback exposure and accepted Host policy, a non-browser client that knows the fixed method, path, and header can request graceful process termination. The method/header controls provide browser-CSRF resistance; they do not identify or authorize a remote principal.

This does not establish public exploitability, production deployment prevalence, harmful frequency, reverse-proxy behavior, or the correct product repair.

## Repair comparison entry

Leading first candidate: **loopback-only shutdown route**.

Why it leads initially:

- preserves the existing ordinary cross-platform SIGINT test path;
- preserves local shutdown behavior;
- prevents remote reachability from inheriting shutdown authority merely through Host acceptance;
- requires no credential protocol or new externally managed secret;
- is small and directly reversible.

Required negative comparisons:

1. test-only route enabled by an explicit target test capability;
2. remove the route and signal the child process through another cross-platform fixture mechanism;
3. explicit authenticated/secret shutdown capability for remote operation;
4. documentation-only retention of current behavior.

No repair is accepted until at least the loopback-only and test-only alternatives are source-shaped and run against the exact upstream SIGINT/lifecycle tests plus the Fieldwork reversing matrix.

## Evidence boundary

Established only on the exact target, Ubuntu 24.04, Node 22, Chromium, and runner-local IPv4. The test used one disposable local page and no external website, account, usable credential, private browser state, production deployment, or public upstream interaction.

The later workflow-free Fieldwork head transfers this receipt and does not claim another target run.