# Upstream pull-request draft — Bind confirmation modification to correlated call

Draft status: `issue first`  
Proposed head: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity` at `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`  
Proposed base: `google-gemini/gemini-cli:main` at or after `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`  
Public interaction authorized: `no`

---

## Summary

- Keep inline and external-editor modification on the tool call identified by the confirmation loop.
- Reject modification output when the call disappears, leaves approval, or enters another approval generation while asynchronous work is pending.
- Add focused stale-authority controls and a real scheduler test with two simultaneous approvals resolved in reverse order.

## Problem

The confirmation loop captures a call ID and waits for a response carrying that approval generation's correlation ID. The baseline modification paths pass `state.firstActiveCall` to the modifier. With multiple active calls, insertion order can select another call's tool and arguments even though the final update targets the captured call ID.

The response, modifier input, invocation rebuild, and argument update need one call and one approval generation as their owner.

## Change

Add a private waiting-call lookup in `confirmation.ts` that:

1. resolves the captured call ID;
2. requires `AwaitingApproval`;
3. passes that exact waiting call to inline/editor modification;
4. repeats the lookup after the asynchronous modifier returns;
5. requires the same waiting-call object before rebuilding and updating arguments.

The revalidated waiting call supplies the tool for invocation rebuild. Stale authority throws before `updateArgs`.

The adjacent confirmation fixture now reflects the real `Validating` to `AwaitingApproval` transition. A scheduler-level test creates two calls, waits until both require approval, sends call 2's modified response before call 1's, and verifies each modifier, rebuild, execution, and final argument set remains call-scoped.

## Exact diff

- base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- commits: one
- files:
  - `packages/core/src/scheduler/confirmation.ts`
  - `packages/core/src/scheduler/confirmation.affinity.repair.test.ts`
  - `packages/core/src/scheduler/confirmation.test.ts`
  - `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts`
- generated/dependency/workflow files: none

## Tests

Focused/current command:

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/scheduler.confirmation-affinity.test.ts \
  src/scheduler/confirmation.test.ts
```

Additional gates:

```text
npm run typecheck --workspace @google/gemini-cli-core
npm run preflight
```

Retained predecessor result at `b359ece8a2bd059aef870a084ab9494eff16fa8f`:

- six focused authority tests passed;
- eight adjacent confirmation tests passed;
- core posttest build and typecheck passed;
- Prettier, staged ESLint, exact fencing, clean tree, and source publication passed.

Current exact-head execution is owned by the immutable-source carrier in the owned fork. Insert its final test count, preflight result, and run link before submission.

## Compatibility

- public API: unchanged
- message/state serialization: unchanged
- existing behavior: response routing, hooks, editor selection, and update publication retained
- platform/runtime: platform-neutral state checks; external editor process behavior unchanged
- performance: two call-map lookups and one object-identity comparison per successful modification
- migration: none
- rollback: one-commit revert

## Alternatives considered

- Explicit approval-generation token: clearer semantics, wider state types/transitions/publication.
- Guarded state-manager update: stronger central compare-and-swap, wider API.
- Initial exact-ID lookup only: insufficient because authority can change during modifier await.
- Insertion-order fallback: repeats the defect.

## Limits

- Current exact-head focused execution and full preflight receipt are pending at this draft revision.
- The scheduler test controls policy, modifier, and executor.
- macOS, Windows, and a real external editor process are untested.
- Production frequency is unmeasured.
- The contribution guide requires an existing issue and maintainer alignment before a public code PR.

## Related work

- Add the authorized public issue after issue-first filing and maintainer direction.
- No equivalent public implementation was found in the 2026-08-01 search; repeat immediately before filing.

---

## Submission checklist

- [x] Branch is a direct child of the inspected current public head.
- [x] Diff contains only product source and target-native tests.
- [x] Temporary workflows, publishers, receipts, and Fieldwork files are absent.
- [x] Every changed file was self-reviewed at `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`.
- [x] Baseline regression reaches the wrong-call assertion.
- [x] Predecessor focused candidate passes inline/editor/stale-authority controls.
- [x] Real two-call reverse-order scheduler control is committed.
- [ ] Real two-call reverse-order scheduler control passes on the proposed head.
- [ ] Core typecheck and `npm run preflight` pass on the proposed head.
- [ ] Clean-tree and exact publication receipt recorded.
- [ ] Current duplicate and overlap search repeated.
- [x] Commit title follows Conventional Commits.
- [ ] Current contribution and AI-disclosure policies checked at filing time.
- [ ] Exact user authorization to file issue/open public PR recorded.
