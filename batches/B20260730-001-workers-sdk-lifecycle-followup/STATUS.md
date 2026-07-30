# B20260730-001 status

Batch issue: #88

State: `ready-for-synthesis`

Coordinator-owned file. Workers must not edit this file directly.

`complete` means bounded research is complete. It does not mean package execution or source integration is complete.

| Assignment | Role | State | Workers SDK branch / PR | Fieldwork result | Review |
| --- | --- | --- | --- | --- | --- |
| A001 | Teardown lifecycle ownership | complete | `fieldwork/teardown-lifecycle-hardening` / fork PR #1 | `results/A001.md` via Fieldwork PR #98 | Mechanism accepted; adjacent Vite findings extracted to #165, #179, #183, #186, #187, and #190; package execution and test-stack split remain |
| A002 | Configuration selection contract | complete | `fieldwork/config-selection-contract` / fork PR #2 | `results/A002.md` | Characterization tightened and accepted; execution remains |
| A003 | Partial deployment state | complete | `fieldwork/deploy-state-reporting` / fork PR #3 | `results/A003.md` | Reporting-failure flaw fixed and modeled; package execution remains |
| A004 | Independent review and prior art | withdrawn | none | `results/A004.md` | Duties redistributed at user direction |

## Exact evidence heads

- A001 core: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`
- #165 container cleanup: `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd`
- #179 logical runtime/tunnel/export/warning: `f6389b5c17f45279c9244f022b875d60940b5d44`
- #183 build operation scope: `26556bcf7cda31009039b3aaf1527a8e4649e37f`
- #186 remote proxy sessions: `f1fa08c44cda1c5a77568dcf8a64a45a91702c88`
- #187 container registry credentials: `f9f6e84fb64d72f5954325855c3846f7a069821b`
- #190 Wrangler import proxy routing: `8f8123f9e0c0d1e0f26ff1e843dc214f10e7af3a`
- A002: `82ffab5d51abf7b5311891f31c6aa77f42bec41f`
- A003: `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376`

## Acceptance queue

### A001

- execute the first three Miniflare tests before and after the runtime-first patch;
- preserve workerd-specific child identity;
- prove no leaked child, worker thread, dispatcher, or unhandled rejection;
- review initialization-plus-cleanup aggregation separately.

### A002

- execute the six-layout matrix on Windows and POSIX;
- verify selected, parsed, watched, and reported paths;
- centralize current outcomes before considering default migration.

### A003

- execute helper tests including the throwing-reporter regression;
- inject legacy/container, versions/trigger, and legacy/trigger failure;
- accept terminal and machine-readable receipt contracts;
- keep automatic rollback out of the first patch.

### #165 — Vite container cleanup ownership

- test multiple dev/preview instances;
- test partial preparation failure and exact-error preservation;
- test preview programmatic close;
- test cleanup failure, warning, retained ownership, and retry;
- test failed restart cleanup retaining old and new tags.

Durable note: `notes/vite-container-cleanup-ownership.md`.

### #179 — Vite logical runtime/tunnel/export/warning ownership

- execute the narrow restart-counter regression;
- execute owner handoff on Vite 6, 7, and 8;
- prove concurrent Miniflare and tunnel isolation;
- prove tunnel logger, shortcut, and expiry ownership;
- prove export maps and warning state do not cross servers;
- prove every live Node warning renderer runs and unregisters on final close;
- prove failed replacement and stale generations retain exactly one owner.

Durable note: `notes/vite-shared-context-ownership.md`.

### #183 — Vite build operation scope

- execute programmatic build followed by independent preview without manual env deletion;
- execute failed-build and concurrent-preview controls;
- prove nested build preview selects prerender while independent preview selects entry;
- prove process environment is unchanged;
- characterize child preview during `configResolved()` on Vite 6, 7, and 8.

Durable note: `notes/vite-build-marker-scope.md`.

### #186 — Vite remote proxy session ownership

- dispose/remove sessions on true Vite final close;
- transfer sessions only to the same logical-owner replacement generation;
- isolate concurrent same-config-path servers;
- replace sessions when account, compliance region, profile, or auth identity changes;
- prevent disposed-entry reuse in Vite and Vitest pool;
- keep asynchronous diagnostics and teardown on the owning session logger;
- preserve primary close/start errors and explicit retry state.

Durable note: `notes/vite-remote-proxy-session-ownership.md`.

### #187 — Vite container registry credential authority

- isolate concurrent account/token endpoints and Authorization headers;
- prove later external-only work cannot inherit earlier credentials;
- make external-only fallback perform no Cloudflare API request without an explicit client;
- prove failed preparation leaves no credential state;
- keep logger/API base operation-scoped;
- prove tokens never enter logs, errors, snapshots, or artifacts;
- retain or explicitly migrate existing Wrangler/container CLI behavior.

Durable note: `notes/vite-container-registry-auth-scope.md`.

### #190 — Wrangler import-time proxy dispatcher ownership

- prove importing Wrangler or the Vite plugin preserves a preinstalled host dispatcher;
- prove import alone emits no Wrangler proxy warning;
- scope proxy dispatcher installation to CLI command lifetime;
- restore the exact prior dispatcher on success and failure;
- keep long-running CLI proxy routing until final close;
- design explicit per-operation dispatchers for embedded Wrangler/Vite APIs;
- prove concurrent host and embedded routes remain isolated.

Durable note: `notes/vite-wrangler-import-proxy-dispatcher.md`.

## Validation

Executed dependency-free models:

- A001 teardown ownership and bounded cleanup;
- A002 discovery and redirect probes;
- A003 receipt and reporting guard;
- #165 container ownership, exit registry, and restart tag retention;
- #179 shared runtime, restart handoff, tunnel lifetime, metadata, and warning-exit ownership;
- #183 sticky build marker and scoped operation state;
- #186 remote-session lifecycle/identity and concurrent logger ownership;
- #187 registry account/token operation scope;
- #190 import-time global dispatcher and explicit operation routing.

Prepared but unexecuted:

- Miniflare package lifecycle tests;
- Vite configuration-selection package matrix;
- deploy-helper package and mocked integration tests;
- Vite container-cleanup plugin tests;
- Vite logical-owner/multi-server tests across Vite 6/7/8;
- Vite programmatic build/preview tests across Vite 6/7/8;
- Vite remote-session mocked lifecycle/identity tests;
- Vite container-registry concurrent-request tests;
- Wrangler/Vite import, CLI dispatcher lifetime, and embedded proxy-routing tests.

## Coordination placement

- #88 is the canonical batch review hub.
- #165, #179, #183, #186, #187, and #190 are separate filterable Vite candidates.
- #112 retains synthesis and durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 is a dated projection, not canonical live state.

No live deployment, proxy, tunnel, remote binding, account access, credential use, Docker reproduction, browser multi-server run, or upstream interaction occurred.
