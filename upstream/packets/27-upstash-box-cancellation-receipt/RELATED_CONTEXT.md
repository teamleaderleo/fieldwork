# Related context — Unit 27 cancellation-request receipt

## In simple words

Several mature APIs separate a caller's cancellation request from the remote operation's terminal result. Upstash's Redis SDK also treats an expected local abort as observer shutdown rather than a remote outcome. These sources support the retained receipt direction and sharpen the TypeScript repair: record which owner aborted the agent stream, keep timeout and cancellation-request errors distinct, preserve the iterator rejection expected by the Box CLI, and publish `detached` for the local reader.

The comparison also exposed an important target boundary. Current Box agent streams attach an `AbortController` to `Run`; command and code streams do not. The candidate may claim local observer shutdown only for observers that actually have an attached controller unless those other stream implementations are deliberately widened and tested.

## Scope and evidence rules

- Retrieval date: `2026-08-01`
- Claim scope: `interface`
- Purpose: explain the already-discovered Box cancellation boundary; these repositories are not new Fieldwork targets in this unit
- Evidence labels: `Documented`, `Observed source`, `Inferred`, and `Unknown`
- Public upstream interaction: none; all sources were read-only

## Target-native context

### Box already has a nonterminal local-observer state

**Observed source** — At `upstash/box@9f7533c645f6b519f612aa977f6f4acf86655db7`, early termination of the agent-stream iterator stores partial output and changes a still-running `Run` to `detached`. The source comment says the run may still be executing server-side.

**Implication** — `detached` is the existing target term for “this reader stopped without authoritative remote completion.” A cancellation-request abort can use that status without adding a new public run state.

**Limit** — This supports local state classification. It does not establish remote cancellation success.

### Box currently loses abort ownership

**Observed source** — Agent run and agent stream create one controller, attach it to `Run`, and use that same controller for the optional timeout. `Run.cancel()` also aborts it. The stream catches every `AbortError`, writes terminal `cancelled`, and throws `BoxError("Stream timed out")`.

**Implication** — The repair must classify the owner before aborting. Examining only the caught error name cannot distinguish timeout from caller-requested observer shutdown.

### Stream types have different local-stop capabilities

**Observed source** — Current agent stream attaches an `AbortController` to its `Run`. Current command and code stream constructors perform fetches without an attached controller.

**Implication** — The retained patch's “abort the current observer” behavior is presently an agent-stream capability, not a general `StreamRun` guarantee. Tests and public wording must name that boundary.

**Unknown** — Whether maintainers want command/code streams to gain equivalent local observer cancellation belongs to a separate decision unless required for API consistency.

### Open CLI work needs iterator rejection

**Observed source** — Open Box PR #82 at head `fce8c8cfc269bc09d07eb991ee39d0433029027e` stores caller intent in `_runCancelled`, calls `run.cancel()`, and relies on the iterator throwing so its catch path renders `Cancelled.` instead of an ordinary error.

**Implication** — Silently ending the iterator would misclassify the command as complete in that consumer. The narrow repair should keep rejection control flow while changing the message from a false timeout to a cancellation-request-specific error and leaving `Run.status` as `detached`.

**Limit** — The PR is open and may change. It is compatibility evidence, not an accepted public contract.

## Same-organization precedent: Upstash Redis subscriptions

Source: `upstash/redis-js@e45fb7848a51d164b6bd2bd8e71fcafcb9034165`, `packages/redis/pkg/commands/subscribe.ts`.

**Observed source**

- Each live subscription owns one `AbortController`.
- `unsubscribe()` aborts that controller and removes the local subscription.
- The request catch suppresses expected `AbortError` and reports other errors to listeners.
- No remote terminal subscription result is fabricated from the local abort.

**Transferable lesson** — Expected local observer teardown should be recognized by its owner and handled separately from transport or server failure.

**Non-transferable limit** — Redis subscription teardown has no Box run-status cache and no separate remote cancellation POST, so it does not answer receipt naming or remote reconciliation.

## Signal-composition precedent: Ky

Source: `sindresorhus/ky@3419113b48e034fdcf8fa6bd3be3da7b3d0d758f`, `source/core/Ky.ts` and `source/utils/timeout.ts`.

**Observed source**

- Ky retains the user-provided abort signal separately from its internal controller.
- It composes them into a managed signal when needed.
- Its timeout owner explicitly rejects with `TimeoutError`; timeout is not inferred solely because a generic abort occurred.

