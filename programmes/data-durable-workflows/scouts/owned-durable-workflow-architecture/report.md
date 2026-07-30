# Scout report: owned durable-workflow architecture

## In simple words

The active portfolio contains several different kinds of durable work. They should not be forced into one worker or retry framework.

- **Stensibly** coordinates shared work and owns durable run state.
- **Smolrunner** owns local execution admission, journals, recovery state, and host observation.
- **Proofwake** stores immutable observations and rebuilds evidence projections.
- **Days Upon** reconciles a local calendar with provider state and provider cursors.
- **Renderprove** runs bounded browser reviews and writes terminal evidence receipts.
- **Starsector Preflight** owns run directories, profiling evidence, reusable caches, and campaign records around a child process.
- **Elatura** treats cache state as disposable derived data and returns to the authenticated application when it cannot trust the cache.
- **Scrapbook** preserves the last successful upstream snapshot while failed refreshes back off visibly.
- **gh-tidy-branches** revalidates a destructive GitHub mutation immediately before applying it and records conservative undo evidence.
- **Botany Sim** advances persistent simulation state from absolute time and preserves pending events and history.
- **Make Good TV** records deterministic controller sessions, copied observations, applied actions, and replay evidence.
- **Quarry** reconstructs paper execution from a hash-chained audit ledger and binds verification receipts to exact durable attempt states.

The runnable comparison evaluates thirteen interruption boundaries across these twelve systems. It asks what identity and evidence survive, who still owns the effect, and which recovery action is authorized.

Recommended campaigns:

1. Stensibly external-runner reconciliation before replacement.
2. Smolrunner attempt, journal, and terminal-receipt integration.
3. Days Upon durable provider-mutation outbox and reconciliation.
4. Renderprove interruption-safe terminal receipt publication.

Strong reusable baselines:

- Stensibly local operation receipts.
- Proofwake append-only observation recovery.
- Scrapbook stale-while-error coordination.
- Quarry audit-chain recovery and attempt-bound verification receipts.

## Assignment

