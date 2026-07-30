# Workers SDK lifecycle follow-up synthesis

State: `ready-for-synthesis`

Batch: `B20260730-001`

Issue: #88

Upstream contact authorized: `false`

Upstream contact performed: `false`

`complete` means a bounded research result is complete. It does not mean target package tests ran or production source is ready.

## Portfolio

The batch now contains three core Workers SDK lanes and three extracted Cloudflare Vite-plugin candidates:

1. A001 — Miniflare teardown can skip or delay `workerd` termination.
2. A002 — Wrangler and Vite can select different configuration files.
3. A003 — Worker code can activate before later deployment failure without a sufficient state receipt.
4. #165 — Vite container cleanup can lose ownership across preparation, multiple instances, close, and restart retry.
5. #179 — process-global Miniflare, restart, tunnel, export, warning, hostname, and logger state can conflate logical servers.
6. #183 — a sticky process environment marker can make later or concurrent preview select prerender configuration as though it still belonged to a build.

None of the target package/plugin suites executed. Dependency-free models establish control-flow and ownership contracts only.

## Exact evidence heads

| Candidate | Head |
| --- | --- |
| A001 | `fa39841a98d71edd2df7561beb877f4dacbc6b7c` |
| A002 | `82ffab5d51abf7b5311891f31c6aa77f42bec41f` |
| A003 | `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376` |
| #165 | `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd` |
| #179 | `de3ed9fbf45a04cf2201a5571ade9afbe081a987` |
| #183 | `26556bcf7cda31009039b3aaf1527a8e4649e37f` |

## A001 — teardown lifecycle ownership

Disposition: **accept mechanism; hold integration for package execution and test-slice separation**

Browser and proxy cleanup are awaited before `Runtime.dispose()`. A rejection can skip runtime disposal; a pending promise can delay it indefinitely. `Runtime.dispose()` sends `SIGKILL` synchronously before returning the child exit promise, so requesting runtime termination earlier is a bounded ownership fix.

The package regression counts only `SIGKILL` calls made on the actual `workerd` child. The first three tests cover pre-runtime rejection, deterministic pending cleanup, and a post-runtime negative control. Initialization-plus-cleanup error aggregation remains separate.

Gate: execute the first three tests before and after the patch and prove no leaked process, worker, dispatcher, or unhandled rejection.

## A002 — configuration selection contract

Disposition: **accept behavior-preserving protocol direction; hold default changes**

Workers Utils and Vite differ across extension precedence, upward versus root-only search, redirect policy, and explicit-path convergence.

The prepared six-layout matrix covers farther parent JSON against nearer JSONC and TOML, uses caller-neutral redirect wording, and begins explicit-path convergence from a Vite-relative path.

Gate: execute on Windows and POSIX, verify selected/parsed/watched/reported paths, then centralize current outcomes before default migration.

## A003 — post-activation deployment state

Disposition: **accept guarded state reporting; hold rollback and integration for execution**

Container rollout follows legacy upload at the pinned revision; trigger failure can follow either activation path.

The helper reports activation method, version when available, failed phase, and possible partial application while rethrowing the exact original error. Reporting is best-effort after review found that a throwing callback could replace the deployment error.

Gate: execute helper and mocked deploy paths, accept terminal/machine-readable output contracts, and keep automatic rollback out of the first patch.

## #165 — Vite container cleanup ownership

Disposition: **accept source/model candidate; hold production changes for mocked plugin tests**

Source and models establish:

- tag ownership is installed after asynchronous image preparation;
- each mode has one process-exit callback slot, so later same-mode instances replace earlier owners;
- preview programmatic close lacks container cleanup;
- failed restart cleanup can lose old tags when later preparation replaces the set.

The per-instance registry draft adds early ownership, old/new tag union, preview close cleanup, warnings, and retry retention. It remains unapplied.

Gate: execute multiple-instance, preparation, close, warning, retry, and restart-tag tests.

## #179 — Vite logical runtime and tunnel ownership

Disposition: **accept source finding and async owner-handoff direction; hold broad implementation**

Every `cloudflare()` call gets a fresh plugin context backed by one process-global shared record. A second plugin can update the first plugin's Miniflare. One server's restart can make another skip final cleanup.

The tunnel plugin also has one module-global manager. `dispose()` clears active state but retains the singleton and its first logger, so a later independent server reuses the disposed manager and routes new tunnel diagnostics through the previous logger.

Vite 6.1.0, 7.1.12, and 8.1.5 all create replacement plugins before closing the old generation. This supports an async-scoped logical-owner handoff across all supported majors.

Executed models cover shared runtime overwrite, unrelated-close suppression, owner isolation, sequential and concurrent restart handoff, failed replacement construction, tunnel logger reuse, per-owner tunnel isolation, and owner-specific removal.

A narrow restart-counter patch is prepared. The full owner record should include Miniflare, a logger-correct TunnelManager, export state, warning state, and tunnel hostnames, with stale-generation protection and final owner deletion.

Gate: execute restart, runtime, tunnel, logger, concurrency, failure, and stale-generation tests on Vite 6/7/8.

## #183 — Vite build operation scope

Disposition: **accept operation-scope invariant; hold scope boundary for real programmatic tests**

The plugin sets `process.env.CLOUDFLARE_VITE_BUILD = "true"` during build config. Preview later reads the process-global marker to choose `prerenderWorkerConfigPath` rather than the ordinary entry path. Production code never restores it.

The package's own programmatic playground harness manually deletes the marker after `buildApp()` because a later independent preview runs in the same process. This is direct acknowledgement of operation-state leakage.

The model proves successful build, failed build, and concurrent unrelated preview all observe sticky process state. An AsyncLocalStorage build scope isolates nested preview, keeps unrelated preview outside the build, preserves failure identity, and leaves no scope afterward.

The draft wraps `builder.buildApp()`. Framework child servers can also be created earlier in `configResolved()`; a child `isPreview` path must be characterized before production use. The related force-build-output flag is a negative control because it is set inside a dedicated `cf-vite` process that exits.

Gate: execute success, failure, concurrency, custom buildApp, environment-restoration, actual deploy-config selection, and configResolved child-preview tests on Vite 6/7/8.

## Executed models

- A001 teardown ownership and bounded cleanup.
- A002 discovery and redirect probes.
- A003 receipt and reporting guard.
- #165 container cleanup ownership models.
- #179 shared-context, restart handoff, and tunnel manager lifetime models.
- #183 sticky marker and scoped build-operation model.

## Centralized visibility

- #88 is the canonical batch review hub.
- #165, #179, and #183 are separate filterable candidates.
- #112 retains this synthesis and durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 is a dated projection and does not override live issue state.

All extracted candidates use:

- `state:ready`
- `type:lane`
- `parallel-safe`
- `target:workers-sdk`
- `programme:sdk-integration-lifecycle`

## Recommended order

1. Execute A001 runtime-first regressions.
2. Execute A003 helper and mocked deploy paths.
3. Execute A002 configuration matrix.
4. Execute #165 container ownership tests.
5. Execute #179 restart and owner-handoff tests on Vite 6/7/8.
6. Execute #183 programmatic build/preview scope tests on Vite 6/7/8.
7. Prove #179 runtime/tunnel isolation before drafting the broad owner registry.
8. Return to A001 aggregation and deadlines separately.

## Boundary

No live deployment, route update, container rollout, tunnel, rollback, Docker reproduction, browser multi-server run, or upstream interaction occurred.
