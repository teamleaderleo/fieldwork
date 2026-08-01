# Review — Unit 16 confirmation modification call affinity

## In simple words

The proposed contribution replaces active-call insertion order with exact confirmation ownership and rejects stale modifier output. The current three-file candidate has strong focused evidence and a clean publication. A final reviewer should challenge the object-identity generation fence and demand the real two-call out-of-order scheduler control before promotion.

## Review subject

- Work class: upstream-fork research and source preparation
- Target repository: `google-gemini/gemini-cli`
- Proposed upstream base: current `main`; latest inspected `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Canonical source branch: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity`
- Exact source head: `b359ece8a2bd059aef870a084ab9494eff16fa8f`
- Exact source base: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- Fieldwork packet branch: `p0/435-unit-16-gemini-confirmation-call-affinity`
- Exact packet head: final branch tip recorded on #435 after packet completion
- Complete changed-file fence: `confirmation.ts`, `confirmation.affinity.repair.test.ts`, `confirmation.test.ts`
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [complete source compare](https://github.com/teamleaderleo/gemini-cli/compare/3499c84f7b8e70c86600e7cd2c67a7c65a667f5e...b359ece8a2bd059aef870a084ab9494eff16fa8f)
6. [product file](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.ts)
7. [focused tests](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.affinity.repair.test.ts)
8. [adjacent tests](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.test.ts)
9. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
10. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: [`3499c84...b359ece`](https://github.com/teamleaderleo/gemini-cli/compare/3499c84f7b8e70c86600e7cd2c67a7c65a667f5e...b359ece8a2bd059aef870a084ab9494eff16fa8f)
- production file: [`confirmation.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.ts)
- focused tests: [`confirmation.affinity.repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.affinity.repair.test.ts)
- adjacent tests: [`confirmation.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.test.ts)
- generated or dependency files: none

## Complete-diff self-review findings

### `confirmation.ts`

- `callId` remains captured once from the validating call.
- `getWaitingCallForModification` requires presence and `AwaitingApproval`.
- Both editor and inline paths pass the exact waiting call to their modifier.
- Both paths repeat the check after the modifier await and require object identity.
- Invocation rebuild uses the revalidated waiting call's tool.
- `updateArgs` uses the same call ID.
- No public types, bus messages, scheduler state methods, hooks, or editor APIs changed.
- Error text names the call ID and distinguishes status loss from generation replacement.

### `confirmation.affinity.repair.test.ts`

- Harness keeps unrelated `call-a` waiting while target `call-b` transitions through approval.
- State lookup is ID-aware.
- Status transition creates a new waiting object with the generated correlation ID.
- Inline and editor selection assertions inspect the modifier's actual call argument.
- Deferred modifier promises provide deterministic pre/post-await race points.
- Removal, status loss, and generation replacement require zero state update.
- The suite still lacks a real scheduler instance with two simultaneous loops.

### `confirmation.test.ts`

- Fixture change makes `getToolCall` reflect `updateStatus(AwaitingApproval)`.
- The change repairs an impossible mock state exposed by the candidate's legitimate re-read.
- Eight adjacent tests passed with this fixture.
- Review should ensure the fixture change stays minimal after current-main rebase.

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| `firstActiveCall` is the wrong authority source | baseline target-native mismatch plus public current source | Can any supported scheduler contract guarantee first active equals response owner? |
| object identity is a valid generation fence | state manager replaces the call object on transitions; replacement test passes | Are same-generation waiting calls ever reconstructed benignly? |
| errors should reject stale modification | removal/status/replacement tests | Should the caller convert these errors into cancellation or a specific user-facing result? |
| private confirmation helper is the right boundary | narrow diff and no API change | Would a state-manager guarded update provide needed atomicity now? |
| current test filename should remain separate | six concentrated controls | Would maintainers prefer these cases in `confirmation.test.ts`? |

## Known risks

- Current source base is five public commits behind; adjacent scheduler changes may affect integration even without direct file overlap.
- Object identity is implicit generation tracking.
- The post-await read and synchronous `updateArgs` are separate operations; JavaScript's run-to-completion prevents an ordinary interleave between them today, but future asynchronous state hooks could alter that.
- External editor work may have effects before stale authority is detected; the candidate prevents publication, not editor-side rollback.
- Throwing on stale authority may need caller-facing error classification.

## Evidence limits

- Linux-only retained run.
- No full preflight.
- No dual-loop scheduler test.
- No real editor process.
- No production prevalence measurement.
- Self-review only.

## Staleness check

- Current upstream head checked: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` on 2026-08-01
- Candidate base relationship: public head is five commits ahead
- Relevant source paths changed upstream since execution: candidate's three files `no`; adjacent `scheduler.ts` and `scheduler.test.ts` `yes`
- Duplicate/overlap search date: 2026-08-01
- Open replacement work found: none in searched issues, PRs, or commits
- Packet and target PR descriptions synchronized: packet is current; PR #6 requires a final comment with this disposition and exact clean head

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in canonical source head.
- [x] No stale execution artifacts.
- [x] No unrelated generated or dependency churn.
- [x] Required snapshots or lock changes are not applicable.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Intended baseline and candidate assertions actually ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Represented failure paths are covered.
- [x] Adjacent compatibility controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Real two-call scheduler ordering control passes.
- [ ] Full preflight passes on current-main rebased head.

## Draft review

- [x] Issue draft avoids impact/prevalence claims beyond evidence.
- [x] PR draft describes the actual three-file diff.
- [x] Target terminology and issue-first contribution flow are used.
- [x] Internal process vocabulary and private links are absent from the public-facing body sections.
- [ ] AI disclosure requirement is checked again at filing time.
- [ ] Explicit public-interaction authority is recorded.

## Reviewer disposition

`REPAIR`

Reviewed source head: `b359ece8a2bd059aef870a084ab9494eff16fa8f`  
Reviewed packet head: final branch tip on #435  
Reason: The mechanism, candidate, and exact execution are credible and clean, while current-main rebase, real parallel scheduler ordering, full preflight, and independent review remain promotion gates.  
Clearing condition: one immutable rebased head passes the dual-call out-of-order test and full target gates, followed by independent complete-diff review.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether object identity is the appropriate approval-generation discriminator;
2. whether stale-authority errors integrate cleanly with scheduler cancellation/error handling;
3. whether the real dual-call out-of-order test exercises both inline and editor paths at the right level;
4. whether issue-first discussion should propose an explicit token or present the narrow implementation first.

Suggested response:

`Unit 16 looks ready for upstream preparation`  
—or—  
`Unit 16 concern: <specific source, test, compatibility, or framing issue>`
