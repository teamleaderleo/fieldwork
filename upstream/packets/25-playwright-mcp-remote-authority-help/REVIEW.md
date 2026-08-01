# Review — unit 25 Playwright MCP remote and shared-browser authority

## In simple words

The proposed contribution adds three CLI help clauses and changes no runtime behavior. Historical target execution supports the tab/session/lifecycle facts. Current source supports the wider BrowserContext authority description. The main review questions are whether the exact wording is precise, whether a direct documentation PR fits Playwright's contribution policy, and whether the current exact-source validation completed cleanly.

## Review subject

- Work class: `documentation with executed behavioral basis`
- Target repository: `microsoft/playwright`
- Proposed upstream base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch: `teamleaderleo/playwright:docs/mcp-remote-authority-help`
- Exact source head: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`
- Fieldwork packet branch: `p0/435-unit-25-playwright-mcp-remote-authority-help`
- Exact packet head: latest #435 handoff
- Complete changed-file fence: `packages/playwright-core/src/tools/mcp/program.ts`
- Upstream-contact authority: `no`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [complete product compare](https://github.com/teamleaderleo/playwright/compare/15b1aec478d90f0293dae7b7b6dafd494d9f0154...745b4dea96ac64eeb1e92d9ce4525b995e64909f)
6. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
7. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
8. current carrier [`teamleaderleo/playwright#38`](https://github.com/teamleaderleo/playwright/pull/38)

## Exact diff links

- Complete compare: [`15b1aec...745b4dea`](https://github.com/teamleaderleo/playwright/compare/15b1aec478d90f0293dae7b7b6dafd494d9f0154...745b4dea96ac64eeb1e92d9ce4525b995e64909f)
- Production file: [`program.ts@745b4dea`](https://github.com/teamleaderleo/playwright/blob/745b4dea96ac64eeb1e92d9ce4525b995e64909f/packages/playwright-core/src/tools/mcp/program.ts)
- Tests: no clean-source test file changes; current carrier runs existing `tests/mcp/http.spec.ts`
- Generated or dependency files: none
- Retained patch: [`patches/0001-docs-mcp-remote-client-authority.patch`](./patches/0001-docs-mcp-remote-client-authority.patch)

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Host validation is DNS-rebinding protection rather than client authentication | current HTTP source, option source, upstream tests, issue #41915 | Is the wording accurate without implying a vulnerability or promising authentication elsewhere? |
| Non-loopback HTTP should use authenticated or equivalently access-controlled deployment protection | source model and maintainer trust-boundary statement | Is this recommendation appropriately specific and neutral across deployment designs? |
| Every accepted shared-context client shares one BrowserContext | current factory source plus historical two-client execution | Does “shares and can control” match the tools and BrowserContext contract? |
| Tabs, cookies, storage, and page state belong to the shared context | source-read BrowserContext semantics; tabs directly executed | Is the evidence classification clear enough to avoid presenting every asset as directly cross-client-tested? |
| Direct PR is appropriate | minor-documentation exception and existing issue #41915 | Does the unsolicited-PR policy still make fresh approval preferable? |

## Known risks

- The help strings are longer and may wrap differently at narrow terminal widths. Semantic assertions normalize whitespace.
- “Authenticated reverse proxy” may read as one preferred deployment architecture. The wording also permits an equivalently access-controlled trusted network boundary.
- “Storage” is concise but broad. It matches BrowserContext-level state; reviewers may prefer “browser storage” or a narrower list.
- Current public main can move before submission. Rebase and rerun the exact gates if `program.ts` or relevant MCP source changes.
- Existing issue #41915 closed the runtime-authentication proposal. The docs patch complements that decision, but maintainers may still decline additional wording.

## Evidence limits

- Historical behavior execution: Ubuntu 24.04, Node 22, Chromium, target `3689414`.
- Current exact-source validation: owned-fork run `30674483330`, pending at initial self-review.
- Cookie and origin-storage cross-client readback were not directly exercised by the retained matrix.
- Reverse-proxy and production deployment behavior remain unexecuted.
- No public exploitability, prevalence, real credential, private browser data, or built-in-authentication need is established.
- Adjacent shutdown-route work is excluded.

## Staleness check

- Current upstream head checked: `15b1aec478d90f0293dae7b7b6dafd494d9f0154` on `2026-08-01`
- Candidate base relationship: one commit directly on that head
- Relevant source paths changed upstream since historical execution: `program.ts` option strings unchanged; other MCP source evolved
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: `no`
- Relevant closed precedent: issue #41915
- Packet and target descriptions synchronized: `yes at source head 745b4dea; current test receipt pending`

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers on the canonical source branch.
- [x] No stale execution artifacts on the canonical source branch.
- [x] No unrelated formatting or generated churn.
- [x] No snapshot, lock, generated, or dependency changes.
- [x] Commit-pinned links resolve to the reviewed head.
- [x] Execution workflow lives only on separate carrier head `d1733107`.

## Test review

- [ ] Intended current assertions completed.
- [x] Historical baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Historical disconnect and cleanup paths are covered.
- [x] Existing complete HTTP suite is included in the current carrier.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately; no full-gate claim is made.

## Draft review

- [x] Issue route does not oversell impact or prevalence.
- [x] PR draft describes the actual current diff.
- [x] Target terminology and contribution format are used.
- [x] Internal process vocabulary is absent from the upstream PR body.
- [x] Contribution and AI-quality policy was checked; no formal disclosure field was found.
- [x] Existing issue #41915 is cited as related context rather than a vulnerability claim.

## Self-review disposition

`EXECUTE`

Reviewed source head: `745b4dea96ac64eeb1e92d9ce4525b995e64909f`  
Reviewed packet head: latest #435 handoff  
Reason: source diff and packet are coherent; current exact-source workflow receipt remains pending  
Clearing condition: run `30674483330` completes successfully, exact receipt is transferred, carrier #38 closes without merge, and packet state updates to `READY`  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether the three descriptions convey the authority model without widening the runtime contract;
2. whether “authenticated reverse proxy or equivalently access-controlled trusted network boundary” is the clearest deployment-neutral sentence;
3. whether the BrowserContext asset list is precise and appropriately evidence-scoped;
4. whether issue #41915 plus the minor-documentation exception supports a direct PR.

Suggested response after exact-source execution:

`Unit 25 looks ready for upstream preparation`  
—or—  
`Unit 25 concern: <specific wording, policy, evidence, or compatibility issue>`
