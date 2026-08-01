# Upstream pull-request draft — Bind confirmation modification to correlated call

Draft status: `issue first`  
Proposed head: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity` at `b6d8e8bb6160aec16555647d81d46a694e44b58b`  
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
- head: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- commits: one
- relationship: one ahead, zero behind
- files:
  - `packages/core/src/scheduler/confirmation.ts`
  - `packages/core/src/scheduler/confirmation.affinity.repair.test.ts`
  - `packages/core/src/scheduler/confirmation.test.ts`
  - `packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts`
- additions/deletions: 775 / 20
- generated/dependency/workflow files: none

## Tests

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/scheduler.confirmation-affinity.test.ts \
  src/scheduler/confirmation.test.ts

npm run typecheck --workspace @google/gemini-cli-core

npx eslint --max-warnings 0 --no-warn-ignored \
  packages/core/src/scheduler/confirmation.ts \
  packages/core/src/scheduler/confirmation.affinity.repair.test.ts \
  packages/core/src/scheduler/confirmation.test.ts \
  packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts
```

Final run `30692554758`, candidate job `91350078426`, Ubuntu 22.04, Node `v20.19.0`, npm `10.8.2`:

- exact parent and four-file fence passed;
- Prettier and staged pre-commit ESLint passed;
- six focused authority/stale-generation tests passed;
- eight adjacent confirmation tests passed;
- one real scheduler reverse-order test passed;
- posttest core build passed;
- standalone core typecheck passed;
- explicit ESLint across all four changed files passed;
- clean tracked tree passed;
- canonical source publication passed.

Full repository preflight reaches `.github/workflows/pr-size-labeler-batch-run.yml` shellcheck `SC2031`. Baseline-control job `91349770438` checked out exact unchanged base and reproduced the same workflow path and warning. The PR changes no workflow.

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

- The scheduler test controls policy, modifier, and executor.
- macOS, Windows, and a real external editor process are untested.
- Production frequency is unmeasured.
- Eligible independent review remains pending.
- The contribution guide requires an existing issue and maintainer alignment before a public code PR.

## Related work

- Add the authorized public issue after issue-first filing and maintainer direction.
- No equivalent public implementation was found in the 2026-08-01 search; repeat immediately before filing.

---

## Submission checklist

- [x] Branch is a direct child of the inspected public head.
- [x] Diff contains only product source and target-native tests.
- [x] Temporary workflows, publishers, receipts, and Fieldwork files are absent.
- [x] Every changed file was self-reviewed at `b6d8e8bb6160aec16555647d81d46a694e44b58b`.
- [x] Baseline regression reaches the wrong-call assertion.
- [x] Inline/editor/stale-authority controls pass.
- [x] Real two-call reverse-order scheduler control passes.
- [x] Core build and typecheck pass.
- [x] Changed-file formatting and lint pass.
- [x] Clean-tree and exact publication receipt recorded.
- [x] Repository preflight blocker reproduced on unchanged base.
- [ ] Eligible independent review completed.
- [ ] Current duplicate and overlap search repeated.
- [x] Commit title follows Conventional Commits.
- [ ] Current contribution and AI-disclosure policies checked at filing time.
- [ ] Exact authorization to file issue/open public PR recorded.