- Fieldwork issue: #29
- Programme: `data-durable-workflows` (#16)
- Worker: `chatgpt:gpt-5.6-thinking`
- Owned path: `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/`
- Expanded retrieval date: 2026-07-30
- Upstream contact authorized: `false`

### Pinned revisions

- Fieldwork base: `teamleaderleo/fieldwork@976b436d4d7e2741dee5505b6715839db9bd4e15`
- Stensibly reviewed source: `teamleaderleo/stensibly@bd16acf3dfe4589628e94f9094b002bc17b5e37c`
- Smolrunner: `teamleaderleo/smolrunner@722bb90ca0833d5118b7e095688a9daa71f3cbd3`
- Proofwake: `teamleaderleo/proofwake@ac421f80a97818c4a8d0d4ed021db678e1a39da5`
- Days Upon: `teamleaderleo/days-upon@3b29577dc3245ed38afa1591c0b3f6d4feb8f7ee`
- Renderprove: `teamleaderleo/renderprove@3e954bdbf37b71dc06db6dd5a0b46bf2f296eb29`
- Starsector Preflight: `teamleaderleo/starsector-preflight@8b58f1e6ede2dd445009128e88fcc409728c7c80`
- Elatura: `teamleaderleo/elatura@bbea414c6e400ba748d053caedb777ecee1cc381`
- Scrapbook: `teamleaderleo/scrapbook@ea708e027d63bd4235ccbcd358e81efcd41a560b`
- gh-tidy-branches: `teamleaderleo/gh-tidy-branches@03caecd2fc9b2b4dd216115b3ce46df522f7eafa`
- Botany Sim: `teamleaderleo/botany-sim@433fff596153a6f93341c3ff350bc3684c3d7a72`
- Make Good TV: `teamleaderleo/make-good-tv@d0fbc5990b24de02c75c2ef47b5886ff5c55467a`
- Quarry: `Quarry-Labs/quarry@f8824c62c57ddaa05ce59bd9d09a6aa6fde269b3`

The Stensibly source map remains pinned to the revision directly inspected in the original corrected scout. Its current default head was observed separately and was not substituted without repeating the full source-and-test map.

PR #36 and its old handoff remain excluded. The earlier two-system handoff on PR #53 is superseded by this portfolio expansion, while its directly inspected Stensibly and Smolrunner evidence remains part of this report.

## Method

Evidence label: **Observed in pinned source, tests, repository documentation, and a fresh synthetic comparison**

The work proceeded in this order:

1. Read the Fieldwork programme and handoff protocol.
2. Inventory recently active owned repositories.
3. Expand the scope from two systems to the active portfolio.
4. Identify the distinct durable-work boundary in each selected system.
5. Pin each reviewed revision.
6. Read a focused architecture, source, receipt, sync, cache, simulation, or audit contract for every added system.
7. Compare systems without assuming a shared worker model.
8. Select interruption authority as the common property.
9. Extend the zero-dependency model to all twelve systems.
10. Separate application gaps from dependency, SDK, platform, or runtime claims.
11. Rank campaigns, baselines, retained patterns, and stops.

No private content, credentials, live trading, real orders, destructive GitHub operations, production mutations, paid calls, or upstream contact were used.

## Portfolio architecture map

| System | Architecture family | Work and entrypoints | Durable identity and state owner | Side effects and concurrency | Cancellation, recovery, and reconciliation | Observability and tests | Decision |
|---|---|---|---|---|---|---|---|
| Stensibly | Shared coordination ledger | Browser, REST, MCP, local server; item and run operations | Item, run, operation, generation, lease generation, idempotency key; Convex or SQLite ledger | Transactional ledger writes; one live run per item; external runner effects remain external | Terminal cancellation; stale lease to abandoned; local operation receipt replay; external effect ambiguity remains | Board, events, runs, checkpoints, usage, receipts; durable run and receipt tests | Campaign external reconciliation; baseline local receipts |
| Smolrunner | Local execution steward | Rust CLI; observe, plan, confirm, journal, execute; personal-worker commands | Request, reservation, action, execution, revision, generation; durable local documents | Writer lock, compare-and-swap publication, reservations, cache leases, typed host effects | Draining cancellation; pre/post effect journal; fresh observation before resume, retry, compensation, or termination | Human/JSON read models, journals, tombstones; extensive state and executor tests | Campaign receipt integration |
| Proofwake | Append-only evidence index | CLI, loopback collector, webhooks, dashboard, MCP, receipt adapters | Provider delivery, receipt ID, canonical digest; append-only observation ledger | Strict bounded ingestion; immutable observations; idempotent duplicates; conflicting identity reuse fails | Incomplete writes preserved for reviewed recovery; projections rebuilt; producer remains authoritative | Coverage, freshness, failure-to-recovery intervals, source citations, diagnostics | Baseline |
| Days Upon | Local-first provider synchronization | Browser calendar, Google adapter, ICS, local workspace | Local event ID, calendar ID, remote event ID, sync token, baseline fingerprint; browser workspace and sync storage | Direct provider create/update/delete calls; parallel calendar pulls; local storage for cursors and baselines | Google 410 resets incremental cursor to full sync; local state can rebuild; no durable mutation outbox or terminal provider disposition | Sync summaries and domain tests; provider state visible through UI | Campaign |
| Renderprove | Bounded verifier and receipt producer | CLI, service, local MCP, browser review, optional container probe | Manifest project, stable route/viewport case IDs; output directory | Starts local runtime, drives Chromium, writes screenshots and receipt; cancellation signal supported | Runtime is stopped in `finally`; terminal receipt is written only after successful review return and shutdown | Versioned receipt, screenshots, hashes, diagnostics, repeatability reports, locked CI | Campaign |
| Starsector Preflight | Run wrapper, profiler, and cache pipeline | Java CLI: doctor, scan, prepare, run, benchmark, lint | Run directory, profile fingerprint, cache artifact, benchmark cohort | Child launcher and game process; JFR; reusable indexes and prepared artifacts; bounded scheduler | Run records finalize across multiple failure classes; campaign collection preserves failed runs; cache validation fails closed | `run.json`, profile, JFR, summaries, adapter evidence, benchmark reports; packaged cross-platform tests | Retain |
| Elatura | Observe-only sidecar and derived cache | Firefox observer, report export, synthetic adapter/cache laboratories | Origin, browser profile, adapter, namespace, resource, content identity, envelope version | Current cache is synthetic and in memory; authenticated application remains authoritative | Missing, corrupt, incompatible, drifted, mismatched, or expired cache returns to authoritative fetch/display | Provenance, freshness, integrity flags, privacy-validating reports, compatibility tests | Retain; stop private persistence until gate |
| Scrapbook | Stale-while-error cache coordinator | Next.js server render and polling API around GitHub activity | Generated snapshot, request ID, failure count, retry deadline | Cross-instance data cache, in-process promise/value coalescing, browser polling | Last successful snapshot survives failed refresh; exponential backoff; 503 only with no usable snapshot | Cache status, source, attempts, failures, next retry, rate limit, headers, unit tests | Baseline |
| gh-tidy-branches | Bounded destructive command with undo receipt | GitHub CLI extension; preview, apply, undo | Repository, branch, merged PR, exact head SHA; GitHub ref plus local receipt | Bounded scan workers; serial deletion; exact ref re-read before each delete | Live revalidation before mutation; atomic local undo receipt; conservative restore | Preview/JSON, deterministic fixtures, installed-extension tests, live workflow | Retain; dependency watch |
| Botany Sim | Deterministic offline simulation | Browser garden and calendar simulation | Calendar ID/version, generator version, mode, event ID, garden year; garden save | Pure deterministic state transition from absolute elapsed time | Pending events survive missed windows; claiming moves to history; equal elapsed time yields equal state; migrations explicit and currently absent | Serialized state, summaries, active/offline equivalence tests | Retain |
| Make Good TV | Deterministic simulation and controller audit | Local game runners, model adapter, planned MCP | Session ID, game, seed, seat, controller, decision number; host state and action trace | Host validates actions; controllers receive copies; one isolated model worker per decision | Stale and cross-session submissions rejected; malformed output becomes safe fallback; replay uses applied actions | Untouched audit snapshots, context events, terminal outcomes, telemetry, adversarial tests | Retain; stop persistent worker until evidence |
| Quarry | Research pipeline and resumable paper execution | Python CLI: experiments, tournaments, walk-forward, paper sessions, verification profiles | Session, audit sequence, attempt, state, verification request, receipt, content digest | Non-blocking session lock; deterministic parallel evaluation; immutable atomic artifacts; simulated fills only | State rebuilt from verified hash chain; kill switch cancels pending targets; request and receipt bind exact attempt states | Audit ledger, risk and reconciliation reports, immutable receipts, extensive tests and isolated verification | Baseline; stop live trading expansion |

## Detailed system findings

### Stensibly

Relevant reviewed paths:

- `README.md`
- `src/runs-core.ts`
- `src/runs.ts`
- `src/runner-contracts.ts`
- `src/operation-receipt-contracts.ts`
- `src/operation-receipts.ts`
- `test/runs.test.ts`
- `test/operation-receipts.test.ts`
- `test/idempotency-scope.test.ts`

The ledger owns coordination truth, run identity, lease generations, retry attempts, checkpoints, terminal status, and local operation receipts. A covered local write can be read back or replayed under the exact same request identity. A generic external runner remains authoritative for its own effect.

The application gap is the replacement policy after lease loss. `abandoned` proves that Stensibly ownership expired; it does not prove that the external operation produced no effect.

### Smolrunner

Relevant reviewed paths:

- `README.md`
- `AGENTS.md`
- `docs/PERSONAL_WORKER_ALPHA.md`
- `docs/EXECUTION_RECEIPTS.md`
- `docs/adr/0014-durable-execution-journal.md`
- personal-worker store, queue, transaction, submit, cancel, and read-model source
- terminal replay and executor checkpoint tests

Smolrunner preserves strong accepted identity, revisions, reservations, tombstones, and pre/post executor journal evidence. An interrupted `executing` state remains uncertain and requires fresh machine observation.

The live receipt document exists, while end-to-end mapping from personal-worker attempt through journal to durable terminal read-back remains incomplete at the reviewed revision.

### Proofwake

Relevant reviewed paths:

- `README.md`
- `docs/architecture.md`
- current evaluation-observation and read-only projection work

Proofwake deliberately does not own execution or coordination. It owns accepted observation identity, immutable source observations, ingestion fingerprints, and rebuildable projections.

Its recovery model is valuable because it separates durable facts from derived status:

```text
producer observation
→ strict identity and schema validation
→ append-only ledger
→ rebuildable repository/revision projection
→ bounded CLI, dashboard, MCP, or export
```

Identical duplicate delivery returns the original accepted result. Conflicting reuse fails. Incomplete writes are detected and preserved for reviewed recovery.

### Days Upon

Relevant reviewed paths:

- `README.md`
- `docs/architecture.md`
- `src/integrations/googleSync.ts`
- `src/integrations/googleSyncStorage.ts`
- Google Calendar adapter and tests

Current pull recovery is explicit:

```text
saved sync token
→ incremental provider pull
→ provider returns 410
→ discard cursor for this pass
→ bounded full pull
→ merge remote additions, changes, and deletions
→ save next sync token and baselines
```

Current push flow iterates deletions, updates, and creations directly against the provider. The durable browser record contains sync tokens and remote baselines, not a mutation outbox with operation identity, attempt state, acknowledgement, or terminal reconciliation.

A crash or disconnect after the provider accepts a mutation and before local baseline publication can create an ambiguous repeat.

### Renderprove

Relevant reviewed paths:

- `README.md`
- `docs/RECEIPT_V1.md`
- `src/core/receipt.mjs`
- `src/service.mjs`

A normal review:

```text
load manifest
→ start runtime
→ run browser cases
→ stop runtime
→ construct receipt
→ write receipt.json
```

The receipt is a bounded evidence contract with stable case IDs, screenshot digests, diagnostics, runtime data, and terminal status. It does not claim universal correctness.

The current service writes `receipt.json` only after `runBrowserReview` returns and runtime shutdown completes. A cancellation, process loss, browser exception, or write interruption can leave case artifacts or a stopped runtime without a durable terminal or interrupted receipt. The write itself is a direct file write rather than an atomic create-and-rename contract.

### Starsector Preflight

Relevant reviewed paths:

- `README.md`
- `docs/automatic-launch.md`
- benchmark collection and comparison source/tests

Preflight owns a durable run directory around a child process without replacing or editing the original launcher. It records workload identity, launch identity, lifecycle evidence, JFR, summaries, and optional adapter evidence.

Its durable pattern is a staged run bundle rather than a queue:

```text
discover
→ census and fingerprint
→ allocate run directory
→ launch child with process-local agent
→ collect raw evidence
→ finalize lifecycle and summaries
→ include run in later campaign comparison
```

Run records cover successful exits, nonzero exits, launch failures, fatal lifecycle evidence, and bounded post-processing failures. The current scout retains this as a run-evidence pattern. A campaign requires a direct interruption reproduction showing an unrecoverable raw-evidence or finalization gap.

### Elatura

Relevant reviewed paths:

- `README.md`
- `docs/cache-and-provenance.md`
- observer and cache compatibility tests

Elatura provides the cleanest derived-cache authority rule:

```text
cache miss, corruption, drift, identity mismatch, or expiry
→ delete or ignore derived entry
→ return control to authenticated application behaviour
```

Envelope version, adapter version, structural compatibility, content identity, freshness, isolation, and provenance are independent checks. A stale entry remains visibly stale.

Current cache work is synthetic and in memory. Private transcript persistence and live alternate-surface bridging remain intentionally gated. The scout stops any campaign that assumes those capabilities already exist.

### Scrapbook

Relevant reviewed paths:

- `README.md`
- `docs/github-activity-cache.md`
- `lib/github-activity-response.ts`
- `lib/github-activity-response.test.ts`

Scrapbook coordinates three freshness layers:

- a shared Next.js data cache across instances;
- an in-process coordinator that coalesces concurrent requests and preserves the last successful value;
- browser polling that reaches the server coordinator without a second CDN freshness clock.

Failed refreshes keep stale data for a bounded hour and back off from 30 seconds to five minutes. Diagnostics expose cache state, source, last attempt, last success, consecutive failures, and next retry.

This is a strong baseline for derived-data availability, not a general durable job engine.

### gh-tidy-branches

Relevant reviewed paths:

- `README.md`
- `docs/ARCHITECTURE.md`
- scanner and live-workflow tests

The command separates bounded concurrent observation from serial mutation. Eligibility requires the current branch SHA to equal the head SHA recorded by the merged pull request. The tool refreshes open pull requests and re-reads each exact ref immediately before deletion.

After successful deletion, it records an atomic local undo receipt. Undo never overwrites a newly recreated branch.

GitHub's delete-ref endpoint lacks an expected-SHA precondition. This creates a remaining compare-then-delete race. That is an API capability boundary rather than evidence of a GitHub defect. A dependency campaign waits for a direct fault-injection reproduction.

### Botany Sim

Relevant reviewed paths:

- `README.md`
- `docs/GARDEN_CALENDAR.md`
- garden calendar validation and tests

A serialized calendar pins its calendar ID, generator version, and time mode. It stores last evaluated day, pending events, and history. Event occurrence identity combines calendar, generator, mode, event, and year.

Offline catch-up uses absolute elapsed seconds. Repeated active advances and one offline jump produce the same state. Missing an active event window changes presentation, not ownership of the pending event.

Migration between calendar versions or time modes is explicit and currently absent. That is a product-state migration concern, not a worker retry campaign.

### Make Good TV

Relevant reviewed paths:

- `README.md`
- `AGENT-PLAY.md`
- deterministic game and controller tests

The shared session layer owns transport and audit identity only:

- deterministic session ID;
- game, seed, seat, and controller;
- monotonically increasing decision number;
- copied observation;
- copied applied action;
- host acceptance;
- context events;
- terminal outcome;
- telemetry.

The game host remains authoritative for legal actions and consequences. Stale, cross-session, malformed, cyclic, or state-illegal submissions fail into visible safe fallbacks.

The architecture intentionally uses one isolated process per low-frequency model decision. A persistent worker or MCP service remains gated on real latency, cost, invalid-action, and replay evidence.

### Quarry

Relevant reviewed paths:

- `README.md`
- `AGENTS.md`
- `docs/paper-trading.md`
- verification execution binding introduced at `f8824c62c57ddaa05ce59bd9d09a6aa6fde269b3`

Paper sessions persist strategy state, pending targets, cash, position, risk state, and signal observation time. Every transition appends sequence, previous hash, details, and resulting state to `events.jsonl`.

The state snapshot is a cache. Missing or stale state is rebuilt from the verified event chain. Modified events fail loading. Mutating commands use a non-blocking session lock. The kill switch cancels pending targets and halts future processing without inventing a liquidation price for an existing simulated position.

The current verification binding adds content-addressed immutable requests and receipts tied to:

- exact attempt identity;
- source and completion state identity and revision;
- repository, base, branch, workspace, and head;
- supervisor;
- profile, suite, and command manifest;
- validated terminal profile receipt bytes.

Verification completion remains separate from attempt completion. The verification runner owns command execution; the attempt store owns state, heartbeat, cancellation, and handoff. This is the strongest current portfolio example of explicit ownership separation.

Live trading and order authority remain outside the scout and outside the current product boundary.

## Property selected after the maps

The useful common property is **authority after interruption**:

1. Which logical identity survives?
2. Which component owns durable state?
3. Which component owns the actual effect?
4. What evidence survived?
5. Can cancellation establish effect outcome, or only stop future work?
6. Does recovery read a receipt, rebuild a projection, reset a cursor, reobserve a host, serve stale data, replay deterministic actions, or return to an authoritative source?
7. Which missing evidence can cause a duplicate, contradiction, silent loss, or false terminal claim?

This property compares the systems while preserving their different architecture families.

## Runnable experiment

Artifacts:

- `artifacts/authority_after_interruption.py`
- `artifacts/latest.json`

Run:

```text
python3 programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/authority_after_interruption.py
```

Environment used for the retained output:

```text
Python 3.13.5
network: disabled
inputs: synthetic profiles derived from pinned owned-system source
```

The model contains thirteen boundaries across twelve systems:

1. Stensibly local ledger.
2. Stensibly external runner.
3. Smolrunner host execution.
4. Proofwake observation ledger.
5. Days Upon Google synchronization.
6. Renderprove browser review.
7. Starsector Preflight run.
8. Elatura derived cache.
9. Scrapbook GitHub activity cache.
10. gh-tidy-branches deletion.
11. Botany Sim garden calendar.
12. Make Good TV agent session.
13. Quarry paper and verification execution.

Assertions verify:

- all twelve systems are represented;
- every boundary declares logical identity, state owner, effect owner, and surviving evidence;
- four concrete application campaigns;
- four reusable baselines;
- five retained architecture patterns;
- explicit portfolio stop decisions.

The model does not execute the repositories or prove deployed behaviour.

## Application design findings

### A1. Stensibly external-runner reconciliation gap

**Current behaviour:** Stensibly can retain a stable local run and external operation reference, then reconcile a stale lease to `abandoned`.

**Risk:** The external executor may have committed an effect before acknowledgement disappeared. Replacement work may duplicate or contradict it.

**Owning boundary:** Stensibly runner integration, external operation adapter, and replacement policy.

**Campaign evidence:** A synthetic external runner commits one effect, loses acknowledgement, lets the lease expire, and receives a replacement attempt. Read-back must produce one final disposition and block a second effect until reconciliation resolves.

**Decision:** campaign.

### A2. Smolrunner attempt, journal, and receipt gap

**Current behaviour:** Durable attempt state and execution journals preserve uncertainty. A receipt contract exists without complete live mapping, publication, and read-back.

**Risk:** A coordinator lacks one durable terminal record joining accepted request, exact execution attempt, journal, and outcome.

**Owning boundary:** Personal-worker broker, execution lane, receipt adapter, and receipt store.

**Campaign evidence:** Interrupt after executor return and before terminal publication. Restart under the same execution ID. The system must return one terminal receipt or `fresh_observation_required` and prevent a second executor call until current evidence authorizes it.

**Decision:** campaign.

### A3. Days Upon durable provider-mutation outbox gap

**Current behaviour:** Pull sync persists tokens and baselines. Provider 410 resets to a full sync. Push sync directly issues sequential delete, update, and create calls.

**Risk:** Provider acceptance followed by process loss or local storage failure can leave an ambiguous mutation. Retrying from a stale baseline can duplicate creation or repeat an update/delete without a durable operation disposition.

**Owning boundary:** Days Upon synchronization engine and local/provider mutation state.

**Campaign evidence:** For create, update, and delete, inject interruption after provider acceptance and before local baseline publication. Restart from durable local state. The system must reconcile by stable operation or provider identity and produce exactly one accepted terminal disposition.

**Required design evidence:**

- durable outbox operation ID;
- exact semantic fingerprint;
- attempt and retry budget;
- provider request identity where available;
- acknowledgement and reconciliation state;
- cancellation semantics for queued versus already accepted mutations;
- terminal read-back and user-visible conflict state.

**Decision:** campaign.

### A4. Renderprove interruption-safe receipt publication gap

**Current behaviour:** Runtime shutdown is protected with `finally`, then a receipt is constructed and written directly after browser review returns.

**Risk:** Process loss or cancellation before receipt publication can leave screenshots, browser diagnostics, or a stopped runtime without a durable terminal or interrupted record. A direct write also lacks an explicit atomic publication contract.

**Owning boundary:** Renderprove review service and receipt store.

**Campaign evidence:** Allocate a stable review ID and initial run manifest before starting the runtime. Inject interruption:

1. after runtime start;
2. after one or more case artifacts;
3. after runtime stop;
4. during terminal receipt publication.

On restart, exact read-back must return one of:

- terminal passed or failed receipt;
- explicit interrupted receipt with completed case evidence;
- safe resumable plan under the same review identity;
- bounded rerun authorization that cannot confuse old artifacts with the new attempt.

**Decision:** campaign.

### A5. Shared correlation envelope

Useful cross-system fields:

- `logical_job_id` or domain-equivalent identity;
- `attempt_id`;
- `operation_id`;
- state revision, generation, cursor, or journal revision;
- effect-owner reference;
- cancellation or kill-switch identity;
- terminal receipt or audit-chain head;
- reconciliation disposition;
- source and ingestion timestamps;
- explicit authority owner.

These fields have different domain names and semantics. They are acceptance criteria inside the four campaigns rather than a universal schema library.

**Decision:** retain.

## Reusable baselines

### B1. Stensibly local operation receipts

Use as the commit-before-response ambiguity baseline for locally owned ledger writes.

### B2. Proofwake append-only observation recovery

Use as the immutable-fact/rebuildable-projection baseline. Durable observations survive while projections remain disposable.

### B3. Scrapbook stale-while-error coordination

Use as the derived-data availability baseline. Keep last known good data, expose staleness, coalesce work, and back off visibly.

### B4. Quarry audit-chain and attempt-bound receipts

Use as the strongest identity and recovery baseline:

- rebuild state from verified immutable history;
- separate snapshot cache from source ledger;
- bind verification requests and receipts to exact attempt states;
- separate verification completion from attempt completion;
- keep execution and state-transition authority distinct.

## Retained architecture patterns

### R1. Starsector Preflight run-directory finalization

Retain staged raw evidence plus final lifecycle summaries. Open a campaign only after direct interruption reveals a recovery failure.

### R2. Elatura authoritative fallback

Retain the rule that derived cache failure returns to the authoritative source and never authorizes unsafe partial behaviour.

### R3. gh-tidy-branches live revalidation and undo

Retain exact-head revalidation and conservative undo receipt. Track conditional GitHub ref deletion as a lower-level capability request, not a defect claim.

### R4. Botany Sim deterministic offline catch-up

Retain absolute-time advancement, preserved pending events, and explicit version/mode identity for persistent simulations.

### R5. Make Good TV deterministic session replay

Retain host authority, copied observations, monotonically ordered decisions, applied-action traces, and safe rejection fallbacks.

## Dependency, SDK, platform, and runtime findings

The scout found no direct lower-level contract violation in:

- SQLite or Convex;
- Rust or Unix filesystem primitives;
- Google Calendar API;
- browser local storage;
- Playwright or Chromium;
- Java, JFR, or child-process lifecycle;
- Next.js or Vercel;
- GitHub webhooks or contribution APIs;
- Firefox extension APIs;
- GitHub refs;
- Python filesystem and process primitives.

One documented capability boundary is relevant: GitHub's delete-reference API does not accept an expected SHA. gh-tidy-branches narrows the race with immediate live revalidation and serial deletion. This is not evidence of a GitHub defect.

A lower-level campaign requires a direct fault injection that reproduces violation of a documented dependency, SDK, platform, or runtime contract.

## Ranked decisions

1. **Campaign — Stensibly external-runner reconciliation before replacement.**
2. **Campaign — Smolrunner personal-worker attempt, journal, and terminal-receipt integration.**
3. **Campaign — Days Upon durable provider-mutation outbox and reconciliation.**
4. **Campaign — Renderprove interruption-safe terminal receipts.**
5. **Baseline — Quarry audit-chain recovery and attempt-bound verification receipts.**
6. **Baseline — Proofwake immutable observations and rebuildable projections.**
7. **Baseline — Stensibly local operation receipts.**
8. **Baseline — Scrapbook stale-while-error coordinator.**
9. **Retain — Starsector Preflight run-directory finalization.**
10. **Retain — Elatura authoritative fallback cache contract.**
11. **Retain — gh-tidy-branches live revalidation and undo receipts.**
12. **Retain — Botany Sim deterministic offline catch-up.**
13. **Retain — Make Good TV deterministic session replay.**
14. **Retain — shared correlation envelope inside campaigns.**
15. **Stop — one universal durable-workflow or retry library across the portfolio.**
16. **Stop — treating caches, simulations, or evidence indexes as background workers.**
17. **Stop — dependency, SDK, platform, or runtime attribution without reproduction.**
18. **Stop — Elatura private-content persistence before its product and security gate.**
19. **Stop — Make Good TV persistent worker or MCP before live-model evidence justifies it.**
20. **Stop — Quarry live trading, exchange credentials, or order authority in this programme.**

## Negative results and uncertainty

- The portfolio does not share one durable-work architecture.
- Retry policy is secondary to effect ownership and surviving evidence.
- A cache fallback, deterministic simulation replay, evidence projection rebuild, provider sync reset, undo receipt, and worker recovery are different operations.
- Strong observability does not automatically create recovery authority.
- A terminal receipt is useful only when its publication boundary is itself durable or its absence is distinguishable.
- Days Upon has durable pull cursors and baselines but lacks a durable provider mutation outbox.
- Renderprove has a strong receipt schema but a post-hoc publication boundary.
- Proofwake and Quarry already provide stronger recovery baselines than the original two-system scout captured.
- Starsector Preflight, Elatura, Scrapbook, gh-tidy-branches, Botany Sim, and Make Good TV add reusable patterns without all becoming worker campaigns.
- The synthetic model establishes decision differences, not deployed consequences.
- Private repositories were read through authorized GitHub access; no private content or data was copied into the report beyond architecture and contract facts.

## Verification

Local retained-artifact verification:

```text
python3 artifacts/authority_after_interruption.py
```

Result:

- passed under Python 3.13.5;
- represented thirteen boundaries across twelve systems;
- produced four campaigns, four baselines, and five retained system patterns;
- generated output matched `artifacts/latest.json` before publication.

Repository CI should validate the exact final PR head for:

- Fieldwork integrity;
- external reference policy.

## Handoff

- Strongest finding: the active portfolio is better described as a set of recovery-authority patterns than a set of retrying workers.
- Newly added high-value systems: Proofwake, Days Upon, Renderprove, Starsector Preflight, Elatura, Scrapbook, gh-tidy-branches, Botany Sim, Make Good TV, and Quarry.
- Strongest new baseline: Quarry's verified audit-chain rebuild and attempt-bound verification receipts.
- Strongest new campaign: Days Upon's durable provider-mutation outbox.
- Most concrete new interruption gap: Renderprove writes its terminal receipt only after review completion and runtime shutdown.
- Durable artifacts:
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/report.md`
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/authority_after_interruption.py`
  - `programmes/data-durable-workflows/scouts/owned-durable-workflow-architecture/artifacts/latest.json`
- Dependencies:
  - A1 needs a synthetic external runner adapter.
  - A2 needs live receipt mapping, persistence, read-back, and interruption injection.
  - A3 needs a fake provider with accepted-but-unacknowledged mutation injection.
  - A4 needs interruption hooks around runtime start, case artifact publication, shutdown, and receipt publication.
- Decision needed: promote A1 through A4 as separate owned-system campaigns.
- PR #36 remains closed and excluded.
- Upstream contact remains unauthorized.
