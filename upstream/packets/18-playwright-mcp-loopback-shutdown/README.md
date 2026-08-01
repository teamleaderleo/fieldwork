# Unit 18 — Remove Playwright MCP network shutdown authority

## In simple words

Playwright MCP exposes an HTTP-only test route that emits `SIGINT` and ends the process. Characterization proved any non-browser caller accepted by listener and Host policy can invoke that route with the fixed method and header. A loopback-only repair passed direct controls, then failed a local-proxy discriminator because the proxy connection appears loopback. An environment capability hid the route by default but retained an operator-enabled network termination primitive.

The selected candidate removes the HTTP shutdown route. The spawning Playwright test process requests the existing graceful SIGINT path through its private Node IPC channel. The private message is accepted once only when it is a plain ordinary object with exactly own `type` and `version` keys and exact values. Malformed messages, extension fields, inherited properties, duplicate valid delivery, and IPC disconnect have native controls.

## Current disposition

`ISSUE FIRST`

Last verified: `2026-08-01`  
Scope: unit 18 only  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Canonical finding: [`teamleaderleo/fieldwork#404`](https://github.com/teamleaderleo/fieldwork/issues/404)  
Public upstream contact authorized/performed: `no` / `none`

Reason: the exact current source head passed every declared gate on Ubuntu 24.04, macOS 15, and Windows 2025, and the packet passed integrity. Playwright's contribution guidance requires a corresponding issue and prior approval/assignment for substantive work, so the next contribution step is design/issue discussion rather than a direct public pull request.

## Contribution

- Target project and proposed destination: `microsoft/playwright`, base `main`
- Proposed title: `fix(mcp): replace HTTP shutdown route with parent IPC`
- Synopsis: remove `/killkillkill` from the MCP HTTP transport and preserve the cross-platform graceful-shutdown lifecycle test through a one-shot private parent-child IPC message.
- Work class: `upstream-fork research`

## Exact identities

- Historical executed public base: [`368941457a82da112aa8610107e25f4bde94339a`](https://github.com/microsoft/playwright/commit/368941457a82da112aa8610107e25f4bde94339a)
- Current inspected base: [`15b1aec478d90f0293dae7b7b6dafd494d9f0154`](https://github.com/microsoft/playwright/commit/15b1aec478d90f0293dae7b7b6dafd494d9f0154)
- Exact-base branch: `teamleaderleo/playwright:fieldwork/435-unit-18-base-15b1aec@15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch: `teamleaderleo/playwright:fix/mcp-parent-ipc-shutdown`
- Canonical source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Packet PR: [`teamleaderleo/fieldwork#451`](https://github.com/teamleaderleo/fieldwork/pull/451)
- Exact-current execution carrier: [`teamleaderleo/fieldwork#455@0323aeaadc391575b572e869258e5e1ac3c4652c`](https://github.com/teamleaderleo/fieldwork/pull/455)
- Exact-current workflow: [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059)
- Adjacent stdin-EOF research source: [`teamleaderleo/playwright#41@86d32569b47fd9f6e98c11517d1699cea5a2465a`](https://github.com/teamleaderleo/playwright/pull/41)
- Adjacent execution carrier: [`teamleaderleo/fieldwork#494@2e32e643cdc6af0a322d49499b0cece3ee9e0699`](https://github.com/teamleaderleo/fieldwork/pull/494)

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

## Exact-current evidence

Run `30690674059` checked out exact source `e99e97da...` and exact base `15b1aec...` on every platform, then ran exact-fence verification, `npm ci`, complete `npm run build`, Chromium installation, the complete native MCP HTTP file, focused ESLint, clean-tree verification, and exact diff checks.

| Platform | Job | Result | Artifact | Digest |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04, Node 22.23.1 | `91344705054` | 18/18 and every declared gate passed | `8815924825` | `sha256:80ea42882f0c6ce9255d57d1a21b23e622b8f68aedda9478caacad818c124e4f` |
| macOS 15 ARM64, Node 22.23.1 | `91344705071` | 18/18 in 32.6s and every declared gate passed | `8815562250` | `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54` |
| Windows Server 2025 x64, Node 22.23.1 | `91344705088` | 18/18 in 34.0s and every declared gate passed | `8815574235` | `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4` |

Packet head `ca95ff2bc643c040ad48a73bb1dc80cdfc64fe8c` passed Fieldwork integrity in run `30691135221`. A new integrity run is required after this research update.

## New approach result

An alternative reused parent stdin ownership instead of adding a private IPC message. The first exact experiment failed on all platforms because parent EOF reaches a readable stream as `end`, while the existing watchdog listened for `close`. A repaired experiment listened for `end` and consumed stdin; run `30704592268` passed the focused 17-test matrix, build, Chromium, lint, and exact diff on Ubuntu, macOS, and Windows.

That repair is not promoted because the watchdog is installed before transport mode is selected. Globally consuming stdin can race the stdio MCP transport and discard early protocol bytes. A safe stdin-based design must be mode-aware and needs dedicated stdio controls. See [Adjacent research](./ADJACENT_RESEARCH.md).

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and retained receipts](./TESTS.md)
- [Current exact-head execution](./CURRENT_EXECUTION.md)
- [Adjacent research and new leads](./ADJACENT_RESEARCH.md)
- [Canonical source generation](./CURRENT_SOURCE.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Continuation handoff](./HANDOFF.md)
- [Compact packet status](./PACKET_STATUS.md)

## Duplicate and prior-art result

- Checked through inspected base `15b1aec478d90f0293dae7b7b6dafd494d9f0154` on `2026-08-01`.
- Prior merged repair `microsoft/playwright#40551`, commit `4a80eed396071d6ed15a74c32723f2bc66849988`, changed the route from GET to POST plus a custom header for browser-CSRF resistance.
- Equivalent route-removal/parent-IPC implementation found: none in the checked source, history, issues, and pull requests.
- No open issue was found for MCP stdin-owner shutdown or MCP signal exit-code semantics in the checked searches.

## Remaining work in order

1. Obtain independent complete-diff review and final acceptance.
2. Decide during issue-first discussion whether maintainers prefer the tested private IPC approach, a mode-aware stdin-owner approach, or removal of the lifecycle test hook.
3. Squash the seven-commit canonical source history before any authorized submission, then prove exact tree equivalence or rerun declared gates at the resulting head.
4. Refresh the public upstream base and duplicate search immediately before authorized contact.
5. Seek Playwright issue approval/assignment only after explicit public-contact authority.
6. Open no public issue, PR, comment, or reaction without separate explicit authority.

Evidence limits: full Playwright repository CI has not run; Node versions outside 22 and non-test parent embeddings remain untested. The stdin-EOF result is a separate experimental generation, not evidence that the canonical source changed.

## Latest handoff

State: `ISSUE FIRST`  
Exact canonical source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`  
Current exact-head tests: 18/18 plus complete declared gates on Ubuntu, macOS, and Windows  
New alternative: mode-naïve stdin EOF repair passed all three platforms but is held for stdio compatibility review  
Next action: obtain independent review, then prepare the issue-first decision surface without public contact  
Public upstream interaction: none; unauthorized
