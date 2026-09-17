# Unit 25 — document Playwright MCP remote and shared-browser authority

## In simple words

Playwright MCP uses standard input/output by default. HTTP is opt-in and binds to localhost unless an operator deliberately chooses a broader host. Host validation reduces DNS-rebinding exposure; it does not identify or authenticate a client.

With `--shared-browser-context`, accepted HTTP clients share one browser context and therefore share authority over its tabs, cookies, storage, and page state. Historical exact-target execution directly proved cross-client tab visibility, continued use after one client disconnects, and final-client browser cleanup. Current source inspection supports the wider BrowserContext state description.

This contribution changes three CLI descriptions so those boundaries appear in runtime help. It changes no behavior.

## Current disposition

`READY`

Last verified: `2026-08-01`  
Worker and reviewer role: `Fieldwork agent`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

The clean source candidate passed exact-source target validation. The complete one-file diff and packet were reviewed with no defect found. The execution-only carrier was closed without merge.

## Contribution

- Target project: `microsoft/playwright`
- Proposed destination: `microsoft/playwright:main`
- Proposed title: `docs(cli): document remote and shared-browser authority`
- Work class: `documentation with executed behavioral basis`
- Changed file: `packages/playwright-core/src/tools/mcp/program.ts`
- Source diff: three help-string replacements, `3 additions / 3 deletions`

The wording:

- identifies `--allowed-hosts` as DNS-rebinding protection rather than authentication;
- recommends an authenticated reverse proxy or equivalently access-controlled trusted network boundary for non-loopback HTTP;
- states that every accepted shared-context client shares and can control the same BrowserContext, including tabs, cookies, storage, and page state.

## Exact identities

