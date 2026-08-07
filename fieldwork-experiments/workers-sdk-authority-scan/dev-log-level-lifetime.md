# Wrangler dev log-level lifetime

Current public source: `cloudflare/workers-sdk@20470fa8b09761c50b5c2c1d6a5f2652b61bd271`.

Relevant files:

- `packages/wrangler/src/dev/start-dev.ts`
- `packages/wrangler/src/api/dev.ts`
- `packages/wrangler/src/logger.ts`

## Source finding

`startDev()` assigns `logger.loggerLevel = args.logLevel` before creating the dev environment.

The value belongs to Wrangler's singleton logger. The startup error path tears down partially created resources but does not restore the previous level. The successful result also provides teardown through the returned dev environment without restoring the level.

The public `unstable_dev()` API exposes `logLevel`, awaits `startDev()`, and later stops the environment through its returned `stop()` method. A caller can therefore start and stop a dev server at a custom level and leave later Wrangler API operations at that level.

Two overlapping dev operations also replace the singleton level read by each other's later diagnostics.

Wrangler's logger already provides `runWithLogLevel()` backed by `AsyncLocalStorage`, which is the direct project precedent for operation-scoped log-level ownership.

## Executed model

```sh
node fieldwork-experiments/workers-sdk-authority-scan/dev-log-level-lifetime.mjs
```

Output:

```text
PASS: failed dev startup leaves the singleton logger overridden
PASS: successful dev stop leaves the singleton logger overridden
PASS: overlapping dev sessions replace each other's log level
PASS: async-local log levels preserve concurrent owner intent
```

No dev server, port, runtime, network request, or public upstream interaction was used.

## Required target controls

1. Failed `startDev()` restores the caller's prior logger level.
2. `unstable_dev().stop()` leaves later API logging unchanged.
3. Dev session A at `debug` and B at `error` retain their own levels.
4. Asynchronous startup, runtime, teardown, and tunnel diagnostics use the intended session level.
5. A session without an explicit level uses the caller/default level without resetting another operation.
6. Out-of-order stop and startup failure do not alter another active session.
7. Existing CLI behavior during one ordinary `wrangler dev` process remains unchanged.
8. Logger hooks and disk logging remain owner-correct.

## Candidate direction

Run each dev operation inside the existing `runWithLogLevel()` async context instead of assigning the singleton property. Long-lived event emitters, runtime controllers, tunnel callbacks, and teardown callbacks require target-native checks to confirm they retain the originating async context. Where they do not, capture an owner-bound logger or level at controller creation.

## Rejected direction

Save and restore the singleton around `startDev()` alone. The function returns while the dev session remains live, and overlapping sessions can stop out of order.

## Boundary

- #472 owns deploy-helper logger/fetch/prompt context.
- #186 owns remote-binding session logger ownership.
- This finding owns Wrangler dev-session log-level lifetime.
