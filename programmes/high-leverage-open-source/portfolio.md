# High-leverage open-source research portfolio

Research snapshot: 2026-07-29

Programme: #114

## In simple words

This portfolio selects open-source targets for serious research and possible contribution based on leverage, technical reputation, visibility, contribution mechanics, and learning value.

The purpose is not to collect easy contribution credits. The purpose is to do work that can plausibly:

- unblock or improve an active owned project;
- demonstrate difficult systems competence;
- produce a respected upstream contribution;
- reveal a durable architecture or failure-model lesson;
- create a realistic integration fixture that remains useful even when no patch follows.

An owned project may motivate a target without already depending on it. A prestigious target may also deserve a lane without immediate adoption when the technical learning and contribution signal are unusually strong. Neither condition permits manufactured defects or low-value churn.

## Ranking rubric

Score targets qualitatively across five dimensions.

| Dimension | Strong evidence |
|---|---|
| Owned-project leverage | A current or plausible product seam can exercise the target under realistic lifecycle and failure conditions. |
| Technical signal | Work touches foundational runtime, rendering, storage, query, media, compiler, security, or cross-platform behavior. |
| Visibility | The project is broadly recognizable or carries strong specialist credibility. |
| Contribution path | Public contribution guidance, active review, tests, recent releases, and accepted outside work exist. |
| Research yield | Architecture maps, probes, compatibility fixtures, or negative decisions remain useful without an upstream patch. |

A lane does not need to maximize every dimension. The portfolio should mix high-probability contribution paths with a few deliberate hard-mode targets.

## Initial portfolio matrix

| Target | Primary signal | Contribution climate | Owned-project backdrop | First useful question | Risk class |
|---|---|---|---|---|---|
| Godot | Flagship open game engine; visible engine and tooling work | Documented contributor guide and contributor chat; large review surface | Botany Sim, Make Good TV | Can web export, automation, input, rendering, and serialization preserve an external authoritative model? | High-complexity, high-visibility |
| Bevy | Respected Rust ECS/game-engine architecture | Explicit contributor guide; simple changes welcome; RFC path for architecture | Botany Sim, Make Good TV | Which ECS, schedule, asset, render, and replay contracts support deterministic simulation without engine-owned truth? | Medium-high complexity, strong community path |
| wgpu | Foundational WebGPU/native graphics substrate used by Firefox, Servo, Deno, and Rust graphics projects | Contributor guide, public tracking issues, regular breaking releases and broad outside contributor set | Botany Sim, Make Good TV, Renderprove | Where do backend portability, browser context loss, diagnostics, validation, and resource lifetime diverge? | High technical signal, tractable probes |
| Wasmtime | Bytecode Alliance WebAssembly runtime and WASI implementation | Documented contributing path, active releases, substantial reviewed PR flow | Smolrunner, Stensibly | Can untrusted local tools be interrupted, limited, observed, and resumed without leaking host authority? | High technical signal, security-sensitive |
| Tauri | Very visible Rust/web desktop and mobile application shell | Contributor guide, request-to-coordinate norm, active core and plugin workspaces | Rollodoro, Relirium, Ourchival | Do permissions, plugins, updater, packaging, webview, and process lifecycle remain explicit enough for trustworthy local apps? | High visibility, broad platform matrix |
| Automerge and Yjs | Leading local-first CRDT systems with different data and sync models | Active maintainers and public contribution guidance; smaller review surfaces than flagship frameworks | Days Upon, Relirium, Proofwake | How do identity, merge, snapshots, schema migration, offline restart, and corruption boundaries compare in real records? | Strong relevance, subtle semantics |
| Apache DataFusion and Polars | Respected Arrow/Parquet analytical engines with Rust cores | Apache contributor process and active mentorship for DataFusion; very active high-volume Polars review | Quarry | Which engine better preserves reproducibility, interruption truth, streaming semantics, plan visibility, and artifact identity? | High-value comparison, large codebases |
| Tantivy | High-performance Rust full-text search library with strong specialist credibility | Straightforward pull-request workflow, stable Rust build, active releases | Baxtori, Ourchival, Relirium, Proofwake | Can commits, reloads, deletes, schema changes, and crashes preserve truthful index visibility and rebuildability? | Good acceptance surface, strong fit |
| FFmpeg | Foundational media infrastructure with exceptional technical prestige | Formal patch rules through Forgejo or mailing list; reviews are expected but can take weeks | Make Good TV, Ourchival, Renderprove | Can interrupted ingest/transcode/probe work publish only truthful media, metadata, and terminal status? | Deliberate hard mode |

## Target profiles

### Godot

#### Why it matters

