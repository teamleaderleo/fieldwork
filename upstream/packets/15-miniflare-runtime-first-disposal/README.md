# Unit 15 — Miniflare runtime-first disposal

## In simple words

Miniflare owns a workerd child process and several independent cleanup hooks. The repaired candidate starts workerd termination before awaiting browser or proxy cleanup, so those hooks cannot skip or indefinitely delay the ownership action. Review also repaired the first regression test so it always completes the remaining Miniflare teardown after the injected proxy failure. The source is one clean commit and is ready for the repository owner’s decision; exact-head workflows are pending.

Current state: **READY FOR OWNER DECISION — source and test cleanup repaired; exact-head workflows pending**

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
| Packet branch | `teamleaderleo/fieldwork:upstream/15-miniflare-runtime-first-disposal` |
| Packet workflow base | `920f87cb25dd0cc7901d59ea2019cd4b4a193b94` |
| Retired materialization run / job | `30674559186` / `91299001548` — success |

## Source mechanism

At the pinned base, `Miniflare.dispose()` awaits browser and proxy cleanup before `Runtime.dispose()`. A rejection exits the cleanup block and an unresolved promise suspends it before the workerd owner receives a chance to terminate the child.

The candidate:

1. removes the exit hook;
2. invokes `Runtime.dispose()` and retains its promise;
3. observes that promise immediately so an earlier failure cannot create an unhandled rejection;
4. awaits browser cleanup;
5. awaits proxy cleanup;
6. awaits runtime exit before closing dispatchers;
7. continues the existing later cleanup sequence.

`Runtime.dispose()` performs the termination request synchronously before returning its child-exit promise.

## Browser Rendering interaction

Source review found no direct dependency on a live workerd process. `closeBrowserProcess()` receives its own browser-process handle and CDP WebSocket endpoint, attempts `Browser.close`, then kills and waits for that browser process if graceful close fails. This supports the selected early-start ordering. Exact target execution remains useful, but the browser question is no longer an unexamined design blocker.

## Exact changed-file fence

The clean branch is one commit over the base and contains exactly:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

Diff summary: `136` additions, `4` deletions. No workflow, packet, experiment, or carrier machinery is present.

## Focused controls

1. Proxy cleanup rejects; the first disposal still requests workerd `SIGKILL`. After restoring the injected failure, the test always calls `mf.dispose()` again to finish remaining teardown, then waits for the killed child to exit.
2. Proxy cleanup remains pending; the workerd kill request occurs before the hook is released.
3. A later `DevRegistry.dispose()` rejection confirms runtime termination already occurred.

The first test repair matters: merely awaiting the killed child did not complete the rest of Miniflare cleanup after the earlier proxy rejection.

## Exact-head workflows

Triggered for `d668e318f5e6b0c1e2cbd66ac4b46d8cddbca642`:

- CI `30756281544`;
- CI (Other Node Versions) `30756281540`;
- Changeset Review `30756281529`;
- Semgrep OSS scan `30756281508`.

Other repository workflows are queued or skipped by path filters. No exact-head pass is claimed before execution. Pending infrastructure is an evidence boundary, not an unfixed source defect.

## Owner decision surface

The repository owner can decide whether this candidate should advance after exact-head results are available. Before public filing, refresh current main, duplicate/overlap, contribution policy, and disclosure requirements. Public contact remains separately unauthorized.

## Packet map

- [`DEEP_DIVE.md`](./DEEP_DIVE.md)
- [`APPROACHES.md`](./APPROACHES.md)
- [`TESTS.md`](./TESTS.md)
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
- [`REVIEW.md`](./REVIEW.md)
