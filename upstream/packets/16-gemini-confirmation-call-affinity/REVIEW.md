# Review — Unit 16 confirmation modification call affinity

## In simple words

The contribution replaces active-call insertion order with exact confirmation ownership and rejects stale modifier output. The candidate is now one clean four-file commit on current public main and includes the previously missing real scheduler-level two-call reverse-order control.

The final technical gate is executing that exact immutable source through focused tests, core typecheck, full preflight, and clean-tree verification. An eligible reviewer should challenge the object-identity generation fence, stale-authority error handling, and whether the scheduler test proves the intended isolation.

## Review subject

- Work class: upstream-fork research and source preparation
- Target repository: `google-gemini/gemini-cli`
- Proposed upstream base: `main` at `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Canonical source branch: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity`
- Exact source head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- Exact source relationship: one commit ahead, zero behind
- Clean source PR: `teamleaderleo/gemini-cli#24`
- Fieldwork packet branch: `p0/435-unit-16-gemini-confirmation-call-affinity`
- Fieldwork packet PR: `teamleaderleo/fieldwork#443`
- Exact packet head: latest branch tip recorded on #435
- Complete source fence: four scheduler source/test files
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [current-main repair receipt](./receipts/2026-08-01-current-main-repair.md)
6. [complete source compare](https://github.com/teamleaderleo/gemini-cli/compare/f47d6c6f7a1308d81f9f57acf7d279f0928c5249...0c3a86b0555e152b50ca55fd5f8dc53608571cbe)
7. [product source](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.ts)
8. [focused authority tests](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.affinity.repair.test.ts)
9. [real scheduler ordering test](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts)
10. [adjacent confirmation tests](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.test.ts)
11. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
12. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- complete compare: [`f47d6c6...0c3a86b`](https://github.com/teamleaderleo/gemini-cli/compare/f47d6c6f7a1308d81f9f57acf7d279f0928c5249...0c3a86b0555e152b50ca55fd5f8dc53608571cbe)
- source PR: [`#24`](https://github.com/teamleaderleo/gemini-cli/pull/24)
- production: [`confirmation.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.ts)
- focused tests: [`confirmation.affinity.repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.affinity.repair.test.ts)
- scheduler test: [`scheduler.confirmation-affinity.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts)
- adjacent tests: [`confirmation.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.test.ts)
- generated/dependency files: none

## Complete-diff self-review

### `confirmation.ts`

- Captures `callId` once from the validating call.
- `getWaitingCallForModification` requires exact-ID presence and `AwaitingApproval`.
- Inline and editor paths pass the exact waiting call to their modifier.
- Both paths repeat the lookup after modifier completion and require object identity.
- Invocation rebuild uses the revalidated waiting call's tool.
- `updateArgs` uses the same call ID.
- Public types, bus messages, hooks, state-manager methods, and editor APIs remain unchanged.
- Error messages distinguish status loss from generation replacement.

### `confirmation.affinity.repair.test.ts`

- Keeps unrelated call A waiting while target call B transitions through approval.
- Uses ID-aware state lookup.
- Models status transition as a new waiting object with generated correlation ID.
- Verifies inline/editor modifier arguments and rebuilt invocation.
- Uses deferred modifier promises for deterministic pre/post-await races.
- Requires zero publication after removal, status loss, or generation replacement.

### `scheduler.confirmation-affinity.test.ts`

- Uses real Scheduler, state manager, and message bus.
- Waits until both calls are simultaneously awaiting approval.
- Responds to call 2 first, then call 1.
- Verifies modifier order and original call arguments.
- Verifies the first response updates only call 2 while call 1 remains waiting.
- Verifies final completed arguments and both rebuild inputs.
- Controls policy, modifier, and executor; it does not claim external service behavior.

### `confirmation.test.ts`

- Makes `getToolCall` reflect the transition to `AwaitingApproval`.
- Repairs the impossible static mock state exposed by legitimate candidate re-reads.
- Retains eight adjacent behavior controls.

## Claims requiring judgment

| Claim/design choice | Evidence | Reviewer question |
| --- | --- | --- |
| `firstActiveCall` is the wrong authority source | exact baseline mismatch | Can any supported contract guarantee first active equals response owner? |
| object identity is a valid generation fence | state transitions replace objects; replacement test | Are same-generation waiting calls reconstructed benignly anywhere? |
| stale authority should throw | removal/status/replacement controls | Should scheduler convert this into cancellation or a specific user-facing error? |
| confirmation helper is the right owner | narrow private diff | Would a guarded state-manager update provide needed atomicity now? |
| real scheduler test proves isolation | simultaneous waits and reverse responses | Does the test observe enough of state publication and execution ordering? |
| specialized test files are appropriate | focused reviewability | Should maintainers fold cases into existing test files? |

## Known risks

- Object identity is implicit generation tracking.
- Post-await read and synchronous `updateArgs` are separate operations; current JavaScript run-to-completion prevents ordinary interleave, while future asynchronous state hooks could alter that.
- External editor effects may occur before stale authority is detected; candidate blocks publication, not editor-side rollback.
- Throwing stale-authority errors may need caller-facing classification.
- Scheduler integration controls executor/modifier and Linux execution only.

## Evidence limits

- Current exact-head execution and preflight are pending at this revision.
- No real external editor process.
- No macOS/Windows run.
- No production prevalence measurement.
- Self-review only.

## Staleness check

- Public head/base checked: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` on 2026-08-01
- Candidate relationship: one commit ahead, zero behind
- Direct candidate files changed between predecessor base and current base: no
- Adjacent scheduler files changed: yes; now covered by the real scheduler control
- Duplicate/overlap search date: 2026-08-01
- Open replacement work found: none in searched issues, PRs, branches, or commits
- Packet and clean source PR synchronized: yes at source head `0c3a86b`

## Source cleanliness

- [x] No Fieldwork-only file in source diff.
- [x] No workflow or publisher in canonical source.
- [x] No generated residue.
- [x] No unrelated formatting or dependency churn.
- [x] One commit directly on current base.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Baseline distinguishing assertion ran.
- [x] Predecessor focused and adjacent assertions ran.
- [x] Setup and product failures are separated.
- [x] Removal, status loss, generation replacement, and missing-call paths are represented.
- [x] Real two-call scheduler control is committed on the exact source head.
- [ ] Real two-call scheduler control passes on the exact source head.
- [ ] Core typecheck passes on the exact source head.
- [ ] Full preflight passes on the exact source head.
- [ ] Clean-tree/current-branch receipt completes.

## Repair-attempt review

- Run `30690542009`: harness lint failure before product execution; two unused declarations.
- Corrected integration head: `6804d0b87c196b265c42276f2939573edaf6d89c`.
- Fallback carrier #22: closed superseded without product execution.
- Source composition PR #23: merged with one squash result.
- Active carrier: PR #6, current run listed in `TESTS.md` and receipt file.

## Draft review

- [x] Issue draft stays within observed mechanism and evidence.
- [x] PR draft targets the current four-file diff.
- [x] Target terminology and issue-first contribution flow are used.
- [x] Private process vocabulary is separated from public-facing draft bodies.
- [ ] AI disclosure requirement rechecked at filing time.
- [ ] Explicit public-interaction authority recorded.

## Reviewer disposition

`REPAIR`

Reviewed source head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`  
Reviewed packet head: latest branch tip recorded on #435  
Reason: source composition, current-main rebase, and the missing scheduler control are complete; exact-head execution, full preflight, and eligible independent review remain.  
Clearing condition: the immutable-source carrier completes its gates, then an eligible reviewer performs complete-diff review.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

Focus on:

1. object identity as approval-generation discriminator;
2. stale-authority error integration with scheduler cancellation/error handling;
3. scheduler reverse-order test adequacy;
4. issue-first framing versus introducing an explicit token;
5. current exact-head test and preflight receipt.

Suggested response:

`Unit 16 looks ready for upstream preparation`  
—or—  
`Unit 16 concern: <specific source, test, compatibility, or framing issue>`
