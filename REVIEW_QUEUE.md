# Fieldwork review queue

Snapshot date: **2026-07-30**

GitHub issues remain the canonical live state. This file is a deliberately small review index: it tells a human or independent agent what deserves attention first, what claim is actually being made, which evidence to inspect, and what decision closes the review.

## In simple words

Fieldwork has enough active research. The immediate constraint is review capacity.

The top of the queue is:

1. **MCP reconnect ownership** — independently verify the strongest executed defect and decide whether upstream contact should be authorized.
2. **Biome safe-fix semantics** — verify the released-package reproduction and decide whether the finding should be promoted.
3. **Codex mutation receipts** — select one canonical receipt implementation before overlapping branches continue.
4. **Vite HMR and graph findings** — review two stable-mode findings separately from the experimental bundled-development case.
5. **Execution-gated candidates** — run the prepared Vercel AI, Workers SDK, Gemini CLI, and T3/OpenCode tests before treating their fixes as validated.

A reviewer does not need to read the whole portfolio. Start with one queue card, follow its evidence links, and return one explicit disposition.

## Reviewer dispositions

Use one of these outcomes:

- **Accept** — the evidence and wording support the stated conclusion.
- **Revise** — the underlying work is useful, but the claim, scope, test, or presentation needs correction.
- **Execute** — the design is reviewable, but target-native or package-level evidence is still required.
- **Hold** — the item is valid but not worth advancing now.
- **Authorize contact** — the evidence is sufficient to permit the specifically described upstream interaction.
- **Reject or stop** — the premise is disproven, duplicated, superseded, or not consequential enough.

A review should record:

```text
Disposition:
Evidence checked:
Strongest supported conclusion:
Overstatement or missing proof:
Required next action:
Next owner:
Upstream contact authorized: yes/no/not requested
```

## Evidence rules

Reviewers must preserve the evidence category used by the underlying work:

- **Executed target or public-path reproduction** — the relevant implementation or released package ran under retained conditions.
- **Source-confirmed** — code at a pinned revision directly supports the mechanism.
- **Probe-reproduced model** — a controlled model demonstrates the mechanism but does not execute the target.
- **Prepared target test** — the test exists in an owned fork but has no retained execution receipt.
- **Candidate contract** — the work proposes a desired invariant; current code is not assumed to promise it.
- **Reported alignment** — public reports agree with the mechanism, but are not independent reproduction evidence.

Do not silently upgrade source analysis into execution evidence, a model into a target result, or a prepared test into a failing test.

Research-file citations below are pinned to exact Fieldwork commits. Live pull-request and issue links are included separately for discussion state and later amendments.

---

## Priority 0 — human decisions and queue control

### RQ-001 — MCP concurrent reconnect retry ownership

