# Upstash Box cancellation repair comparison

Decision ID: `F254-UPSTASH-CANCEL-RECEIPT-V1`  
Comparison base: `upstash/box@b55d832d6e3ae0156e32d21ea3863e231dfff9cd`  
Fieldwork characterization: PR #337 at `68622329d7140a7328902cfa108c8215bed9983f`  
Finding state: `comparative-evaluation-active`  
Upstream contact authorized: no

## Bounded question

How should concurrent callers observe one cancellation attempt when the provider request may fail and the actual remote run outcome remains unknown?

The characterization established two independent defects:

1. concurrent callers issue duplicate provider requests;
2. request failure is suppressed and local run status becomes terminal `cancelled` without remote confirmation.

These defects are orthogonal. Treating request sharing and outcome truth as competing alternatives is therefore the wrong decision shape.

## Governing invariant

- one logical cancellation attempt owns at most one provider request;
- provider-request observation and remote run outcome remain distinct facts;
- `Run.status` remains an authoritative run-state field;
- later authoritative completion or cancellation may replace earlier local request observations;
- no untrusted provider error text is retained or published;
- later callers do not silently replay an outcome-unknown request;
- cancelling one caller's wait does not cancel the shared provider request for other callers.

## Stable options

### A — shared request plus terminal status

Share one in-flight operation across callers but retain the current terminal `cancelled` assignment.

Advantage: smallest duplicate-request repair.

Failure: a failed or merely accepted request still becomes a confirmed terminal outcome.

### B — public `cancelling` status plus independent requests

Represent local intent through a new public run status but leave request ownership per caller.

Advantage: avoids the false terminal `cancelled` claim.

Failures:

- duplicate provider requests remain;
- the public authoritative status vocabulary now mixes server state with local request progress;
- existing exhaustive consumers must handle a new status value.

### C — shared immutable cancellation receipt

Share one at-most-once request task and publish an immutable receipt separately from `Run.status`:

```text
request_state: accepted | failed
outcome_state: unknown
fixed diagnostic: absent | cancellation request failed
```

`Run.status` remains unchanged until an authoritative server update arrives.

Advantages:

- fixes duplicate ownership and false terminal state together;
- preserves the existing run-status vocabulary;
- allows later `completed` or `cancelled` observations to remain authoritative;
- gives all concurrent and later callers one stable receipt;
- isolates the shared request from one caller cancelling its own wait;
- does not automatically replay an ambiguous provider request.

Cost: adds a small receipt type/property or changes `cancel()` to return a receipt. Exact target API compatibility remains to be tested.

## Ordered criteria

1. preserve truthful remote-outcome semantics;
2. prevent duplicate provider effects;
3. preserve the existing public run-status contract;
4. retain later authoritative reconciliation;
5. minimize retained untrusted detail;
6. preserve shared-operation settlement when one waiter is cancelled;
7. minimize implementation and generation complexity across TypeScript, async Python, and generated sync Python.

## Executable discriminator

`cancel_repair_comparison.py` and `test_cancel_repair_comparison.py` execute all three options with deterministic concurrent barriers.

Required controls:

- A shares one request but still overclaims terminal cancellation;
- B preserves outcome uncertainty but sends two requests;
- C shares one request and leaves authoritative status unchanged;
- cancelling one C waiter does not cancel the shared request or surviving waiter;
- C publishes fixed failure prose and does not auto-replay;
- accepted request remains outcome-unknown until authoritative cancellation;
- failed request can later reconcile to natural completion;
- the receipt is immutable.

## Selected direction

Select **C — shared immutable cancellation receipt**.

Tiebreak ladder step: `1 — make the objection executable`.

No neutral arbitration or arbitrary selector is needed. The model shows that A and B each repair only one independent invariant, while C composes both repairs and avoids widening `RunStatus`.

## Target materialization contract

A target-native successor should compare the smallest compatible API shapes:

1. `cancel()` returns the shared receipt;
2. `cancel()` remains void/None and exposes `cancel_receipt` after settlement;
3. a separate `request_cancel()` returns the receipt while legacy `cancel()` delegates.

It must cover:

- TypeScript concurrent callers;
- async Python concurrent callers;
- generated sync Python parity;
- accepted, failed, caller-cancelled, and later-authoritative outcomes;
- no automatic replay after outcome-unknown settlement;
- fixed diagnostics without raw provider detail;
- existing consumers that ignore the return value;
- complete target formatting, type, generation, and package gates.

## Reopening triggers

Reopen this selection if exact target source proves:

- the cancel endpoint response is a documented authoritative terminal outcome;
- a public `cancelling` state already exists or is required by another accepted contract;
- returning or storing a receipt breaks supported callers more severely than the status expansion;
- the provider exposes an idempotency key or authoritative reconciliation endpoint that changes request ownership.

No merge, deployment, provider call, account, credential, spending, private data, or public upstream interaction is included.