Godot is recognizable outside specialist circles and still carries serious engine credibility. It spans editor tooling, rendering, physics, scripting, serialization, import pipelines, web and native export, audio, input, networking, and platform integration. A meaningful contribution can be both visible and technically substantial.

Botany Sim already has deterministic content recipes plus Canvas, WebGL2, and WebGPU laboratories. Make Good TV already separates deterministic simulation from several renderers and physical prototypes. Those projects can test whether Godot behaves well as a client, editor, renderer, or content surface without granting it sole authority over product truth.

#### Initial source surfaces

- engine contribution guide and contributor communication path;
- web platform and export code;
- input, focus, resize, audio, and context-loss lifecycle;
- scene and resource serialization;
- editor automation and headless test surfaces;
- rendering server, physics server, and asset importer boundaries;
- demo projects and regression infrastructure.

#### Strong first probes

- round-trip a deterministic external fixture through a Godot client without making node identity authoritative;
- exercise focus loss, resize, touch cancellation, context loss, reload, and web export;
- compare browser automation and deterministic screenshot/trace capture with current owned browser laboratories;
- inspect where web restrictions or editor assumptions produce false terminal success or unrecoverable partial state.

#### Stop

Do not rewrite an owned game around Godot merely to justify the lane. Stop generic feature tours and screenshot-only demos.

### Bevy

#### Why it matters

Bevy offers a different engine philosophy: explicit ECS data, schedules, plugins, assets, rendering extraction, and Rust type boundaries. Its contributor documentation explicitly distinguishes direct changes from architecture work that should begin as an RFC. That makes it a useful target for both implementation and design research.

#### Initial source surfaces

- ECS world, entity identity, change detection, commands, and deferred mutation;
- schedule construction, system ordering, ambiguity detection, and run conditions;
- asset loading, handles, hot reload, and lifecycle events;
- render extraction, preparation, queue, and GPU-resource lifetime;
- state transitions, fixed timestep, web support, and headless tests;
- RFC and contributor review process.

#### Strong first probes

- deterministic replay across schedule changes and deferred commands;
- entity or asset identity through save/load and hot reload;
- fixed-step simulation under suspension or variable rendering cadence;
- browser export and GPU backend behavior with an external simulation model.

#### Stop

Do not frame ordinary floating-point or physics nondeterminism as a defect without a documented contract. Do not propose architecture changes before understanding RFC expectations.

### wgpu

#### Why it matters

wgpu is an unusually strong specialist-prestige target. It is a cross-platform Rust implementation of WebGPU-style APIs across Vulkan, Metal, Direct3D 12, OpenGL, WebGL2, and browser WebGPU. It is used in Firefox, Servo, Deno, and much of the Rust graphics ecosystem. Small correctness, diagnostics, validation, backend, and lifecycle contributions can have broad downstream reach.

The project publishes regular releases, keeps public contributor guidance, and has a visible mix of maintainer and outside contributions.

#### Initial source surfaces

- instance, adapter, device, queue, surface, and presentation lifetime;
- validation and error-scope behavior;
- device loss, surface loss, timeout, out-of-memory, and context recovery;
- backend capability and limit normalization;
- shader translation through Naga;
- trace, replay, CTS, examples, and cross-backend test infrastructure;
- wasm and browser-specific adapters.

#### Strong first probes

- exact state and diagnostics after canvas detach, resize-to-zero, context/device loss, or page suspension;
- cross-backend validation consistency for limits and resource usage;
- resource cleanup and terminal reporting after interrupted readback or submission;
- reproducible owned fixture across native and browser backends.

#### Stop

Do not report expected backend capability differences as bugs. Require an API, standard, documented policy, or cross-backend inconsistency before escalation.

### Wasmtime

#### Why it matters

Wasmtime is the strongest infrastructure lane in the first portfolio. It combines Rust, compilers, WebAssembly standards, WASI, host capability design, JIT/AOT execution, resource limiting, interruption, and security. It has substantial specialist prestige and an active public contribution process.

Smolrunner and Stensibly provide realistic motivation: execute third-party or agent-produced work while preserving identity, cancellation, resource ceilings, receipts, and host authority.

#### Initial source surfaces

- Engine, Config, Module, Store, Instance, Linker, and component-model ownership;
- epoch interruption, fuel, async yields, deadlines, traps, and cancellation;
- resource limiters, pooling allocator, memory/table growth, and instance reuse;
- WASI preview 2/3 capability and filesystem/network surfaces;
- component model, host functions, async host calls, and reentrancy;
- cache, compilation, serialization, and artifact compatibility;
- fuzzing, security policy, and release process.

#### Strong first probes

