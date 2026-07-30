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
- #187 revised registry credential client: `e92165ac96cd0648a2c824920e7605128a82afb4`
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

- test multiple dev/preview instances, partial preparation, restart, close, warning, and retry;
- preserve exact primary errors and per-instance ownership.

Durable note: `notes/vite-container-cleanup-ownership.md`.

### #179 — Vite logical runtime/tunnel/export/warning ownership

- execute owner handoff on Vite 6, 7, and 8;
- prove runtime, tunnel, logger, shortcut, export-map, warning-latch, and exit-reporter isolation;
- prove failed replacement and stale generations retain exactly one owner.

Durable note: `notes/vite-shared-context-ownership.md`.

### #183 — Vite build operation scope

- execute programmatic build/preview success, failure, concurrency, and child-preview controls on Vite 6/7/8;
- prove process environment remains unchanged.

Durable note: `notes/vite-build-marker-scope.md`.

### #186 — Vite remote proxy session ownership

- execute close/restart/concurrent same-path tests;
- replace sessions on account/compliance/profile/auth changes;
- prevent disposed-entry reuse;
- preserve session-owned logger routing and primary errors.

Durable note: `notes/vite-remote-proxy-session-ownership.md`.

### #187 — Vite container registry credential authority

State: `investigating — client boundary revised; mocked request execution required`.

The first client sketch was rejected because it spread mutable global OpenAPI auth/logger fields and retained a silent global-service fallback. The revised artifact:

- builds a closed config from explicit inputs;
- clears token and Basic-auth fields;
- sets operation logger and path encoder explicitly;
- requires an explicit client for Cloudflare credential lookup;
- makes external-only no-client work perform zero Cloudflare API requests;
- reran eight dependency-free contamination/redaction/fallback controls successfully.

Remaining gate:

- capture actual generated request config under contaminated global state;
- run concurrent account A/B requests at dispatch;
- prove no silent global fallback;
- prove managed-image missing credentials fail before preparation;
- prove Authorization is absent from diagnostics/artifacts;
- retain or explicitly migrate existing CLI callers.

Durable note: `notes/vite-container-registry-auth-scope.md`.

### #190 — Wrangler import-time proxy dispatcher ownership

- prove library import preserves host dispatcher and emits no CLI warning;
- scope CLI proxy dispatcher to command lifetime and restore on success/failure;
- design explicit embedded-operation dispatchers;
- prove concurrent host and embedded routes remain isolated.

Durable note: `notes/vite-wrangler-import-proxy-dispatcher.md`.

## Validation

Executed dependency-free models cover A001–A003 and all six extracted Vite candidates. #187's revised model includes deliberate global TOKEN, Basic-auth, headers, encoder, and logger contamination controls.

Prepared but unexecuted:

- all target package, mocked request, multi-server, Vite-version, and CLI/embedded matrices listed above.

## Coordination placement

- #88 is the canonical batch review hub.
- #165, #179, #183, #186, #187, and #190 are separate filterable candidates.
- #112 retains synthesis and durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 is a dated projection, not canonical live state.

No live deployment, proxy, tunnel, remote binding, account access, credential use, Docker operation, browser multi-server run, or upstream interaction occurred.
