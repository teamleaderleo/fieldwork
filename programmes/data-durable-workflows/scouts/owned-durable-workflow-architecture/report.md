# Scout report: owned durable-workflow architecture

## In simple words

The three repositories represent different kinds of work.

- Stensibly is a server-owned responsibility ledger with browser, REST, and MCP clients. It persists work items, authority, events, artifacts, and run state.
- Smolrunner is a local Rust control plane that observes a machine, plans bounded actions, checkpoints durable state, and performs explicitly authorized host or worker operations.
- Fin Agent is a request-scoped chat application. It runs planning and read-oriented financial tool calls inside one HTTP request and saves completed conversation messages in the browser.

The broad maps reveal a useful comparison: after an interruption, which component owns enough durable evidence to decide the next action? Stensibly answers this well for its own ledger writes, leaves an external-runner gap, and keeps rich run state. Smolrunner records stronger pre-effect journal evidence and requires fresh host observation, while its live attempt-to-receipt path remains incomplete. Fin Agent has a request lifecycle instead of a durable worker lifecycle.

Recommended campaigns:

1. Stensibly external-runner reconciliation before replacement.
2. Smolrunner personal-worker attempt, journal, and receipt integration.

Recommended stops:

- Fin Agent durable-job recovery at the current revision;
- a generic shared retry framework;
- dependency, SDK, platform, or runtime attribution without a direct lower-level reproduction.

## Assignment

