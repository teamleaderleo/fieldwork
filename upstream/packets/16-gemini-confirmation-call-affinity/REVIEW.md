# Review — Unit 16 confirmation modification call affinity

## In simple words

The contribution replaces active-call insertion order with exact confirmation ownership and rejects stale modifier output. The final candidate is one clean four-file commit directly on the inspected public base. It includes a real scheduler-level test with two simultaneous approvals resolved in reverse order.

Every candidate-owned gate passed. Repository-wide preflight reaches an unrelated workflow shellcheck warning that the unchanged base reproduces. The remaining promotion gates are eligible independent review, current duplicate search, and explicit issue-filing authority.

## Review subject

- Work class: upstream-fork research and source preparation
- Target repository: `google-gemini/gemini-cli`
- Proposed upstream base: `main` at `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Canonical source branch: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity`
- Exact source head: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- Source relationship: one commit ahead, zero behind
- Clean source PR: `teamleaderleo/gemini-cli#24`
- Final execution: run `30692554758`, candidate job `91350078426`, baseline-control job `91349770438`
- Fieldwork packet branch: `p0/435-unit-16-gemini-confirmation-call-affinity`
- Fieldwork packet PR: `teamleaderleo/fieldwork#443`
- Exact packet head: final branch tip recorded on #435
- Complete source fence: four scheduler source/test files
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [repair receipt](./receipts/2026-08-01-current-main-repair.md)
6. [complete source compare](https://github.com/teamleaderleo/gemini-cli/compare/f47d6c6f7a1308d81f9f57acf7d279f0928c5249...b6d8e8bb6160aec16555647d81d46a694e44b58b)
7. [product source](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/confirmation.ts)
8. [focused authority tests](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/confirmation.affinity.repair.test.ts)
9. [scheduler ordering test](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts)
10. [adjacent confirmation tests](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/confirmation.test.ts)
11. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
12. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Complete-diff self-review

### `confirmation.ts`

- Captures `callId` once from the validating call.
- Requires exact-ID presence and `AwaitingApproval` before modification.
- Passes the exact waiting call to both modifier paths.
- Repeats the lookup after modifier completion and requires object identity.
- Rebuilds from the revalidated waiting call's tool.
- Updates the same call ID.
- Leaves public types, messages, hooks, state APIs, and editor APIs unchanged.
- Distinguishes status loss from generation replacement in error text.

### `confirmation.affinity.repair.test.ts`

- Keeps unrelated call A waiting while target call B owns the response.
- Verifies inline and editor modifier inputs.
- Uses deferred modifiers for deterministic authority-loss timing.
- Covers removal, status loss, same-ID generation replacement, and missing call.
- Requires zero publication on stale authority.

### `scheduler.confirmation-affinity.test.ts`

- Uses real Scheduler, scheduler state manager, and MessageBus.
- Observes two calls simultaneously awaiting approval.
- Delivers call 2's modified response before call 1's.
- Verifies modifier order, original arguments, first-response isolation, final arguments, rebuild inputs, and two executions.
- Uses controlled policy, modifier, and executor.

### `confirmation.test.ts`

- Makes the test state reflect the real `Validating` to `AwaitingApproval` transition.
- Retains eight adjacent confirmation controls.

## Claims requiring judgment

| Claim/design choice | Evidence | Reviewer question |
| --- | --- | --- |
| `firstActiveCall` carries no response authority | exact baseline mismatch | Does any supported contract make first active equal response owner? |
| object identity is a valid generation fence | state transitions replace call objects; replacement control passes | Can one approval generation be reconstructed as a new object legitimately? |
| stale authority should throw | removal/status/replacement controls | Should the scheduler translate this into a distinct cancellation/error result? |
| confirmation helper is the right owner | narrow private diff | Does a guarded state-manager update offer needed atomicity now? |
| scheduler test proves isolation | two simultaneous waits and reverse responses | Are controlled modifier/executor boundaries adequate for this contract? |

## Evidence review

Run `30692554758`, candidate job `91350078426`:

- exact parent and four-file fence: pass
- Prettier: pass
- staged pre-commit ESLint: pass
- 3 files / 15 tests: pass
- posttest core build: pass
- standalone core typecheck: pass
- explicit ESLint across all four changed files: pass
- clean tree: pass
- source publication: pass

Baseline-control job `91349770438` checked out the exact unchanged base and reproduced:

```text
.github/workflows/pr-size-labeler-batch-run.yml
SC2031
```

This confirms the repository-wide preflight lint blocker predates unit 16.

## Known risks

- Object identity is implicit generation tracking.
- External editor effects may occur before stale authority is detected; the candidate blocks publication, not editor-side rollback.
- Stale-authority exceptions may need caller-facing classification.
- The scheduler test controls policy, modifier, and executor.
- Linux-only execution; no real editor process.

## Staleness and overlap

- Public head/base checked: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` on 2026-08-01
- Candidate relationship: one commit ahead, zero behind
- Duplicate/overlap search date: 2026-08-01
- Open replacement found: none in searched issues, PRs, branches, or commits
- Repeat search required immediately before filing

## Source cleanliness

- [x] No Fieldwork file in source diff.
- [x] No workflow or publisher in canonical source.
- [x] No generated residue or dependency churn.
- [x] One commit directly on the inspected base.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Baseline distinguishing assertion ran.
- [x] Inline/editor/stale-authority controls pass.
- [x] Real two-call reverse-order scheduler control passes.
- [x] Core build and typecheck pass.
- [x] Changed-file formatting and lint pass.
- [x] Clean-tree and publication receipt complete.
- [x] Full-preflight failure is independently reproduced on the unchanged base.
- [ ] Eligible independent complete-diff review completed.

## Draft review

- [x] Issue draft stays within observed mechanism and evidence.
- [x] PR draft matches the final four-file diff.
- [x] Target terminology and issue-first route are used.
- [ ] Current issue template and AI-disclosure policy checked at filing time.
- [ ] Explicit public-interaction authority recorded.

## Reviewer disposition

`ISSUE FIRST`

Reviewed source head: `b6d8e8bb6160aec16555647d81d46a694e44b58b`  
Reviewed packet head: final branch tip recorded on #435  
Reason: the repair and candidate-owned validation are complete; target policy calls for issue-first discussion, while independent review and filing authority remain.  
Clearing condition: eligible independent review, current duplicate search, and explicit authority to file the issue.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

Focus on:

1. object identity as the approval-generation discriminator;
2. stale-authority error integration with scheduler cancellation/error handling;
3. scheduler reverse-order test adequacy;
4. whether maintainers would prefer an explicit token or guarded state update;
5. issue-first framing and public disclosure requirements.