- interrupt during guest compute, host call, filesystem mutation, and output publication;
- prove that timeout or cancellation does not imply rollback of committed host effects;
- test resource-limit exhaustion and terminal result classification;
- compare fresh instance, pooled instance, and restored application-level operation identity;
- bind execution receipts to exact module, configuration, capabilities, inputs, and observed effects.

#### Stop

No claims about sandbox security from a toy guest alone. No production credentials or unrestricted host filesystem/network access.

### Tauri

#### Why it matters

Tauri combines high public visibility with deep cross-platform systems work. It spans Rust core code, JavaScript APIs, native webviews, mobile platforms, permissions, IPC, plugins, packaging, signing, updater behavior, and process lifecycle. Its contribution guidance asks contributors to coordinate substantive work, which improves acceptance odds when the evidence is strong and the scope is agreed.

Rollodoro, Relirium, and Ourchival can test real local-first, private-data, notification, file, update, extension-adjacent, and packaging requirements.

#### Initial source surfaces

- core runtime and platform webview adapters;
- command and IPC serialization, permissions, capabilities, and scopes;
- plugin workspace and generated permission manifests;
- filesystem, notification, store, updater, stronghold, and process plugins;
- app restart, window state, deep link, single-instance, and mobile lifecycle;
- bundler, signing, updater artifacts, CI, and release metadata.

#### Strong first probes

- stale frontend request or duplicate IPC after webview reload;
- updater interruption, artifact identity, rollback, and terminal reporting;
- permission-scope drift between source config and packaged application;
- window/process restart with local durable state and pending notifications;
- cross-platform package-content and capability comparison.

#### Stop

Do not treat platform differences as defects without a promised abstraction. Do not use real signing credentials or release channels.

### Automerge and Yjs

#### Why they matter

These projects are central to serious local-first application design. Automerge provides a Rust core, compact change format, and sync protocol; its maintainers describe the goal as doing for local-first applications what relational databases did for server applications. Yjs provides shared types, relative positions, providers, snapshots, undo, and a documented threat model. Comparing them against real owned records is more useful than choosing from benchmarks alone.

#### Initial source surfaces

- operation/change identity and causal metadata;
- document storage, sync messages, partial sync, restart, and duplicate delivery;
- sequence/text behavior, relative positions, maps, arrays, and tombstones;
- snapshots, compaction or garbage collection, schema evolution, and migration;
- corrupted or hostile updates and resource ceilings;
- network-provider separation and application-owned authorization;
- Rust/WASM and JavaScript boundaries.

#### Strong first probes

- concurrent calendar edits with deletes, moves, recurrence, and provider identities;
- chapter edits, annotations, and stable positions across large rewrites;
- offline edits followed by duplicate, reordered, truncated, or malicious sync messages;
- backup/export and engine replacement without losing application-owned identity;
- memory and document growth under long-lived realistic histories.

#### Stop

Do not confuse convergence with product-correct conflict resolution. No private manuscripts or calendar data are needed.

### Apache DataFusion and Polars

#### Why they matter

Both projects carry strong data-engine credibility. DataFusion is an Apache query engine built around Arrow and Parquet with an explicit contributor community and mentorship path. Polars is highly visible, fast-moving, and widely used through Python and Rust. Quarry can supply real deterministic analytical workloads, interruption points, artifact publication, and audit requirements.

#### Initial source surfaces

- logical and physical planning, optimizer rules, expression identity, and explain output;
- streaming execution, memory pools, spilling, repartitioning, cancellation, and errors;
- object-store reads and writes, Parquet metadata, partitioning, and schema evolution;
- lazy-plan serialization or reproducibility boundaries;
- Python/Rust bridge behavior and exception mapping;
- deterministic output ordering, numerical behavior, and parallel execution;
- benchmark and regression infrastructure.

#### Strong first probes

- interrupt or resource-exhaust an analytical plan and classify published artifacts;
- compare explainability and reproducibility of equivalent lazy/query plans;
- test schema drift, corrupted partitions, partial object-store data, and retries;
- compare stable ordering, grouped results, joins, and floating-point aggregation under parallelism;
- preserve exact input, plan, engine, configuration, and output hashes in a Quarry receipt.

#### Stop

Do not promote microbenchmarks without a real workload and profile. Separate engine defects from unspecified ordering or floating-point expectations.

### Tantivy

#### Why it matters

Tantivy has strong specialist recognition, active releases, stable Rust builds, and a straightforward pull-request workflow. Its architecture exposes useful lifecycle questions: documents are immutable, edits are delete-and-reindex, commits make changes durable, readers must reload, and newly acquired searchers see the updated state. Those explicit boundaries fit Baxtori, Ourchival, Relirium, and Proofwake.

