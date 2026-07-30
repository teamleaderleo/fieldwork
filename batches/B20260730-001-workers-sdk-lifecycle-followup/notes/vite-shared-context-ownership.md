# Vite shared-context ownership follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #179

Sibling candidates: #165, #183

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `de3ed9fbf45a04cf2201a5571ade9afbe081a987`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

The Cloudflare Vite plugin deliberately preserves state across one server restart. Today that state is held in process-global objects shared by every `cloudflare()` instance.

Unrelated or later servers can therefore share Miniflare, restart classification, tunnels, export state, warning state, tunnel hostnames, and even the first server's tunnel logger.

## Source findings

`src/index.ts` creates one module-global `SharedContext`. Every `cloudflare()` call creates a fresh `PluginContext` backed by it.

The shared record owns Miniflare, Worker export types, worker-config warning state, restart accounting, and tunnel hostnames.

A second plugin can call `setOptions()` on the Miniflare observed by the first. Server A's shared restart counter can also make unrelated server B skip final container, tunnel, and Miniflare teardown.

The tunnel plugin uses one module-global `TunnelManager`. Starting or closing another server mutates that manager. `dispose()` clears active tunnel state but does not clear the module slot or constructor-captured logger. A later server therefore reuses the disposed manager and routes fresh tunnel startup, warning, close, and exit diagnostics through the previous server's logger.

Global tunnel helper functions also target this shared manager rather than one server owner.

The dev tunnel allowed-host path is a negative control: after public hostnames are discovered, the plugin records them and restarts the dev server when its resolved host list is missing them.

## Vite restart order

The plugin supports Vite 6, 7, and 8. Vite 6.1.0, 7.1.12, and 8.1.5 all create replacement plugins before closing the old generation, then graft the replacement onto the existing user-facing server object.

This makes an async-scoped logical-owner handoff viable across all supported majors and explains why a completely independent context per factory call would strand restart state.

## Executed models

Executed identical committed content:

```sh
node /tmp/vite-shared-context-ownership.mjs
node /tmp/vite-restart-owner-handoff.mjs
node /tmp/vite-tunnel-manager-reuse.mjs
```

Results:

```text
PASS: a global runtime lets one plugin overwrite another plugin runtime
PASS: a global restart counter can suppress an unrelated final close
PASS: owner-scoped runtimes isolate concurrent servers
PASS: owner-scoped restart state does not suppress another owner cleanup
PASS: sequential generations of one logical server retain restart continuity
PASS: independent first-generation servers receive distinct owners
PASS: replacement plugins inherit only the restarting server owner
PASS: unrelated final close proceeds during another server restart
PASS: concurrent restarts keep owner handoffs isolated
PASS: failed replacement construction preserves the original server owner and error
PASS: a disposed global tunnel manager is reused with the old logger
PASS: owner-scoped tunnel managers keep concurrent loggers isolated
PASS: final close removes only the intended tunnel owner
```

Evidence class: `source-read` plus `model-executed`.

No Vite package, live tunnel, browser, or multi-server integration test executed.

## Draft repair slices

### Narrow restart-state patch

`vite-instance-restart-scope.patch` moves restart accounting into one `PluginContext`. This prevents one server's restart from suppressing another server's close. It remains unapplied.

### Logical owner and generation handoff

A promising foundation is an async-scoped handoff:

- first-generation plugin factories outside restart create distinct owners;
- patched restart runs Vite's original restart inside that owner's async context;
- replacement factories claim only that owner;
- concurrent restarts keep separate contexts;
- failed replacement construction preserves the old owner and exact error.

The owner record should include Miniflare, one TunnelManager constructed with the current owner's logger, export types, warning state, and tunnel hostnames.

True final close must dispose and delete only that owner record. A later independent server must construct a manager with its own logger. A stale old generation must not dispose a replacement.

Do not key only by project root and do not use a process-global handoff queue.

## Required tests

1. A restarting server does not suppress unrelated final cleanup.
2. Its own restart close still skips final teardown.
3. Concurrent servers retain distinct Miniflare options and routing.
4. Updating or closing B does not mutate or dispose A.
5. Concurrent tunnels retain distinct origins, URLs, loggers, host state, toggle behavior, and expiry state.
6. Final close of A removes A's manager; later C logs through C's logger.
7. Sequential generations inherit only their owner.
8. Concurrent restarts do not cross-claim owners.
9. Failed replacement preserves the old owner and exact error.
10. A stale old generation cannot dispose the replacement.
11. Export and warning state do not cross servers.
12. Final close removes only the intended owner and repeated close is safe.

Run the restart and handoff matrix on Vite 6, 7, and 8.

## Coordination placement

- #179 is canonical for this finding.
- #165 remains the container cleanup candidate.
- #183 remains the build-operation marker candidate.
- #88 remains the parent review hub.
- #112 retains the durable synthesis.
- #87 and PR #105 own the generated review projection.

## Boundary

Do not merge this broad owner work into the first Miniflare patch, #165, or #183. The restart counter is a narrow slice; runtime and tunnel ownership require dedicated integration evidence.

No upstream interaction occurred.
