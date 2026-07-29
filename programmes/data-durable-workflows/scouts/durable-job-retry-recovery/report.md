# Scout report: durable job retry and recovery

## In simple words

Stensibly and Smolrunner both preserve durable work, yet they protect different failure boundaries. Stensibly keeps one run identity across bounded retries and can reconcile its own ledger mutations with operation receipts. Smolrunner records exact request, reservation, attempt, cancellation, and terminal evidence and treats an interrupted executor action as uncertain until the host is observed again. Fin Agent runs one request-scoped streaming loop and persists chat messages, so it has no durable job to recover. Two owned-system campaigns are justified: reconcile Stensibly external runner effects before replacement, and connect Smolrunner execution journals and receipts to the personal-worker attempt lifecycle. Generic convergence work, Fin Agent durability work, and dependency/runtime campaigns should stop.

## Assignment

- Fieldwork issue: #29
- Programme: `data-durable-workflows` (#16)
- Worker: `chatgpt:gpt-5.6-thinking`
- Owned path: `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/`
- Claim scope supported: `interface`
- Retrieval date: 2026-07-29
- Upstream contact authorized: `false`

### Pinned revisions

- Fieldwork: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`
- Stensibly: `teamleaderleo/stensibly@bd16acf3dfe4589628e94f9094b002bc17b5e37c`
- Smolrunner: `teamleaderleo/smolrunner@722bb90ca0833d5118b7e095688a9daa71f3cbd3`
- Fin Agent: `teamleaderleo/fin-agent@844ec26d775b24cc7a8cf7b5e06b358be77a7d69`

The owned repositories are the systems under investigation, so this lane does not apply `testbed:*` labels. No stable target hub has yet been established for either owned-system campaign.

## Shared interruption and retry scenario

The retained zero-dependency model is:

- `artifacts/retry_recovery_scenario.py`

Run:

```text
python3 programmes/data-durable-workflows/scouts/durable-job-retry-recovery/artifacts/retry_recovery_scenario.py
```

Environment used:

```text
Python 3.11
network: disabled
inputs: synthetic
```

The scenario applies the same sequence to each system:

1. Accept one logical job under an exact request identity.
2. Begin one attempt.
3. Commit an effect.
4. Lose the response and process before terminal acknowledgement.
5. Record cancellation.
6. Restart and decide whether retry is safe.

The model checks these invariants:

- retry preserves logical identity;
- changed intent cannot reuse the same identity;
- cancellation does not erase a committed effect;
- uncertain execution requires reconciliation before repetition;
- terminal evidence is replayable.

Observed model dispositions:

| System and boundary | Result after commit, lost response, cancellation, and restart |
|---|---|
| Stensibly local ledger mutation with a recorded receipt | Replay/read the recorded result; do not repeat the mutation. |
| Stensibly local ledger mutation with no receipt | Retry the exact same request and key; the ledger decides whether it was already recorded. |
| Smolrunner executor action recorded as uncertain | Require fresh observation before resume, retry, compensation, or termination. |
| Fin Agent request stream | Outside the durable-job comparison; the request has no durable worker identity or recovery record. |

This is a contract model derived from pinned source. It does not execute the owned applications or prove deployed behaviour.

## Code and state maps

### Stensibly

Evidence label: **Observed in source and tests**

Relevant paths:

- `src/runs-core.ts`
- `src/runs.ts`
- `src/runner-contracts.ts`
- `src/operation-receipt-contracts.ts`
- `test/runs.test.ts`
- `test/operation-receipts.test.ts`

#### Logical identity

A work item owns at most one live run. The run has a stable `id` and `itemId`; optional `externalRunId` links another executor. Retry requeues the same run instead of creating a fresh logical run. `retryAttempt` counts failed attempts, while `leaseGeneration` fences renewed ownership. Run creation and commands accept idempotency keys and reject reuse with different request semantics.

This is a strong logical-job identity. Attempt identity exists as the tuple of run ID, retry attempt, run generation, and lease generation. It is distributed across fields instead of exported as one explicit attempt ID.

#### Retries

Failure increments `retryAttempt`, computes a bounded `nextRetryAt`, and releases the lease. The `retry` transition is allowed only after the delay and while the budget remains. It requeues the same run and advances lease generation. Tests cover delayed eligibility, budget exhaustion, exact replay, and replacement after the terminal run releases the item.

The retry scheduler knows whether the runner reported failure. It does not by itself establish whether an external side effect completed before a response or heartbeat disappeared.

#### Checkpoints

Heartbeats and transitions can replace one durable free-form `checkpoint` string. Heartbeat replay is idempotent, and changed checkpoint content under the same key conflicts. The checkpoint is useful for continuation and operator context.

The checkpoint has no typed cursor, effect identity, or declared resume contract. Automatic resumption from the string would therefore be an application assumption.

#### Cancellation

Cancellation is a terminal run transition available from queued, active, blocked, and retryable failed states. Generation fencing prevents stale cancellation from overwriting a newer terminal result. A supervisor can cancel without holding the execution lease, which is appropriate for control-plane authority.

Cancellation records intent and terminal run state. It cannot undo an external effect that already committed.

#### Recovery

Expired active leases reconcile exactly once to `abandoned`, clear the lease, and retain an explicit reason. Reopening the SQLite store preserves this recovery result. Once the run is terminal, the item can receive a replacement run.

`abandoned` is honest about lost runner liveness. Before replacement, an external system may still require read-back through `externalRunId` or another operation handle.

#### Reconciliation

Stensibly operation receipts cover item, event, and artifact ledger mutations. A recorded receipt says `do_not_retry` and directs the caller to read the item. An unknown receipt says to retry the same request with the same key. Receipt tests also enforce project scope and omit mutation payloads.

This closes the commit-before-response ambiguity for covered Stensibly ledger writes. It does not cover every side effect produced by a generic runner.

#### Observability

Runs expose status, run and lease generations, lease owner and expiry, heartbeat time, checkpoint, outcome, continuation reference, retry attempt and budget, next retry time, usage, and lifecycle events. Execution records bind terminal actuals to run and lease generations. Operation receipts expose a bounded reconciliation decision.

The missing observable correlation is one exported identifier connecting a logical work item, every run attempt, an external operation, and its terminal receipt.

### Smolrunner

Evidence label: **Observed in source, tests, and accepted repository decisions**

Relevant paths:

- `src/personal_worker_queue.rs`
- `src/personal_worker_store.rs`
- `src/personal_worker_store_transaction.rs`
- `src/personal_worker_submit_command.rs`
- `src/personal_worker_cancel_command.rs`
- `src/personal_worker_read_model.rs`
- `tests/personal_worker_terminal_replay.rs`
- `docs/PERSONAL_WORKER_ALPHA.md`
- `docs/adr/0014-durable-execution-journal-checkpoints.md`
- `docs/EXECUTION_RECEIPTS.md`

#### Logical identity

A personal-worker request binds `ExecutionRequestId`, verification profile, runner profile, immutable repository, commit, tree, resource limits, cache identity, submission time, and cancellation state. Reservation ID and generation identify admitted capacity. Store revision and queue generation fence writers.

Exact duplicate submissions return a duplicate receipt without advancing durable state. Reusing a request ID with changed semantics conflicts. Retained terminal tombstones prevent accidental recreation under the same request identity.

The alpha contract also calls for immutable attempt and receipt identities. The personal-worker store currently carries request, admission, reservation, and terminal evidence; the complete live attempt-to-execution-receipt connection remains a later slice.

#### Retries

The operator loop is deliberately `run-once`: one accepted action, fresh observation, one durable result or continuation. It does not hide an unbounded polling or retry loop. Verification profiles may permit bounded lower-concurrency retry, normally none.

At the executor layer, an interrupted `executing` action is explicitly uncertain. The accepted journal protocol requires fresh observation of ownership and preconditions before resume, retry, or compensation. This is the stronger rule for side-effecting retries.

#### Checkpoints

The durable execution journal publishes:

1. an all-pending snapshot before the first executor call;
2. `executing` before each action;
3. completed or failed immediately after return;
4. `rollback_in_progress` before inverse or compensation;
5. terminal rollback outcome after return.

A checkpoint publication failure stops execution. A surviving `executing` record means the action may or may not have changed the host.

The personal-worker store separately advances one canonical snapshot through exact revision and queue generation. Staged successor recovery runs before a new mutation.

#### Cancellation

Queued cancellation records one exact cancellation time and replays an identical request as a duplicate. Active cancellation requires exact `draining` admission evidence and validates transition order. Cancellation therefore coordinates admission and cleanup instead of treating a boolean as proof that execution ended.

The current strict CLI sends no draining evidence, so it covers queued cancellation. Active cancellation belongs to the broker/run-once path that can supply exact admission evidence.

#### Recovery

Every typed store mutation calls `recover()` before reading the current snapshot. Stale revisions and generations fail closed. Terminal release atomically removes active work and cache lease and appends a bounded terminal tombstone. Exact terminal replay is a duplicate; conflicting terminal evidence fails closed.

The execution journal keeps uncertain pre-action or rollback state and requires re-observation. This gives Smolrunner the clearest recovery rule in the comparison.

#### Reconciliation

Reconciliation is evidence-driven: observe current ownership and preconditions, then resume, retry, compensate, or terminate. A journal is explanatory evidence and never proof that the host still matches it.

The external execution receipt contract binds an exact execution ID and source digest and can report completion, failure, or `fresh_observation_required`. At the pinned revision, documentation states that live report mapping, receipt persistence, read-back, transport, and scheduling are still absent.

#### Observability

Typed read models expose store revision, queue generation, counts, request source identity, admission state, reservation generation, cache lease, terminal reason, drain acknowledgement, and evidence digest. Public mutation receipts identify applied versus duplicate transitions and their old/new revisions.

The execution receipt is designed for cross-system correlation, yet it is still a document contract. Until live mapping and durable publication land, operators must combine personal-worker state and execution journal evidence manually.

### Fin Agent

Evidence label: **Observed in source**

Relevant paths:

- `app/api/chat/route.ts`
- `hooks/useChat.ts`
- `services/chat-service.ts`
- `README.md`

The backend runs a planner/tool loop entirely inside one HTTP request, keeps conversation history and reasoning trace in memory, then streams the synthesis over SSE. The frontend persists messages to browser local storage after they arrive.

The current application has:

- no durable logical job ID;
- no explicit attempt identity;
- no server-side checkpoint;
- no retry budget or replay record;
- no cancellation token passed to the backend;
- no reconnect cursor;
- no recovery worker;
- no reconciliation API;
- console logs and a client-visible reasoning trace as its main observability.

A disconnected request can leave the user without a final response, while the server invocation and external reads may already have occurred. The integrated financial tools are read-oriented in this revision, so the shared duplicate-side-effect scenario lacks a consequential durable effect. Fin Agent is therefore unsuitable for this scout beyond a negative boundary result.

## Cross-system comparison

| Property | Stensibly | Smolrunner | Fin Agent |
|---|---|---|---|
| Logical job identity | Work item plus stable run ID | Exact execution request plus immutable source | HTTP request and message array only |
| Attempt identity | Retry attempt plus run/lease generations | Reservation and admission generations; planned exact attempt identity | None |
| Duplicate replay | Run commands and ledger operation receipts | Typed mutations and terminal tombstones | None |
| Changed-input conflict | Yes | Yes | None |
| Retry policy | Bounded delayed retry on reported failure | Explicit bounded profile policy; uncertain effects require observation | None |
| Checkpoint | Durable free-form run checkpoint | Durable pre/post executor journal snapshots | In-memory loop state |
| Cancellation | Durable terminal transition | Durable queued cancellation; active drain evidence | UI loading state only |
| Crash recovery | Lease expiry becomes abandoned | Staged snapshot recovery plus uncertain journal state | Fresh request starts over |
| Reconciliation | Operation receipt for covered local mutations | Fresh host observation before retry/compensation | None |
| Observability | Events, generations, retry fields, checkpoint, outcome, receipt | Typed status, revisions, admission, tombstone, journal, planned receipt | Console logs and reasoning metadata |

## Application design findings

### A1. Stensibly external-run ambiguity survives local receipt coverage

**Current behaviour:** local item, event, and artifact mutations can be reconciled by operation receipt. A generic run can also carry `externalRunId`, expire to `abandoned`, and later be replaced.

**Consequence:** a replacement may begin while the external executor already committed an effect whose acknowledgement was lost.

**Owning boundary:** Stensibly runner integration and external operation adapter.

**Evidence needed:** a fault-injection adapter that commits one synthetic external effect, loses acknowledgement, expires the run lease, and attempts replacement. The test passes only when reconciliation prevents a second effect and records one final disposition.

**Recommendation:** open a campaign.

### A2. Smolrunner has strong journal semantics and an incomplete live receipt path

**Current behaviour:** executor journal checkpoints make interrupted effects explicitly uncertain, while the personal-worker store provides exact request and terminal replay. The execution receipt document exists, but live report mapping, persistence, and read-back remain absent.

**Consequence:** another coordinator cannot yet consume one durable receipt that joins personal-worker request, exact attempt, journal, and terminal outcome.

**Owning boundary:** Smolrunner personal-worker broker, durable lane execution, execution receipt adapter, and receipt store.

**Evidence needed:** inject interruption after executor return and before terminal publication; restart; read the same execution ID; prove one terminal receipt or `fresh_observation_required`; prove a second executor call cannot occur without accepted fresh evidence.

**Recommendation:** open a campaign.

### A3. Cross-system correlation vocabulary is useful but premature as a campaign

A reusable envelope should eventually expose:

- `logical_job_id`;
- `attempt_id`;
- `operation_id`;
- `checkpoint_id` or journal revision;
- `cancellation_id`;
- `terminal_receipt_id`;
- final disposition and reconciliation state.

The current comparison reveals translation work, not a demonstrated failure caused by missing common field names.

**Recommendation:** retain as a finding and use it as acceptance criteria inside A1 and A2. Open a separate observability campaign only after a runnable integration loses correlation across a real boundary.

### A4. Fin Agent lacks a durable-job product boundary

Adding a queue, durable checkpoints, cancellation, and reconciliation would be a product redesign. Its current read-oriented, request-scoped flow provides no consequential duplicate-effect reproduction.

**Recommendation:** stop. Revisit only after Fin Agent gains long-running asynchronous analysis, write-capable tools, resumable execution, or an explicit operator requirement.

## Dependency or runtime findings

No observed result establishes a defect in SQLite, Convex, Bun, Rust, Unix filesystem primitives, Lima, Next.js, Vercel, the OpenAI SDK, or the browser SSE APIs.

- Stensibly gaps sit in application-level external operation ownership and reconciliation.
- Smolrunner gaps sit in its own adapter and publication slices; its accepted design already treats filesystem and process uncertainty conservatively.
- Fin Agent gaps come from its request-scoped application design.

**Recommendation:** open no dependency or runtime campaign from this scout. A lower-level campaign requires direct fault injection that violates a documented dependency/runtime contract.

## Ranked branch decisions

1. **Campaign — Stensibly external-run reconciliation before replacement.**
   Highest risk of duplicate or contradictory external effects; bounded synthetic evidence path exists.

2. **Campaign — Smolrunner personal-worker attempt to execution-receipt recovery.**
   Strong existing primitives and an explicit missing integration slice make the next question concrete.

3. **Retain finding — shared durable-job correlation envelope.**
   Carry into both campaigns as acceptance criteria.

4. **Stop — Fin Agent durable-job recovery.**
   No suitable durable job or write effect at the pinned revision.

5. **Stop — generic cross-owned retry framework or shared retry library.**
   The systems own different boundaries; convergence would hide useful differences.

6. **Stop — dependency/runtime attribution.**
   No reproduction crosses an owned application boundary into a violated lower-level contract.

## Negative results and uncertainty

- The first hypothesis that all three named repositories offered comparable durable job paths was false; Fin Agent is request-scoped.
- Stensibly local operation receipts close a narrower ambiguity than generic runner execution. This scout did not implement or execute an external runner adapter.
- Smolrunner documents strong execution-journal recovery, while the personal-worker alpha remains incomplete. This scout did not run Linux or Lima fault injection.
- The synthetic model establishes decision differences, not deployed production consequences.
- No private data, credentials, paid calls, production systems, or upstream interactions were used.

## Handoff

- Strongest supported finding: durable retry safety depends on preserving logical identity and retaining enough evidence to distinguish recorded result, exact replay, and uncertain execution. Stensibly and Smolrunner each implement a strong subset at different boundaries.
- Durable artifacts:
  - `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/report.md`
  - `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/artifacts/retry_recovery_scenario.py`
  - `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/artifacts/latest.json`
- Failed hypothesis: Fin Agent supplies a durable background-job test surface.
- Dependencies discovered: future campaign A1 depends on a synthetic external runner adapter; A2 depends on Smolrunner live receipt mapping and fault injection.
- Decision needed: programme coordinator may promote A1 and A2 as separate owned-target campaigns.
- Upstream contact remains unauthorized.
