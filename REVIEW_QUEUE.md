# Fieldwork review queue

Snapshot date: **2026-07-30**

GitHub issues remain the canonical live state. This page is a compact review index: it tells a reviewer what claim is being made, which evidence to inspect, which uncertainty must survive review, and which decision closes the card.

## In simple words

Fieldwork has enough active research. The scarce resource is independent review.

The current front of the queue is:

1. **Playwright bounded fixture recovery** — review the executed dependency-safe recovery design and decide the final combined cross-platform gate.
2. **MCP reconnect ownership** — independently verify the strongest executed defect and decide whether upstream contact should be authorized.
3. **Biome safe-fix semantics** — verify the released-package reproduction and decide whether the finding should be promoted.
4. **Codex mutation evidence** — continue from the selected canonical receipt owner into result persistence and compaction gates.
5. **Vite HMR and graph findings** — review the stable-mode candidates separately from the experimental bundled-development case.
6. **Execution-gated work** — run the prepared Vercel AI, Workers SDK, Gemini CLI, T3/OpenCode, and Playwright outcome-model tests before promoting implementation claims.

A reviewer does not need to read the whole portfolio. Take one card, follow its evidence, and return one explicit disposition.

## Reviewer dispositions

Use one of these outcomes:

- **Accept** — the evidence and wording support the conclusion.
- **Revise** — the work is useful, but the claim, scope, test, or presentation needs correction.
- **Execute** — the design is reviewable, but target-native evidence is still required.
- **Hold** — the item is valid but should not advance now.
- **Authorize contact** — the evidence supports the specifically described upstream interaction.
- **Reject or stop** — the premise is disproven, superseded, duplicated, or not consequential enough.

Record:

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

Preserve the evidence class used by the underlying work:

- **Executed target or public-path reproduction** — the relevant implementation or released package ran under retained conditions.
- **Source-confirmed** — pinned code directly supports the mechanism.
- **Probe-reproduced model** — a controlled model demonstrates the mechanism without executing the exact target path.
- **Prepared target test** — the test exists in an owned fork but has no retained execution receipt.
- **Candidate contract** — a desired invariant is proposed; current code is not assumed to promise it.
- **Reported alignment** — public reports agree with the mechanism but are not independent reproduction evidence.

Do not silently upgrade source analysis into execution evidence, a model into a target result, or a prepared test into a failing test.

Research links below are pinned where useful. Live issues and pull requests remain the source for current state.

---

## Priority 0 — human decisions and strongest executed candidates

### RQ-009 — Playwright bounded fixture recovery before `afterAll`

