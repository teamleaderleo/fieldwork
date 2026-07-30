# Workers SDK lifecycle follow-up synthesis

State: `ready-for-synthesis`

Batch: `B20260730-001`

Issue: #88

Upstream contact authorized: `false`

Upstream contact performed: `false`

`complete` means bounded research is complete. It does not mean target package tests ran or production source is ready.

## Portfolio

Three core Workers SDK lanes and five extracted Cloudflare Vite-plugin candidates are now retained:

1. A001 — Miniflare teardown can skip or delay `workerd` termination.
2. A002 — Wrangler and Vite can select different configuration files.
3. A003 — Worker code can activate before later deployment failure without a sufficient state receipt.
4. #165 — container cleanup ownership across preparation, instances, close, and restart retry.
5. #179 — logical ownership for Miniflare, restart state, tunnels, export metadata, warnings, hostnames, and process-exit reporters.
6. #183 — operation-scoped build intent versus sticky process environment.
7. #186 — authenticated remote-binding session lifecycle, connection identity, disposed-entry reuse, and logger ownership.
8. #187 — account/token authority for container-registry credential generation.

None of the target package/plugin suites executed. Dependency-free models establish control-flow, authority, and ownership contracts only.

## Exact evidence heads

| Candidate | Head |
| --- | --- |
| A001 | `fa39841a98d71edd2df7561beb877f4dacbc6b7c` |
| A002 | `82ffab5d51abf7b5311891f31c6aa77f42bec41f` |
| A003 | `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376` |
| #165 | `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd` |
| #179 | `f6389b5c17f45279c9244f022b875d60940b5d44` |
| #183 | `26556bcf7cda31009039b3aaf1527a8e4649e37f` |
| #186 | `f1fa08c44cda1c5a77568dcf8a64a45a91702c88` |
| #187 | `f9f6e84fb64d72f5954325855c3846f7a069821b` |

## Core lanes

### A001 — teardown lifecycle ownership

Disposition: **accept mechanism; hold integration for package execution and test-slice separation**

Browser and proxy cleanup are awaited before `Runtime.dispose()`. Rejection can skip runtime disposal; a pending promise can delay it indefinitely. The real-runtime regression counts only `SIGKILL` calls made on the actual `workerd` child. Initialization-plus-cleanup error aggregation remains separate.

Gate: execute the first three tests before and after the runtime-first patch and prove no leaked process, worker, dispatcher, or unhandled rejection.

### A002 — configuration selection contract

Disposition: **accept behavior-preserving protocol direction; hold default changes**

The six-layout matrix covers extension precedence, upward versus root-only search, redirect policy, and explicit-path convergence, including farther parent JSON against nearer JSONC/TOML.

Gate: execute on Windows/POSIX, verify selected/parsed/watched/reported paths, then centralize current outcomes before default migration.

### A003 — post-activation deployment state

Disposition: **accept guarded reporting; hold rollback and integration for execution**

Code activation can precede container or trigger failure. Reporting is best-effort so a throwing callback cannot replace the exact original deployment error.

Gate: execute helper and mocked deploy paths, accept terminal/machine-readable output contracts, and keep automatic rollback out of the first patch.

## #165 — container cleanup ownership

Disposition: **accept source/model candidate; hold production edits for mocked tests**

Source/models establish late tag ownership, one same-mode exit callback slot, missing preview-close cleanup, and old-tag loss after failed restart cleanup. The per-instance registry draft adds early ownership, old/new tag union, close cleanup, warnings, and retry retention.

Gate: execute multiple-instance, preparation, close, warning, retry, and restart-tag tests.

## #179 — logical runtime, tunnel, metadata, and warning ownership

Disposition: **accept source finding and async owner-handoff direction; hold broad implementation**

Every `cloudflare()` context shares process-global Miniflare, export map, warning latch, restart counter, and tunnel hostnames. One server can update another's runtime or suppress final cleanup.

One TunnelManager is shared, reused after dispose, and retains the first logger. Tunnel helpers and shortcuts target it globally. Shared export maps can assert or trigger false HMR restart in another server. The warning latch crosses servers, while one Node-warning process-exit callback drops earlier server warning maps.

