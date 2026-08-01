# Upstream pull-request draft — Bind confirmation modification to the correlated call

Draft status: `issue first`  
Proposed head: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity` after current-main rebase and final gates  
Proposed base: `google-gemini/gemini-cli:main`; latest inspected head `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`  
Public interaction authorized: `no`

---

## Summary

- Keep inline and external-editor modification on the tool call identified by the confirmation loop.
- Reject modification output when the call disappears, leaves approval, or enters another approval generation while asynchronous work is pending.
- Add focused affinity and stale-authority controls while preserving adjacent confirmation behavior.

## Problem

The confirmation loop captures a call ID and waits for a response carrying that approval generation's correlation ID. The modification paths then pass `state.firstActiveCall` to the modifier. With multiple active calls, insertion order can select another call's tool and arguments even though the final update targets the captured call ID.

The governing rule is that response, modifier input, invocation rebuild, and argument update remain owned by one call and one approval generation.

## Change

Add a private waiting-call lookup in `confirmation.ts` that:

1. resolves the captured call ID;
2. requires `AwaitingApproval`;
3. passes that exact waiting call to inline/editor modification;
4. repeats the lookup after the asynchronous modifier returns;
5. requires the same waiting-call object before rebuilding and updating arguments.

The current waiting call supplies the tool for invocation rebuild. Stale authority throws before `updateArgs`.

The adjacent confirmation fixture now reflects the real `Validating` to `AwaitingApproval` transition so the focused and existing tests exercise compatible state.

## Tests

- `npm run test --workspace @google/gemini-cli-core -- src/scheduler/confirmation.affinity.repair.test.ts src/scheduler/confirmation.test.ts`
- `npm run typecheck --workspace @google/gemini-cli-core`
- core posttest build
- Prettier and pre-commit ESLint on the three changed files
- exact parent/three-file fence, `git diff --check`, and clean tracked tree
- before submission: add the real two-call out-of-order scheduler control and run `npm run preflight` on the rebased head

Current retained result on source head `b359ece8a2bd059aef870a084ab9494eff16fa8f`: 14/14 tests passed with core build and typecheck.

## Compatibility

- public API: unchanged
- existing behavior retained: approval response routing, editor selection, hooks, update publication, and confirmation-loop behavior
- platform or runtime notes: platform-neutral state checks; external editor process behavior unchanged
- performance or allocation notes: two call-map lookups and one object-identity comparison per successful modification
- migration or rollback: no migration; one-commit revert

## Alternatives considered

- Explicit approval-generation token: clearer semantics but widens state types, transitions, and serialization.
- Guarded state-manager update: stronger central compare-and-swap boundary but introduces a broader API before another caller requires it.
- Initial exact-ID lookup only: insufficient because authority can change during the modifier await.

## Limits

- The retained clean head is based on `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`; rebase and rerun are required.
- The focused harness models another waiting call and stale generations but does not run two real simultaneous confirmation loops.
- Full preflight and platform matrix remain.
- The target contribution guide requires an existing issue and maintainer alignment before a code PR.

## Related work

- Public issue link: add after authorized issue-first filing and maintainer direction.
- No equivalent public implementation was found in the 2026-08-01 search.

---

## Submission checklist

- [ ] Branch is a direct child or clean rebase of a recent upstream head.
- [x] Diff contains only product source and target-native tests.
- [x] Temporary workflows, publishers, receipts, and evidence-only files are absent from the clean source branch.
- [x] Every changed file was self-reviewed at `b359ece8a2bd059aef870a084ab9494eff16fa8f`.
- [x] Focused regression fails on baseline and passes on the current candidate.
- [ ] Real two-call out-of-order scheduler control passes.
- [ ] `npm run preflight` passes on the proposed head.
- [ ] Current duplicate and overlap search is repeated.
- [x] Commit title follows Conventional Commits.
- [ ] Current target contribution and AI-disclosure policies are checked at filing time.
- [ ] Exact user authorization to open the pull request is recorded.