#### Initial source surfaces

- schema, documents, index writer, segments, commits, deletes, merges, and garbage collection;
- index reader reload policies and searcher snapshots;
- directory and managed-file lifecycle;
- tokenizer and query parser boundaries;
- crash recovery, lock handling, corruption detection, and fast fields;
- incremental indexing, index sorting, and merge policies.

#### Strong first probes

- crash before, during, and after commit and reader reload;
- delete-and-reindex identity under duplicate capture or publication retry;
- schema-version migration and full rebuild from authoritative records;
- bounded hostile text, tokenizer behavior, and query resource use;
- exact visibility receipt describing commit generation and reader/searcher generation.

#### Stop

Do not treat delayed reader visibility as a defect when reload is required by contract. Keep the source archive authoritative.

### FFmpeg

#### Why it matters

FFmpeg is the deliberate hard-mode lane. It is foundational, technically prestigious, and directly relevant to media ingestion, probing, transcoding, thumbnails, streaming, codecs, containers, and metadata. Its contribution process is formal: patches follow strict coding and testing rules, are submitted through Forgejo or the development mailing list, and can require several review rounds. The project states that patches are reviewed, while large work may take weeks.

A narrow, well-tested FFmpeg fix is more valuable than many superficial contributions elsewhere. It is also expensive to pursue, so the lane must be evidence-driven.

#### Initial source surfaces

- libavformat open/read/write/trailer and protocol lifecycle;
- libavcodec send/receive, flush, drain, threading, and error propagation;
- interruption callbacks, I/O errors, seeks, network timeouts, and partial files;
- metadata, timestamps, stream disposition, attachment, and side-data handling;
- image extraction, filter graphs, hardware acceleration, and fallback;
- FATE regression tests, sample policy, patch rules, and maintainer ownership.

#### Strong first probes

- interrupt probe/transcode/remux at controlled byte, frame, packet, and trailer boundaries;
- classify when a partial output is valid, playable, misleading, or corrupt;
- ensure callers can distinguish clean EOF, truncated input, cancelled work, and failed finalization;
- preserve exact command/library configuration, input hashes, stream mapping, warnings, and output hashes;
- test metadata and thumbnail pipelines relevant to Ourchival and Make Good TV.

#### Stop

No vague performance or codec claims. No upstream packet without FATE-quality reproduction, minimal patch shape, and explicit authorization.

## Dispatch strategy

### Wave 1: broad but tractable

1. wgpu portability and lifecycle.
2. Wasmtime capability sandboxing.
3. Tauri application authority and packaging.
4. Tantivy index visibility and recovery.

These have high specialist signal, strong owned-project seams, and contribution processes that can support focused outside work.

### Wave 2: comparative application architecture

5. Automerge versus Yjs.
6. DataFusion versus Polars.
7. Godot engine boundaries.

These require larger comparative fixtures or broader source maps before a narrow contribution question is likely to emerge.

### Wave 3: exploratory engine and hard mode

8. Bevy ECS/render/replay architecture.
9. FFmpeg media lifecycle and publication truth.

Bevy is a high-learning architecture lane. FFmpeg is reserved for narrow, consequential evidence because its submission and review cost is intentionally high.

## Evidence levels

Use these labels in reports, not necessarily as GitHub labels:

- **source-confirmed** — direct implementation, tests, or maintained documentation;
- **released-reproduced** — observed against an exact published release;
- **tree-reproduced** — observed against an exact source revision;
- **owned-integration** — observed in a pinned owned project scenario;
- **cross-platform** — independently reproduced on more than one relevant platform/backend;
- **upstream-ready** — minimized, reviewed, regression-tested, and authorized for contact.

Do not jump from source reading to a defect claim. Do not jump from one owned integration to a universal recommendation.

## Contribution-value outcomes

A lane can succeed by producing:

- an accepted upstream fix, test, diagnostic, or documentation correction;
- a high-quality upstream packet awaiting authorization;
- an adopted owned-project integration;
- a reusable compatibility or fault-injection fixture;
- a durable rejection with measured reasons;
- an architecture case study that informs several projects;
- a negative result that prevents expensive integration work.

## Portfolio controls

- Keep upstream contact unauthorized by default.
- Prefer public, synthetic, or generated fixtures.
- Do not expose private repositories, data, credentials, signing keys, calendars, manuscripts, media, or account records.
- Avoid several lanes editing the same target branch.
- Pin every source and owned-testbed revision before execution claims.
- Review prestige lanes for actual opportunity before spending integration time.
- Close or park lanes that only rediscover documented behavior without a consequential question.
