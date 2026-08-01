# Deep dive — Unit 16 confirmation modification call affinity

## In simple words

The confirmation loop owns one `callId` and creates a correlation ID for each approval generation. The baseline waits for the matching response, then gives modification authority to `state.firstActiveCall`. With two active calls, insertion order can select a different call. The modifier reads that other call's arguments and tool while the final write still targets the response-owned call ID.

The current-main candidate resolves the exact call ID, requires `AwaitingApproval`, passes that waiting call to the modifier, then repeats the lookup after the asynchronous modifier returns. The second check requires the same waiting object, rejecting a new approval generation under the same call ID. A real scheduler test now drives two simultaneous approval waits and sends the responses in reverse order.

## Governing invariant

> Every confirmation response, modification input, invocation rebuild, and argument update must remain owned by the same call ID and approval generation.

## Exact current identity

- public/fork base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- clean source head: `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`
- clean branch: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity`
- clean review PR: `teamleaderleo/gemini-cli#24`
- source composition PR: merged `teamleaderleo/gemini-cli#23`
- active immutable-source carrier: PR #6, run `30691280000`

## Current behavior

- entrypoint: `resolveConfirmation(toolCall, signal, deps)`
- state owner: `SchedulerStateManager`, keyed by `request.callId`
- response owner: the correlation ID created by the confirmation loop for that call
- side effects: hook notification, waiting-state publication, modifier invocation, invocation rebuild, `updateArgs`
- asynchronous boundaries: response wait, external editor resolution, modifier work
- publication boundary: `SchedulerStateManager.updateStatus` and `updateArgs` publish snapshots
- stale-authority possibilities: call removal, status transition, same-ID approval replacement

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| confirmation loop | [`confirmation.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.ts) — `resolveConfirmation` | owns call ID, approval generation, response routing, and modification dispatch | focused and scheduler tests below |
| authority fence | same file — `getWaitingCallForModification` | exact-ID, status, and object-identity checks | [`confirmation.affinity.repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.affinity.repair.test.ts) |
| state owner | [`state-manager.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f47d6c6f7a1308d81f9f57acf7d279f0928c5249/packages/core/src/scheduler/state-manager.ts) | stores active calls by ID; replaces call objects on transitions; exposes insertion-order `firstActiveCall` | adjacent and scheduler controls |
| adjacent confirmation behavior | [`confirmation.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/confirmation.test.ts) | confirms ordinary loop behavior with a stateful waiting transition | eight adjacent tests |
| concurrent ordering | [`scheduler.confirmation-affinity.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/0c3a86b0555e152b50ca55fd5f8dc53608571cbe/packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts) | drives real scheduler/state/bus with two simultaneous waits and reverse response order | current-main carrier |

## Baseline reproduction

### Setup

- revision: `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- fixture: `call-a` first in active order; confirmation loop owns `call-b`; response uses call B's correlation ID
- command:

```text
npm run test --workspace @google/gemini-cli-core -- src/scheduler/confirmation.affinity.test.ts
```

### Result

Run `30505534210` reached the distinguishing assertion: the modifier received `call-a` where response-correlated `call-b` was required. Core typecheck passed.

## Predecessor candidate evidence

At `b359ece8a2bd059aef870a084ab9494eff16fa8f`:

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/confirmation.test.ts
```

Run `30595253180` passed two files and 14 tests: six focused authority controls and eight adjacent controls. Core posttest build, core typecheck, formatting, staged ESLint, exact three-file fencing, clean tree, and source publication passed.

## Current-main scheduler characterization

The new test uses:

- a real `Scheduler`;
- its real `SchedulerStateManager`;
- a real `MessageBus`;
- two requests, `call-1` and `call-2`;
- both calls observed simultaneously in `AwaitingApproval`;
- response for `call-2` with modified content before response for `call-1`;
- controlled policy, modifier, and executor fakes.

Required result:

1. modifier calls occur in response order: `call-2`, then `call-1`;
2. each modifier receives its own original arguments;
3. the first response updates only `call-2` while `call-1` remains waiting;
4. final completed arguments preserve `two-updated` on call 2 and `one-updated` on call 1;
5. both rebuilt invocations and executions remain call-scoped.

The test is committed at the exact source head. Target execution is owned by run `30691280000`.

## Failure model

Baseline sequence:

1. The loop captures call B's ID and publishes an approval generation with a new correlation ID.
2. The response listener accepts only that correlation ID.
3. Baseline modification reads `state.firstActiveCall`, which may be call A.
4. The modifier uses call A's arguments/tool while the write targets call B.

Candidate stale-authority sequence:

1. The candidate resolves call B as the waiting call.
2. Modification begins and awaits editor or inline work.
3. Call B disappears, leaves approval, or becomes a new waiting object.
4. The post-await fence rejects before rebuild and `updateArgs`.

## Consequence and claim boundary

### Established

- The baseline wrong-call path reached its exact target-native assertion.
- Current public main retained the baseline `firstActiveCall` mechanism when the candidate was rebased.
- The predecessor candidate passed inline, editor, removal, status-loss, generation-replacement, and missing-call controls.
- The current candidate is a one-commit four-file diff directly on current main.
- The real scheduler ordering test exists at the exact candidate head.

### Inferred

- Object identity is a practical approval-generation token because state transitions replace the active call object.
- The private confirmation helper is the narrowest owner because it already owns call ID, correlation, modifier dispatch, and update.

### Pending execution

- Current-main scheduler test result.
- Current-main core typecheck.
- Full `npm run preflight`.
- Final clean-tree and canonical publication receipt.

### Unmeasured

- Production frequency and prevalence.
- macOS and Windows execution.
- Real external-editor process effects before stale authority is detected.
- End-to-end TUI/IDE presentation.

## Selected implementation

`confirmation.ts` adds one private lookup helper. Before modification it requires an existing waiting call for the exact call ID. After modifier completion it repeats that check and requires the same object. The revalidated call supplies the tool for rebuilding, and the same call ID goes to `updateArgs`.

No public API, serialized type, message schema, or state-manager method changes.

## Compatibility analysis

- public API: unchanged
- source compatibility: private implementation plus tests
- binary/wire compatibility: not applicable
- persistence/format compatibility: unchanged
- platform behavior: platform-neutral TypeScript checks
- performance: two map lookups and one identity comparison per successful modification
- cancellation/recovery: stale authority rejects before state publication; existing cancellation path unchanged
- generated output: none
- rollback: revert one commit

## Adversarial controls

- unrelated active call present: focused harness
- two real simultaneous waits: scheduler control
- out-of-order responses: scheduler control
- call removed during inline await: rejects
- call leaves approval during editor await: rejects
- same-ID generation replacement: rejects
- call lost before modifier: rejects
- editor loop re-entry: adjacent tests
- other call isolation: focused and scheduler assertions

## Repair-attempt classification

Run `30690542009` stopped before product execution because the transiently generated scheduler test retained two unused declarations. Prettier passed; pre-commit ESLint failed. The corrected test was committed at `6804d0b87c196b265c42276f2939573edaf6d89c`, then included in source head `0c3a86b0555e152b50ca55fd5f8dc53608571cbe`.

## Review risks

- **Object identity may be stricter than a future explicit token.** Current state transitions replace objects, so replacement currently signals changed authority.
- **Thrown stale-authority errors may need caller classification.** Existing loss paths already throw; reviewer should inspect scheduler error presentation.
- **The integration test controls executor and modifier.** It targets scheduler identity and ordering, not external service behavior.
- **Specialized test filenames may be reorganized.** Test placement can change without changing the contract.

## Reversing evidence

Reopen the design if:

- current main introduces an explicit approval-generation token;
- a real scheduler run shows exact-ID lookup selects the wrong lifecycle object;
- maintainers define same-ID object replacement as authority-preserving;
- current-main preflight exposes a candidate-caused compatibility failure.

## Adjacent work excluded

- global waiting-indicator ownership after abort
- external-editor process/session lifetime
- scheduler cancellation policy
- durable approval receipts across resume
- generic state-manager compare-and-swap APIs
