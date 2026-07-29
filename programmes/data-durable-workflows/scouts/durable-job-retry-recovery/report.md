# Scout report: owned durable-workflow systems

## In simple words

The three repositories represent different kinds of work.

- Stensibly is a server-owned responsibility ledger with browser, REST, and MCP clients. It persists work items, authority, events, artifacts, and run state.
- Smolrunner is a local Rust control plane that observes a machine, plans bounded actions, checkpoints durable state, and performs explicitly authorized host or worker operations.
- Fin Agent is a request-scoped chat application. It runs planning and read-oriented financial tool calls inside one HTTP request and saves completed conversation messages in the browser.

That broad map narrows the useful retry-and-recovery comparison to Stensibly and Smolrunner. They both preserve durable work, yet they protect different failure boundaries. Stensibly keeps one run identity across bounded retries and can reconcile its own ledger mutations with operation receipts. Smolrunner records exact request, reservation, cancellation, journal, and terminal evidence and treats an interrupted executor action as uncertain until the machine is observed again.

Two owned-system campaigns are justified: reconcile Stensibly external runner effects before replacement, and connect Smolrunner personal-worker attempts, execution journals, and terminal receipts. Fin Agent durability work, generic cross-system retry abstractions, and dependency or runtime campaigns should stop at this revision.

## Assignment and scope correction

