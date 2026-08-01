# Unit 18 — Remove Playwright MCP network shutdown authority

## In simple words

Playwright MCP exposes an HTTP-only test route that emits `SIGINT` and ends the process. Characterization proved any caller accepted by the configured listener and Host policy can invoke that route with a fixed method and header. A loopback-only repair passed direct controls, then failed a realistic local-proxy discriminator because the proxy's connection appears loopback. An explicit environment capability avoided default exposure while retaining an operator-enabled network shutdown route.

The selected direction removes the HTTP shutdown route entirely. The spawning Playwright test process requests the existing graceful `SIGINT` path through its private Node IPC channel. The clean current-source candidate also tightens the private message contract to one plain object with exactly two own keys, accepts it once, ignores duplicates and malformed variants, and keeps HTTP serving after IPC disconnect.

## Current disposition

`EXECUTE`

Last verified: `2026-08-01`  
Worker: `OpenAI Codex session for unit 18`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `microsoft/playwright`
- Proposed upstream destination: `microsoft/playwright`, base `main`
- Proposed title: `fix(mcp): replace HTTP shutdown route with parent IPC`
- Contribution synopsis: remove the special `/killkillkill` HTTP route and preserve the cross-platform graceful-shutdown lifecycle test through a one-shot private parent-child IPC message.
- Work class: `upstream-fork research`

## Exact identities

- Previously executed public base: [`368941457a82da112aa8610107e25f4bde94339a`](https://github.com/microsoft/playwright/commit/368941457a82da112aa8610107e25f4bde94339a)
- Current public base inspected: [`15b1aec478d90f0293dae7b7b6dafd494d9f0154`](https://github.com/microsoft/playwright/commit/15b1aec478d90f0293dae7b7b6dafd494d9f0154)
- Current-base relation: two commits ahead of the executed base; changed paths are disjoint from the three-file candidate fence.
- Owned target fork: `teamleaderleo/playwright`
- Exact-base branch: `fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch: `fix/mcp-parent-ipc-shutdown`
- Canonical source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Fieldwork packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Fieldwork packet head: updated by this packet series; see latest handoff
- Execution carriers: Fieldwork PRs #405, #410, #414, #416, #419, #423, #425, #430, and #432
- Superseded source branch: `teamleaderleo/playwright#37`, loopback-only head `a834222d585371636eea7fd013e551fb819d9f7d`

## Current code and tests

### Product code

- [`packages/playwright-core/src/entry/mcp.ts`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/packages/playwright-core/src/entry/mcp.ts) — installs a one-shot private IPC listener only when the child has a parent channel and accepts one exact plain-object message.
- [`packages/playwright-core/src/tools/utils/mcp/http.ts`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/packages/playwright-core/src/tools/utils/mcp/http.ts) — removes the special HTTP shutdown route.

### Target-native tests

- [`tests/mcp/http.spec.ts`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/tests/mcp/http.spec.ts) — proves the old HTTP request is inert, malformed/private-message variants are inert, the exact message is one-shot, duplicate delivery closes once, IPC disconnect is inert, and the real-browser graceful SIGINT lifecycle remains active.

### Required generated or dependency files

- `not applicable`

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/playwright-core/src/entry/mcp.ts` | production | yes |
| `packages/playwright-core/src/tools/utils/mcp/http.ts` | production | yes |
| `tests/mcp/http.spec.ts` | regression | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| accepted non-loopback HTTP caller could terminate MCP on the historical base | `target-executed` | Fieldwork PR #405, run `30649849111`, job `91220131763`, 3/3 | Ubuntu only; deliberate non-loopback listener and wildcard Host policy |
| loopback peer checks fail through a local proxy | `integration-executed` | Fieldwork PR #416, run `30656319708`, loopback artifact `8803406788` | Ubuntu local proxy topology |
| bare parent-owned IPC removes HTTP authority and preserves lifecycle testing | `target-executed` | Fieldwork PR #425, run `30657930500`, 17/17 on Ubuntu/macOS/Windows | exact historical target base |
| hardened one-shot IPC preserves behavior across platforms | `target-executed` | Fieldwork PR #432, run `30659762667`, 18/18 on Ubuntu/macOS/Windows | validator accepted extension fields at that generation |
| current-base candidate rejects extra-field and inherited-property messages | `target-test-prepared` | current source head `e99e97d...` | exact current-head execution pending |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Continuation handoff](./HANDOFF.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream source and history checked through public head `15b1aec478d90f0293dae7b7b6dafd494d9f0154`.
- Prior upstream repair: merged PR `microsoft/playwright#40551`, commit `4a80eed396071d6ed15a74c32723f2bc66849988`, changed the route from GET to POST plus a custom header for browser-CSRF resistance.
- Equivalent implementation found: `no`
- Relationship to prior work: complementary authority repair; the prior patch protects against browser-coerced requests, while this unit removes the network shutdown authority used only by the test lifecycle.

## Remaining work

Complete in this order:

1. Run the complete native `tests/mcp/http.spec.ts` suite, focused ESLint, build, and exact three-file diff checks at current source head `e99e97d...`.
2. Execute the unchanged current-head candidate on Ubuntu, macOS, and Windows or record an explicit platform carry-forward judgment from the disjoint-base proof.
3. Perform independent complete-diff review and decide issue-first versus direct PR under the current Playwright contribution policy.

## Blockers and limits

- The current source head has no exact-head execution receipt yet.
- Playwright requires a corresponding issue and prior approval/assignment for substantive contributions; public upstream contact remains unauthorized.
- The current branch has a clean three-file net diff; its commit history still requires squash before any submission.
- Full Playwright repository CI has not run for this candidate.

## Latest handoff

State: `EXECUTE`  
Exact source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`  
Exact packet head: see issue #435 handoff comment after packet completion  
Tests: historical 18/18 native suite across Ubuntu/macOS/Windows passed at the hardened predecessor; current exact-head execution pending  
Temporary machinery remaining: historical Fieldwork execution carriers remain open; no temporary workflow exists on the target source branch  
Next worker action: execute and review the exact current source head without changing the three-file fence  
Public upstream interaction: none; unauthorized
