# Workers SDK lifecycle follow-up synthesis

State: `ready-for-synthesis`

Batch: `B20260730-001`

Issue: #88

Upstream contact authorized: `false`

Upstream contact performed: `false`

`complete` means bounded research is complete. It does not mean target package tests ran or production source is ready.

## Portfolio

Three core Workers SDK lanes and six extracted Cloudflare Vite-plugin candidates are retained:

1. A001 — Miniflare teardown can skip or delay `workerd` termination.
2. A002 — Wrangler and Vite can select different configuration files.
3. A003 — Worker code can activate before later deployment failure without a sufficient state receipt.
4. #165 — container cleanup ownership across preparation, instances, close, and restart retry.
5. #179 — logical ownership for Miniflare, restart state, tunnels, export metadata, warnings, hostnames, and process-exit reporters.
6. #183 — operation-scoped build intent versus sticky process environment.
7. #186 — authenticated remote-binding session lifecycle, connection identity, disposed-entry reuse, and logger ownership.
8. #187 — account/token authority for container-registry credential generation.
9. #190 — host fetch routing changed by importing Wrangler as a library.

None of the target package/plugin suites executed. Dependency-free models establish control-flow, authority, and ownership contracts only.

## Exact evidence heads

| Candidate | Head | State |
| --- | --- | --- |
| A001 | `fa39841a98d71edd2df7561beb877f4dacbc6b7c` | mechanism accepted; execute next |
| A002 | `82ffab5d51abf7b5311891f31c6aa77f42bec41f` | characterization accepted; execute next |
| A003 | `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376` | guarded reporting accepted; execute next |
| #165 | `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd` | `state:ready` |
| #179 | `f6389b5c17f45279c9244f022b875d60940b5d44` | `state:ready` |
| #183 | `26556bcf7cda31009039b3aaf1527a8e4649e37f` | `state:ready` |
| #186 | `f1fa08c44cda1c5a77568dcf8a64a45a91702c88` | `state:ready` |
| #187 | `e92165ac96cd0648a2c824920e7605128a82afb4` | `state:investigating`; client boundary revised, mocked request execution required |
| #190 | `8f8123f9e0c0d1e0f26ff1e843dc214f10e7af3a` | `state:ready` |

## Core lanes

### A001 — teardown lifecycle ownership

Disposition: **accept mechanism; hold integration for package execution and test-slice separation**

Browser and proxy cleanup run before `Runtime.dispose()`. A rejection can skip runtime disposal; a pending promise can delay it indefinitely. The package regression counts only `SIGKILL` calls made on the actual `workerd` child. Initialization-plus-cleanup error aggregation remains separate.

### A002 — configuration selection contract

Disposition: **accept behavior-preserving protocol direction; hold default changes**

The matrix covers extension precedence, upward versus root-only search, redirect policy, and explicit-path convergence, including farther parent JSON against nearer JSONC/TOML.

### A003 — post-activation deployment state

Disposition: **accept guarded reporting; hold rollback and integration for execution**

Code activation can precede container or trigger failure. Reporting is best-effort so a throwing callback cannot replace the exact original deployment error.

## Extracted Vite candidates

### #165 — container cleanup ownership

Late tag ownership, one same-mode exit callback slot, missing preview-close cleanup, and failed-restart old-tag loss. The per-instance registry draft adds early ownership, old/new tag union, close cleanup, warnings, and retry retention.

### #179 — logical runtime, tunnel, metadata, and warning ownership

Every `cloudflare()` context shares process-global Miniflare, export map, warning latch, restart counter, and tunnel hostnames. One server can update another's runtime or suppress final cleanup.

One TunnelManager is shared, reused after dispose, and retains the first logger. Tunnel helpers and shortcuts target it globally. Shared export maps can assert or trigger false HMR restart in another server. The warning latch crosses servers, while one Node-warning exit callback drops earlier warning maps.

Vite 6.1.0, 7.1.12, and 8.1.5 construct replacement plugins before old-generation close, supporting an async-scoped logical-owner handoff.

### #183 — build operation scope

The build hook sets `CLOUDFLARE_VITE_BUILD=true`; preview reads it to select prerender rather than entry configuration. Production never restores it, and the package playground manually deletes it after `buildApp()` because later preview shares the process.

The scoped model isolates nested build preview, concurrent unrelated preview, success, and failure. A `configResolved` child-preview path remains an explicit gate.

### #186 — authenticated remote proxy session ownership

Vite caches live remote-binding sessions globally by config path and never disposes them on final close. Reuse comparison omits account ID, compliance region, profile directory, Worker name, and current logger. A disposed cached entry can be returned later; the Vitest pool disposes without deleting its entry.

The remote-bindings package also uses one module-global live logger. Session B can redirect session A's later error and teardown diagnostics.

### #187 — container registry credential authority

The authority invariant is accepted: Vite mutates one generated OpenAPI singleton with an account URL and bearer token before asynchronous image preparation, allowing sequential or concurrent account/token contamination.

Independent review correctly rejected the first per-operation client sketch because spreading `OpenAPI` could inherit global token, Basic credentials, headers, logger, credential mode, or encoder, and a default `ImageRegistriesService` parameter reopened the global path.

The revised artifact now:

- constructs a closed `OpenAPIConfig` from explicit constants and operation inputs;
- clears token, username, and password fields;
- sets Authorization, credential mode, path encoder, and operation logger explicitly;
- requires an explicit operation client for Cloudflare credential lookup;
- makes external-only no-client work perform zero Cloudflare API requests;
- reran eight contamination, concurrency, redaction, and fallback controls successfully.

Disposition: **investigating — execute generated-request controls before promotion**.

### #190 — Wrangler import-time proxy routing

The Vite plugin imports Wrangler's public root, which resolves to the CLI bundle. With proxy environment variables present, Wrangler module evaluation installs an Undici global proxy dispatcher and emits a startup warning before `main()` is called.

Import can therefore replace a host application's custom dispatcher and reroute unrelated fetches. The draft moves dispatcher installation into CLI command lifetime and requires explicit embedded-operation dispatchers rather than library import side effects.

## Executed dependency-free models

- A001 teardown ownership and bounded cleanup.
- A002 discovery and redirect probes.
- A003 receipt and reporting guard.
- #165 container cleanup ownership.
- #179 runtime, restart, tunnel, metadata, and warning ownership.
- #183 build-operation scope.
- #186 remote-session lifecycle, identity, and logger ownership.
- #187 revised closed-client authority and no-fallback controls.
- #190 import-time dispatcher and explicit operation routing.

## Centralized visibility

- #88 is the canonical live review index.
- #165, #179, #183, #186, #187, and #190 are separate filterable candidates.
- #112 retains this synthesis and durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 is a dated projection and does not override live issue state.

## Recommended execution order

1. A001 runtime-first regressions.
2. A003 helper and mocked deploy paths.
3. A002 configuration matrix.
4. #165 container ownership tests.
5. #179 owner handoff and state isolation on Vite 6/7/8.
6. #183 programmatic build/preview scope.
7. #186 remote-session lifecycle/identity/logger.
8. #187 generated-request account/token authority and secret-redaction tests.
9. #190 import/CLI/embedded proxy routing.
10. A001 aggregation separately.

## Boundary

No live deployment, route update, proxy request, tunnel, remote binding, account access, credential use, container operation, rollback, browser multi-server run, or upstream interaction occurred.