**State:** Ready for independent technical review.  
**Primary issue:** [#141](https://github.com/teamleaderleo/fieldwork/issues/141)  
**Primary record:** [PR #49](https://github.com/teamleaderleo/fieldwork/pull/49)  
**Evidence:** [canonical report](https://github.com/teamleaderleo/fieldwork/blob/8d7ed3a79d40e8b99a170f20fc46663e41d3acfc/programmes/web-tooling-runtime-correctness/scouts/playwright-execution-isolation-artifacts/report.md), [repository-intent review](https://github.com/teamleaderleo/fieldwork/blob/8d7ed3a79d40e8b99a170f20fc46663e41d3acfc/programmes/web-tooling-runtime-correctness/scouts/playwright-execution-isolation-artifacts/fixture-teardown-repository-intent-review-2026-07-30.md), [alignment runs](https://github.com/teamleaderleo/fieldwork/blob/8d7ed3a79d40e8b99a170f20fc46663e41d3acfc/programmes/web-tooling-runtime-correctness/scouts/playwright-execution-isolation-artifacts/fixture-teardown-repository-alignment-run-2026-07-30.md), and owned source PRs [#24](https://github.com/teamleaderleo/playwright/pull/24)/[#26](https://github.com/teamleaderleo/playwright/pull/26).

**Human summary:** A test fixture can lose its cleanup callback when the shared After Hooks slot is exhausted because Playwright skips the body and deletes the fixture record. The campaign rejected one shared fallback slot, equal per-fixture timeout races, and retry placement after `afterAll`. The current design retains only never-started finalizers, budgets by connected dependency group, spends one existing bounded cleanup slot before `afterAll`, reuses the remainder later, and emits an internal receipt before `testEnd`.

**Executed evidence:**

- dependency-group scheduler: eight tests passed on Ubuntu, macOS, and Windows;
- rejected late placement: `afterAll` reused the failed test's still-live fixture;
- corrected placement: eleven tests passed in 22.9 seconds and the repository's existing fresh-`afterAll` fixture regression passed in 4.5 seconds;
- internal receipt refinement: eleven tests passed in 22.8 seconds.

**Review ask:**

1. Verify the skip-and-delete mechanism.
2. Inspect the no-budget, equal-share, dependency-safety, and `afterAll` negative controls.
3. Confirm the corrected source change reuses one budget instead of extending cleanup time.
4. Review `_fixture-cleanup`, its four-state vocabulary, opaque registration id, and pre-`testEnd` timing.
5. Decide **accept**, **revise**, **execute final combined macOS/Windows stack**, or **hold**.
6. Keep expected-failure outcome accounting in RQ-010.

**Uncertainty to preserve:** The scheduler itself has three-platform evidence. The final combined pre-`afterAll` ordering and internal-receipt stack currently has retained Ubuntu evidence. Production frequency and impact magnitude were not measured.

**Done when:** One independent review records a disposition and the final combined cross-platform execution decision.

### RQ-001 — MCP concurrent reconnect retry ownership

**State:** Ready for independent technical review and an upstream-contact decision.  
**Primary record:** [PR #82](https://github.com/teamleaderleo/fieldwork/pull/82)  
**Evidence:** [lane report](https://github.com/teamleaderleo/fieldwork/blob/fbbea68332ecd57e7abad538453ad07d541387b1/campaigns/0004-mcp-streamable-http-reconnect/lanes/L01-concurrent-reconnect-ownership/report.md), [era amendment](https://github.com/teamleaderleo/fieldwork/blob/fbbea68332ecd57e7abad538453ad07d541387b1/campaigns/0004-mcp-streamable-http-reconnect/lanes/L01-concurrent-reconnect-ownership/era-scope-amendment.md), and [owned fork PR](https://github.com/teamleaderleo/typescript-sdk/pull/1).

**Human summary:** Two concurrent Streamable HTTP request streams can receive different SSE `retry` values, but the transport stores retry timing in shared state. A reconnect can therefore use the other stream's later value. The case reproduced in both directions on Node 20, 22, and 24.

**Review ask:** Confirm stream-specific POST/SSE state, directional controls, scope wording, and the held upstream issue. Choose **authorize contact**, **revise**, or **hold**.

**Uncertainty to preserve:** Production impact magnitude and server diversity were not measured.

**Done when:** An independent review and explicit upstream-contact decision are recorded.

### RQ-002 — Biome `useObjectSpread` accessor semantics

**State:** Ready for independent technical review; promotion decision follows.  
**Primary record:** [PR #97](https://github.com/teamleaderleo/fieldwork/pull/97)  
**Evidence:** [report](https://github.com/teamleaderleo/fieldwork/blob/a1ad034eb3500f20d5815ea3d34a1244d0029a59/programmes/web-tooling-runtime-correctness/scouts/biome-safe-fix-runtime-semantics/report.md), [reproduction guide](https://github.com/teamleaderleo/fieldwork/blob/a1ad034eb3500f20d5815ea3d34a1244d0029a59/programmes/web-tooling-runtime-correctness/scouts/biome-safe-fix-runtime-semantics/reproductions/use-object-spread-accessors/README.md), and [released-package run](https://github.com/teamleaderleo/fieldwork/actions/runs/30479636589).

**Human summary:** Biome 2.5.6 labels the transformation safe, but flattening accessor-bearing object literals from `Object.assign` into object spread changes setter invocation, getter timing, and property descriptors. The released package applied the fix and the retained Node 22 run demonstrated the semantic difference.

**Review ask:** Verify the runtime descriptors, safe-fix classification, missing accessor guard, ordinary data-property controls, and current prior art. Choose **accept for promotion**, **revise**, or **hold**.

**Uncertainty to preserve:** The reproduction proves a semantic change, not how common the pattern is.

**Done when:** An independent reviewer records the semantic disposition and promotion decision.

### RQ-003 — Codex direct-result persistence and compaction gates

**State:** Canonical receipt owner selected; next wiring slice is active.  
**Primary record:** [Campaign #83](https://github.com/teamleaderleo/fieldwork/issues/83)  
**Evidence:** [question](https://github.com/teamleaderleo/fieldwork/blob/0c1fa8af2dd1f5ab95ba85b6492c67c5f0f0437f/campaigns/0003-compaction-mutation-identity/question.md), [source map](https://github.com/teamleaderleo/fieldwork/blob/0c1fa8af2dd1f5ab95ba85b6492c67c5f0f0437f/campaigns/0003-compaction-mutation-identity/source-map.md), and [decision](https://github.com/teamleaderleo/fieldwork/blob/0c1fa8af2dd1f5ab95ba85b6492c67c5f0f0437f/campaigns/0003-compaction-mutation-identity/decision.md).

**Human summary:** The earlier branch-selection decision is complete. The accepted foundation now includes raw-history identity validation, a privacy-safe receipt vocabulary, exact effect delegation, and one bounded session-owned receipt lifecycle. The open work is authoritative result persistence, pre-dispatch closure, compaction gates, durable checkpoint carriage, and replay suppression.

**Review ask:**

1. Keep raw identity, terminal state, result persistence, client delivery, and display separate.
2. Verify direct result persistence is recorded only after authoritative append.
3. Require raw-history and receipt gates before compaction request construction and replacement installation.
4. Define safe receipt retirement before relying on the 1,024-entry bound.
5. Execute local, remote v1, and remote v2 ambiguity cases before claiming replay prevention.

**Done when:** Authoritative persistence and all compaction gates have retained tests, and ambiguous mutation evidence fails closed without replay.

---

## Priority 1 — independent review and execution gates

### RQ-004 — Vite plugin invalidation and post-transform graph correctness

**State:** Ready for independent review; treat each candidate separately.  
**Primary record:** [PR #48](https://github.com/teamleaderleo/fieldwork/pull/48)

**Human summary:** A rejected `watchChange` hook can stop Vite-owned invalidation; a post-ordered transform can introduce imports after dev import analysis; and experimental bundled development can observe a file change while skipping the plugin's `hotUpdate` path. The first two are stable-mode candidates. The third remains experimental.

**Review ask:** Review stable-mode cases independently, preserve the experimental qualifier, check browser/runtime consequences, and decide which candidate deserves its own packet.

**Done when:** Each candidate has a separate disposition.

### RQ-010 — Playwright cleanup failure after expected body failure

**State:** Ready for independent result-model review; no implementation selected.  
**Primary issue:** [#142](https://github.com/teamleaderleo/fieldwork/issues/142)  
**Primary record:** [PR #49](https://github.com/teamleaderleo/fieldwork/pull/49)  
**Evidence:** [canonical report](https://github.com/teamleaderleo/fieldwork/blob/8d7ed3a79d40e8b99a170f20fc46663e41d3acfc/programmes/web-tooling-runtime-correctness/scouts/playwright-execution-isolation-artifacts/report.md), owned probe [#28](https://github.com/teamleaderleo/playwright/pull/28), and execution PR [#29](https://github.com/teamleaderleo/playwright/pull/29).

**Human summary:** A test marked with `test.fail()` failed as expected, then its fixture cleanup threw. With one retry configured, only attempt zero ran, no fresh worker appeared, and the nested run reported `1 passed`. Public `status` versus `expectedStatus` accounting absorbed the unrelated cleanup exception.

**Review ask:** Verify the failure independence, trace the smallest internal signal through worker replacement, retry selection, and final outcome, and inspect reporter, serial-suite, and max-failure effects. Keep this separate from RQ-009.

**Uncertainty to preserve:** The negative result is executed. The correct internal representation is still an open design question.

**Done when:** The invariant is accepted or corrected and an implementation owner plus regression matrix is named, or the candidate is explicitly held.

### RQ-005 — Vercel AI terminal outcomes and resumable Stop ownership

**State:** Design review is possible; target-native execution remains the gate.  
**Primary records:** [PR #34](https://github.com/teamleaderleo/fieldwork/pull/34), campaigns [#76](https://github.com/teamleaderleo/fieldwork/issues/76), [#94](https://github.com/teamleaderleo/fieldwork/issues/94), and [#95](https://github.com/teamleaderleo/fieldwork/issues/95).

**Human summary:** Explicit operation abort, silent provider truncation, and application-owned resumable Stop are separate terminal-state problems. The split is sound, but the fork candidates need retained Node and Edge execution and the truncation representation still needs a compatibility matrix.

**Review ask:** Execute the abort and stale-Stop race matrices, run truncation classification cases, and reject any patch that collapses the three questions.

**Done when:** Exact tested heads and a bounded truncation representation decision exist.

### RQ-006 — Workers SDK lifecycle batch

**State:** Active batch; consult live issue #88 and synthesis records before acting.  
**Primary records:** [Batch #88](https://github.com/teamleaderleo/fieldwork/issues/88), [coordination PR #92](https://github.com/teamleaderleo/fieldwork/pull/92).

**Human summary:** The batch covers teardown ownership, configuration selection, partial deployment state, and independent review. Live records have advanced beyond the original dated card, so reviewers should use the batch issue and synthesis PR as canonical.

**Review ask:** Preserve assignment evidence classes, require the cross-review loop, and do not infer live Cloudflare consequences solely from source models.

**Done when:** Every assignment has a bounded outcome and batch synthesis records which candidates advance.

### RQ-007 — Gemini CLI deterministic lifecycle packet

**State:** Source review ready; target tests remain the promotion gate.  
**Primary record:** [PR #45](https://github.com/teamleaderleo/fieldwork/pull/45)

**Human summary:** The packet contains narrow source-confirmed defects, a proposed asynchronous termination-ownership contract, and broader recovery questions. The evidence wording is disciplined, but fork tests need target-native receipts.

**Review ask:** Recheck the source defects, execute waiting-state and call-affinity tests, expand abort to a real process-tree case, and keep proposed contracts labeled as proposals.

**Done when:** Source review is recorded and every promoted defect has an exact target-test receipt.

### RQ-008 — T3/OpenCode completion reconciliation

**State:** Source-supported campaign with a prepared target test.  
**Primary records:** [PR #63](https://github.com/teamleaderleo/fieldwork/pull/63), [Campaign #71](https://github.com/teamleaderleo/fieldwork/issues/71), and [PR #75](https://github.com/teamleaderleo/fieldwork/pull/75).

**Human summary:** T3 restores the OpenCode session identity after restart but not the previous active T3 turn identity. A simple idle-to-ready fallback might repair stale state but could let a delayed old-session event close a newer turn.

**Review ask:** Execute the restart regression, add the delayed-old-idle control, compare thread-scoped reconciliation with durable turn identity, and test interruption with and without later idle.

**Done when:** A target trace confirms or disproves the gap and the selected repair survives event-affinity controls.

---

## Monitored work — not ahead of the queue

- **DuckDB remote publication:** [Campaign #96](https://github.com/teamleaderleo/fieldwork/issues/96). Continue the object-store matrix until reproducible publication-state evidence exists.
- **Supabase auth refresh settlement:** [Campaign #78](https://github.com/teamleaderleo/fieldwork/issues/78), [PR #91](https://github.com/teamleaderleo/fieldwork/pull/91). Complete the real-code two-variant matrix before selecting a settlement contract.
- **OpenTelemetry NodeSDK lifecycle:** [PR #32](https://github.com/teamleaderleo/fieldwork/pull/32). Execute package tests before choosing between the instance guard and broader startup transaction work.

## Queue policy

- A reviewer should own one card at a time.
- Every completed review must leave a durable disposition on the relevant issue or pull request.
- Implementation must not outrun its evidence gate.
- Upstream contact remains unauthorized unless a card reaches **Authorize contact** and the user or coordinator approves that exact interaction.
- When live issue state conflicts with this snapshot, the live issue wins and this queue should be amended.
