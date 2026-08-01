# Deep dive — Unit 16 confirmation modification call affinity

## In simple words

The confirmation loop owns one `callId` and creates a correlation ID for each approval generation. The baseline waits for the matching response, then gives modification authority to `state.firstActiveCall`. With two active calls, insertion order can select a different call. The modifier reads that other call's arguments and tool while the final write still targets the response-owned call ID.

The repaired implementation resolves the exact call ID, requires `AwaitingApproval`, passes that waiting call to the modifier, then repeats the lookup after asynchronous modification. The second check requires the same waiting object, rejecting a new approval generation under the same call ID. A real scheduler test drives two simultaneous approval waits and sends the responses in reverse order.

## Governing invariant

> Every confirmation response, modification input, invocation rebuild, and argument update must remain owned by the same call ID and approval generation.

## Exact current identity

- public/fork base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- final source head: `b6d8e8bb6160aec16555647d81d46a694e44b58b`
- clean branch: `teamleaderleo/gemini-cli:fix/scheduler-confirmation-call-affinity`
- clean review PR: `teamleaderleo/gemini-cli#24`
- final run: `30692554758`
- candidate job: `91350078426`
- baseline-control job: `91349770438`

## Current behavior and ownership

- entrypoint: `resolveConfirmation(toolCall, signal, deps)`
- state owner: `SchedulerStateManager`, keyed by `request.callId`
- response owner: the correlation ID created by the confirmation loop for that call
- side effects: hook notification, waiting-state publication, modifier invocation, invocation rebuild, `updateArgs`
- asynchronous boundaries: response wait, external editor resolution, modifier work
- stale-authority possibilities: call removal, status transition, same-ID approval replacement

## Source map

| Area | Exact path and symbol | Responsibility | Evidence |
| --- | --- | --- | --- |
| confirmation loop | [`confirmation.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/confirmation.ts) — `resolveConfirmation` | owns call ID, response routing, and modification dispatch | focused and scheduler tests |
| authority fence | same file — `getWaitingCallForModification` | exact-ID, status, and object-identity checks | [`confirmation.affinity.repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/confirmation.affinity.repair.test.ts) |
| state owner | [`state-manager.ts`](https://github.com/teamleaderleo/gemini-cli/blob/f47d6c6f7a1308d81f9f57acf7d279f0928c5249/packages/core/src/scheduler/state-manager.ts) | stores calls by ID; replaces call objects on transitions; exposes insertion-order `firstActiveCall` | source-read and integration control |
| adjacent behavior | [`confirmation.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/confirmation.test.ts) | ordinary confirmation behavior with a stateful waiting transition | eight passing tests |
| concurrent ordering | [`scheduler.confirmation-affinity.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b6d8e8bb6160aec16555647d81d46a694e44b58b/packages/core/src/scheduler/scheduler.confirmation-affinity.test.ts) | two simultaneous waits and reverse response order through real scheduler/state/bus | one passing integration test |

## Baseline reproduction

At `3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`, the fixture kept `call-a` first in active order while the confirmation loop owned `call-b`. A response using call B's correlation ID led the modifier to receive call A.

Run `30505534210` reached the distinguishing assertion. Core typecheck passed.

## Final candidate execution

Command:

```text
npm run test --workspace @google/gemini-cli-core -- \
  src/scheduler/confirmation.affinity.repair.test.ts \
  src/scheduler/scheduler.confirmation-affinity.test.ts \
  src/scheduler/confirmation.test.ts
```

Run `30692554758` passed:

- 6 focused authority/stale-generation tests
- 8 adjacent confirmation tests
- 1 real scheduler reverse-order test
- posttest core build
- standalone core typecheck
- Prettier and staged pre-commit ESLint
- explicit ESLint across all four changed files
- exact parent and four-file fence
- clean tracked tree
- canonical source publication

## Scheduler reverse-order control

The integration test uses:

- real `Scheduler`;
- real `SchedulerStateManager` through the scheduler;
- real `MessageBus`;
- two requests, `call-1` and `call-2`;
- both calls observed simultaneously in `AwaitingApproval`;
- call 2 modified response before call 1;
- controlled policy, modifier, and executor.

It proves:

1. modifier calls follow response order: call 2, then call 1;
2. each modifier receives its own original arguments;
3. the first response updates only call 2 while call 1 remains waiting;
4. final completed arguments preserve `two-updated` on call 2 and `one-updated` on call 1;
5. both rebuilt invocations and executions remain call-scoped.

## Failure model

Baseline sequence:

1. The loop captures call B's ID and publishes a correlation ID.
2. The listener accepts call B's response.
3. Baseline modification reads insertion-order `firstActiveCall`, which may be call A.
4. The modifier uses call A's arguments/tool while the state write targets call B.

Candidate stale-authority sequence:

1. The candidate resolves call B as the waiting call.
2. Modification begins and awaits editor or inline work.
3. Call B disappears, leaves approval, or becomes a new waiting object.
4. The post-await fence rejects before rebuild and `updateArgs`.

## Established claims

- The baseline wrong-call path reached its exact target-native assertion.
- The final source is one four-file commit directly on the inspected base.
- Inline and editor paths use the response-owned call.
- Removal, status loss, same-ID generation replacement, and missing call prevent publication.
- Two real simultaneous scheduler waits remain isolated under reverse response order.
- Candidate-owned build, typecheck, formatting, lint, fence, clean-tree, and publication gates pass.
- Full repository preflight is blocked by an unchanged workflow shellcheck issue that the exact base reproduces.

## Inferences and limits

- Object identity functions as an approval-generation token because state transitions replace active call objects.
- A future explicit generation token could make the contract clearer.
- Production frequency remains unmeasured.
- macOS, Windows, real editor process behavior, and end-to-end TUI/IDE presentation remain unexecuted.

## Selected implementation

`confirmation.ts` adds a private lookup helper. Before modification it requires an existing waiting call for the exact call ID. After modifier completion it repeats the check and requires the same object. The revalidated call supplies the tool for rebuilding, and the same ID goes to `updateArgs`.

Public APIs, serialized types, message schemas, and state-manager methods remain unchanged.

## Compatibility analysis

- public API: unchanged
- source compatibility: private implementation plus tests
- wire/persistence compatibility: unchanged
- performance: two map lookups and one identity comparison per successful modification
- cancellation/recovery: stale authority rejects before state publication
- generated output: none
- rollback: revert one commit

## Baseline preflight blocker

Candidate preflight completed clean/install/format/build, then `lint:ci` reported `SC2030`/`SC2031` in `.github/workflows/pr-size-labeler-batch-run.yml`. The candidate changes no workflow.

Baseline-control job `91349770438` checked out exact base `f47d6c6f7a1308d81f9f57acf7d279f0928c5249` and reproduced the same workflow path and `SC2031`. This isolates the failure from unit 16.

## Review risks

- Object identity may be stricter than a future explicit token.
- Stale-authority exceptions may need caller-facing classification.
- External editor effects can occur before stale authority is detected; the candidate blocks publication, not editor-side rollback.
- The integration test controls executor and modifier.

## Reversing evidence

Reopen the design if:

- current main introduces an explicit approval-generation token;
- exact-ID lookup selects the wrong lifecycle object in a real scheduler case;
- maintainers define same-ID object replacement as authority-preserving;
- an eligible review identifies a candidate-caused compatibility regression.

## Adjacent work excluded

- global waiting-indicator ownership after abort
- external-editor process/session lifetime
- scheduler cancellation policy
- durable approval receipts across resume
- generic state-manager compare-and-swap APIs
