# Review — Unit 18 Playwright MCP shutdown authority

## In simple words

The candidate removes a test-only process termination route from MCP HTTP and preserves the same graceful lifecycle test through the spawning parent's private IPC channel. Historical cross-platform execution strongly supports the authority model. The final reviewer should challenge the strict private-message validator, the placement of the listener in the CLI entrypoint, and the lack of exact current-head execution.

## Review subject

- Work class: `upstream-fork research`
- Target repository: `teamleaderleo/playwright` for owned-source review; proposed destination `microsoft/playwright`
- Proposed upstream base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch: `fix/mcp-parent-ipc-shutdown`
- Exact source head: `c4c5e2db6f0305237be4de4c167dfb2344abb305`
- Fieldwork packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Exact packet head: see latest branch head and issue #435 handoff
- Complete changed-file fence: `mcp.ts`, `http.ts`, `http.spec.ts`
- Upstream-contact authority: `none`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [complete source compare](https://github.com/teamleaderleo/playwright/compare/fieldwork/435-unit-18-base-15b1aec...fix/mcp-parent-ipc-shutdown)
6. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
7. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: [`15b1aec...c4c5e2d`](https://github.com/teamleaderleo/playwright/compare/fieldwork/435-unit-18-base-15b1aec...fix/mcp-parent-ipc-shutdown)
- production entrypoint: [`mcp.ts`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/packages/playwright-core/src/entry/mcp.ts)
- HTTP transport: [`http.ts`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/packages/playwright-core/src/tools/utils/mcp/http.ts)
- tests: [`http.spec.ts`](https://github.com/teamleaderleo/playwright/blob/c4c5e2db6f0305237be4de4c167dfb2344abb305/tests/mcp/http.spec.ts)
- generated or dependency files: `not applicable`

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Parent IPC owns the test action more narrowly than HTTP | PR #425/#432 cross-platform receipts | Is any supported external use of `/killkillkill` being removed? |
| Listener belongs in `mcp.ts` | source diff | Is there a more test-local existing hook that preserves packaging and Windows behavior? |
| Exact own-property validation is appropriate | current source and prepared controls | Is this private protocol clear and fail-closed without unnecessary cleverness? |
| Duplicate handling is one-shot | predecessor 18/18 and listener removal before SIGINT | Could queued duplicate messages run after listener removal in any supported Node behavior? |
| Current-base carry-forward is low risk | disjoint compare from `3689414` to `15b1aec` | Does current-head execution remain mandatory for all three platforms? |

## Known risks

- `process.send` may be present in embeddings beyond the native test harness; the parent already owns the child, yet the exact internal message becomes an accepted control in those embeddings.
- The validator checks a plain ordinary object and all own keys; reviewer should inspect getter/proxy behavior and whether IPC deserialization guarantees plain data.
- The fixture adds IPC to every child in this test suite, though ordinary-suite and disconnect controls passed on the predecessor.
- Source history includes transient add/delete cleanup commits; submission requires squash.

## Evidence limits

- strict extra-field and inherited-property controls have not run at `c4c5e2d...`
- no full repository CI at the current source head
- no explicit current Node versions other than 22
- same-account reviews and historical selections do not satisfy independent final acceptance
- upstream issue approval is absent

## Staleness check

- Current upstream head checked: `15b1aec478d90f0293dae7b7b6dafd494d9f0154` on `2026-08-01`
- Candidate base relationship: direct child branch of an owned exact-base ref
- Relevant source paths changed upstream since historical execution: `no` through `15b1aec...`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: `none in the checked searches`
- Packet and target PR descriptions synchronized: `owned-fork source record still to be opened or updated after exact-head checks`

## Source cleanliness

- [x] No Fieldwork-only files in the target net diff.
- [x] No temporary workflows or publishers.
- [x] No retained execution artifacts.
- [x] Three-file net fence only.
- [ ] Remove incidental comment/newline churn if the owned-fork PR diff shows it.
- [ ] Squash transient commit history before submission.
- [x] No snapshots, locks, generated files, or dependency changes.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Historical intended assertions ran and failures were classified.
- [x] Baseline/candidate relationship is explicit.
- [x] Setup and product failures are separated.
- [x] Failure and cleanup paths have predecessor coverage.
- [x] Compatibility controls exist.
- [x] Platform and integration limits are explicit.
- [x] Ordinary historical target gates are named accurately.
- [ ] Current exact-head tests run.

## Draft review

- [x] Issue draft avoids prevalence and severity claims.
- [x] PR draft describes the actual selected three-file direction.
- [x] Playwright terminology and issue-first contribution policy are represented.
- [x] Internal Fieldwork links are excluded from the public drafts.
- [ ] AI disclosure requirement checked again at filing time.

## Reviewer disposition

`EXECUTE`

Reviewed source head: `c4c5e2db6f0305237be4de4c167dfb2344abb305`  
Reviewed packet head: branch head after packet completion  
Reason: selected design has persuasive retained cross-platform evidence, but the current strict-validator generation has new executable controls and lacks an exact-head receipt.  
Clearing condition: exact current-head native suite, build, focused lint, diff review, and independent judgment on the CLI listener/message validator.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether removing the route is compatible with every intended use
2. whether `mcp.ts` is the clearest home for the test-parent listener
3. whether strict plain-object validation handles proxies/getters and Node IPC deserialization honestly
4. whether historical three-platform execution can be carried forward or must be repeated unchanged

Suggested response:

`Unit 18 looks ready for exact-head execution`  
—or—  
`Unit 18 concern: <specific source, test, compatibility, or framing issue>`
