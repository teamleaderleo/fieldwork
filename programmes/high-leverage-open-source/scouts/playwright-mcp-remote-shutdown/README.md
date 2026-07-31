# Playwright MCP remote shutdown authority probe

Owning issue: #404  
Parent finding: `F371-playwright-mcp-remote-shared-context`  
Exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
Evidence state: `target-executed / comparative-evaluation-active`  
Target-executed Fieldwork head: `69b8390fe4db742043de2615e4a06c0760415963`  
Exact workflow/job: `30649849111` / `91220131763`  
Artifact: `8800945684`, digest `sha256:ce7c9a2d02affa71367c2f1fdc56a0a338b2afcb5d50d72d72a0f6a50310cf8b`  
Upstream contact authorized: `no`

## Question

When an operator explicitly enables Playwright MCP HTTP on a non-loopback interface, which client owns process-shutdown authority?

The exact ordinary HTTP handler accepts:

```text
POST /killkillkill
x-pw-mcp-kill: 1
```

and emits `SIGINT`. The normal MCP watchdog then gracefully closes tracked browser work and exits. Source describes the custom header as browser-CSRF protection and Host validation as DNS-rebinding protection.

This is not a vulnerability claim and does not infer deployment prevalence or public exploitability.

## Exact executed result

The target-native matrix ran on Ubuntu 24.04, Node 22, Chromium, exact Playwright source, one disposable local page, and runner-local IPv4.

```text
Running 3 tests using 1 worker
3 passed (8.9s)
```

### Non-loopback accepted path

With `--host=0.0.0.0`, `--allowed-hosts=*`, and one live isolated browser session:

- GET with the exact header returned 405 and the MCP client remained responsive;
- POST without the header returned 405 and the MCP client remained responsive;
- POST with the wrong header returned 405 and the MCP client remained responsive;
- the exact POST/header returned HTTP 200 `Killing process`;
- the process exited with code 0;
- debug receipts contained one HTTP session, one isolated browser, and `gracefully closing 1`.

### Host reversing control

Without wildcard Host permission, the non-loopback exact shutdown request returned 403 before route handling. An accepted loopback wrong-header request still returned 405 and the process remained live.

### Loopback comparison

The same exact route through loopback returned HTTP 200 and exited cleanly with `gracefully closing 0` when no browser was open.

The complete receipt is retained in `execution-receipt.md`.

## Current conclusion

The shutdown route follows ordinary HTTP reachability. After explicit non-loopback exposure and accepted Host policy, a non-browser client that knows the fixed path and header can request graceful process termination. Method/header validation prevents simple browser-coerced requests; it does not authenticate or authorize a remote principal.

Unknown: deployment prevalence, public exploitability, reverse-proxy behavior, operating-system variation, harmful frequency, and upstream preference.

## Repair comparison

Leading first candidate: **loopback-only shutdown route**.

It preserves the existing cross-platform SIGINT test path and local shutdown behavior while preventing remote Host acceptance from implicitly granting process-shutdown authority.

Required comparisons before selection:

1. loopback-only source guard;
2. route enabled only by an explicit test capability;
3. removal plus a different cross-platform child-signal fixture;
4. explicit authenticated/secret shutdown capability;
5. documentation-only retention of current behavior.

At minimum, source-shape and execute the loopback-only and test-only alternatives against:

- the existing target `http transport browser sigint` test;
- ordinary HTTP lifecycle tests;
- the three Fieldwork reversing controls;
- target formatting, typecheck/build, and diff hygiene.

## Evidence boundary

Established only for the exact target, one Linux runner, Node 22, Chromium, and runner-local networking. No external website, account, usable credential, private browser state, source repair, merge, deployment, spending, or public-upstream interaction occurred.

The workflow-free head transfers the exact receipt; it does not claim a second target run.