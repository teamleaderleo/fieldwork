# Owned-project open-source opportunity and testbed map

## In simple words

The active owned portfolio is a standing R&D backdrop for Fieldwork. Each project can suggest open-source libraries, SDKs, runtimes, developer tools, storage systems, and design approaches worth examining—even when the project does not use them yet.

The useful sequence is broader than “pick a library, then find a testbed”:

1. inspect what an active project does now and may plausibly need next;
2. brainstorm relevant open-source categories and specific projects;
3. quietly audit promising candidates for architecture, contracts, tests, failure boundaries, and contribution opportunities;
4. run small distinguishing probes where useful;
5. use the owned project as a realistic integration testbed only when adoption or lifecycle evidence becomes worthwhile.

A prospective connection is enough to create an R&D lead. It is not enough to claim real usage, user demand, an upstream defect, or an approved integration.

The architecture findings from issue #29 remain useful as case-study evidence. They do not automatically create implementation campaigns in the owned repositories.

## Four roles for an owned repository

### 1. Opportunity source

The repository reveals domains and seams where open-source work may become relevant.

Examples:

- Days Upon suggests local-first databases, sync engines, browser persistence, calendar SDKs, and conflict-resolution libraries.
- Starsector Preflight suggests Java profiling, archive handling, packaging, filesystem scanning, and updater libraries.
- Make Good TV suggests model SDKs, structured-output systems, agent runtimes, model gateways, and sandboxed workers.

This role supports brainstorming and target discovery. It does not require an existing dependency or immediate implementation plan.

### 2. Prospective target context

The repository explains why a library or platform might matter to us if Fieldwork audits it.

A scout may examine a promising external project before integration exists, while clearly labelling the owned-project connection as prospective. The audit should answer whether the candidate is architecturally relevant, mature enough to try, interesting for R&D, or unlikely to fit.

No `testbed:*` label is used at this stage.

### 3. External-target testbed

The repository exercises a separate Fieldwork target under realistic conditions.

Example shape:

```text
external target: Playwright
owned testbed: Renderprove
scenario: browser process lifecycle, screenshots, teardown, and receipt publication
result: integration evidence about Playwright plus an optional Renderprove improvement
```

Use `target:<external-target>` and add `testbed:<owned-project>` only after a real controlled trial begins.

### 4. Architecture case study or owned-project target

The repository may supply an existing pattern, failure model, or acceptance criterion without implying a change. Examples include Quarry audit-chain recovery, Proofwake immutable observations, Scrapbook stale-while-error behaviour, and Botany Sim deterministic offline catch-up.

The repository itself becomes a direct target only after a concrete consequential problem is selected deliberately. An interesting source observation is a lead, not an automatic campaign.

## Practical opportunity-selection test

For a prospective open-source target, answer:

1. Which active owned project suggests this target or category?
2. Is the connection current, planned, plausible, or merely illustrative?
3. What capability, lifecycle, or design direction makes the target interesting?
4. What can a source audit establish before any integration is attempted?
5. What would make the candidate worth a small probe or realistic trial?
6. What evidence would make us reject or defer it?
7. Could a later experiment improve the project even if upstream work stops?
8. Can all research remain local, synthetic, public, or redacted?

A target does not need to solve an urgent current defect. It should have a credible relationship to active project work or a plausible future direction. Fieldwork should avoid completely manufactured relevance, but it should permit exploratory R&D.

## Portfolio opportunity map

