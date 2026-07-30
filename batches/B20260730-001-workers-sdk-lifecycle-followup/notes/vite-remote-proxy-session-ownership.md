# Vite remote proxy session ownership follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #186

Related logical-owner candidate: #179

Sibling candidates: #165, #183

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `06db1944c9b0b2ff0c4efc939ac924a6766a7f46`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

The Cloudflare Vite plugin caches live remote-binding proxy sessions in one module-global map keyed only by Worker config path. Dev and preview share that map. Final Vite close neither disposes nor removes its entries.

The session represents an authenticated remote connection, but its reuse decision does not include Worker name, account ID, compliance region, profile directory, or the current Vite logger.

## Source findings

Both Vite dev and preview:

- look up `remoteProxySessionsDataMap` by `configPath`;
- pass the existing entry into `maybeStartOrUpdateRemoteProxySession()`;
- write the returned live session back under that path.

`maybeStartOrUpdateRemoteProxySession()` compares only explicit auth-hook identity and remote bindings. Vite passes explicit auth as `undefined`; the actual auth hook is created only when starting a session from account ID, profile directory, and logger.

When config path and bindings remain stable, account, compliance, profile, Worker name, and logger changes therefore retain the old live session and connection string.

Wrangler's LocalRuntimeController owns and disposes its session during controller teardown. The Vitest pool also disposes its session during worker stop, but currently leaves the map entry present.

A disposed cached entry has no disposed marker. Later unchanged bindings can return the disposed session because its ready promise remains resolved and no update is requested.

## Executed model

Executed:

```sh
node /tmp/vite-remote-proxy-session-ownership.mjs
```

The executed content is identical to the committed Workers SDK artifact.

Output:

```text
PASS: Vite final close leaves a cached remote proxy session live
PASS: same config path reuses stale account, profile, worker, and logger identity
PASS: disposing without deleting the cache returns a disposed session later
PASS: owner-scoped sessions isolate servers and dispose only on final close
PASS: connection identity changes replace and dispose the old session
```

Evidence class: `source-read` plus `model-executed`.

No live remote binding, credential, account, network, Vite package, or Vitest pool test executed.

## Draft repair slices

`remote-proxy-session-identity.patch`:

- records Worker name, account ID, compliance region, profile directory, and explicit auth identity;
- replaces the session when connection identity changes;
- retains `updateBindings()` for binding-only changes under stable identity;
- deletes the exact Vitest pool cache entry after disposing it, without deleting a replacement installed concurrently.

Vite lifecycle ownership should integrate with #179's logical-server owner record:

- sequential restart generations of one owner may inherit stable sessions;
- concurrent servers do not share sessions merely because config path matches;
- true final close disposes and removes all owner sessions;
- cleanup failure preserves the primary close error and leaves an explicit retry/diagnostic state only while a retry owner remains reachable.

The exact Worker-name replacement rule needs protocol review. Account, compliance, profile, and auth changes must not silently retain the old authenticated session.

## Required tests

1. Vite final close disposes and removes all owner sessions.
2. Restart transfers sessions only to the same logical owner replacement.
3. Concurrent same-config-path servers receive distinct sessions and loggers.
4. Changed account, compliance, profile, or auth generation starts a new session.
5. Worker-name changes are characterized.
6. Binding-only changes use updateBindings under stable identity.
7. Failed replacement does not silently continue the old identity.
8. Disposed cache entries are never returned in Vite or Vitest pool.
9. Current owner logger receives new session diagnostics.
10. Final-close disposal failure preserves primary error and explicit retry state.
11. Dev and preview do not share solely by config path.
12. Tests use mocked session/auth factories; no credentials or network required.

## Coordination placement

- #186 is canonical for remote proxy session ownership and identity.
- #179 owns the broader logical-server generation registry.
- #165 and #183 remain separate Vite candidates.
- #88 remains the batch hub.
- #112 retains synthesis and notes.
- #87 and PR #105 own generated coordination.

## Boundary

This candidate controls a live authenticated network session and should remain a distinct review surface even though its eventual lifecycle owner integrates with #179.

No upstream interaction occurred.