- Fieldwork issue: #29
- Programme: `data-durable-workflows` (#16)
- Worker: `chatgpt:gpt-5.6-thinking`
- Owned path: `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/`
- Claim scope supported: `interface`
- Retrieval date: 2026-07-29
- Upstream contact authorized: `false`

The issue was claimed under a retry-and-recovery comparison. A later issue comment withdrew the retry-first premise and requested a broad map of representative owned systems: entrypoints, work representation, control and data flow, state ownership, side effects, persistence, concurrency, cancellation, progress, observability, tests, and user-facing behaviour. This report follows that order. The shared interruption scenario appears only after the wider map identifies suitable systems.

### Pinned revisions

- Fieldwork: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`
- Stensibly: `teamleaderleo/stensibly@bd16acf3dfe4589628e94f9094b002bc17b5e37c`
- Smolrunner: `teamleaderleo/smolrunner@722bb90ca0833d5118b7e095688a9daa71f3cbd3`
- Fin Agent: `teamleaderleo/fin-agent@844ec26d775b24cc7a8cf7b5e06b358be77a7d69`

The owned repositories are the systems under investigation, so this lane does not apply `testbed:*` labels. No stable target hub has yet been established for either recommended owned-system campaign.

## Representative system selection

Evidence label: **Observed in pinned repository source, tests, and repository documentation**

The systems were selected because they cover three distinct work models:

1. a shared server ledger and coordination service;
2. a local machine and execution steward with durable mutation evidence;
3. a request-scoped agent application with browser history.

This spread exposes which reliability properties belong to durable work itself and which arise only after a product chooses a durable worker boundary.

## Broad owned-system map

### Stensibly

#### Entry points and user-facing behaviour

Stensibly exposes:

- a browser dashboard and item-detail client;
- REST v1;
- remote Streamable HTTP MCP;
- local stdio MCP;
- local SQLite server and token administration commands.

Hosted clients call a Cloudflare Worker, which authenticates browser sessions or bearer tokens and calls Convex through a private service credential. Local mode serves the browser, REST, and MCP directly over SQLite. Human users see a board projection of the ledger; machine clients read and mutate the same work facts through typed operations.

Relevant paths:

- `README.md`
- `src/app.ts`
- `src/mcp.ts`
- `src/convex-ledger.ts`
- `src/sqlite-ledger.ts`

#### Work representation

The primary work unit is an item inside a workspace and project. Related records include actors, claims, dependencies, reservations, events, artifacts, and work runs. The item describes responsibility and next action. A run records one executor's lifecycle against the item. External code, files, CI, deployments, and private execution remain owned by their original systems; Stensibly stores references and coordination history.

#### Control and data flow

```text
human or agent client
→ browser, REST, or MCP operation
→ authentication and project scope
→ ledger mutation or read
→ Convex or SQLite transaction
→ item/event/artifact/run projection
→ browser, API, MCP, or later worker observation
```

Run control follows a separate state machine:

```text
create run
→ acquire lease
→ start
→ run / wait / block
→ heartbeat and checkpoint
→ succeed / fail / cancel
→ bounded retry or terminal release
```

#### State owner

The server-owned ledger is authoritative. Convex owns hosted state. SQLite owns local compatibility state. Clients hold tokens, cursors, and projections; they do not own shared work truth.

#### Side effects

Stensibly directly creates or changes ledger records: items, claims, events, artifacts, dependencies, reservations, and runs. Generic runners may create effects in external systems, linked through fields such as `externalRunId` and artifact references. Those external systems remain authoritative for their own effects.

#### Persistence

Hosted state is durable in Convex. Local state is durable in SQLite. Mutations use transactions, append lifecycle events, and retain idempotency records for covered operations. Run rows retain lifecycle, lease, retry, checkpoint, outcome, continuation, and usage data.

#### Concurrency

Concurrency controls include:

- one live run per item;
- expected run generation;
- expected lease generation;
- lease owner and expiry;
- idempotency keys for run creation and commands;
- exact request replay and changed-request conflict;
- transactional compare-and-update conditions.

These controls prevent stale workers and duplicate callers from silently replacing newer state.

#### Cancellation and progress

Cancellation is a durable terminal run transition. It clears lease and retry state while retaining the outcome. Progress appears through item events, run status, heartbeat time, checkpoint text, continuation reference, and usage counters.

#### Observability

The dashboard, REST, MCP, item events, run rows, operation receipts, and deterministic project briefs expose current work and history. Run observability includes logical run ID, generations, lease owner and expiry, retry attempt and budget, checkpoint, outcome, continuation, usage, and terminal time.

#### Tests

Pinned tests cover:

- exact run creation replay;
- one live run per item;
- lease ownership and generation fencing;
- heartbeat checkpoint replay;
- bounded retry and exhaustion;
- cancellation;
- stale lease reconciliation after database reopen;
- operation receipt lookup for item, event, and artifact mutations;
- project-scoped unknown receipt behaviour.

Relevant paths:

- `test/runs.test.ts`
- `test/operation-receipts.test.ts`
- `test/idempotency-scope.test.ts`

### Smolrunner

#### Entry points and user-facing behaviour

Smolrunner is a Rust CLI. Current public commands include diagnostics, deterministic planning, host observation and planning, one explicitly confirmed host-preparation phase, and strict personal-worker state, queue, job, and cancellation commands. Human and JSON outputs derive from typed reports.

The product deliberately keeps mutation behind observe, plan, confirmation, and evidence checks. The personal-worker alpha adds a bounded `run-once` model: one invocation performs at most one accepted lifecycle or job action, records the result or continuation, and returns.

Relevant paths:

- `README.md`
- `src/main.rs`
- `docs/PERSONAL_WORKER_ALPHA.md`

#### Work representation

Smolrunner represents several related units:

- repository manifests and desired-state plans;
- host-preparation actions with immutable action IDs, lanes, rollback classes, and preconditions;
- durable execution journals;
- personal-worker requests binding request ID, immutable repository source, verification profile, runner profile, resource limits, cache identity, priority, deadline, and cancellation state;
- reservations, admission generations, durable cache leases, and terminal tombstones.

#### Control and data flow

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

#### State owner

Smolrunner's accepted local documents own host-installation, lease, execution-journal, and personal-worker state. Personal-worker request, queue generation, reservation, cancellation, cache lease, active work, profile intent, terminal identity, and recovery evidence live in the durable store. Current host state remains authoritative for machine facts and must be observed again after uncertainty.

#### Side effects

Current mutation can create or adjust reviewed host resources through typed executors. Planned worker operation can start and stop Lima profiles, manage runner readiness, create workspaces, execute repository-owned verification commands, maintain approved caches, and record terminal results. Host resources and external services retain their own current facts; journals record attempted transitions and evidence.

#### Persistence

Smolrunner uses bounded canonical documents, cooperative writer locks, exact revision and generation expectations, staged successor recovery, synchronized atomic publication, retained terminal tombstones, and durable pre/post executor journal checkpoints.

The execution receipt document contract exists at the pinned revision. Live report mapping, durable receipt publication, exact receipt read-back, and cross-system transport remain future slices.

#### Concurrency

Concurrency controls include:

- one cooperative writer;
- expected store revision;
- expected queue generation;
- reservation ID and generation;
- bounded active reservations;
- cache lease compatibility;
- exact duplicate mutation detection;
- changed-evidence conflicts;
- retained terminal identity;
- no-replace and compare-and-swap publication.

The first personal-worker journey supports one job at a time even though lower-level queue types can represent bounded active reservations.

#### Cancellation and progress

Queued cancellation records an exact cancellation time and replays an identical request as a duplicate. Active cancellation requires exact draining admission evidence. Progress is intentionally bounded: state transitions, one `run-once` action, durable journal snapshots, typed continuation, blocker, failure, or terminal receipt.

#### Observability

Human and JSON reports expose store revision, queue generation, desired and current profile, queue counts, request source identity, admission state, reservation, cache lease, cancellation, terminal reason, acknowledgement, and evidence digest. Execution journals explain uncertain action or rollback state. Future external receipts are designed to expose exact execution identity and a bounded terminal or fresh-observation disposition.

#### Tests

Pinned tests cover:

- durable personal-worker store and writer contracts;
- queue evaluation and capacity;
- submit, read, and cancel CLI behaviour;
- exact duplicate mutation replay;
- terminal tombstone replay and changed-evidence conflict;
- lock behaviour and staged successor recovery;
- durable execution checkpoint semantics through fake executors and stores.

Relevant paths:

- `tests/personal_worker_store_contract.rs`
- `tests/personal_worker_store_transaction.rs`
- `tests/personal_worker_terminal_replay.rs`
- `tests/personal_worker_queue_contract.rs`
- `src/lima_lifecycle_executor/tests.rs`

### Fin Agent

#### Entry points and user-facing behaviour

Fin Agent is a Next.js chat application. The browser presents chat and transaction analysis views. A client hook sends conversation messages to `/api/chat`; the route runs planning, tool calls, and synthesis; SSE returns reasoning metadata and content. Completed messages are saved to browser local storage.

Relevant paths:

- `README.md`
- `app/api/chat/route.ts`
- `hooks/useChat.ts`
- `services/chat-service.ts`

#### Work representation

The work unit is an in-memory chat request containing a message array. During the request, the backend builds a reasoning trace and planner action. Tool results feed a final synthesis. There is no durable server-side job, attempt, reservation, checkpoint, or terminal receipt.

#### Control and data flow

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

The route performs up to twelve planner steps, although the current flow returns after one tool execution and synthesis.

#### State owner

The browser owns retained chat history. The server request owns transient messages, planner action, tool result, and reasoning trace. External providers own financial data. No durable worker owns an accepted job after the request ends.

#### Side effects

At the pinned revision, financial tools are read-oriented. Application-side persistence consists of browser chat history. Network calls can consume time and provider quota, while the reviewed path does not expose a consequential durable write suitable for duplicate-effect testing.

#### Persistence

The browser debounces message-array saves to local storage. Backend loop state disappears with the request or process. SSE content has no durable cursor or server-side replay record.

#### Concurrency

The client blocks a second submission while `isLoading` is true. The backend handles each HTTP request independently. There is no shared request identity, optimistic version, lease, deduplication record, retry budget, or cross-request serialization.

#### Cancellation and progress

The client has no abort controller in the reviewed path. Loading state can end on `done` or `error`. Progress appears as streamed reasoning metadata and content, with no resumable cursor.

#### Observability

The route emits console logs and returns a reasoning trace and step count to the client. It lacks durable operation correlation, attempt history, cancellation evidence, reconciliation state, and terminal read-back.

#### Tests

Repository search at the pinned revision found no Jest, Vitest, Playwright, Cypress, or comparable application tests. Source inspection therefore carries more uncertainty than the Stensibly and Smolrunner findings.

## Broad comparison

| Property | Stensibly | Smolrunner | Fin Agent |
|---|---|---|---|
| Product role | Shared responsibility and run ledger | Local machine and execution steward | Request-scoped financial chat |
| Main entry points | Browser, REST, MCP, local server/CLI | Rust CLI and strict worker commands | Browser and `/api/chat` |
| Work unit | Item plus claim, event, artifact, and run | Plan action plus exact worker request and admission | Message array and transient planner action |
| State owner | Convex or SQLite ledger | Durable local documents plus fresh host observations | Browser history and request memory |
| Direct side effects | Ledger mutations; external effects referenced | Typed host and execution mutations | External reads and browser history |
| Persistence | Convex/SQLite transactions and receipts | Atomic files, revisions, journals, tombstones | localStorage only |
| Concurrency | Versions, leases, generations, idempotency | Writer lock, CAS, generations, reservations, cache leases | Client loading flag |
| Cancellation | Durable terminal run transition | Durable queued cancellation and active drain evidence | No backend cancellation path |
| Progress | Events, heartbeat, checkpoint, continuation | Journal snapshots, run-once result, typed continuation | SSE content and reasoning metadata |
| Observability | Board, API, events, runs, receipts | Human/JSON reports, read models, journals, future receipts | Console logs and client trace |
| Test depth | Durable run and receipt tests | Extensive state, queue, recovery, and executor tests | No comparable tests found |

## Evidence-led child experiment selection

The broad map produces three conclusions.

1. Stensibly and Smolrunner both accept durable work identities and retain recovery evidence. Their failure boundaries differ enough to justify one shared interruption scenario.
2. Fin Agent has a request lifecycle rather than a durable worker lifecycle. A durability campaign would redesign the product before testing an observed reliability gap.
3. The strongest common experiment is commit-before-disconnect followed by cancellation and restart. It exercises identity, retry, checkpoints, recovery, reconciliation, and observability without forcing the systems into one implementation model.

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

The scenario applies this sequence:

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

## Focused durable-work findings

### Stensibly

#### Logical identity and retries

A work item owns at most one live run. The run has a stable `id` and `itemId`; optional `externalRunId` links another executor. Retry requeues the same run instead of creating a fresh logical run. `retryAttempt` counts failed attempts, while run generation and lease generation fence state and ownership. Failure computes a bounded `nextRetryAt`; retry becomes legal only after the delay and while budget remains.

#### Checkpoints, cancellation, and recovery

Heartbeats and transitions can replace one durable free-form checkpoint. Exact heartbeat replay is idempotent; changed checkpoint content under the same key conflicts. Cancellation is terminal and generation-fenced. Expired active leases reconcile exactly once to `abandoned`, including after SQLite reopen.

The checkpoint helps operators and continuations, yet it carries no typed cursor, effect identity, or declared resume contract. `abandoned` proves lost Stensibly lease ownership; it does not prove the external executor left the world unchanged.

#### Reconciliation and observability

Operation receipts cover item, event, and artifact ledger mutations. A recorded receipt directs the caller to read the item and avoid repetition. An unknown receipt directs exact same-request, same-key replay. This resolves commit-before-response ambiguity for covered local writes.

Generic runner effects remain outside that receipt boundary. A replacement run can begin after abandonment even when an external effect's acknowledgement was lost. Run fields and events expose rich local evidence, while one exported correlation chain from logical job through external operation to terminal receipt remains absent.

### Smolrunner

#### Logical identity and retries

A personal-worker request binds exact request ID, profiles, immutable source, resources, cache identity, time, and cancellation state. Reservation and admission generations identify accepted capacity. Exact duplicates replay; changed semantics under a reused identity conflict; terminal tombstones prevent recreation.

The operator loop performs one bounded action per invocation. Verification profiles may authorize a bounded retry, normally none. An interrupted `executing` journal record is uncertain and requires fresh observation before resume, retry, or compensation.

#### Checkpoints, cancellation, and recovery

The execution journal publishes all-pending state before the first executor call, `executing` before each action, and terminal action state after return. Rollback follows the same pre-call and post-call checkpoint rule. Checkpoint publication failure stops execution.

Queued cancellation records exact evidence. Active cancellation requires a valid draining transition. Every typed personal-worker mutation calls store recovery before loading current state, checks exact revision and generation, and publishes a valid successor. Terminal release removes active work and its cache lease and appends a tombstone; exact terminal replay is a duplicate.

#### Reconciliation and observability

Recovery re-observes ownership and preconditions, then chooses resume, retry, compensation, or termination. The journal explains uncertainty without claiming current host truth. Typed read models expose request, admission, reservation, cache lease, cancellation, terminal reason, and evidence digest.

The execution receipt document can represent completion, failure, or `fresh_observation_required`. At the pinned revision, live report mapping, receipt persistence, exact read-back, and connection to the personal-worker attempt remain incomplete.

### Fin Agent

Fin Agent provides no durable logical job, attempt ID, server checkpoint, retry budget, cancellation token, recovery worker, reconciliation API, or terminal read-back. A disconnected request can lose the final response after external reads have occurred. Its reviewed tool path lacks a durable write whose duplicate would support the shared correctness scenario.

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

The current comparison reveals translation work without a demonstrated cross-system correlation failure.

**Recommendation:** retain as acceptance criteria inside A1 and A2. Open a separate observability campaign after a runnable integration loses correlation across a real boundary.

### A4. Fin Agent lacks a durable-job product boundary

Adding a queue, durable checkpoints, cancellation, and reconciliation would be a product redesign. Its current read-oriented, request-scoped flow provides no consequential duplicate-effect reproduction.

**Recommendation:** stop. Revisit after Fin Agent gains long-running asynchronous analysis, write-capable tools, resumable execution, or an explicit operator requirement.

## Dependency or runtime findings

No observed result establishes a defect in SQLite, Convex, Bun, Rust, Unix filesystem primitives, Lima, Next.js, Vercel, the OpenAI SDK, or browser SSE APIs.

- Stensibly gaps sit in application-level external operation ownership and reconciliation.
- Smolrunner gaps sit in its own adapter and publication slices.
- Fin Agent gaps come from its request-scoped product design.

**Recommendation:** open no dependency or runtime campaign from this scout. A lower-level campaign requires direct fault injection that violates a documented dependency or runtime contract.

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

6. **Stop — dependency or runtime attribution.**
   No reproduction crosses an owned application boundary into a violated lower-level contract.

## Negative results and uncertainty

- The initial hypothesis that all three named repositories offered comparable durable job paths was false; Fin Agent is request-scoped.
- The broad map found more shared value in explicit identity and reconciliation rules than in a common retry implementation.
- Stensibly local operation receipts close a narrower ambiguity than generic runner execution. This scout did not implement or execute an external runner adapter.
- Smolrunner documents strong execution-journal recovery, while the personal-worker alpha remains incomplete. This scout did not run Linux or Lima fault injection.
- The synthetic model establishes decision differences, not deployed production consequences.
- Fin Agent has thinner test evidence than the other two repositories.
- No private data, credentials, paid calls, production systems, or upstream interactions were used.

## Handoff

- Strongest supported finding: the broad system map separates a server ledger, a local machine steward, and a request-scoped chat application. Durable retry comparison applies to the first two. Safety depends on preserving logical identity and retaining enough evidence to distinguish recorded result, exact replay, and uncertain execution.
- Durable artifacts:
  - `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/report.md`
  - `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/artifacts/retry_recovery_scenario.py`
  - `programmes/data-durable-workflows/scouts/durable-job-retry-recovery/artifacts/latest.json`
- Failed hypothesis: Fin Agent supplies a durable background-job test surface.
- Dependencies discovered: future campaign A1 depends on a synthetic external runner adapter; A2 depends on Smolrunner live receipt mapping and fault injection.
- Decision needed: programme coordinator may promote A1 and A2 as separate owned-target campaigns.
- Upstream contact remains unauthorized.