| Owned project | Current or plausible workload | Strong current Fieldwork target matches | Prospective open-source discovery areas | What an early audit could establish | What a later testbed adds | Possible retained value | Safety and scope boundary |
|---|---|---|---|---|---|---|---|
| Stensibly | Multi-user coordination, run ownership, MCP and REST operations, hosted and local state | MCP TypeScript SDK, Codex, Gemini CLI, OpenTelemetry JS | agent SDKs, auth/OAuth libraries, realtime backends, durable execution adapters, workflow engines | whether identity, capability, auth, realtime, and recovery contracts fit coordinated work | concurrent users, persisted coordination state, approvals, cancellation, reconnect, and external executor boundaries | production-quality integration, diagnostics, adapter, or regression fixture | isolated accounts and synthetic effects; no production mutation or upstream contact by default |
| Smolrunner | Local CLI execution, process observation, journals, reservations, cancellation, and restart | Codex, Gemini CLI, MCP TypeScript SDK, OpenTelemetry JS | terminal libraries, process-control crates, local databases, VM APIs, sandbox systems, structured logging | whether process, state, cancellation, and local durability models align with a machine steward | real machine state, subprocess lifecycle, durable local documents, and operator-facing recovery | stronger executor adapter, receipt support, tracing integration, or compatibility test | synthetic commands and disposable machines; no destructive host action |
| Proofwake | Evidence ingestion, immutable observations, webhooks, projections, CLI, dashboard, and MCP reads | OpenTelemetry JS, MCP TypeScript SDK, Supabase | event stores, schema validators, webhook frameworks, content-addressed storage, projection engines | whether candidate systems preserve source identity, immutable facts, replay, and bounded ingestion | duplicate delivery, conflicting identity, partial ingestion, projection rebuild, and source provenance | new source adapter, observation schema, event backend, or regression corpus | synthetic or public evidence only; producer authority remains external |
| Days Upon | Local-first calendar state, provider synchronization, browser persistence, offline use, and conflicts | Supabase, Vite, Playwright | local-first databases, sync engines, calendar SDKs, IndexedDB wrappers, CRDTs, conflict-resolution libraries | whether a candidate can represent offline state, provider identity, merge semantics, and migration | real create/update/delete reconciliation, offline restart, provider cursors, and user-visible conflicts | replace or improve storage/sync layer, retain a provider adapter, or reject an unsuitable model | fake providers and synthetic calendars; no production calendar or account data |
| Renderprove | Browser verification, local runtime startup, route matrices, screenshots, diagnostics, and receipts | Playwright, Vite, Workers SDK | browser automation libraries, image-diff tools, local server runners, artifact stores, container browser systems | whether lifecycle, artifact, browser-isolation, and reporting contracts fit bounded review work | multi-case browser lifecycle, teardown, partial artifacts, deterministic review manifests, and operator evidence | better verifier backend, receipt format, artifact store, or reproducible browser fixture | local synthetic sites; no unrelated production deployment |
| Starsector Preflight | Java child processes, JFR profiling, filesystem scanning, packaging, caches, and run directories | no strong current hub; possible cross-check with agent CLI process work | JFR tooling, Java CLI frameworks, archive libraries, filesystem watchers, cache libraries, packaging and updater tools | whether candidates handle large trees, long-running children, profiling data, packaging, and cross-platform constraints | large real filesystem, long-lived child process, profiling evidence, cache invalidation, and packaging | faster scanner, better profiler integration, archive backend, or packaging compatibility suite | synthetic fixtures where possible; do not require private game data in public evidence |
| Elatura | Browser extension observation, content provenance, cache compatibility, privacy gates, and fallback | Vite, Playwright, Workers SDK where extension tooling overlaps | extension frameworks, Firefox and Chromium APIs, storage wrappers, provenance libraries, privacy-preserving transforms | whether candidate frameworks preserve browser authority, origin isolation, versioning, and privacy constraints | browser profiles, extension lifecycle, authenticated-page authority, version drift, and privacy boundaries | safer extension adapter, cache envelope, provenance mechanism, or compatibility matrix | no private page content persistence before an explicit product and security gate |
| Scrapbook | Server-rendered web application, GitHub activity fetching, cache fallback, browser polling, and deployment | Vite, Playwright, Workers SDK, OpenTelemetry JS | Next.js and deployment adapters, cache libraries, GitHub clients, rate-limit helpers, data-fetching libraries | whether caching, request coalescing, rate-limit, deployment, and observability models suit the product | real server/browser freshness layers, stale data, rate limits, deployment configuration, and user-facing availability | retained cache strategy, deployment adapter, client replacement, or observability instrumentation | public or synthetic activity; no hidden user data or automatic production release |
| gh-tidy-branches | GitHub API scanning, bounded concurrency, destructive mutation, exact-head checks, CLI UX, and undo | Codex and Gemini CLI for tool execution; OpenTelemetry JS only if instrumentation is justified | Octokit and GitHub API clients, CLI frameworks, policy engines, transactional command libraries, approval systems | whether clients and command frameworks expose safe preconditions, retries, permissions, and audit hooks | actual API races, dry-run/apply distinction, serial mutation, permission errors, and conservative undo | safer command engine, API capability finding, policy integration, or reusable fixture | test repositories only; never run destructive trials against valuable branches |
| Botany Sim | Persistent deterministic simulation, absolute time, offline catch-up, versioned generators, and migrations | Vite and Playwright for application lifecycle | state-machine libraries, deterministic RNG, persistence layers, migration tools, time simulation libraries | whether candidates preserve determinism, save compatibility, replay, and explicit migration identity | long-term state evolution, clock jumps, replay equivalence, save compatibility, and user-facing history | adopted state library, migration mechanism, time model, or deterministic regression suite | synthetic worlds only; preserve exact generator and save versions |
| Make Good TV | Deterministic games, model/controller adapters, copied observations, applied actions, replay, and safe fallbacks | Vercel AI SDK, MCP TypeScript SDK, Codex, Gemini CLI | model gateways, structured-output libraries, agent runtimes, sandboxed workers, evaluation frameworks | whether model-facing libraries preserve host authority, schema handling, cancellation, cost control, and replayability | adversarial model output, stale decisions, host authority, deterministic replay, and end-to-end controller ergonomics | new controller adapter, evaluation harness, gateway, or safe model integration | deterministic local games first; paid or live model calls require explicit approval |
| Quarry | Analytical research, deterministic experiments, walk-forward evaluation, paper sessions, audit chains, and verification receipts | DuckDB, OpenTelemetry JS where trace evidence helps | dataframe and Parquet libraries, experiment trackers, schedulers, content-addressed artifact stores, numerical and optimization libraries | whether candidates preserve determinism, data identity, reproducibility, interruption handling, and audit evidence | substantial analytical workloads, reproducibility, interruption, state rebuild, and audit requirements | faster analytical backend, experiment integration, scheduler, or verification fixture | paper and synthetic execution only; no live trading, credentials, or order authority |
| Baxtori | Repository collection, cursor-based history, model review, exact code evidence, publication, accounts, browser tests, and deployment | Codex, Vercel AI SDK, Playwright, Supabase where storage/auth fits | GitHub App clients, content-addressed stores, job schedulers, model gateways, search/index systems, auth and account stores | whether candidates preserve untrusted-input boundaries, repository identity, exact evidence, search quality, and publication authority | multi-repository evidence collection, history rewrite, strict validation, publication, reader state, and browser lifecycle | better collector, reviewer, search, account, scheduler, or publishing component | use selected repositories and bounded evidence; keep collection, model review, and publication authority separate |