**Transferable lesson** — Preserve cancellation ownership before signals are combined, and let the timeout owner publish timeout semantics.

**Non-transferable limit** — Ky models one HTTP request, not a local observer plus a separately cancellable remote operation.

## Long-running-operation contract: Google APIs

Source: `googleapis/googleapis@3f9c9d72cb20768ca4ac9f12030faaf43b13c231`, `google/longrunning/operations.proto`.

**Documented**

- `CancelOperation` starts asynchronous cancellation.
- Cancellation is best effort and success is not guaranteed.
- Clients must read the operation later to learn whether cancellation succeeded or the operation completed despite the request.
- The cancellation method returns an empty response rather than a terminal operation result.

**Transferable lesson** — Successful request completion can truthfully acknowledge the cancellation operation while leaving the remote outcome unresolved.

**Non-transferable limit** — Box's endpoint response and provider semantics remain undocumented in this packet; the Google contract cannot define Box behavior.

## Cancellation-stage vocabulary: Temporal Go SDK

Source: `temporalio/sdk-go@a1c9f1042a611eb6caf98b684770f228cd21b44d`, `workflow/workflow.go`.

**Documented** — Temporal exposes distinct cancellation modes for abandoning, trying cancellation, waiting until the request is received, and waiting until the operation completes.

**Transferable lesson** — “request initiated,” “request received,” and “operation completed” are separate lifecycle facts. A Box receipt should name only the fact its endpoint response establishes.

**Naming consequence** — The candidate value `requestState: "accepted"` may overstate the evidence if a successful HTTP response means only that the request was sent or received. Keep naming as an explicit API-review question until endpoint semantics are confirmed.

## Selected repair model

### First-owner abort classification

Use a private module-local `WeakMap<AbortController, "cancel-request" | "timeout">` and one helper that:

1. returns without changing the cause when the controller is already aborted;
2. records the first owner;
3. calls `abort()` with the ordinary runtime behavior.

Route both the timeout callback and `Run.requestCancel()` through that helper. The first abort wins deterministically, later calls cannot relabel it, controller replacement naturally gets a fresh map entry, and the map does not retain completed runs.

In the agent-stream `AbortError` branch:

- `cancel-request` — throw a cancellation-request-specific `BoxError`; let `finally` publish partial output and `detached`;
- `timeout` or unknown — preserve the current timeout branch during this unit unless separate evidence justifies changing it.

This avoids depending on cross-runtime propagation of `AbortController.abort(reason)` while still preserving origin.

## Why the main alternatives lose

### Silent iterator completion

It fits local detachment but breaks the open CLI consumer's catch-based cancellation presentation and can lead it to publish ordinary completion.

### Custom abort reason only

`AbortSignal.reason` is useful, but fetch/body-stream rejection behavior for arbitrary reasons varies across runtimes. A private ownership map keeps the normal `AbortError` path and records cause independently.

### Mutable cause field on `Run`

It can work, but it requires reset rules when the controller changes and is easier to leave stale. Controller-keyed ownership matches the actual resource and is garbage-collectable.

### Separate controller families plus `AbortSignal.any()`

This is explicit but wider. It adds composition and compatibility questions when the current defect can be repaired by recording the first owner of the existing controller.

## Required reversing controls

1. Agent stream body read remains pending; cancellation request aborts first; iterator rejects with cancellation-specific prose, status becomes `detached`, partial output is retained, and the cancellation POST may still be pending.
2. Timeout aborts first; iterator retains current timeout error/status behavior.
3. Cancellation and timeout scheduled in each order preserve the first recorded cause.
4. A fresh controller attached after receipt settlement is still aborted by a later legacy `cancel()` without another POST.
5. Two `Run` wrappers with the same remote ID send independent requests, proving per-object single-flight scope.
6. Command/code stream tests document that local observer abort is absent unless that separate capability is implemented.
7. Later authoritative server updates can replace `detached` with their terminal result.

## Findings retained, not promoted

- Completed timeout timers are not visibly cleared in the inspected agent paths. This may retain timers or cause late aborts, but it is not required to prove the cancellation-receipt invariant and needs its own execution before becoming a change claim.
- Command/code stream observer cancellation is asymmetric with agent stream. Record the boundary now; widen only with an explicit target decision and tests.
- Google and Temporal support the lifecycle distinction, but neither proves Box endpoint idempotency, billing behavior, or terminal semantics.
