# Vite remote proxy session ownership follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #186

Related logical-owner candidate: #179

Sibling candidates: #165, #183, #187

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `f1fa08c44cda1c5a77568dcf8a64a45a91702c88`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

The Cloudflare Vite plugin caches live remote-binding proxy sessions in one module-global map keyed only by Worker config path. Dev and preview share that map. Final Vite close neither disposes nor removes its entries.

The session represents an authenticated remote connection, but its reuse decision does not include Worker name, account ID, compliance region, profile directory, or current logger.

The remote-bindings package also stores one module-global live logger. Starting a second session redirects the first session's later error and teardown diagnostics to the second session's logger.

## Source findings

Both Vite dev and preview:

- look up `remoteProxySessionsDataMap` by `configPath`;
- pass the existing entry into `maybeStartOrUpdateRemoteProxySession()`;
- write the returned live session back under that path.

`maybeStartOrUpdateRemoteProxySession()` compares only explicit auth-hook identity and remote bindings. Vite passes explicit auth as `undefined`; the actual auth hook is created only when starting a session from account ID, profile directory, and logger.

When config path and bindings remain stable, account, compliance, profile, Worker name, and logger changes therefore retain the old live session and connection string.

Wrangler's LocalRuntimeController owns and disposes its session during controller teardown. The Vitest pool also disposes its session during worker stop, but currently leaves the map entry present.

A disposed cached entry has no disposed marker. Later unchanged bindings can return the disposed session because its ready promise remains resolved and no update is requested.

`startRemoteProxySession()` calls `initLogger()`, which replaces an exported module-global logger. `DevEnv` imports that live binding and reads it later during errors, proxy-send failures, and teardown. A second session can therefore reroute the first session's asynchronous diagnostics.

## Executed models

Executed:

```sh
node /tmp/vite-remote-proxy-session-ownership.mjs
node /tmp/remote-bindings-global-logger.mjs
```

The executed content is identical to committed Workers SDK artifacts.

Output:

```text
PASS: Vite final close leaves a cached remote proxy session live
PASS: same config path reuses stale account, profile, worker, and logger identity
PASS: disposing without deleting the cache returns a disposed session later
PASS: owner-scoped sessions isolate servers and dispose only on final close
PASS: connection identity changes replace and dispose the old session
PASS: a global live logger routes session A diagnostics to session B
PASS: session-captured loggers preserve concurrent diagnostic ownership
```

Evidence class: `source-read` plus `model-executed`.

No live remote binding, credential, account, network, Vite package, or Vitest pool test executed.

## Draft repair slices

`remote-proxy-session-identity.patch`:

- records Worker name, account ID, compliance region, profile directory, and explicit auth identity;
- replaces the session when connection identity changes;
- retains `updateBindings()` for binding-only changes under stable identity;
- deletes the exact Vitest pool cache entry after disposal without deleting a concurrently installed replacement.

Vite lifecycle ownership should integrate with #179's logical-server owner record:

- sequential restart generations may inherit stable sessions;
- concurrent servers do not share solely because config path matches;
- final close disposes and removes all owner sessions;
- cleanup failure preserves the primary close error and retains retry state only while a retry owner remains reachable.

Remote-bindings runtime objects should receive or capture a session-owned logger. Constructor/context injection is preferred over async-local logger state because long-lived event callbacks may run outside startup context.

The Worker-name replacement rule needs protocol review. Account, compliance, profile, and auth changes must not silently retain the old authenticated session.

## Required tests

1. Vite final close disposes and removes all owner sessions.
2. Restart transfers sessions only to the same logical owner replacement.
3. Concurrent same-config-path servers receive distinct sessions and loggers.
4. Changed account, compliance, profile, or auth generation starts a new session.
5. Worker-name changes are characterized.
6. Binding-only changes use updateBindings under stable identity.
7. Failed replacement does not silently continue the old identity.
8. Disposed cache entries are never returned in Vite or Vitest pool.
9. Session A diagnostics and teardown keep logger A after session B starts.
10. New sessions use the current owner logger.
11. Final-close disposal failure preserves primary error and explicit retry state.
12. Dev and preview do not share solely by config path.
13. Tests use mocked session/auth factories; no credentials or network required.

## Coordination placement

- #186 is canonical for remote proxy session ownership, identity, and logger routing.
- #179 owns the broader logical-server generation registry.
- #165, #183, and #187 remain separate Vite candidates.
- #88 remains the batch hub.
- #112 retains synthesis and notes.
- #87 and PR #105 own generated coordination.

## Boundary

This candidate controls a live authenticated network session and remains distinct even though its lifecycle owner integrates with #179.

No upstream interaction occurred.