- Fieldwork issue: #29
- Programme: `data-durable-workflows` (#16)
- Worker: `chatgpt:gpt-5.6-thinking`
- Owned path: `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/`
- Retrieval date: 2026-07-29
- Upstream contact authorized: `false`

### Pinned revisions

- Fieldwork: `teamleaderleo/fieldwork@976b436d4d7e2741dee5505b6715839db9bd4e15`
- Stensibly: `teamleaderleo/stensibly@bd16acf3dfe4589628e94f9094b002bc17b5e37c`
- Smolrunner: `teamleaderleo/smolrunner@722bb90ca0833d5118b7e095688a9daa71f3cbd3`
- Fin Agent: `teamleaderleo/fin-agent@844ec26d775b24cc7a8cf7b5e06b358be77a7d69`

PR #36 and its old handoff are excluded. This report was produced on the corrected owned path from pinned source, tests, repository documentation, and the fresh `authority-after-interruption` experiment.

## Method

Evidence label: **Observed in pinned source, tests, and repository documentation**

The work proceeded in this order:

1. Map each repository broadly.
2. Compare similarities and differences without forcing one common implementation.
3. Select a property exposed by the maps.
4. Build and run a zero-dependency model for that property.
5. Separate owned application findings from dependency, SDK, platform, or runtime findings.
6. Rank campaigns, retained findings, baselines, and stops.

The selected systems cover three distinct work models:

- a shared server ledger and coordination service;
- a local machine and execution steward with durable mutation evidence;
- a request-scoped agent application with browser history.

## System map: Stensibly

### Entry points and user-facing behaviour

Stensibly exposes:

- a browser dashboard and item-detail client;
- REST v1;
- remote Streamable HTTP MCP;
- local stdio MCP;
- a local SQLite server and token administration commands.

Hosted clients call a Cloudflare Worker, which authenticates sessions or bearer tokens and calls Convex through a private service credential. Local mode serves browser, REST, and MCP over SQLite. Humans see a board projection. Machine clients use typed ledger operations.

Relevant paths:

- `README.md`
- `src/app.ts`
- `src/mcp.ts`
- `src/convex-ledger.ts`
- `src/sqlite-ledger.ts`

### Work representation and inputs

The primary work unit is an item inside a workspace and project. Related records include actors, claims, dependencies, reservations, events, artifacts, and work runs. Inputs include project, item identity, actor authority, command, expected generation, expected lease generation, idempotency key, checkpoint, outcome, continuation, and usage.

A run records one executor lifecycle against the item. External code, files, CI, deployments, and private execution remain owned by their original systems; Stensibly stores references and coordination history.

### Control and data flow

```text
human or agent client
→ browser, REST, or MCP operation
→ authentication and project scope
→ ledger read or mutation
→ Convex or SQLite transaction
→ item, event, artifact, or run projection
→ browser, API, MCP, or worker observation
```

Run control:

```text
create run
→ acquire lease
→ start
→ run / wait / block
→ heartbeat and checkpoint
→ succeed / fail / cancel
→ bounded retry or terminal release
```

### State ownership and side effects

The server ledger owns shared coordination truth. Convex owns hosted state. SQLite owns local compatibility state. Clients hold projections and credentials.

Stensibly directly changes ledger records: items, claims, events, artifacts, dependencies, reservations, and runs. Generic runners may change external systems. Fields such as `externalRunId` and artifact references connect those effects to the ledger, while the external system remains authoritative for its own result.

### Persistence and concurrency

Hosted state persists in Convex. Local state persists in SQLite. Transactions retain item and run changes, append lifecycle events, and preserve idempotency records for covered writes.

Concurrency controls include:

- one live run per item;
- expected run generation;
- expected lease generation;
- lease owner and expiry;
- idempotency keys for run creation and commands;
- exact request replay;
- changed-request conflict;
- transactional compare-and-update conditions.

### Logical identity and retries

A work item owns at most one live run. The run keeps a stable `id` and `itemId`; optional `externalRunId` links another executor. Retry requeues the same run. `retryAttempt`, run generation, and lease generation distinguish attempts and ownership changes.

Failure increments `retryAttempt`, computes a bounded `nextRetryAt`, and releases the lease. Retry becomes eligible after the delay and while budget remains. Tests cover delayed retry, exhaustion, exact replay, and replacement after terminal release.

### Checkpoints, cancellation, recovery, and reconciliation

Heartbeats and transitions can replace one durable free-form checkpoint. Exact heartbeat replay is idempotent; changed checkpoint content under the same key conflicts.

Cancellation is a generation-fenced terminal transition. It clears lease and retry state while retaining outcome. Expired active leases reconcile exactly once to `abandoned`, including after SQLite reopen.

Operation receipts cover item, event, and artifact ledger writes. A recorded receipt directs the caller to read the retained result. An unknown receipt directs exact same-request, same-key replay. This closes commit-before-response ambiguity for covered local writes.

The same guarantee does not yet cover every generic runner effect. Lease expiry proves lost Stensibly ownership; it cannot prove the external system stayed unchanged.

### Progress and observability

The dashboard, REST, MCP, deterministic project briefs, events, run rows, and operation receipts expose current work and history. Run evidence includes logical run ID, status, generations, lease owner and expiry, heartbeat time, retry attempt and budget, checkpoint, continuation, outcome, usage, and terminal time.

### Tests

Pinned tests cover:

- exact run creation replay;
- one live run per item;
- lease ownership and generation fencing;
- heartbeat checkpoint replay;
- bounded retry and exhaustion;
- cancellation;
- stale lease reconciliation after database reopen;
- operation receipt lookup for item, event, and artifact writes;
- project-scoped unknown receipt behaviour.

Relevant paths:

- `test/runs.test.ts`
- `test/operation-receipts.test.ts`
- `test/idempotency-scope.test.ts`

## System map: Smolrunner

### Entry points and user-facing behaviour

Smolrunner is a Rust CLI. Current public commands include diagnostics, deterministic planning, host observation and planning, one explicitly confirmed host-preparation phase, and strict personal-worker state, queue, job, and cancellation commands. Human and JSON output derive from typed reports.

The mutation path requires observe, plan, exact confirmation, evidence checks, checkpoint, and execution. The personal-worker alpha uses a bounded `run-once` model: one invocation performs at most one accepted lifecycle or job action, records a result or continuation, and returns.

Relevant paths:

- `README.md`
- `src/main.rs`
- `docs/PERSONAL_WORKER_ALPHA.md`

### Work representation and inputs

Smolrunner represents:

- repository manifests and desired-state plans;
- host-preparation actions with immutable action IDs, execution lanes, rollback classes, and preconditions;
- durable execution journals;
- personal-worker requests binding request ID, immutable repository source, verification profile, runner profile, resource limits, cache identity, priority, deadline, and cancellation state;
- reservations, admission generations, cache leases, and terminal tombstones.

### Control and data flow

Host preparation:

```text
manifest
→ bounded host observation
→ deterministic plan
→ exact confirmation
→ durable all-pending journal
→ pre-action checkpoint
→ typed executor call
→ post-action checkpoint
→ fresh observation barrier or terminal report
```

Personal worker:

```text
exact request
→ revision-checked durable submission
→ queue evaluation
→ reservation and cache lease
→ starting / running / draining admission
→ durable execution evidence
→ terminal release and tombstone
→ read model and operator next action
```

### State ownership and side effects

Smolrunner's local documents own installation, lease, execution-journal, and personal-worker records. Current machine state remains authoritative for host facts and must be observed after uncertainty.

Current mutation can create or adjust reviewed host resources through typed executors. Planned worker activity can manage Lima profiles, runner readiness, workspaces, repository verification commands, approved caches, and terminal results.

### Persistence and concurrency

Smolrunner uses bounded canonical documents, cooperative writer locks, exact revision and generation expectations, staged successor recovery, synchronized atomic publication, retained tombstones, and pre/post executor journal checkpoints.

Concurrency controls include:

- one cooperative writer;
- expected store revision;
- expected queue generation;
- reservation ID and generation;
- bounded active reservations;
- cache lease compatibility;
- exact duplicate mutation detection;
- changed-evidence conflict;
- retained terminal identity;
- no-replace and compare-and-swap publication.

### Logical identity and retries

A personal-worker request binds exact request ID, profiles, immutable source, resources, cache identity, time, and cancellation state. Reservation and admission generations identify accepted capacity. Exact duplicates replay; changed semantics under a reused identity conflict; terminal tombstones prevent recreation.

The operator loop performs one bounded action per invocation. Verification profiles may authorize a bounded retry, normally none. An interrupted `executing` journal record is uncertain and requires fresh observation before resume, retry, or compensation.

### Checkpoints, cancellation, recovery, and reconciliation

The execution journal publishes all-pending state before the first executor call, `executing` before each action, and terminal action state after return. Rollback follows the same pre-call and post-call rule. Checkpoint publication failure stops execution.

Queued cancellation records exact evidence. Active cancellation requires a valid draining transition. Every typed personal-worker mutation calls store recovery before loading current state, checks exact revision and generation, and publishes a valid successor. Terminal release removes active work and cache lease and appends a tombstone; exact terminal replay is a duplicate.

Recovery re-observes ownership and preconditions, then chooses resume, retry, compensation, or termination. The journal explains uncertainty without claiming current host truth.

The execution receipt document can represent completion, failure, or `fresh_observation_required`. Live report mapping, durable receipt publication, exact read-back, and connection to the personal-worker attempt remain incomplete at the pinned revision.

### Progress and observability

Human and JSON reports expose store revision, queue generation, current and desired profile, queue counts, request source identity, admission state, reservation, cache lease, cancellation, terminal reason, acknowledgement, and evidence digest. Execution journals expose pending, executing, failed, completed, rollback, and uncertain states.

### Tests

Pinned tests cover:

- durable personal-worker store and writer contracts;
- queue evaluation and capacity;
- submit, read, and cancel CLI behaviour;
- exact duplicate mutation replay;
- terminal tombstone replay and changed-evidence conflict;
- lock behaviour and staged successor recovery;
- execution checkpoint semantics through fake executors and stores.

Relevant paths:

- `tests/personal_worker_store_contract.rs`
- `tests/personal_worker_store_transaction.rs`
- `tests/personal_worker_terminal_replay.rs`
- `tests/personal_worker_queue_contract.rs`
- `src/lima_lifecycle_executor/tests.rs`

## System map: Fin Agent

### Entry points and user-facing behaviour

Fin Agent is a Next.js chat application. The browser presents chat and transaction analysis. A client hook sends conversation messages to `/api/chat`; the route runs planning, a financial tool, and synthesis; SSE returns reasoning metadata and content. Completed messages are saved to browser local storage.

Relevant paths:

- `README.md`
- `app/api/chat/route.ts`
- `hooks/useChat.ts`
- `services/chat-service.ts`

### Work representation and inputs

The work unit is an in-memory chat request containing a message array. During the request, the backend builds a reasoning trace and planner action. Tool results feed a final synthesis. Inputs are messages and request context. There is no durable server-side job, attempt, reservation, checkpoint, or terminal receipt.

### Control and data flow

```text
browser messages
→ POST /api/chat
→ planner model
→ one selected financial tool
→ external read-oriented API
→ synthesis model stream
→ SSE metadata and content
→ browser state
→ delayed localStorage history save
```

### State ownership and side effects

The browser owns retained chat history. The server request owns transient messages, planner action, tool result, and reasoning trace. External providers own financial data.

At the pinned revision, financial tools are read-oriented. Application persistence consists of browser history. Network calls consume time and provider quota, while the reviewed path lacks a consequential durable write suitable for duplicate-effect testing.

### Persistence and concurrency

The browser debounces message-array saves to local storage. Backend loop state disappears with the request or process. SSE has no durable cursor or server-side replay record.

The client blocks a second submission while `isLoading` is true. The backend handles each HTTP request independently. There is no shared request identity, optimistic version, lease, deduplication record, retry budget, or cross-request serialization.

### Logical identity, retries, checkpoints, cancellation, and recovery

Fin Agent provides no durable logical job, attempt ID, server checkpoint, retry budget, cancellation token, recovery worker, reconciliation API, or terminal read-back. A disconnected request can lose the final response after external reads have occurred. A fresh request begins a new request lifecycle.

### Progress, observability, and tests

Progress appears as streamed reasoning metadata and content. The route emits console logs and returns a reasoning trace and step count. It lacks durable operation correlation and attempt history.

Repository search found no Jest, Vitest, Playwright, Cypress, or comparable application tests at the pinned revision. Source inspection therefore carries more uncertainty than the Stensibly and Smolrunner findings.

## Broad comparison

| Property | Stensibly | Smolrunner | Fin Agent |
|---|---|---|---|
| Product role | Shared responsibility and run ledger | Local machine and execution steward | Request-scoped financial chat |
| Main entry points | Browser, REST, MCP, local server/CLI | Rust CLI and strict worker commands | Browser and `/api/chat` |
| Work unit | Item plus claim, event, artifact, and run | Plan action plus exact worker request and admission | Message array and transient planner action |
| State owner | Convex or SQLite ledger | Durable local documents plus fresh host observation | Browser history and request memory |
| Direct side effects | Ledger writes; external effects referenced | Typed host and execution changes | External reads and browser history |
| Persistence | Convex/SQLite transactions and receipts | Atomic files, revisions, journals, tombstones | localStorage only |
| Concurrency | Versions, leases, generations, idempotency | Writer lock, CAS, generations, reservations, cache leases | Client loading flag |
| Cancellation | Durable terminal run transition | Durable queued cancellation and active drain evidence | No backend cancellation path |
| Progress | Events, heartbeat, checkpoint, continuation | Journal snapshots, run-once result, typed continuation | SSE content and reasoning metadata |
| Observability | Board, API, events, runs, receipts | Human/JSON reports, read models, journals, planned receipts | Console logs and client trace |
| Test depth | Durable run and receipt tests | Extensive state, queue, recovery, and executor tests | No comparable tests found |

## Property selected after the maps

The maps show that durable retry policy is secondary to **authority after interruption**:

- Who owns the accepted work identity?
- Who owns the effect?
- Which durable evidence survived?
- Can cancellation prove effect outcome?
- Does recovery read a receipt, consult another system, observe the machine, or begin again?

That property produces a bounded comparison without assuming one shared architecture.

## Runnable experiment

Artifacts:

- `artifacts/authority_after_interruption.py`
- `artifacts/latest.json`

Run:

```text
python3 programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/authority_after_interruption.py
```

Environment:

```text
Python 3.11
network: disabled
inputs: synthetic profiles derived from pinned source
```

The model evaluates four boundaries:

1. Stensibly local ledger write.
2. Stensibly run coordinating an external effect.
3. Smolrunner durable host execution.
4. Fin Agent request stream.

Observed dispositions:

| Boundary | Durable decision | Branch |
|---|---|---|
| Stensibly local ledger | Read retained result; when unknown, replay exact same request and key. | Baseline |
| Stensibly external runner | Reconcile the external effect owner before retry or replacement. | Campaign |
| Smolrunner host execution | Require fresh observation before resume, retry, compensation, or termination. | Campaign |
| Fin Agent request | Request ended; no durable recovery contract exists. | Stop |

Assertions verify one baseline, two campaign candidates, and one product-boundary stop. The model does not execute the repositories or prove deployed behaviour.

## Application design findings

### A1. Stensibly external-runner reconciliation gap

**Current behaviour:** local ledger writes have operation receipts. A generic run can carry `externalRunId`, expire to `abandoned`, and later release the item for replacement.

**Consequence:** the external executor may have committed an effect before acknowledgement disappeared. A replacement can duplicate or contradict it.

**Owning boundary:** Stensibly runner integration and external operation adapter.

**Campaign evidence:** a synthetic runner commits one external effect, drops acknowledgement, lets the lease expire, and attempts replacement. The campaign passes when read-back produces one final disposition and prevents a second effect.

**Decision:** campaign.

### A2. Smolrunner attempt, journal, and receipt gap

**Current behaviour:** the executor journal records uncertain pre/post effect state. The personal-worker store preserves exact request and terminal replay. The receipt document exists without live mapping, persistence, and read-back.

**Consequence:** a coordinator cannot consume one durable record joining personal-worker request, exact attempt, journal, and terminal outcome.

**Owning boundary:** Smolrunner personal-worker broker, durable execution lane, receipt adapter, and receipt store.

**Campaign evidence:** interrupt after executor return and before terminal publication; restart; read the same execution ID; prove one terminal receipt or `fresh_observation_required`; prevent a second executor call until fresh evidence authorizes it.

**Decision:** campaign.

### A3. Shared correlation envelope

Useful fields include:

- `logical_job_id`;
- `attempt_id`;
- `operation_id`;
- `checkpoint_id` or journal revision;
- `cancellation_id`;
- `terminal_receipt_id`;
- reconciliation disposition.

The maps expose translation needs, while no runnable cross-system loss of correlation has yet occurred.

**Decision:** retain as acceptance criteria in A1 and A2. A separate observability campaign waits for a direct reproduction.

### A4. Fin Agent request boundary

A durable queue, checkpoint, cancellation record, and reconciliation API would redesign the current product. Its read-oriented request path lacks a durable write effect for the experiment.

**Decision:** stop. Revisit after an asynchronous, write-capable, resumable, or operator-owned product requirement appears.

## Dependency, SDK, platform, and runtime findings

The scout found no direct violation of a lower-level contract in SQLite, Convex, Bun, Rust, Unix filesystem primitives, Lima, Next.js, Vercel, the OpenAI SDK, or browser SSE APIs.

- Stensibly findings belong to its external operation adapter and replacement policy.
- Smolrunner findings belong to its live receipt integration.
- Fin Agent findings belong to its request-scoped product design.

**Decision:** open no dependency, SDK, platform, or runtime campaign. A lower-level campaign requires fault injection that reproduces a documented contract failure below the application boundary.

## Ranked decisions

1. **Campaign — Stensibly external-runner reconciliation before replacement.**
2. **Campaign — Smolrunner personal-worker attempt, journal, and receipt integration.**
3. **Baseline — Stensibly local ledger operation receipts.**
4. **Retain — shared correlation envelope inside the two campaigns.**
5. **Stop — Fin Agent durable-job recovery at this revision.**
6. **Stop — generic cross-owned retry framework or shared retry library.**
7. **Stop — dependency, SDK, platform, or runtime attribution.**

## Negative results and uncertainty

- The systems do not share one durable-work architecture.
- Fin Agent supplies a request lifecycle, not a durable worker test surface.
- Retry configuration alone does not decide safe repetition; effect ownership and surviving evidence decide it.
- Stensibly local receipts cover a narrower boundary than generic runner execution.
- Smolrunner has strong accepted recovery semantics and incomplete live receipt integration.
- Fin Agent has thinner test evidence than the other repositories.
- The synthetic model establishes decision differences, not deployed consequences.
- No private data, credentials, paid calls, production systems, or upstream interactions were used.

## Handoff

- Strongest finding: the broad maps separate a server ledger, a local machine steward, and a request-scoped chat application. The fresh experiment shows that safe recovery follows effect ownership and retained evidence: local receipt, external read-back, fresh host observation, or no durable contract.
- Durable artifacts:
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/report.md`
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/authority_after_interruption.py`
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/latest.json`
- Failed hypothesis: all three systems offer comparable durable background-job paths.
- Dependencies: A1 needs a synthetic external runner adapter; A2 needs live receipt mapping, persistence, read-back, and interruption injection.
- Decision needed: promote A1 and A2 as separate owned-system campaigns.
- PR #36 remains closed and excluded.
- Upstream contact remains unauthorized.
