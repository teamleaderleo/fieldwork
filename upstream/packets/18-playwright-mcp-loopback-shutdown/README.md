# Unit 18 — Remove Playwright MCP network shutdown authority

## In simple words

Playwright MCP exposes an HTTP-only test route that emits `SIGINT` and ends the process. Characterization proved any non-browser caller accepted by listener and Host policy can invoke that route with the fixed method and header. A loopback-only repair passed direct controls, then failed a local-proxy discriminator because the proxy connection appears loopback. An environment capability hid the route by default but retained an operator-enabled network termination primitive.

The selected candidate removes the HTTP shutdown route. The spawning Playwright test process requests the existing graceful SIGINT path through its private Node IPC channel. The private message is accepted once only when it is a plain ordinary object with exactly own `type` and `version` keys and exact values. Malformed messages, extension fields, inherited properties, duplicate valid delivery, and IPC disconnect have native controls.

## Current disposition

`EXECUTE`

Last verified: `2026-08-01`  
Scope: unit 18 only  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Public upstream contact authorized/performed: `no` / `none`

Reason: exact current-head macOS and Windows execution is fully green; Ubuntu 24.04 remains queued before runner allocation. No product failure has appeared. After Ubuntu success or an explicit reviewed carry-forward decision, the contribution route becomes `ISSUE FIRST` under Playwright's current contribution guidance.

## Contribution

- Target project and proposed destination: `microsoft/playwright`, base `main`
- Proposed title: `fix(mcp): replace HTTP shutdown route with parent IPC`
- Synopsis: remove `/killkillkill` from the MCP HTTP transport and preserve the cross-platform graceful-shutdown lifecycle test through a one-shot private parent-child IPC message.
- Work class: `upstream-fork research`

## Exact identities

- Historical executed public base: [`368941457a82da112aa8610107e25f4bde94339a`](https://github.com/microsoft/playwright/commit/368941457a82da112aa8610107e25f4bde94339a)
- Current public base inspected: [`15b1aec478d90f0293dae7b7b6dafd494d9f0154`](https://github.com/microsoft/playwright/commit/15b1aec478d90f0293dae7b7b6dafd494d9f0154)
- Exact-base branch: `teamleaderleo/playwright:fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown`
- Canonical source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Packet PR: [`teamleaderleo/fieldwork#451`](https://github.com/teamleaderleo/fieldwork/pull/451)
- Current execution carrier: [`teamleaderleo/fieldwork#455@0323aeaadc391575b572e869258e5e1ac3c4652c`](https://github.com/teamleaderleo/fieldwork/pull/455)
- Current workflow: [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059)
- Superseded loopback source: `teamleaderleo/playwright#37@a834222d585371636eea7fd013e551fb819d9f7d`

## Current code and tests

- [`packages/playwright-core/src/entry/mcp.ts`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/packages/playwright-core/src/entry/mcp.ts) — one-shot strict parent-IPC listener, removed before SIGINT.
- [`packages/playwright-core/src/tools/utils/mcp/http.ts`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/packages/playwright-core/src/tools/utils/mcp/http.ts) — special HTTP shutdown branch removed.
- [`tests/mcp/http.spec.ts`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/tests/mcp/http.spec.ts) — old request inert, malformed and non-exact messages inert, valid message one-shot, duplicate close once, IPC disconnect inert, and real-browser graceful shutdown retained.
- Required generated or dependency files: none.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/playwright-core/src/entry/mcp.ts` | production | yes |
| `packages/playwright-core/src/tools/utils/mcp/http.ts` | production | yes |
| `tests/mcp/http.spec.ts` | regression | yes |

Temporary workflows, receipts, Fieldwork files, dependencies, locks, snapshots, and generated output are absent from the target net diff.

## Evidence summary

| Claim | Evidence | Current result or limit |
| --- | --- | --- |
| accepted non-loopback HTTP caller could terminate MCP | Fieldwork PR #405, run `30649849111`, job `91220131763` | 3/3 passed on Ubuntu with deliberate non-loopback listener/wildcard Host policy |
| direct loopback identity fails through a local proxy | Fieldwork PR #416, run `30656319708`, job `91241456610` | direct suite 19/19 plus proxy discriminator 1/1 passed; loopback candidate terminated |
| bare parent IPC works cross-platform | Fieldwork PRs #423/#425, run `30657930500` | 17/17 plus build, browser setup, focused lint, and diff on Ubuntu/macOS/Windows |
| hardened one-shot IPC works cross-platform | Fieldwork PRs #430/#432, run `30659762667` | 18/18 plus all declared gates on Ubuntu/macOS/Windows; predecessor accepted extension fields |
| current strict validator works on macOS | carrier #455, run `30690674059`, job `91344705071` | exact source `e99e97d...`; 18/18 in 32.6s; all declared gates passed; artifact `8815562250`, digest `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54` |
| current strict validator works on Windows | carrier #455, run `30690674059`, job `91344705088` | exact source `e99e97d...`; 18/18 in 34.0s; all declared gates passed; artifact `8815574235`, digest `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4` |
| current strict validator works on Ubuntu | carrier #455, job `91344705054` | queued before runner allocation; no execution and no product failure yet |
| full repository CI | none | not run and not claimed |

The previous packet head `7fe2bb3b619e6b1675c260d0304fd262eca71f1f` passed Fieldwork integrity in run `30675345841`. This updated packet must complete a fresh integrity run.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and retained receipts](./TESTS.md)
- [Current exact-head execution](./CURRENT_EXECUTION.md)
- [Canonical source generation](./CURRENT_SOURCE.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Continuation handoff](./HANDOFF.md)
- [Compact packet status](./PACKET_STATUS.md)

## Duplicate and prior-art result

- Checked through public head `15b1aec478d90f0293dae7b7b6dafd494d9f0154` on `2026-08-01`.
- Prior merged repair `microsoft/playwright#40551`, commit `4a80eed396071d6ed15a74c32723f2bc66849988`, changed the route from GET to POST plus a custom header for browser-CSRF resistance.
- Equivalent route-removal/parent-IPC implementation found: none in the checked source, history, issues, and pull requests.
- Relationship: complementary authority repair. The prior patch addresses browser-coerced requests; this candidate removes the test-only network termination authority.

## Remaining work in order

1. Complete Ubuntu exact-head execution or record an explicit reviewed carry-forward decision.
2. Complete Fieldwork integrity at the updated packet head.
3. Obtain independent complete-diff review and final acceptance.
4. Squash the seven-commit source history before any authorized submission, then prove exact tree equivalence or rerun declared gates at the resulting head.
5. Seek Playwright issue approval/assignment only after explicit public-contact authority.
6. Open no public issue, PR, comment, or reaction without separate explicit authority.

Evidence limits: full Playwright repository CI has not run; Node versions outside 22 and non-test parent embeddings remain untested.

## Latest handoff

State: `EXECUTE`  
Exact source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`  
Exact packet head: use the latest `p0/435-unit-18-playwright-mcp-shutdown` head and issue #435 handoff after this packet update  
Current exact-head tests: macOS 18/18 and Windows 18/18 plus complete build, Chromium, focused ESLint, clean tree, and exact diff; Ubuntu queued before allocation  
Next action: inspect run `30690674059`, classify Ubuntu separately, transfer its exact receipt if it runs, then move to `ISSUE FIRST` only when the platform gate is cleared  
Public upstream interaction: none; unauthorized