**State:** Ready for independent technical review and an upstream-contact decision.  
**Primary record:** [Fieldwork PR #82](https://github.com/teamleaderleo/fieldwork/pull/82)  
**Evidence:** [lane report](https://github.com/teamleaderleo/fieldwork/blob/fbbea68332ecd57e7abad538453ad07d541387b1/campaigns/0004-mcp-streamable-http-reconnect/lanes/L01-concurrent-reconnect-ownership/report.md), [era-scope amendment](https://github.com/teamleaderleo/fieldwork/blob/fbbea68332ecd57e7abad538453ad07d541387b1/campaigns/0004-mcp-streamable-http-reconnect/lanes/L01-concurrent-reconnect-ownership/era-scope-amendment.md), [owned-fork draft](https://github.com/teamleaderleo/typescript-sdk/pull/1), and [final fork workflow run](https://github.com/teamleaderleo/typescript-sdk/actions/runs/30476941445).

**Human summary:** Two concurrent Streamable HTTP request streams can receive different SSE `retry` values, but the transport stores retry timing in shared state. When one stream later reconnects after its own GET failure, it can use the other stream's retry value. The case reproduced in both directions on Node 20, 22, and 24.

**Review ask:**

1. Confirm the fixture uses two real POST/SSE streams with distinct retry values and stream-specific `Last-Event-ID` values.
2. Confirm the failed reconnect for stream A is scheduled using stream B's later value in both directional controls.
3. Confirm the packet does not claim measured production frequency or impact magnitude.
4. Review the held upstream issue wording for a narrow shared-state ownership claim.
5. Choose **authorize contact**, **revise**, or **hold**.

**Uncertainty to preserve:** Production impact magnitude and server diversity were not measured. The separate retry-budget investigation did not promote successful reopen/reset behaviour as a defect.

**Done when:** One independent review is recorded and the coordinator explicitly authorizes or declines the prepared upstream issue.

### RQ-002 — Biome `useObjectSpread` accessor semantics

**State:** Ready for independent technical review; promotion decision follows.  
**Primary record:** [Fieldwork PR #97](https://github.com/teamleaderleo/fieldwork/pull/97)  
**Evidence:** [lane report](https://github.com/teamleaderleo/fieldwork/blob/a1ad034eb3500f20d5815ea3d34a1244d0029a59/programmes/web-tooling-runtime-correctness/scouts/biome-safe-fix-runtime-semantics/report.md), [reproduction guide](https://github.com/teamleaderleo/fieldwork/blob/a1ad034eb3500f20d5815ea3d34a1244d0029a59/programmes/web-tooling-runtime-correctness/scouts/biome-safe-fix-runtime-semantics/reproductions/use-object-spread-accessors/README.md), [fixture](https://github.com/teamleaderleo/fieldwork/blob/a1ad034eb3500f20d5815ea3d34a1244d0029a59/programmes/web-tooling-runtime-correctness/scouts/biome-safe-fix-runtime-semantics/reproductions/use-object-spread-accessors/input.mjs), and [released-package workflow run](https://github.com/teamleaderleo/fieldwork/actions/runs/30479636589).

**Human summary:** Biome 2.5.6 labels the transformation safe, but flattening accessor-bearing object literals from `Object.assign` into object spread changes setter invocation, getter timing, and property descriptors. The released package applied the fix and the retained Node 22 workflow demonstrated the semantic difference.

**Review ask:**

1. Re-run or inspect the released-package reproduction and compare the before/after runtime object descriptors.
2. Verify the rule's safe-fix classification and the implementation's lack of an accessor guard.
3. Confirm ordinary data-property cases remain valid and that declining accessor-bearing cases is a narrow plausible correction.
4. Recheck current prior art before promotion.
5. Choose **accept for promotion**, **revise**, or **hold**. Upstream contact remains a separate decision.

**Uncertainty to preserve:** The reproduction proves a semantic change, not the frequency of accessor-bearing `Object.assign` patterns in real projects.

**Done when:** An independent reviewer confirms or rejects the semantic claim and records whether an upstream packet should be prepared.

### RQ-003 — Canonical Codex mutation-receipt branch

**State:** Human coordination decision required before additional implementation wiring.  
**Primary record:** [Campaign #83](https://github.com/teamleaderleo/fieldwork/issues/83)  
**Evidence:** [campaign question](https://github.com/teamleaderleo/fieldwork/blob/dd75315202f5e66c90961cddd6d914766d7db576/campaigns/0003-compaction-mutation-identity/question.md), [source map](https://github.com/teamleaderleo/fieldwork/blob/dd75315202f5e66c90961cddd6d914766d7db576/campaigns/0003-compaction-mutation-identity/source-map.md), [decision](https://github.com/teamleaderleo/fieldwork/blob/dd75315202f5e66c90961cddd6d914766d7db576/campaigns/0003-compaction-mutation-identity/decision.md), [raw-history validator PR](https://github.com/teamleaderleo/codex/pull/2), [receipt contract PR](https://github.com/teamleaderleo/codex/pull/3), and [alternate receipt-primitives PR](https://github.com/teamleaderleo/codex/pull/4).

**Human summary:** The campaign correctly separates raw call/result validation from a privacy-safe operation-effect and terminal-receipt contract. However, Codex PRs #3 and #4 now overlap on the receipt primitive. Continuing both would multiply review work and risk semantic drift.

**Review ask:**

1. Keep Codex PR #2 separate as the raw-history validator.
2. Compare PRs #3 and #4 for receipt states, duplicate handling, readiness rules, API placement, tests, and privacy boundaries.
3. Select one canonical receipt branch.
4. Move any uniquely stronger tests or semantics from the other branch.
5. Close or archive the duplicate before dispatch, persistence, or compaction wiring continues.
6. Record the baseline CI limitation separately from branch-owned failures.

**Uncertainty to preserve:** Neither receipt branch yet proves end-to-end ownership through dispatch, durable result persistence, all compaction paths, or retry suppression.

**Done when:** One canonical receipt branch exists, the duplicate is stopped, and the next wiring slice names exactly one runtime owner.

---

## Priority 1 — independent technical review

### RQ-004 — Vite plugin invalidation and post-transform graph correctness

**State:** Ready for independent review; treat each candidate separately.  
**Primary record:** [Fieldwork PR #48](https://github.com/teamleaderleo/fieldwork/pull/48)  
**Evidence:** [scout report](https://github.com/teamleaderleo/fieldwork/blob/201dc6c59f2a2108c39ebd3ecd2273c547a4c198/programmes/web-tooling-runtime-correctness/scouts/vite-plugin-hmr-invalidation/report.md), [watch-change execution update](https://github.com/teamleaderleo/fieldwork/blob/201dc6c59f2a2108c39ebd3ecd2273c547a4c198/programmes/web-tooling-runtime-correctness/scouts/vite-plugin-hmr-invalidation/execution-update-2026-07-29.md), [post-transform update](https://github.com/teamleaderleo/fieldwork/blob/201dc6c59f2a2108c39ebd3ecd2273c547a4c198/programmes/web-tooling-runtime-correctness/scouts/vite-plugin-hmr-invalidation/execution-update-post-transform-2026-07-29.md), and [bundled-development update](https://github.com/teamleaderleo/fieldwork/blob/201dc6c59f2a2108c39ebd3ecd2273c547a4c198/programmes/web-tooling-runtime-correctness/scouts/vite-plugin-hmr-invalidation/execution-update-bundled-dev-2026-07-30.md). Target reproductions are in [Vite PR #1](https://github.com/teamleaderleo/vite/pull/1), [#2](https://github.com/teamleaderleo/vite/pull/2), and [#3](https://github.com/teamleaderleo/vite/pull/3).

**Human summary:** Three distinct findings are bundled in the scout. A rejected `watchChange` hook can stop Vite-owned invalidation; a post-ordered transform can introduce imports after dev import analysis; and experimental bundled development can observe a file change while skipping the plugin's `hotUpdate` path. The first two are stable-mode correctness candidates. The third is an experimental compatibility question.

**Review ask:**

1. Review the `watchChange` error-isolation case and post-transform graph case as independent stable-mode candidates.
2. Confirm the browser/runtime consequences and the retained cross-version or cross-platform evidence.
3. Keep bundled-development wording explicitly qualified as experimental.
4. Check whether warning-only remedies would leave stale state or graph divergence in place.
5. Recommend which candidate, if any, deserves a separate upstream packet.

**Done when:** Each candidate has its own disposition and the experimental case is not used to overstate stable Vite behaviour.

### RQ-005 — Vercel AI terminal outcomes and resumable Stop ownership

**State:** Design review is possible; target-native execution remains the gate.  
**Primary record:** [Scout PR #34](https://github.com/teamleaderleo/fieldwork/pull/34), campaigns [#76](https://github.com/teamleaderleo/fieldwork/issues/76), [#94](https://github.com/teamleaderleo/fieldwork/issues/94), and [#95](https://github.com/teamleaderleo/fieldwork/issues/95).  
**Evidence:** [scout report](https://github.com/teamleaderleo/fieldwork/blob/1d20c755072207d8c21441b505c1ec6fc3324fe4/programmes/sdk-integration-lifecycle/scouts/vercel-ai-stream-tool-lifecycle/report.md), [terminal-outcome follow-up](https://github.com/teamleaderleo/fieldwork/blob/1d20c755072207d8c21441b505c1ec6fc3324fe4/programmes/sdk-integration-lifecycle/scouts/vercel-ai-stream-tool-lifecycle/follow-up-terminal-outcomes.md), [surrounding candidates](https://github.com/teamleaderleo/fieldwork/blob/1d20c755072207d8c21441b505c1ec6fc3324fe4/programmes/sdk-integration-lifecycle/scouts/vercel-ai-stream-tool-lifecycle/surrounding-lifecycle-candidates.md), [explicit-abort candidate](https://github.com/teamleaderleo/ai/pull/1), and [resumable-Stop candidate](https://github.com/teamleaderleo/ai/pull/3).

**Human summary:** Explicit operation abort, silent provider truncation, and application-owned resumable Stop are separate terminal-state problems. The split is sound. The explicit-abort and stale-Stop candidates are written but not executed in the retained environment; truncated-stream classification still needs a compatibility matrix before choosing an API representation.

**Review ask:**

1. Verify that ordinary consumer cancellation remains distinct from operation abort.
2. Run the explicit-abort candidate against Node and Edge suites, including pre-abort and abort/error race controls.
3. Run the resumable Stop cases for Stop A then run B, delayed Stop A, duplicate Stop, and reconnect without Stop.
4. Execute the truncation matrix before selecting `incomplete`, typed error, metadata, or another public representation.
5. Reject any attempt to collapse all three questions into one patch.

**Done when:** Exact tested heads and retained outputs exist for the candidates, and the truncation campaign has a bounded compatibility decision.

### RQ-006 — Workers SDK lifecycle batch

**State:** Batch structure is ready; evidence work is underway.  
**Primary records:** [Batch #88](https://github.com/teamleaderleo/fieldwork/issues/88), [coordination PR #92](https://github.com/teamleaderleo/fieldwork/pull/92).  
**Evidence:** [dispatch](https://github.com/teamleaderleo/fieldwork/blob/f03ceaa97a9051a99a56b35567c81d0bde66443f/batches/B20260730-001-workers-sdk-lifecycle-followup/DISPATCH.md), [status](https://github.com/teamleaderleo/fieldwork/blob/f03ceaa97a9051a99a56b35567c81d0bde66443f/batches/B20260730-001-workers-sdk-lifecycle-followup/STATUS.md), [manifest](https://github.com/teamleaderleo/fieldwork/blob/f03ceaa97a9051a99a56b35567c81d0bde66443f/batches/B20260730-001-workers-sdk-lifecycle-followup/manifest.json), and [A001 owned-fork draft](https://github.com/teamleaderleo/workers-sdk/pull/1).

**Human summary:** Four bounded assignments cover teardown ownership, configuration selection, partial deployment state, and independent review. A001 now contains a real Miniflare failure-injection regression for an early disposal rejection that can skip `Runtime.dispose()` and therefore skip the `workerd` kill path.

**Review ask:**

1. Execute A001 and retain the expected current failure before considering a repair.
2. Dispatch or complete A002 and A003 without sharing result paths.
3. Keep A004 independent from the implementation owners.
4. Require the declared cross-review loop before synthesis.
5. Do not infer live Cloudflare deployment consequences solely from source models.

**Done when:** A001–A004 each return a bounded result or negative result and the batch synthesis identifies which campaign, if any, should advance.

### RQ-007 — Gemini CLI deterministic lifecycle packet

**State:** Ready for source and presentation review; target tests remain unexecuted.  
**Primary record:** [Fieldwork PR #45](https://github.com/teamleaderleo/fieldwork/pull/45)  
**Evidence:** [review packet](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/review-packet-2026-07-30.md), [report](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/report.md), [exploration log](https://github.com/teamleaderleo/fieldwork/blob/9515e6a091f1c654f5ccdd6d60656b469f7b5889/programmes/agent-cli-execution/scouts/gemini-tool-session-recovery/exploration-log-2026-07-30.md), and owned-fork drafts [#1](https://github.com/teamleaderleo/gemini-cli/pull/1), [#2](https://github.com/teamleaderleo/gemini-cli/pull/2), [#3](https://github.com/teamleaderleo/gemini-cli/pull/3), and [#4](https://github.com/teamleaderleo/gemini-cli/pull/4).

**Human summary:** The packet contains three narrow source-confirmed defects, one proposed asynchronous termination-ownership contract, and broader recovery questions. The evidence wording is now disciplined, but the four fork tests still need target-native execution receipts.

**Review ask:**

1. Recheck the three narrow source defects against the pinned revision.
2. Execute the waiting-state and call-affinity tests first.
3. Expand the discovered-tool abort case from helper wiring to a real parent/descendant ownership test.
4. Review lifecycle termination as a proposed contract, not a current API guarantee.
5. Preserve the open status of MCP remote cancellation and durable session receipts.

**Done when:** The source review is accepted or corrected and each promoted defect has an exact target-test receipt.

### RQ-008 — T3/OpenCode completion reconciliation

**State:** Source-supported campaign with a prepared but unexecuted target test.  
**Primary records:** [Scout PR #63](https://github.com/teamleaderleo/fieldwork/pull/63), [Campaign #71](https://github.com/teamleaderleo/fieldwork/issues/71), [campaign PR #75](https://github.com/teamleaderleo/fieldwork/pull/75).  
**Evidence:** [control-surface report](https://github.com/teamleaderleo/fieldwork/blob/174bd677d0c67c2e371e884665eb3971e822e0ab/programmes/agent-cli-execution/scouts/harness-control-surfaces/report.md), [contract cases](https://github.com/teamleaderleo/fieldwork/blob/174bd677d0c67c2e371e884665eb3971e822e0ab/programmes/agent-cli-execution/scouts/harness-control-surfaces/artifacts/contract-cases.json), and the prepared target test described in PR #75.

**Human summary:** T3 restores the OpenCode session identity after restart but not the previous active T3 turn identity. Provider idle can therefore lack the correlation needed to close stale persisted running state. A simple idle-to-ready fallback might fix the stale state but could also let a delayed old-session event close a newer turn.

**Review ask:**

1. Execute the prepared restart regression.
2. Add the adapter-replacement control where an old idle event arrives after a newer turn begins.
3. Compare a narrow thread-scoped reconciliation with durable turn identity.
4. Test interruption both with and without a later provider idle event.
5. Do not apply the fallback until exact event affinity is demonstrated.

**Done when:** The target trace confirms or disproves the restart identity gap and one repair survives the delayed-old-event control.

---

## Monitored work — not ahead of the queue

These remain valuable, but they should not displace the reviews above unless new evidence creates a security, data-loss, or urgent compatibility concern:

- **Playwright fixture teardown:** [PR #49](https://github.com/teamleaderleo/fieldwork/pull/49) and owned-fork PRs [#10](https://github.com/teamleaderleo/playwright/pull/10)/[#11](https://github.com/teamleaderleo/playwright/pull/11). Consolidate the dependency-group intervention and exact-run evidence before opening more scheduler variants.
- **DuckDB remote publication:** [Campaign #96](https://github.com/teamleaderleo/fieldwork/issues/96). Continue the MinIO-backed object-store matrix; no human decision is needed until reproducible publication-state evidence exists.
- **Supabase auth refresh settlement:** [Campaign #78](https://github.com/teamleaderleo/fieldwork/issues/78) and [PR #91](https://github.com/teamleaderleo/fieldwork/pull/91). Complete the real-code two-variant matrix before selecting a settlement contract.
- **OpenTelemetry NodeSDK lifecycle:** [PR #32](https://github.com/teamleaderleo/fieldwork/pull/32) and owned-fork PRs [#2](https://github.com/teamleaderleo/opentelemetry-js/pull/2)/[#3](https://github.com/teamleaderleo/opentelemetry-js/pull/3). Execute package tests before choosing between the instance guard and broader startup transaction work.

## Queue policy

- No new campaign moves ahead of RQ-001 through RQ-004 without an explicit coordinator decision or materially higher-risk evidence.
- A reviewer should own one queue card at a time.
- Every completed review must leave a durable disposition on the relevant issue or pull request.
- Implementation work must not outrun its evidence gate.
- Upstream contact remains unauthorized unless the queue card explicitly reaches **Authorize contact** and the user or coordinator approves that exact interaction.
- When live issue state conflicts with this snapshot, the live issue wins and this queue should be amended.
