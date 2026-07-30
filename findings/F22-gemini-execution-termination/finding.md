# F22-gemini-execution-termination: Keep cancellation ownership until termination settles

Finding state: `comparative-evaluation-active`

Workstream: `E — agents and CLIs`  
Canonical Fieldwork issue: `#22`  
Canonical finding path: `findings/F22-gemini-execution-termination/finding.md`  
Canonical implementation: `none; current source candidate still needs materialization`  
Exact implementation head: `none`  
Exact base or source revision: `teamleaderleo/gemini-cli@3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`  
Strongest evidence class: `target-executed` fixed-input contract plus `source-read` API comparison  
Current review disposition: `REPAIR and EXECUTE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Gemini CLI keeps a promise for each running command. Today, asking the lifecycle service to stop an externally owned command immediately resolves that promise, reports exit code `130`, emits exit, and forgets the command even when the external stop operation is still running.

The selected contract keeps two answers distinct:

- **termination receipt** — whether the stop request reached a known terminal outcome, failed, or became uncertain;
- **execution result** — the command's authoritative final output and real exit details.

`kill()` stays a synchronous request method and returns one reusable, non-rejecting termination receipt. Existing callers may ignore the return value. Callers that need certainty can observe it. Repeated kill requests receive the same receipt while one termination attempt owns the command.

## Why we care

Premature settlement lets the service say a command ended while its process, remote agent, pseudo-terminal, output producer, or cleanup work may continue. During that interval the service has discarded the owner needed to reconcile a natural exit, kill rejection, timeout, late output, or process-tree escalation.

The consequence is an authority and recovery gap: user-visible completion, process reality, output retention, and cleanup can disagree.

## What happens if we leave it alone

At the pinned source revision, `ExecutionLifecycleService.kill()` invokes the registered hook and immediately calls `completeWithResult(createAbortedResult(...))`.

A pending asynchronous hook therefore coexists with all of these published facts:

- `ExecutionHandle.result` has settled as aborted;
- an exit event with synthetic code `130` has been emitted;
- listeners and active ownership have been removed;
- `isActive()` can report false;
- later real exit details have no service-owned generation to update.

The executed fixed-input control reproduced that ordering. It does not yet establish whether a real operating-system descendant survives.

## Governing invariant

One execution owns one terminal lineage.

A cancellation request may begin termination, but terminal publication and ownership removal occur only after one of these outcomes:

1. a real natural or signalled exit settles the execution;
2. the registered termination operation confirms completion;
3. bounded escalation confirms completion;
4. the service publishes a typed terminal-unknown outcome while preserving enough identity and evidence for reconciliation.

Real exit details outrank a synthetic cancellation code when they arrive during termination.

## Decision criteria

Ordered criteria:

1. preserve authoritative final output and real exit details;
2. make repeated cancellation idempotent under one owner;
3. expose request failure, timeout, and uncertainty without unhandled promise rejection;
4. preserve existing callers that treat `kill()` as a fire-and-forget request;
5. keep request settlement separate from final execution settlement;
6. avoid a second competing final-result promise;
7. make natural-exit, background, listener, and cleanup races directly testable;
8. support synchronous and asynchronous adapters without broad caller rewrites.

## Options compared

### A — make `kill()` an asynchronous method

Shape:

```ts
kill(executionId): Promise<TerminationOutcome>
```

Advantages:

- direct awaitable operation;
- straightforward repeated-request joining.

Losing reasons:

- current callers can ignore the returned promise, so rejection would become an unhandled background failure unless every path is forced into a non-rejecting result;
- the method name would carry both request and completion semantics without clarifying the separate final execution result;
- callback and event-handler call sites gain implicit asynchronous behavior;
- a promise alone provides no stable receipt identity or metadata for retries and outcome-unknown classification.

This option remains viable only if caller inventory proves every invocation is awaited or deliberately voided and the result type never rejects. Current evidence does not justify that migration.

### B — keep `kill(): void` and use only `ExecutionHandle.result`

Advantages:

- smallest public API change;
- the existing result promise already owns final execution settlement.

Losing reasons:

- a failed or timed-out termination request is not itself a final process result;
- keeping the execution active after request failure gives the caller no observable receipt;
- settling the execution to expose request failure can falsely claim terminality;
- repeated kill requests cannot join or inspect one explicit termination attempt.

The existing result promise remains authoritative for final execution, but it cannot serve as the only termination-request receipt.

### C — selected: synchronous request returning one non-rejecting termination receipt

Shape:

```ts
interface TerminationReceipt {
  executionId: number;
  completion: Promise<TerminationOutcome>;
}