Vite 6.1.0, 7.1.12, and 8.1.5 all construct replacement plugins before old-generation close, supporting an async-scoped logical-owner handoff.

Gate: execute restart, runtime, tunnel, logger, export, warning, concurrency, failure, and stale-generation tests on Vite 6/7/8.

## #183 — build operation scope

Disposition: **accept operation-scope invariant; hold scope boundary for real programmatic tests**

The build hook sets `CLOUDFLARE_VITE_BUILD=true`; preview reads it to select prerender rather than entry configuration. Production never restores it, and the package playground manually deletes it after `buildApp()` because later preview shares the process.

The scoped model isolates nested build preview, concurrent unrelated preview, success, and failure. The draft wraps `builder.buildApp`; a configResolved child-preview path remains an explicit gate.

Gate: execute success, failure, concurrency, custom buildApp, environment-restoration, actual deploy-config selection, and child-preview tests on Vite 6/7/8.

## #186 — authenticated remote proxy session ownership

Disposition: **accept lifecycle/identity/logger invariants; hold implementation for mocked session tests**

Vite caches live remote-binding sessions globally by config path and never disposes them on final close. Reuse comparison omits account ID, compliance region, profile directory, Worker name, and current logger. A disposed cached entry can be returned later; the Vitest pool disposes without deleting its entry.

The remote-bindings package also uses one module-global live logger. Session B can redirect session A's later error and teardown diagnostics.

Draft slices add full connection identity, owner-scoped lifecycle, exact Vitest entry deletion after dispose, and session-captured logger injection. Vite ownership integrates with #179's logical-server generations.

Gate: execute close/restart/concurrent same-path tests, account/compliance/profile replacement, disposed-entry controls, and concurrent logger ownership without real credentials or network.

## #187 — container registry credential authority

Disposition: **accept per-operation credential invariant; hold implementation for mocked authority tests**

Vite mutates one generated OpenAPI singleton with an account URL and bearer token before asynchronous image preparation. Concurrent operations can send A's credential request through B's account/token. Later external-only work can inherit prior credentials despite never configuring the client.

The immutable per-operation client draft passes account/token/base/logger explicitly through image preparation. External-only work without a client must make no Cloudflare API request and follow the existing warning/public-pull fallback. Restoring a global in `finally` is rejected as concurrency-unsafe.

Gate: execute concurrent/sequential account-token isolation, external-only fallback, failure cleanup, custom API base, and no-token-leakage tests.

## Executed models

- A001 teardown ownership and bounded cleanup.
- A002 discovery and redirect probes.
- A003 receipt and reporting guard.
- #165 container cleanup ownership models.
- #179 shared runtime, restart handoff, tunnel lifetime, metadata, and warning-exit models.
- #183 sticky marker and scoped build-operation model.
- #186 remote-session lifecycle/identity and concurrent logger models.
- #187 registry account/token operation-scope model.

## Centralized visibility

- #88 is the canonical batch review hub.
- #165, #179, #183, #186, and #187 are separate filterable candidates.
- #112 retains this synthesis and durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 is a dated projection and does not override live issue state.

All extracted candidates use `state:ready`, `type:lane`, `parallel-safe`, `target:workers-sdk`, and `programme:sdk-integration-lifecycle`.

## Recommended order

1. Execute A001 runtime-first regressions.
2. Execute A003 helper and mocked deploy paths.
3. Execute A002 configuration matrix.
4. Execute #165 container ownership tests.
5. Execute #179 owner handoff and state isolation on Vite 6/7/8.
6. Execute #183 programmatic build/preview scope tests.
7. Execute #186 mocked remote-session lifecycle/identity/logger tests.
8. Execute #187 mocked registry credential authority tests.
9. Return to A001 aggregation and deadlines separately.

## Boundary

No live deployment, route update, container rollout, tunnel, remote binding, account access, credential use, rollback, Docker reproduction, browser multi-server run, or upstream interaction occurred.