## Opportunity-oriented views

### Agent, model, and tool execution

Best project backdrops:

- Stensibly for coordinated, persistent, multi-user agent work.
- Smolrunner for local process execution and recovery.
- Make Good TV for deterministic model decisions and replay.
- Baxtori for model judgment over untrusted repository evidence.
- gh-tidy-branches for permissioned, potentially destructive tool execution.

Targets and discovery areas:

- Codex and Gemini CLI lifecycle;
- MCP TypeScript SDK;
- Vercel AI SDK and other model SDKs;
- structured output and schema libraries;
- model gateways and provider adapters;
- approval, sandbox, and tool-policy systems;
- agent memory, evaluation, and orchestration libraries.

The practical question is not merely whether a model can call a tool. It is whether identity, authority, cancellation, result delivery, replay, cost, and operator evidence can remain coherent in an actual project.

### Browser, web runtime, and visual verification

Best project backdrops:

- Renderprove for browser control and artifacts.
- Scrapbook for server/browser caching and deployment.
- Elatura for extension and web-platform boundaries.
- Days Upon for offline browser persistence and synchronization.
- Baxtori for authenticated web state, exact evidence views, and browser testing.

Targets and discovery areas:

- Playwright;
- Vite;
- Workers SDK;
- browser-extension frameworks;
- local server runners;
- image-diff and artifact tooling;
- deployment and preview platforms;
- client-state and offline persistence libraries.

### Data, storage, synchronization, and analytics

Best project backdrops:

- Quarry for analytical engines, artifacts, and reproducibility.
- Days Upon for local-first storage and provider synchronization.
- Proofwake for append-only ingestion and rebuildable views.
- Scrapbook for stale-while-error derived data.
- Botany Sim for persistent versioned state and migrations.
- Baxtori for indexed evidence, account data, and publication state.

Targets and discovery areas:

- DuckDB;
- Supabase;
- local-first and embedded databases;
- event stores and content-addressed stores;
- IndexedDB wrappers;
- schema and migration tools;
- Parquet, dataframe, and experiment-tracking libraries;
- search, indexing, synchronization, and CRDT systems.

### Processes, filesystems, profiling, and packaging

Best project backdrops:

- Smolrunner for local execution and host observation.
- Starsector Preflight for Java process and profiling evidence.
- Renderprove for local server and browser process teardown.
- gh-tidy-branches for bounded concurrent reads and serial mutation.
- Quarry for deterministic parallel evaluation and atomic artifacts.

Targets and discovery areas:

- process-control and terminal libraries;
- JFR and Java profiling tools;
- filesystem watchers and atomic-write libraries;
- archive, package, and updater systems;
- schedulers and bounded-concurrency primitives;
- sandbox, VM, and container execution APIs.

### Observability, evidence, and verification

Best project backdrops:

- Proofwake for immutable observations and projections.
- Renderprove for bounded review receipts.
- Quarry for audit-chain rebuild and attempt-bound verification.
- Baxtori for evidence packs, strict claim validation, and publication receipts.
- Stensibly and Smolrunner for execution identity and recovery evidence.

Targets and discovery areas:

- OpenTelemetry JS;
- structured logging and trace correlation;
- receipt and provenance formats;
- event ingestion and projection libraries;
- artifact signing and content addressing;
- audit logging, replay, and verification systems.

## How a new library enters Fieldwork

### Step 1: Read the active project surface

Record both current and plausible future directions, such as:

- calendar state may need a stronger offline sync model;
- browser evidence may need a different artifact backend;
- repository review may benefit from another search or scheduling system;
- analytical runs may benefit from a columnar or experiment-tracking library;
- a local executor may eventually need a different process or sandbox abstraction;
- a simulation may need versioned state migration.

The direction may be exploratory. Label it as current, planned, plausible, or illustrative.

### Step 2: Generate opportunity leads

Identify open-source categories and concrete projects that might fit. This is allowed before any adoption decision.

A useful lead records:

- the owned project that inspired it;
- the prospective capability or seam;
- why the external project is technically interesting;
- what a quiet source audit should determine;
- what evidence would justify or reject further work.

### Step 3: Quietly audit promising targets

Read architecture, implementation, tests, public contracts, recent changes, contribution policy, and known failure boundaries. The audit may end with:

- relevant and worth probing;
- interesting as a case study only;
- unsuitable for the project;
- mature and sound with no contribution opportunity;
- a concrete external question deserving a scout or campaign.

Do not claim actual use merely because an owned project supplied the motivation.

### Step 4: Run the smallest distinguishing probe

Use a playground to eliminate unsuitable options or isolate one contract. A synthetic probe is useful at this stage, but it is not the final evidence when application lifecycle matters.

### Step 5: Run an owned integration trial when useful

Pin target and testbed revisions. Record baseline, candidate, failure paths, ergonomics, resource behaviour, cleanup, and what the trial omits.

### Step 6: Keep a useful result even without upstream work

Possible outcomes:

- adopt the library or feature in the owned project;
- retain a compatibility or regression fixture;
- reject or defer the library with a durable reason;
- publish a Fieldwork finding or architecture case study;
- open a deeper campaign;
- prepare an upstream packet only after explicit authorization.

## Activation rules

An opportunity lead or source audit does not create `testbed:*` labels, integration branches, or claims of real adoption.

A quiet external-target scout may begin when it has:

- a credible current or prospective connection to one or more active projects;
- a bounded architectural or behavioural question;
- clear labelling of whether project relevance is current, planned, plausible, or illustrative;
- a useful stop condition;
- no fabricated usage or consequence claim.

Activate an owned integration trial only when it has:

- one external target;
- one owned testbed;
- one realistic scenario;
- exact source revisions;
- a baseline and distinguishing outcome;
- reversible setup and cleanup;
- a result useful to the project or the research programme.

An owned-project observation becomes a direct lead only when it states current behaviour, concrete consequence, likely owning boundary, and a falsifiable evidence path. It becomes a campaign only after a deliberate priority decision.

## Disposition of issue #29 findings

- Use the active projects as standing opportunity sources for brainstorming and triaging current and future open-source targets.
- Permit quiet audits based on prospective relevance before an integration exists, while labelling that relevance honestly.
- Retain the twelve-system interruption comparison as an architecture case study.
- Add Baxtori as a later case-study and opportunity source, not as a retroactive input to the verified model.
- Treat the Stensibly, Smolrunner, Days Upon, and Renderprove internal questions as dormant leads unless separately prioritized.
- Use this map as the primary continuation surface for selecting audits, probes, and realistic testbeds.
- Do not build a universal workflow abstraction from the portfolio.
- Do not manufacture a usage claim or integration merely to justify work on an external repository.
