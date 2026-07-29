# Owned repository testbed suitability map

## In simple words

The owned portfolio is not primarily a backlog of internal defects. It is a set of realistic places to evaluate open-source libraries, SDKs, runtimes, developer tools, storage systems, and design ideas.

A useful Fieldwork target should connect to an actual project need:

- a real lifecycle or integration boundary exists;
- the owned project can provide a baseline that a toy case cannot;
- the experiment is reversible and safe;
- success could become a useful project feature, regression test, or informed rejection;
- the result explains why the target matters to us even when no upstream contribution follows.

The architecture findings from issue #29 remain useful as case-study evidence. They do not automatically create implementation campaigns in the owned repositories.

## Three roles for an owned repository

### 1. External-target testbed

The repository exercises a separate Fieldwork target under realistic conditions.

Example shape:

```text
external target: Playwright
owned testbed: Renderprove
scenario: browser process lifecycle, screenshots, teardown, and receipt publication
result: integration evidence about Playwright plus an optional Renderprove improvement
```

Use `target:<external-target>` and add `testbed:<owned-project>` only after a real trial begins.

### 2. Architecture case study

The repository supplies an existing pattern, failure model, or acceptance criterion. No project change is implied.

Examples include Quarry audit-chain recovery, Proofwake immutable observations, Scrapbook stale-while-error behaviour, and Botany Sim deterministic offline catch-up.

### 3. Owned-project target

The repository itself becomes the subject only after a concrete consequential problem is selected deliberately. An interesting source observation is a lead, not an automatic campaign.

## Practical target-selection test

Before choosing an external library or platform, answer:

1. Which owned project has a natural integration seam for it?
2. What realistic behaviour does that project preserve that a toy test omits?
3. What baseline can be measured before introducing or changing the target?
4. Could the experiment improve the project even if upstream work stops?
5. What result would make us remove or reject the target?
6. Can the trial run locally or in an isolated test environment without private or production data?

A target with no convincing answers is probably curiosity, not yet Fieldwork.

## Portfolio map

| Owned project | Realistic workload or lifecycle | Strong current Fieldwork target matches | Useful future target discovery | What the testbed adds beyond a toy | Possible retained value | Safety and scope boundary |
|---|---|---|---|---|---|---|
| Stensibly | Multi-user coordination, run ownership, MCP and REST operations, hosted and local state | MCP TypeScript SDK, Codex, Gemini CLI, OpenTelemetry JS | agent SDKs, auth/OAuth libraries, realtime backends, durable execution adapters | concurrent users, persisted coordination state, approvals, cancellation, reconnect, and external executor boundaries | production-quality integration, diagnostics, or regression fixture | isolated accounts and synthetic effects; no production mutation or upstream contact by default |
| Smolrunner | Local CLI execution, process observation, journals, reservations, cancellation, and restart | Codex, Gemini CLI, MCP TypeScript SDK, OpenTelemetry JS | terminal libraries, process-control crates, local databases, VM and sandbox APIs | real machine state, subprocess lifecycle, durable local documents, and operator-facing recovery | stronger executor adapter, receipt support, or host compatibility test | synthetic commands and disposable machines; no destructive host action |
| Proofwake | Evidence ingestion, immutable observations, webhooks, projections, CLI, dashboard, and MCP reads | OpenTelemetry JS, MCP TypeScript SDK, Supabase | event stores, schema validators, webhook frameworks, content-addressed storage | duplicate delivery, conflicting identity, partial ingestion, projection rebuild, and source provenance | new source adapter, observation schema, or regression corpus | synthetic or public evidence only; producer authority remains external |
| Days Upon | Local-first calendar state, provider synchronization, browser persistence, offline use, and conflicts | Supabase, Vite, Playwright | local-first databases, sync engines, calendar SDKs, IndexedDB wrappers, conflict-resolution libraries | real create/update/delete reconciliation, offline restart, provider cursors, and user-visible conflicts | replace or improve storage/sync layer, or retain a provider adapter | fake providers and synthetic calendars; no production calendar or account data |
| Renderprove | Browser verification, local runtime startup, route matrices, screenshots, diagnostics, and receipts | Playwright, Vite, Workers SDK | browser automation libraries, image-diff tools, local server runners, artifact stores | multi-case browser lifecycle, teardown, partial artifacts, deterministic review manifests, and operator evidence | better verifier backend, receipt format, or reproducible browser fixture | local synthetic sites; no unrelated production deployment |
| Starsector Preflight | Java child processes, JFR profiling, filesystem scanning, packaging, caches, and run directories | no strong current hub; possible cross-check with agent CLI process work | JFR tooling, Java CLI frameworks, archive libraries, filesystem watchers, packaging and updater tools | large real filesystem, long-lived child process, profiling evidence, cache invalidation, and cross-platform packaging | faster scanner, better profiler integration, or packaging compatibility suite | synthetic fixtures where possible; do not require private game data in public evidence |
| Elatura | Browser extension observation, content provenance, cache compatibility, privacy gates, and fallback | Vite, Playwright, Workers SDK where extension tooling overlaps | extension frameworks, Firefox and Chromium APIs, storage wrappers, provenance libraries, privacy-preserving transforms | browser profiles, extension lifecycle, authenticated-page authority, version drift, and privacy boundaries | safer extension adapter, cache envelope, or compatibility matrix | no private page content persistence before an explicit product and security gate |
| Scrapbook | Server-rendered web application, GitHub activity fetching, cache fallback, browser polling, and deployment | Vite, Playwright, Workers SDK, OpenTelemetry JS | Next.js and deployment adapters, cache libraries, GitHub clients, rate-limit helpers | real server/browser freshness layers, stale data, rate limits, deployment configuration, and user-facing availability | retained cache strategy, deployment adapter, or observability instrumentation | public or synthetic activity; no hidden user data or automatic production release |
| gh-tidy-branches | GitHub API scanning, bounded concurrency, destructive mutation, exact-head checks, CLI UX, and undo | Codex and Gemini CLI for tool execution; OpenTelemetry JS only if instrumentation is justified | Octokit and GitHub API clients, CLI frameworks, policy engines, transactional command libraries | actual API races, dry-run/apply distinction, serial mutation, permission errors, and conservative undo | safer command engine, API capability finding, or reusable fixture | test repositories only; never run destructive trials against valuable branches |
| Botany Sim | Persistent deterministic simulation, absolute time, offline catch-up, versioned generators, and migrations | Vite and Playwright for application lifecycle | state-machine libraries, deterministic RNG, persistence layers, migration tools, time simulation libraries | long-term state evolution, clock jumps, replay equivalence, save compatibility, and user-facing history | adopted state library, migration mechanism, or deterministic regression suite | synthetic worlds only; preserve exact generator and save versions |
| Make Good TV | Deterministic games, model/controller adapters, copied observations, applied actions, replay, and safe fallbacks | Vercel AI SDK, MCP TypeScript SDK, Codex, Gemini CLI | model gateways, structured-output libraries, agent runtimes, sandboxed worker APIs | adversarial model output, stale decisions, host authority, deterministic replay, and end-to-end controller ergonomics | new controller adapter, evaluation harness, or safe model integration | deterministic local games first; paid or live model calls require explicit approval |
| Quarry | Analytical research, deterministic experiments, walk-forward evaluation, paper sessions, audit chains, and verification receipts | DuckDB, OpenTelemetry JS where trace evidence helps | dataframe and Parquet libraries, experiment trackers, schedulers, content-addressed artifact stores, numerical and optimization libraries | substantial analytical workloads, reproducibility, interruption, state rebuild, and audit requirements | faster analytical backend, reproducible experiment integration, or verification fixture | paper and synthetic execution only; no live trading, credentials, or order authority |
| Baxtori | Repository collection, cursor-based history, model review, exact code evidence, publication, accounts, browser tests, and deployment | Codex, Vercel AI SDK, Playwright, Supabase where storage/auth fits | GitHub App clients, content-addressed stores, job schedulers, model gateways, search/index systems | multi-repository evidence collection, history rewrite, untrusted source content, strict validation, publication authority, and reader state | better collector, reviewer, search, account, or publishing component | use selected repositories and bounded evidence; keep collection, model review, and publication authority separate |