- Public upstream base: [`microsoft/playwright@15b1aec478d90f0293dae7b7b6dafd494d9f0154`](https://github.com/microsoft/playwright/commit/15b1aec478d90f0293dae7b7b6dafd494d9f0154)
- Owned target fork: [`teamleaderleo/playwright`](https://github.com/teamleaderleo/playwright)
- Canonical source branch: [`docs/mcp-remote-authority-help`](https://github.com/teamleaderleo/playwright/tree/docs/mcp-remote-authority-help)
- Canonical source head: [`745b4dea96ac64eeb1e92d9ce4525b995e64909f`](https://github.com/teamleaderleo/playwright/commit/745b4dea96ac64eeb1e92d9ce4525b995e64909f)
- Source review surface: [`teamleaderleo/playwright#39`](https://github.com/teamleaderleo/playwright/pull/39)
- Fieldwork packet branch: [`p0/435-unit-25-playwright-mcp-remote-authority-help`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-25-playwright-mcp-remote-authority-help/upstream/packets/25-playwright-mcp-remote-authority-help)
- Exact packet head: recorded in the latest #435 handoff because a commit cannot embed its own SHA
- Retired execution carrier: [`teamleaderleo/playwright#38`](https://github.com/teamleaderleo/playwright/pull/38), head `d173310733d2783347a8572271558f1328b736f7`, closed without merge

The canonical source head remains source-only and contains no workflow, Fieldwork file, generated output, dependency change, lock change, or execution artifact.

## Current exact-source receipt

- Run: [`30674483330`](https://github.com/teamleaderleo/playwright/actions/runs/30674483330)
- Job: `91298776583`
- Environment: Ubuntu 24.04, Node 22.23.1, Chromium 152.0.7977.8
- Exact source verified: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`
- Exact base verified: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Changed-file fence verified: one file, `packages/playwright-core/src/tools/mcp/program.ts`
- `npm ci`: passed
- `npm run build`: passed
- generated MCP `--help` semantic checks: passed for all three complete statements
- focused ESLint: passed
- Chromium installation: passed
- `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`: `17/17 passed in 31.7s`
- Artifact: `8810504057`
- Artifact digest: `sha256:01231f3607e7f56b7e110307fc36c1dfb4aaef7a686b940c8ba34304c23da6bf`

Fieldwork packet integrity also passed on run `30674919682`, job `91300030376` before this receipt update; the updated packet branch must retain a green integrity check at its final head.

## Historical behavioral receipts

### Shared and isolated HTTP behavior

- Target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`
- Carrier: [`teamleaderleo/fieldwork#375`](https://github.com/teamleaderleo/fieldwork/pull/375)
- Head: `2a7b6c45179ac3f9e78b8540702e7e88f849b3fd`
- Run/job: `30633739476` / `91166043729`
- Result: `19/19 passed in 30.4s`
- Artifact/digest: `8794430468` / `sha256:e53fc07dbfb1dfecd98e5e4a4227c50e8774fe5fb4bc05f880f3f56c73403235`

This directly established isolated-session tab separation, shared cross-client tab visibility, continuity after the first client disconnected, and browser cleanup after the final session.

### Historical help-patch feasibility

- Carrier: [`teamleaderleo/fieldwork#377`](https://github.com/teamleaderleo/fieldwork/pull/377)
- Head: `204b96c94dfd2fef3ea4981796b2cb98ceae09a9`
- Run/job: `30634831167` / `91169666445`
- Artifact/digest: `8794842941` / `sha256:d0347ff4a0ed8408f9c5d01b36b703d931bc5bab8e6ac79da373a6bfcb2d0683`

This established ordinary contextual patch application, installation, build, generated runtime help, semantic assertions, and diff hygiene on the historical target. The current receipt above validates the revised wording on the current base.

## Evidence by claim

| Claim | Evidence class | Receipt | Limit |
| --- | --- | --- | --- |
| HTTP is opt-in, localhost-bound by default, and Host validation is not client authentication | `source-read` | current MCP option and HTTP source at base `15b1aec` | source/configuration semantics |
| Current candidate is exactly one source file and three help strings | `source-read` | compare `15b1aec...745b4dea` | source identity only |
| Current candidate installs, builds, generates the expected help, lints, and preserves the HTTP suite | `target-executed` | run `30674483330`, job `91298776583` | Ubuntu, Node 22, Chromium; named gates only |
| Isolated sessions keep tab state separate | `target-executed` | run `30633739476`, job `91166043729` | historical target and one platform/browser |
| Shared clients see the same tab and survive another client disconnect | `target-executed` | same historical run/job | direct tab, continuity, and cleanup controls |
| Cookies, storage, and page state belong to the shared BrowserContext | `source-read` | shared BrowserContext creation path and contract | no direct two-client cookie/storage readback |
| Authenticated proxy or equivalent access control is appropriate for non-loopback deployment | `source-read / recommendation` | transport and authority model | proxy deployment was not executed |

No full-repository-gate, cross-platform, exploitability, prevalence, or built-in-authentication claim is made.

## Duplicate and prior art

- Search date: `2026-08-01`
- Equivalent current implementation found: `no`
- Relevant precedent: [`microsoft/playwright#41915`](https://github.com/microsoft/playwright/issues/41915), closed `not planned` after maintainers described opt-in HTTP, localhost default, and deliberate non-loopback binding as intended behavior.
- Relationship: complementary documentation that preserves the intended runtime model.

## Contribution policy

Current `CONTRIBUTING.md` generally asks for a corresponding issue, exempts minor documentation fixes, and warns that unsolicited PRs without a linked issue or prior approval may close. This is a three-string documentation-only change with existing directly relevant issue context. The packet therefore prepares a direct PR while recording the policy risk.

## Review result

Complete exact-diff agent review covered:

- the full `15b1aec...745b4dea` source diff;
- runtime-help wording and wrapping;
- evidence classification per claim;
- source cleanliness and carrier retirement;
- duplicate/prior-art and contribution-policy fit;
- the proposed upstream issue route and PR body.

Disposition: `ACCEPT for upstream preparation`. No source or packet repair is required.

## Remaining limits and authority

- Public upstream interaction remains unauthorized and is the only action blocker.
- Public main may move; rebase and rerun the named gates if relevant MCP source changes before submission.
- Maintainers may prefer prior approval despite the minor-documentation exception.
- Historical behavior coverage is Ubuntu/Node 22/Chromium only.
- Proxy behavior, production deployment prevalence, public exploitability, and need for built-in authentication remain unestablished.
- Adjacent shutdown-route work belongs to unit 18 / Fieldwork #404 and is excluded.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue result](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review receipt](./REVIEW.md)
- [Retained patch](./patches/0001-docs-mcp-remote-client-authority.patch)

## Latest handoff

State: `READY`  
Exact source head: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`  
Exact packet head: see latest #435 handoff  
Tests: current exact-source run passed; historical behavioral and help receipts passed  
Temporary machinery: carrier PR #38 closed without merge; canonical source remains workflow-free  
Review: complete exact-diff agent review accepted the unit for upstream preparation  
Public upstream interaction: `none; unauthorized`
