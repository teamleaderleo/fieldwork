# Vite shared-context ownership follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #179

Sibling candidate: #165

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

The Cloudflare Vite plugin deliberately keeps state across one dev server's restart. Today that state is process-global, so two unrelated Cloudflare Vite servers in the same Node.js process can accidentally share a runtime, restart flag, tunnel, export map, warning latch, and tunnel hostnames.

A restart in one server can make another server skip final teardown. Starting or updating the second server can replace the Miniflare options observed by the first.

## Source findings

`src/index.ts` creates one module-global `SharedContext`. Every `cloudflare()` call creates a fresh `PluginContext` backed by that same object.

The shared object owns:

- Miniflare;
- Worker export-type state;
- worker-config warning state;
- restart accounting;
- tunnel hostnames.

`startOrUpdateMiniflare()` creates the shared runtime once and later plugin instances call `setOptions()` on the same object. The second plugin can therefore change the runtime observed by the first.

The restart counter is also shared. Dev and tunnel close wrappers skip final teardown when that counter is non-zero. Server A restarting while unrelated server B closes can cause B to skip its final container, tunnel, and Miniflare cleanup.

The tunnel plugin uses one module-global `TunnelManager`. A later server can replace the active tunnel, and closing any server can dispose the shared tunnel. Tunnel hostnames are stored in the same shared context and folded into Vite `allowedHosts` during config.

This proves process-wide ownership conflation. Real-world incidence remains unknown because ordinary CLI use commonly runs one server per process.

## Vite restart order across supported majors

The plugin declares support for Vite `^6.1.0 || ^7.0.0 || ^8.0.0`.

Vite 6.1.0, 7.1.12, and 8.1.5 all use the same relevant sequence:

1. create the replacement server, plugins, and middleware from the existing inline config;
2. close the old server;
3. copy the replacement server onto the existing user-facing object;
4. rebind the replacement's internal server reference;
5. listen again.

Replacement plugin construction therefore occurs inside the old server's `restart()` call before old-generation close. This supports an async-scoped logical-owner handoff across all supported majors.

It also rules out the naive repair of creating an unrelated shared context for every `cloudflare()` call: the old close intentionally skips final teardown during restart, so the replacement must claim the old logical owner's state or the old runtime becomes stranded.

## Executed models

Executed:

```sh
node /tmp/vite-shared-context-ownership.mjs
node /tmp/vite-restart-owner-handoff.mjs
```

The executed content is identical to the committed Workers SDK artifacts.

### Global-versus-owner-scoped state

```text
PASS: a global runtime lets one plugin overwrite another plugin runtime
PASS: a global restart counter can suppress an unrelated final close
PASS: owner-scoped runtimes isolate concurrent servers
PASS: owner-scoped restart state does not suppress another owner cleanup
PASS: sequential generations of one logical server retain restart continuity
```

### Async restart owner handoff

```text
PASS: independent first-generation servers receive distinct owners
PASS: replacement plugins inherit only the restarting server owner
PASS: unrelated final close proceeds during another server restart
PASS: concurrent restarts keep owner handoffs isolated
PASS: failed replacement construction preserves the original server owner and error
```

Evidence class: `source-read` plus `model-executed`.

No Vite package, multi-server, tunnel, or browser test executed.

## Draft repair slices

### Narrow restart-state correction

`vite-instance-restart-scope.patch` moves restart accounting from `SharedContext` into one `PluginContext`.

The patched `restart()` and close wrappers for one Vite server capture that same context, so unrelated servers do not need to share the counter.

This patch remains unapplied pending package tests.

### Logical runtime-owner handoff

A promising foundation is an async-scoped handoff:

- initial `cloudflare()` calls outside a restart create separate owners;
- the patched `restart()` runs Vite's original restart inside that owner's async context;
- replacement plugin factories invoked during config reload claim only that owner;
- concurrent restarts keep distinct async contexts;
- failed replacement construction retains the old generation and its owner.

The complete owner record should contain Miniflare, tunnel manager, export types, warning state, and tunnel hostnames. A generation protocol must prevent an old close from disposing a replacement that already claimed the owner.

Do not use a project-root-only key or process-global handoff queue. Concurrent servers can share a root and concurrent restarts can interleave.

## Required tests

1. Server A restarting does not suppress unrelated server B's final cleanup.
2. Server A's own restart close still skips final teardown.
3. Two concurrent servers retain distinct Miniflare options and request routing.
4. Updating server B does not mutate server A's runtime.
5. Closing server B does not dispose server A's runtime or tunnel.
6. Two tunnels retain distinct origins, public URLs, loggers, and allowed-host state.
7. Sequential generations of server A inherit only A's owner.
8. Concurrent restarts of A and B do not cross-claim owners.
9. Failed replacement construction preserves the old owner and exact failure.
10. A stale old generation cannot dispose the replacement.
11. Export-type and warning state from one server cannot alter another server's validation.
12. Final close removes the owner record and repeated close remains safe.

The restart and owner-handoff tests should run against Vite 6, 7, and 8.

## Coordination placement

- Candidate issue #179 is the canonical review and disposition surface.
- Candidate #165 remains the separate container cleanup callback/tag-ownership candidate.
- Batch issue #88 remains the parent Workers SDK review hub.
- PR #112 remains the repository-backed synthesis snapshot.
- Meta issue #87 and PR #105 own the centralized review projection.

The established labels are sufficient for discovery:

- `state:ready`
- `type:lane`
- `parallel-safe`
- `target:workers-sdk`
- `programme:sdk-integration-lifecycle`

## Boundary

Do not merge the broad logical-owner work into the first Miniflare runtime-first or container-cleanup patch. The restart counter is a small independent slice; runtime and tunnel ownership need dedicated integration evidence.

No upstream interaction occurred.
