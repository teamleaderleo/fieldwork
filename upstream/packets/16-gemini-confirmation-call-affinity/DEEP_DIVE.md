# Deep dive — Unit 16 confirmation modification call affinity

## In simple words

The confirmation loop owns one immutable `callId` and creates a correlation ID for each approval generation. Public main still waits for the matching response, then hands modification authority to `state.firstActiveCall`. With two active calls, insertion order can select a different call. The modifier reads that other call's arguments and tool while `updateArgs` writes under the confirmation-owned call ID.

The candidate replaces insertion-order authority with an exact call lookup. It validates that the call is still `AwaitingApproval`, passes that exact waiting call into the modifier, then repeats the lookup after the asynchronous modifier returns. The second check requires the same object, which rejects a new approval generation under the same call ID.

## Governing invariant

> Every confirmation response, modification input, tool rebuild, and argument update must remain owned by the same call ID and approval generation.

## Current behavior

- entrypoint: `resolveConfirmation(toolCall, signal, deps)`
- state owner: `SchedulerStateManager`, keyed by `request.callId`
- caller-visible result: `ResolutionResult` with outcome and last serializable confirmation details
- side effects: hook notification, approval-state publication, modifier invocation, invocation rebuild, `updateArgs`
- cleanup owner: `waitForConfirmation` removes the parent abort listener and aborts the losing wait path in `finally`
- persistence or publication boundary: `SchedulerStateManager.updateStatus` and `updateArgs` publish tool-call snapshots
- relevant ordering: the response wait and modifier/editor work are asynchronous; the call may disappear, leave approval, or enter another approval generation while modification is pending

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| confirmation loop | [`confirmation.ts` at candidate head](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.ts) — `resolveConfirmation` | owns `callId`, approval generation, response routing, and modification dispatch | [focused repair tests](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.affinity.repair.test.ts) |
| authority check | same file — `getWaitingCallForModification` | exact-ID, status, and object-identity fence | focused tests 3–6 |
| state owner | [`state-manager.ts` at tested base](https://github.com/teamleaderleo/gemini-cli/blob/3499c84f7b8e70c86600e7cd2c67a7c65a667f5e/packages/core/src/scheduler/state-manager.ts) | stores active calls by ID; `firstActiveCall` exposes insertion order; `updateStatus` replaces the active call object | [adjacent confirmation tests](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.test.ts) |
| public baseline | [`confirmation.ts` at current public head](https://redirect.github.com/google-gemini/gemini-cli/blob/f47d6c6f7a1308d81f9f57acf7d279f0928c5249/packages/core/src/scheduler/confirmation.ts) | still uses `firstActiveCall` in both modification paths | evidence PR #2 |

## Reproduction or characterization

### Setup

- exact upstream revision: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- environment: Ubuntu 24.04, Node `v22.23.1`, npm `10.9.8`
- fixture: `call-a` first in active order; confirmation loop owns `call-b`; response uses `call-b` correlation ID
- command:

```text
npm run test --workspace @google/gemini-cli-core -- src/scheduler/confirmation.affinity.test.ts
```

### Baseline result

The target-native evidence test reached the distinguishing assertion: the modifier received `call-a` where `call-b` was required. Core typecheck passed in the dedicated evidence workflow.

### Candidate result

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/confirmation.test.ts
```

Run `30595253180` passed two files and 14 tests: six focused authority controls and eight adjacent controls. Posttest core build and core typecheck also passed.

## Failure model

Confirmed sequence:

1. `resolveConfirmation` captures `call-b`'s ID and publishes an approval generation with a new correlation ID.
2. The response listener accepts only that correlation ID.
3. Baseline modification calls `state.firstActiveCall`, which may be `call-a`.
4. The modifier receives `call-a`'s arguments/tool, while the subsequent write targets `call-b`.

Candidate hostile sequence:

1. The candidate resolves `call-b` as the waiting call.
2. Modification begins and awaits editor or inline processing.
3. `call-b` is removed, leaves approval, or is replaced by a new waiting object.
4. The post-await fence rejects before rebuild and `updateArgs`.

## Consequence and claim boundary

### Established

- The baseline authority mismatch exists in target-native execution for the inline path.
- Public current main retains the same `firstActiveCall` behavior in both inline and editor paths.
- The candidate selects the exact call for both paths and fails closed for represented stale-authority cases.
- The three candidate files passed focused/adjacent tests, formatting, pre-commit lint, core build, typecheck, and diff hygiene.

### Inferred

- The editor path carries the same baseline defect because it uses the same insertion-order lookup. Candidate execution directly covers the repaired editor path.
- Object identity is a practical approval-generation token because `updateStatus(AwaitingApproval)` replaces the active call object.

### Unknown or unmeasured

- Production frequency and user impact.
- Behavior through a real scheduler with two simultaneous approval loops and out-of-order responses.
- Compatibility after rebasing onto current public main.
- Full-repository preflight and platform matrix.

## Selected implementation

`confirmation.ts` owns the invariant because it already owns the call ID, correlation ID, response wait, modifier dispatch, and final update. The candidate adds one private lookup helper and changes only the two modification paths.

Before modification, the helper requires:

- `state.getToolCall(callId)` returns a call;
- status equals `AwaitingApproval`.

After modification, it repeats those checks and requires the same waiting-call object. The current waiting call supplies the tool used to rebuild the invocation, and the same `callId` is passed to `updateArgs`.

No public API, serialized type, wire message, or state-manager method changes.

## Compatibility analysis

- public API: unchanged
- source compatibility: private implementation and tests only
- binary or wire compatibility: not applicable
- persistence or format compatibility: unchanged
- platform behavior: platform-neutral TypeScript logic; editor launch behavior itself remains unchanged
- performance and allocation: two map lookups and one identity comparison per successful modification
- cancellation, retry, and recovery: stale authority rejects before update; existing confirmation-loop cancellation remains unchanged
- generated output: none
- migration or rollback: single-commit revert

## Adversarial and edge controls

- re-entry: adjacent editor-loop tests remain green
- concurrency: another waiting call exists in the focused harness; a real dual-loop scheduler test remains
- cancellation or interruption: removal/status loss while modifier awaits rejects
- failure before ownership transfer: missing correlated call before modifier rejects
- failure after partial effect: modifier may have external/editor effects before state publication; stale result is withheld
- cleanup failure: outside this unit
- same-key collision: replaced waiting generation under the same call ID rejects by identity
- unrelated-resource isolation: `call-a` remains untouched in focused controls
- platform boundary: external editor implementation is mocked; real editor lifecycle remains outside this unit

## Review risks

- **Identity may be too strict.** The state manager replaces objects on status transitions; a same-ID new object represents changed authority. Rejecting it is the safer behavior. A maintainer could choose an explicit generation token later.
- **Thrown errors may surface harshly.** Existing confirmation loss already throws. Review should confirm scheduler error handling yields acceptable user feedback.
- **Focused harness may mask integration behavior.** The unresolved real two-call out-of-order test directly addresses this.
- **New test filename may feel specialized.** The assertions can be merged into the existing confirmation test file without changing the production design.

## Reversing evidence

Reopen the conclusion if:

- current main removes insertion-order authority or introduces an explicit approval token;
- a real scheduler test shows the exact-ID design targets the wrong lifecycle object;
- maintainers define same-ID object replacement as authority-preserving;
- current-main preflight reveals a compatibility failure tied to this change.

## Adjacent work excluded

- global waiting-indicator ownership after abort
- external-editor process/session lifetime
- scheduler cancellation policy
- durable approval receipts across resume
- generic state-manager compare-and-swap APIs