## Target-oriented views

### Agent, model, and tool execution

Best testbeds:

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
- approval, sandbox, and tool-policy systems.

The practical question is not merely whether a model can call a tool. It is whether identity, authority, cancellation, result delivery, replay, and operator evidence stay coherent in an actual project.

### Browser, web runtime, and visual verification

Best testbeds:

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
- deployment and preview platforms.

### Data, storage, synchronization, and analytics

Best testbeds:

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
- Parquet, dataframe, and experiment-tracking libraries.

### Processes, filesystems, profiling, and packaging

Best testbeds:

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
- schedulers and bounded-concurrency primitives.

### Observability, evidence, and verification

Best testbeds:

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
- artifact signing and content addressing.

## How a new library enters Fieldwork

### Step 1: Start from the project need

Record a concrete seam such as:

- calendar state must sync offline;
- browser evidence must survive teardown;
- repository review needs safe untrusted-input handling;
- analytical runs need reproducible columnar storage;
- a local executor needs truthful cancellation and restart;
- a simulation needs versioned persistent state.

### Step 2: Shortlist targets

Compare existing libraries, SDKs, and platform capabilities that naturally fit that seam. A niche library is worthwhile when it solves or exposes something specific in the owned project, not merely because it has open issues.

### Step 3: Run the smallest distinguishing probe

Use a playground only to eliminate obviously unsuitable options or isolate one contract. Do not treat the probe as the final evidence when application lifecycle matters.

### Step 4: Run an owned integration trial

Pin target and testbed revisions. Record baseline, candidate, failure paths, ergonomics, resource behaviour, cleanup, and what the trial omits.

### Step 5: Keep a useful result even without upstream work

Possible outcomes:

- adopt the library or feature in the owned project;
- retain a compatibility or regression fixture;
- reject the library with a durable reason;
- publish a Fieldwork finding;
- open a deeper campaign;
- prepare an upstream packet only after explicit authorization.

## Activation rules

A candidate testbed mapping does not create labels, branches, campaigns, or upstream work.

Activate a trial only when it has:

- one external target;
- one owned testbed;
- one realistic scenario;
- exact source revisions;
- a baseline and distinguishing outcome;
- reversible setup and cleanup;
- a result useful to the project or the research programme.

An owned-project observation becomes a direct lead only when it states current behaviour, concrete consequence, likely owning boundary, and a falsifiable evidence path. It becomes a campaign only after a deliberate priority decision.

## Disposition of issue #29 findings

- Retain the twelve-system interruption comparison as an architecture case study.
- Add Baxtori as a later case-study and testbed candidate, not as a retroactive input to the verified model.
- Treat the Stensibly, Smolrunner, Days Upon, and Renderprove internal questions as dormant leads unless separately prioritized.
- Use this map as the primary continuation surface for selecting realistic testbeds for current and future Fieldwork targets.
- Do not build a universal workflow abstraction from the portfolio.
- Do not manufacture a project integration merely to justify work on an external repository.
