# Unit 15 — Miniflare runtime-first disposal

## In simple words

Miniflare can fail to request termination of its owned workerd child when an earlier browser or proxy cleanup rejects or remains pending. The candidate starts runtime disposal first and the repaired tests now complete their own teardown correctly. Source review supports the mechanism, but the repaired exact head is not yet ready for an owner decision: the broad matrix contains four unclassified red test shards, and a dedicated focused execution carrier is queued.

Current state: **EXECUTION UNDER SCRUTINY — NOT YET OWNER DECISION**

Date: `2026-08-03`

Upstream contact authorized: `false`  
Upstream contact performed: `false`

## Bounded unit

This packet covers one ownership invariant in `Miniflare.dispose()`:

> Once disposal begins, the workerd termination request should start before an independently awaited teardown hook can reject or remain pending.

The unit contains only:

1. the focused disposal-order source change;
2. three target-native lifecycle controls;
3. one Miniflare patch changeset.

It excludes multi-error aggregation, initialization-error precedence, generic cleanup deadlines, Vite owner handoff, Durable Object teardown, and causal claims about public reports.

## Exact current revisions

| Record | Exact revision |
| --- | --- |
| Pinned Workers SDK base | `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d` |
| Clean target branch | `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal` |
| Clean target head | `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642` |
| Canonical owned-fork source PR | `teamleaderleo/workers-sdk#5` |
| Focused execution carrier | `teamleaderleo/workers-sdk#16` |
| Focused carrier head | `0f9d818c3c9bfceb01d070d971e44e276e325055` |
| Focused workflow run | `30796108253` — queued at refresh |
| Packet branch | `teamleaderleo/fieldwork:upstream/15-miniflare-runtime-first-disposal` |

## Source mechanism

At the pinned base, `Miniflare.dispose()` awaits browser and proxy cleanup before `Runtime.dispose()`. A rejection exits the cleanup block and an unresolved promise suspends it before the runtime owner requests child termination.

The candidate:

1. removes the exit hook;
2. invokes `Runtime.dispose()` and retains its promise;
3. observes that promise immediately so an earlier failure cannot create an unhandled rejection;
4. awaits browser cleanup;
5. awaits proxy cleanup;
6. awaits runtime exit before closing dispatchers;
7. continues the existing later cleanup sequence.

`Runtime.dispose()` performs the workerd termination request synchronously before returning its child-exit promise.

## Browser Rendering interaction

Source review found no direct dependency on a live workerd process. `closeBrowserProcess()` receives its own browser-process handle and CDP WebSocket endpoint, attempts `Browser.close`, then kills and waits for that browser process if graceful close fails. This supports the selected early-start ordering, but it does not replace target execution.

## Exact changed-file fence

The clean branch is one commit over the base and contains exactly:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

Diff summary: `136` additions, `4` deletions. No workflow, packet, experiment, or carrier machinery is present on the canonical source branch.

## Focused controls

1. Proxy cleanup rejects; the first disposal still requests workerd `SIGKILL`. After restoring the injected failure, the test always calls `mf.dispose()` again to finish remaining teardown and waits for the identified child exit.
2. Proxy cleanup remains pending; the workerd kill request occurs before the hook is released.
3. A later `DevRegistry.dispose()` rejection confirms runtime termination already occurred.

## Completed broad workflow classification

Succeeded at source head `d668e318...`:

- Validate PR Description;
- Semgrep;
- Local Explorer UI E2E;
- C3 E2E;
- CI on other Node versions;
- Vite Plugin E2E;
- Wrangler E2E;
- Vite plugin playgrounds.

Changeset Review calculated a valid `miniflare` patch release, then failed while trying to post a GitHub review because the integration lacked permission. That is workflow-token noise, not a changeset-content failure.

Main CI run `30756281544` contains four failed shards that are not yet classified:

- Ubuntu package tests shard 1/3;
- macOS package tests shard 1/3;
- Windows package tests shard 1/3;
- Windows fixture tests shard 5/6.

Those red shards cannot be dismissed without logs or a narrower exact-head receipt.

## Focused execution

Execution-only PR `teamleaderleo/workers-sdk#16` adds one temporary workflow over the canonical source head and runs:

```text
pnpm install --frozen-lockfile
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare check:type
```

The carrier is not a delivery candidate and must be closed after its receipt is transferred.

## Decision rule

Do not ask the owner to advance this unit until the focused workflow executes successfully or produces a concrete defect that is repaired. The broad red shards must also be classified far enough to show whether they touch this three-file candidate.

## Packet map

- [`DEEP_DIVE.md`](./DEEP_DIVE.md)
- [`APPROACHES.md`](./APPROACHES.md)
- [`TESTS.md`](./TESTS.md)
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
- [`REVIEW.md`](./REVIEW.md)
