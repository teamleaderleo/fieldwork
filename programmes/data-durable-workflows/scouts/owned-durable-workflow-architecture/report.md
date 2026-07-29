# Scout report: owned durable-workflow architecture

## In simple words

This scout compares two owned systems with genuinely durable work:

- Stensibly is a server-owned responsibility ledger with browser, REST, and MCP clients. It persists work items, authority, events, artifacts, operation receipts, and run state.
- Smolrunner is a local Rust control plane that observes a machine, plans bounded actions, checkpoints durable state, and performs explicitly authorized host or worker operations.

The useful question exposed by the maps is: after an interruption, which component owns enough durable evidence to decide the next action?

Stensibly answers this well for its own ledger writes, while generic external-runner effects still need reconciliation before replacement. Smolrunner records strong pre-effect journal evidence and requires fresh machine observation, while its live attempt-to-receipt path remains incomplete.

Recommended campaigns:

1. Stensibly external-runner reconciliation before replacement.
2. Smolrunner personal-worker attempt, journal, and receipt integration.

Recommended stops:

- a generic shared retry framework;
- dependency, SDK, platform, or runtime attribution without a direct lower-level reproduction.

## Assignment

- Fieldwork issue: #29
- Programme: `data-durable-workflows` (#16)
- Worker: `chatgpt:gpt-5.6-thinking`
- Owned path: `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/`
- Retrieval date: 2026-07-29
- Scope narrowed: 2026-07-30
- Upstream contact authorized: `false`

### Pinned revisions

- Fieldwork: `teamleaderleo/fieldwork@976b436d4d7e2741dee5505b6715839db9bd4e15`
- Stensibly: `teamleaderleo/stensibly@bd16acf3dfe4589628e94f9094b002bc17b5e37c`
- Smolrunner: `teamleaderleo/smolrunner@722bb90ca0833d5118b7e095688a9daa71f3cbd3`

PR #36 and its old handoff remain excluded. This report was produced on the corrected owned path from pinned source, tests, repository documentation, and the `authority-after-interruption` experiment.

## Method

Evidence label: **Observed in pinned source, tests, and repository documentation**

The work proceeded in this order:

1. Map each repository across entrypoints, work representation, inputs, control and data flow, state ownership, side effects, persistence, concurrency, cancellation, progress, observability, tests, and user-facing behaviour.
2. Compare similarities and differences without forcing one common implementation.
3. Select a property exposed by the maps.
4. Build and run a zero-dependency model for that property.
5. Separate owned application findings from dependency, SDK, platform, or runtime findings.
6. Rank campaigns, retained findings, baselines, and stops.

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

The primary work unit is an item inside a workspace and project. Related records include actors, claims, dependencies, reservations, events, artifacts, and work runs.

Run inputs include project and item identity, actor authority, command, expected generation, expected lease generation, idempotency key, checkpoint, outcome, continuation, and usage.

A run records one executor lifecycle against an item. External code, files, CI, deployments, and private execution remain owned by their original systems; Stensibly stores references and coordination history.

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

Stensibly directly changes ledger records: items, claims, events, artifacts, dependencies, reservations, and runs. Generic runners may change external systems. Fields such as `externalRunId` and artifact references connect those effects to the ledger, while the external system remains authoritative for its result.

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

The same guarantee does not cover every generic runner effect. Lease expiry proves lost Stensibly ownership; it cannot prove the external system stayed unchanged.

### Progress and observability

The dashboard, REST, MCP, deterministic project briefs, events, run rows, and operation receipts expose current work and history.

Run evidence includes logical run ID, status, generations, lease owner and expiry, heartbeat time, retry attempt and budget, checkpoint, continuation, outcome, usage, and terminal time.

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

## Broad comparison

| Property | Stensibly | Smolrunner |
|---|---|---|
| Product role | Shared responsibility and run ledger | Local machine and execution steward |
| Main entry points | Browser, REST, MCP, local server/CLI | Rust CLI and strict worker commands |
| Work unit | Item plus claim, event, artifact, and run | Plan action plus exact worker request and admission |
| State owner | Convex or SQLite ledger | Durable local documents plus fresh machine observation |
| Direct side effects | Ledger writes; external effects referenced | Typed host and execution changes |
| Persistence | Convex/SQLite transactions and receipts | Atomic files, revisions, journals, tombstones |
| Concurrency | Versions, leases, generations, idempotency | Writer lock, CAS, generations, reservations, cache leases |
| Cancellation | Durable terminal run transition | Durable queued cancellation and active drain evidence |
| Progress | Events, heartbeat, checkpoint, continuation | Journal snapshots, run-once result, typed continuation |
| Observability | Board, API, events, runs, receipts | Human/JSON reports, read models, journals, planned receipts |
| Test depth | Durable run and receipt tests | Extensive state, queue, recovery, and executor tests |

## Property selected after the maps

The maps show that retry policy is secondary to **authority after interruption**:

- Who owns the accepted work identity?
- Who owns the effect?
- Which durable evidence survived?
- Can cancellation prove effect outcome?
- Does recovery read a receipt, consult another system, or observe the machine?

That property produces a bounded comparison without assuming one shared implementation.

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

The model evaluates three boundaries:

1. Stensibly local ledger write.
2. Stensibly run coordinating an external effect.
3. Smolrunner durable host execution.

Observed dispositions:

| Boundary | Durable decision | Branch |
|---|---|---|
| Stensibly local ledger | Read retained result; when unknown, replay exact same request and key. | Baseline |
| Stensibly external runner | Reconcile the external effect owner before retry or replacement. | Campaign |
| Smolrunner host execution | Require fresh observation before resume, retry, compensation, or termination. | Campaign |

Assertions verify one baseline and two campaign candidates. The model does not execute the repositories or prove deployed behaviour.

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

## Dependency, SDK, platform, and runtime findings

The scout found no direct violation of a lower-level contract in SQLite, Convex, Bun, Rust, Unix filesystem primitives, or Lima.

- Stensibly findings belong to its external operation adapter and replacement policy.
- Smolrunner findings belong to its live receipt integration.

**Decision:** open no dependency, SDK, platform, or runtime campaign. A lower-level campaign requires fault injection that reproduces a documented contract failure below the application boundary.

## Ranked decisions

1. **Campaign — Stensibly external-runner reconciliation before replacement.**
2. **Campaign — Smolrunner personal-worker attempt, journal, and receipt integration.**
3. **Baseline — Stensibly local ledger operation receipts.**
4. **Retain — shared correlation envelope inside the two campaigns.**
5. **Stop — generic cross-owned retry framework or shared retry library.**
6. **Stop — dependency, SDK, platform, or runtime attribution.**

## Negative results and uncertainty

- Stensibly and Smolrunner own different durable-work boundaries.
- Retry configuration alone does not decide safe repetition; effect ownership and surviving evidence decide it.
- Stensibly local receipts cover a narrower boundary than generic runner execution.
- Smolrunner has strong accepted recovery semantics and incomplete live receipt integration.
- The synthetic model establishes decision differences, not deployed consequences.
- No private data, credentials, paid calls, production systems, or upstream interactions were used.

## Handoff

- Strongest finding: safe recovery follows effect ownership and retained evidence—local receipt, external read-back, or fresh machine observation.
- Durable artifacts:
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/report.md`
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/authority_after_interruption.py`
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/latest.json`
- Dependencies: A1 needs a synthetic external runner adapter; A2 needs live receipt mapping, persistence, read-back, and interruption injection.
- Decision needed: promote A1 and A2 as separate owned-system campaigns.
- PR #36 remains closed and excluded.
- Upstream contact remains unauthorized.
