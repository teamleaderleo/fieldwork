# Agent review receipt — unit 25 Playwright MCP remote and shared-browser authority

## In simple words

The proposed contribution adds three CLI help clauses and changes no runtime behavior. The complete exact source diff is one file with three string replacements. Current exact-source execution passed installation, build, generated-help checks, focused lint, and all 17 MCP HTTP tests. Historical target execution supports the tab/session/lifecycle facts, while current source supports the wider BrowserContext state description.

No defect was found in the source candidate or packet. The unit is ready for upstream preparation. Public upstream interaction remains unauthorized.

## Review subject

- Work class: `documentation with executed behavioral basis`
- Target repository: `microsoft/playwright`
- Proposed upstream base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch: `teamleaderleo/playwright:docs/mcp-remote-authority-help`
- Exact source head: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`
- Source PR: [`teamleaderleo/playwright#39`](https://github.com/teamleaderleo/playwright/pull/39)
- Packet branch: `p0/435-unit-25-playwright-mcp-remote-authority-help`
- Packet PR: [`teamleaderleo/fieldwork#448`](https://github.com/teamleaderleo/fieldwork/pull/448)
- Complete changed-file fence: `packages/playwright-core/src/tools/mcp/program.ts`
- Upstream-contact authority: `no`

## Complete diff reviewed

Base-to-head compare:

[`15b1aec478d90f0293dae7b7b6dafd494d9f0154...745b4dea96ac64eeb1e92d9ce4525b995e64909f`](https://github.com/teamleaderleo/playwright/compare/15b1aec478d90f0293dae7b7b6dafd494d9f0154...745b4dea96ac64eeb1e92d9ce4525b995e64909f)

The diff contains exactly three description changes:

1. `--allowed-hosts` now says Host validation protects against DNS rebinding and does not authenticate clients.
2. `--host` now recommends an authenticated reverse proxy or equivalently access-controlled trusted network boundary for non-loopback HTTP.
3. `--shared-browser-context` now states that every accepted client shares and can control the same BrowserContext, including tabs, cookies, storage, and page state.

Diff size: `1 file changed, 3 insertions, 3 deletions`.

No option, parser, default, transport, session lifecycle, browser behavior, Host policy, or authentication mechanism changes.

## Exact-source execution reviewed

- Carrier PR: [`teamleaderleo/playwright#38`](https://github.com/teamleaderleo/playwright/pull/38), closed without merge
- Carrier head: `d173310733d2783347a8572271558f1328b736f7`
- Run/job: [`30674483330`](https://github.com/teamleaderleo/playwright/actions/runs/30674483330) / `91298776583`
- Environment: Ubuntu 24.04, Node 22.23.1, Chromium 152.0.7977.8
- Artifact: `8810504057`
- Digest: `sha256:01231f3607e7f56b7e110307fc36c1dfb4aaef7a686b940c8ba34304c23da6bf`

Passed phases:

- exact carrier and source identity;
- exact one-file changed-file fence;
- `git diff --check`;
- `npm ci`;
- `npm run build`;
- generated MCP help containing all three complete statements;
- `npx eslint packages/playwright-core/src/tools/mcp/program.ts`;
- Chromium installation;
- `npm run test-mcp tests/mcp/http.spec.ts -- --project=chromium`: `17/17 passed in 31.7s`.

The intended assertions ran. No setup, fixture, installation, or unrelated precondition failure is being treated as product evidence.

## Claim review

| Claim or design choice | Evidence class | Review conclusion |
| --- | --- | --- |
| Host validation is DNS-rebinding protection rather than client authentication | `source-read` | accurate and appropriately narrow |
| Non-loopback HTTP should use authenticated or equivalently access-controlled protection | `source-read / recommendation` | specific enough to be actionable without requiring one deployment architecture |
| Shared-context clients share and can control one BrowserContext | `source-read` plus historical `target-executed` tab control | wording matches the server factory, tool authority, and BrowserContext model |
| Tabs are visible across shared clients and the remaining client continues after another disconnects | `target-executed` | directly supported by historical run `30633739476` |
| Cookies, storage, and page state belong to the shared context | `source-read` | correctly classified; packet does not claim direct two-client readback execution |
| The three revised statements survive generation and wrapping | `target-executed` | current generated-help semantic checks passed |
| Existing HTTP behavior remains intact | `target-executed` | complete current Chromium HTTP suite passed 17/17 |
| Direct documentation PR route is defensible | contribution-policy read plus issue #41915 prior art | minor-docs exception and existing issue support the route; maintainer preference risk remains visible |

## Source cleanliness review

- [x] Canonical source head is exact and unchanged: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`.
- [x] Source diff contains one product file only.
- [x] No Fieldwork-only files are present.
- [x] No workflow, publisher, receipt, or execution artifact is present.
- [x] No generated, dependency, lock, snapshot, or formatting churn is present.
- [x] Temporary carrier PR #38 is closed without merge.
- [x] Carrier workflow remains outside the canonical source branch.
- [x] Source PR #39 remains draft and source-only.

## Packet review

Reviewed packet components:

- `README.md`
- `DEEP_DIVE.md`
- `APPROACHES.md`
- `TESTS.md`
- `UPSTREAM_ISSUE.md`
- `UPSTREAM_PR.md`
- retained mail patch
- this review receipt

Findings:

- evidence class is separated per claim;
- historical carrier failures are classified as carrier/harness failures;
- selected and rejected approaches are recorded;
- adjacent shutdown-route work is excluded;
- duplicate/prior-art result is current as of `2026-08-01`;
- proposed issue and PR drafts avoid vulnerability, prevalence, or built-in-authentication claims;
- the PR draft describes the actual one-file diff and exact test commands;
- public-contact authority is clearly separate from technical readiness.

## Known limits

- Current and historical execution are Ubuntu/Node 22/Chromium only.
- Cookies and origin storage were not directly read back across two clients; that part remains source-backed.
- Reverse-proxy and production deployment behavior were not executed.
- No claim is made about exploitability, prevalence, ecosystem demand, or need for built-in authentication.
- Public upstream main can move before submission; relevant source movement requires rebase and rerun.
- Maintainers may prefer prior approval despite the minor-documentation exception.

These limits do not block upstream preparation for this documentation-only diff.

## Disposition

`ACCEPT`

Accepted transition: mark unit 25 `READY` for upstream preparation at exact source head `745b4dea96ac64eeb1e92d9ce4525b995e64909f`.

No repair is required. The only blocked action is public upstream interaction, because authorization is `no`.
