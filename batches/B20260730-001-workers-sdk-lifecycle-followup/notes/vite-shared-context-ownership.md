# Vite shared-context ownership follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #179

Sibling candidate: #165

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `a4fbcd0b2bce78199e24529725409b19546c2df0`

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

## Executed model

Executed:

```sh
node /tmp/vite-shared-context-ownership.mjs
```

The executed content is identical to the committed Workers SDK artifact:

`fieldwork-experiments/teardown-lifecycle-hardening/vite-shared-context-ownership.mjs`

Output:

```text
PASS: a global runtime lets one plugin overwrite another plugin runtime
PASS: a global restart counter can suppress an unrelated final close
PASS: owner-scoped runtimes isolate concurrent servers
PASS: owner-scoped restart state does not suppress another owner cleanup
PASS: sequential generations of one logical server retain restart continuity
```

Evidence class: `source-read` plus `model-executed`.

No Vite package, multi-server, tunnel, or browser test executed.

## Draft repair slices

### Narrow restart-state correction

`vite-instance-restart-scope.patch` moves restart accounting from `SharedContext` into one `PluginContext`.

The patched `restart()` and close wrappers for one Vite server capture that same context, so unrelated servers do not need to share the counter.

This patch remains unapplied pending package tests.

### Logical runtime-owner design

The Miniflare, tunnel, export-map, warning, and tunnel-hostname fields still need continuity across sequential restart generations without being shared by concurrent servers.

A complete design needs:

- an opaque logical-server owner token;
- one state record per owner;
- a bounded handoff from an old restart generation to its replacement;
- no project-root-only key, because concurrent servers may intentionally share a root;
- protection against a stale generation disposing the replacement;
- owner removal after true final close;
- primary-error preservation when handoff cleanup also fails.

The exact Vite restart construction order needs package instrumentation before choosing the handoff mechanism.

## Required tests

1. Server A restarting does not suppress unrelated server B's final cleanup.
2. Server A's own restart close still skips final teardown.
3. Two concurrent servers retain distinct Miniflare options and request routing.
4. Updating server B does not mutate server A's runtime.
5. Closing server B does not dispose server A's runtime or tunnel.
6. Two tunnels retain distinct origins, public URLs, loggers, and allowed-host state.
7. Sequential generations of server A retain only A's state.
8. Failed restart leaves exactly one reachable cleanup owner.
9. Export-type and warning state from one server cannot alter another server's validation.
10. Final close removes the owner record and repeated close remains safe.

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
