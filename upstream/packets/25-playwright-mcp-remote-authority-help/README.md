# Unit 25 — document Playwright MCP remote and shared-browser authority

## In simple words

Playwright MCP uses standard input/output by default. HTTP transport is opt-in and binds to localhost unless an operator deliberately chooses a broader host. Host-header validation reduces DNS-rebinding exposure; it does not identify or authenticate a client.

When HTTP clients use `--shared-browser-context`, they share one browser context. Historical exact-target execution proved cross-client tab visibility, continued use after the first client disconnects, and final-client browser cleanup. Current source inspection shows that the same context also owns cookies, storage, and page state.

This contribution changes three CLI descriptions so operators see those authority boundaries before enabling remote HTTP or shared-browser mode. It changes no runtime behavior.

## Current disposition

`EXECUTE`

Last verified: `2026-08-01`  
Worker: `OpenAI GPT-5.6 Thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

The clean current-source candidate exists. Exact current-source build, generated-help, lint, and HTTP-suite execution are running on a separate owned-fork carrier. Promote to `READY` only after that receipt is transferred and the carrier closes.

## Contribution

- Target project: `microsoft/playwright`
- Proposed upstream destination: `microsoft/playwright:main`
- Proposed title: `docs(cli): document remote and shared-browser authority`
- Contribution synopsis: clarify that `--allowed-hosts` is DNS-rebinding protection rather than client authentication, tell non-loopback HTTP operators to use an authenticated reverse proxy or equivalently access-controlled trusted network boundary, and name the browser-context authority shared by every accepted client under `--shared-browser-context`.
- Work class: `documentation with executed behavioral basis`

## Exact identities

- Public upstream base inspected: [`microsoft/playwright@15b1aec478d90f0293dae7b7b6dafd494d9f0154`](https://github.com/microsoft/playwright/commit/15b1aec478d90f0293dae7b7b6dafd494d9f0154)
- Historical target execution base: [`microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`](https://github.com/microsoft/playwright/commit/368941457a82da112aa8610107e25f4bde94339a)
- Owned target fork: [`teamleaderleo/playwright`](https://github.com/teamleaderleo/playwright)
- Canonical source branch: [`docs/mcp-remote-authority-help`](https://github.com/teamleaderleo/playwright/tree/docs/mcp-remote-authority-help)
- Canonical source head: [`745b4dea96ac64eeb1e92d9ce4525b995e64909f`](https://github.com/teamleaderleo/playwright/commit/745b4dea96ac64eeb1e92d9ce4525b995e64909f)
- Fieldwork packet branch: [`p0/435-unit-25-playwright-mcp-remote-authority-help`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-25-playwright-mcp-remote-authority-help/upstream/packets/25-playwright-mcp-remote-authority-help)
- Exact packet head: recorded in the latest #435 handoff because a commit cannot embed its own SHA
- Current execution carrier: [`teamleaderleo/playwright#38`](https://github.com/teamleaderleo/playwright/pull/38), head [`d173310733d2783347a8572271558f1328b736f7`](https://github.com/teamleaderleo/playwright/commit/d173310733d2783347a8572271558f1328b736f7), workflow run [`30674483330`](https://github.com/teamleaderleo/playwright/actions/runs/30674483330)
- Superseded Fieldwork finding surfaces: [`#374`](https://github.com/teamleaderleo/fieldwork/pull/374) and [`#399`](https://github.com/teamleaderleo/fieldwork/pull/399)
- Historical behavior carrier: [`#375`](https://github.com/teamleaderleo/fieldwork/pull/375) at `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`
- Historical help carrier: [`#377`](https://github.com/teamleaderleo/fieldwork/pull/377) at `204b96c94dfd2fef3ea4981796b2cb98ceae09a9`

## Current code and tests

### Product code

- [`program.ts@745b4dea`](https://github.com/teamleaderleo/playwright/blob/745b4dea96ac64eeb1e92d9ce4525b995e64909f/packages/playwright-core/src/tools/mcp/program.ts#L34-L76) — three help-string changes only.
- [Complete source compare](https://github.com/teamleaderleo/playwright/compare/15b1aec478d90f0293dae7b7b6dafd494d9f0154...745b4dea96ac64eeb1e92d9ce4525b995e64909f)

### Target-native tests

- [`tests/mcp/http.spec.ts@3689414`](https://github.com/microsoft/playwright/blob/368941457a82da112aa8610107e25f4bde94339a/tests/mcp/http.spec.ts) — complete historical upstream HTTP suite executed with the Fieldwork controls.
- [`fieldwork-remote-shared.spec.ts`](https://github.com/teamleaderleo/fieldwork/blob/2a7b6c45179ac3f9e78b8540702e7e88f849b3fd/programmes/high-leverage-open-source/scouts/playwright-mcp-remote-shared-context/fieldwork-remote-shared.spec.ts) — isolated/shared two-client controls retained on historical carrier head.
- Current carrier workflow: [`unit-25-mcp-remote-authority-help.yml@d1733107`](https://github.com/teamleaderleo/playwright/blob/d173310733d2783347a8572271558f1328b736f7/.github/workflows/unit-25-mcp-remote-authority-help.yml)

### Required generated or dependency files

- Not applicable. The clean candidate changes one TypeScript source file and no dependency, lock, snapshot, generated, or workflow file.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/playwright-core/src/tools/mcp/program.ts` | CLI help descriptions | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| HTTP is opt-in, localhost-bound by default, and Host validation is separate from client authentication | `source-read` | current [`program.ts`](https://github.com/microsoft/playwright/blob/15b1aec478d90f0293dae7b7b6dafd494d9f0154/packages/playwright-core/src/tools/mcp/program.ts) and historical source map in #374 | source and configuration semantics only |
| Explicit remote-equivalent isolated sessions keep browser state separate | `target-executed` | Fieldwork run `30633739476`, job `91166043729`, 19/19 | Ubuntu 24.04, Node 22, Chromium, historical target `3689414` |
| Explicit shared mode gives the second client cross-client tab authority and survives first-client disconnect | `target-executed` | same run and job; artifact `8794430468` | direct control exercised tabs, continuity, and cleanup |
| Shared mode uses the same BrowserContext, including its cookies, storage, and page state | `source-read` | current `program.ts` shared-browser creation path and Playwright BrowserContext semantics | cookies/storage were not directly cross-client-tested by the retained matrix |
| The historical three-string patch applied, built, and appeared in generated runtime help | `target-executed` | run `30634831167`, job `91169666445`; artifact `8794842941` | historical wording and target `3689414`; current wording requires current receipt |
| The revised current candidate builds, lints, generates exact help, and preserves the HTTP suite | `target-executed` when complete | owned-fork run `30674483330` | pending at packet creation |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue result](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Retained patch](./patches/0001-docs-mcp-remote-client-authority.patch)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues/PRs checked: exact searches for `allowed-hosts`, client authentication, shared-browser context, remote host, and reverse proxy.
- Relevant precedent: [`microsoft/playwright#41915`](https://github.com/microsoft/playwright/issues/41915), closed `not planned` after a maintainer stated that opt-in HTTP, localhost default, and deliberate non-loopback binding are working as intended.
- Equivalent implementation found: `no`
- Relationship to prior work: `complementary documentation`; the candidate accepts the intended runtime model and clarifies the operator-visible authority boundary.

## Contribution policy result

Current `CONTRIBUTING.md` requires a corresponding issue for most contributions but exempts minor documentation fixes. It also states that unsolicited PRs without linked issue or prior approval will close. This candidate is a three-string documentation-only change with an existing directly relevant issue, so the packet prepares a direct PR while preserving the policy risk for human judgment.

## Remaining work

Complete in this order:

1. transfer the current execution receipt from owned-fork PR #38;
2. close PR #38 without merge and confirm the canonical source head remains workflow-free;
3. update this packet to `READY` or record the exact failed phase;
4. obtain eligible independent complete-diff and packet review;
5. seek separate human authorization before any public upstream interaction.

## Blockers and limits

- Current exact-source execution is still pending.
- Public submission authority is absent.
- Maintainer policy may still prefer prior approval despite the minor-documentation exception and existing issue #41915.
- Historical behavior execution covers one operating system, one Node major, and Chromium.
- Reverse-proxy behavior, deployment prevalence, public exploitability, and any need for built-in authentication remain unestablished.
- Adjacent shutdown-route research belongs to unit 18 / Fieldwork #404 and is excluded from this unit.

## Latest handoff

State: `EXECUTE`  
Exact source head: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`  
Exact packet head: see latest #435 handoff  
Tests: historical behavior and help receipts passed; current run `30674483330` queued  
Temporary machinery remaining: owned-fork PR #38 and its one workflow file  
Next worker action: inspect run `30674483330`, transfer its exact job/artifact receipt, then close PR #38  
Public upstream interaction: `none`