kill(executionId: number): TerminationReceipt | undefined;
```

`completion` resolves to a typed outcome and never rejects:

```ts
type TerminationOutcome =
  | { status: 'terminated'; result: ExecutionResult }
  | { status: 'request_failed'; error: Error }
  | { status: 'outcome_unknown'; error: Error };
```

Why it wins:

- ignored return values preserve existing fire-and-forget callers;
- observing callers gain explicit request certainty without unhandled rejection;
- repeated requests can return the same receipt;
- `ExecutionHandle.result` remains the only authoritative final execution result;
- request failure can remain observable while the execution stays active and retryable;
- timeout can become typed outcome-unknown without inventing a fake exit;
- natural exit can settle both the execution result and the active receipt with real details;
- the receipt gives tests one stable owner for idempotency and cleanup.

## Selected source direction

The first production slice should:

1. widen virtual and external termination hooks from `() => void` to `() => void | Promise<void>`;
2. store one active termination receipt on the managed execution;
3. keep `kill()` synchronous and return that receipt;
4. return the same receipt for repeated requests while termination is pending;
5. keep active execution ownership, listeners, output, and the result resolver until authoritative settlement;
6. let `completeExecution()` or `completeWithResult()` win with real exit details during termination;
7. settle successful hook completion as aborted only when the same execution generation remains active and no real result won;
8. resolve hook rejection as `request_failed`, clear the active attempt, and keep the execution available for another request or natural exit;
9. add a bounded timeout policy in a separate small slice, resolving `outcome_unknown` while retaining reconciliation identity;
10. prevent background completion injection from treating an unconfirmed cancellation request as completed work.

The first slice should avoid widening `ExecutionResult` until the receipt controls establish which uncertainty belongs to request state and which belongs to terminal execution state.

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| current `kill()` publishes abort immediately after invoking the hook | `source-read` | `executionLifecycleService.ts` at `3499c84...` | source ordering only |
| asynchronous hook can remain pending after the service removes ownership | `target-executed` | `teamleaderleo/gemini-cli#4@e33c6715...`, run `30504716033` | fixed-input hook; no real process tree |
| existing `ExecutionHandle.result` already owns final execution settlement | `source-read` | `ExecutionHandle` and active resolver paths at `3499c84...` | caller inventory remains incomplete |
| a `void` request cannot expose nonterminal hook failure without another receipt | `source-read` plus API reasoning | current `kill`, `ExecutionHandle`, and hook types | source candidate still needs execution |
| a returned non-rejecting receipt preserves ignored-return callers | `inferred` from TypeScript/JavaScript call semantics | selected API comparison | exact caller/type gates still required |

## Required discriminating controls

### Focused lifecycle matrix

1. pending asynchronous hook keeps result unresolved and ownership active;
2. repeated kill returns the identical receipt and invokes the hook once;
3. synchronous hook preserves immediate successful cancellation behavior;
4. natural exit during pending termination wins with real code and signal;
5. hook rejection resolves `request_failed`, leaves the result pending, and permits retry;
6. second attempt after request failure can terminate successfully;
7. listener and output state survive until final settlement;
8. backgrounded execution avoids completion injection before confirmed settlement;
9. hook completion after natural exit performs no second publication;
10. reset and cleanup remove receipt ownership.

### Real-process matrix

1. real parent plus descendant termination;
2. natural exit racing cancellation;
3. repeated cancellation;
4. graceful request followed by bounded escalation;
5. timeout or adapter rejection with process still observable;
6. partial output retained through termination;
7. node-pty, child-process, and remote-agent adapters classified separately.

## Historical precedent inside the current design

`ExecutionHandle.result` already separates starting an execution from observing its terminal result. The termination receipt extends the same ownership pattern to cancellation requests while preserving one final result owner.

The important difference is that a termination request can fail or become uncertain while the execution remains alive, so its receipt cannot simply replace or prematurely settle `ExecutionHandle.result`.

## Approaches declined or deferred

- **Immediate synthetic `130`:** rejected because it discards ownership before external settlement.
- **Always await inside every caller:** rejected pending caller inventory and because ignored rejected promises remain hazardous.
- **Use only `isActive()` polling:** rejected because process liveness does not settle output, remote effect, cleanup, or exit identity.
- **Make hook rejection terminal:** rejected because request failure does not prove process termination.
- **Add timeout and escalation in the first source slice:** deferred to keep the initial ownership repair small and executable.
- **Unify local process-tree cancellation with remote-agent certainty:** deferred because adapters have different settlement evidence.

## Edge cases covered by current evidence

| Edge case | Evidence | Result |
| --- | --- | --- |
| asynchronous hook pending | PR #4, run `30504716033` | current source settles too early |
| service ownership after kill request | PR #4 | current source removes it |
| final result before hook release | PR #4 | current source resolves synthetic abort |
| core type compatibility of the evidence fixture | run `30504716033` | passed |

## Edge cases deferred

| Edge case | Next owner |
| --- | --- |
| complete caller inventory | source successor review |
| real parent/descendant termination | source successor integration carrier |
| hook rejection and retry | first source candidate |
| timeout and escalation policy | second bounded source slice |
| remote-agent terminal certainty | adapter-specific finding |
| node-pty platform differences | platform execution matrix |
| restart persistence of unresolved termination | durable execution receipt finding |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/gemini-cli@e33c6715cd289f912574025580cd74e4da9fe5bc` | carrier run `30504716033`; focused async-kill test plus core typecheck | predicted lifecycle assertion failed; typecheck passed | `target-executed` defect contract |
| `teamleaderleo/gemini-cli@3499c84f7b8e70c86600e7cd2c67a7c65a667f5e` | source read | immediate synthetic completion path confirmed | `source-read` |

## Complete-diff and compatibility boundary

This finding changes Fieldwork documentation only. It selects an API direction and creates no Gemini source acceptance.

Source promotion requires:

- current-base renewal;
- caller and hook inventory;
- one clean source-and-tests branch;
- focused controls above;
- core typecheck and repository formatting;
- real-process execution;
- complete diff and independent review;
- temporary carrier cleanup.

## Current disposition and routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `REPAIR and EXECUTE`
- Selected direction: synchronous request plus one non-rejecting termination receipt
- Losing directions: async method as the sole surface; `void` plus execution result only
- Exact next transition: materialize the first source slice and focused lifecycle matrix
- Reopening trigger: caller inventory proves the returned receipt breaks a supported API, or execution shows one promise can safely own request failure and final result without false terminality
- Non-delegable human decision: `none`
- Merge, release, deployment, and public upstream contact: require separate human authority

## Changes to the canonical conclusion

| Date | Change |
| --- | --- |
| 2026-07-31 | Replaced the open three-option API question with a selected non-rejecting termination receipt and explicit losing reasons |

## References

- Fieldwork issues `#22`, `#24`, and `#254`.
- Owned Gemini CLI PR `#4` and closed execution carrier `#5`.
- `DECISIONS.md` and `REVIEWING.md` from composed Fieldwork protocol PR `#283`.
- Public upstream interaction: none.
