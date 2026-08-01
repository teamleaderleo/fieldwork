# Unit 15 — Miniflare runtime-first disposal

## In simple words

Miniflare owns a workerd child process and several independent cleanup hooks. Its current disposal order waits for browser and proxy cleanup before asking workerd to exit. A rejected or pending hook can therefore leave the child alive. The clean candidate starts runtime disposal first, then preserves the existing cleanup order. The source branch and focused tests now exist; repository execution is running on the owned-fork draft PR.

Current disposition: **EXECUTE**

Date: `2026-08-01`

Upstream contact authorized: `false`  
Upstream contact performed: `false`

## Bounded unit

This packet covers one ownership invariant in `Miniflare.dispose()`:

> Once disposal begins, the workerd termination request should start before an independently awaited teardown hook can reject or remain pending.

The unit contains only:

1. the focused disposal-order source change;
2. three target-native lifecycle controls;
3. one Miniflare patch changeset.

The following remain outside this unit:

- aggregation of multiple teardown errors;
- preservation of initialization errors when later cleanup also fails;
- deadlines or phase-wide `allSettled()` cleanup;
- Vite server owner handoff;
- browser-process teardown implementation;
- Durable Object teardown behavior;
- claims that this mechanism caused any particular public report.

## Exact current revisions

| Record | Exact revision |
| --- | --- |
| Current public Workers SDK base | [`cloudflare/workers-sdk@95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`](https://github.com/cloudflare/workers-sdk/commit/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d) |
| Owned fork `main` | [`teamleaderleo/workers-sdk@95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`](https://github.com/teamleaderleo/workers-sdk/commit/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d) |
| Clean target branch | `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal` |
| Clean target head | [`56f4df168d7c4707890ca3345e3d4a34ee3fa08a`](https://github.com/teamleaderleo/workers-sdk/commit/56f4df168d7c4707890ca3345e3d4a34ee3fa08a) |
| Canonical owned-fork source PR | [`teamleaderleo/workers-sdk#5`](https://github.com/teamleaderleo/workers-sdk/pull/5) |
| Packet branch | `teamleaderleo/fieldwork:upstream/15-miniflare-runtime-first-disposal` |
| Packet workflow base | [`920f87cb25dd0cc7901d59ea2019cd4b4a193b94`](https://github.com/teamleaderleo/fieldwork/commit/920f87cb25dd0cc7901d59ea2019cd4b4a193b94) |
| Legacy carrier PR | [`teamleaderleo/workers-sdk#1`](https://github.com/teamleaderleo/workers-sdk/pull/1) |
| Legacy carrier head | [`7d51105349020151c2efd0a961706c59228ca9fd`](https://github.com/teamleaderleo/workers-sdk/commit/7d51105349020151c2efd0a961706c59228ca9fd) |
| Accepted A001 evidence point | [`fa39841a98d71edd2df7561beb877f4dacbc6b7c`](https://github.com/teamleaderleo/workers-sdk/commit/fa39841a98d71edd2df7561beb877f4dacbc6b7c) |
| Legacy source base | [`161443215fba3ac77407ba30f6996aa9963a0276`](https://github.com/teamleaderleo/workers-sdk/commit/161443215fba3ac77407ba30f6996aa9963a0276) |
| Durable review hub | [`teamleaderleo/fieldwork#88`](https://github.com/teamleaderleo/fieldwork/issues/88) |
| A001 result PR | [`teamleaderleo/fieldwork#98`](https://github.com/teamleaderleo/fieldwork/pull/98) |
| Coordinator synthesis | [`teamleaderleo/fieldwork#112`](https://github.com/teamleaderleo/fieldwork/pull/112) |
| Retired materialization carrier | [`teamleaderleo/workers-sdk#4`](https://github.com/teamleaderleo/workers-sdk/pull/4) |
| Materialization run / job | [`30674559186`](https://github.com/teamleaderleo/workers-sdk/actions/runs/30674559186) / `91299001548` — success |

## Current-source observation

At exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`, [`packages/miniflare/src/index.ts`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/packages/miniflare/src/index.ts) awaits cleanup in this order inside `Miniflare.dispose()`:

1. `#closeBrowserProcesses()`;
2. `#proxyClient?.dispose()`;
3. `#runtime?.dispose()`;
4. later dispatchers, loopback server, WebSockets, temporary files, registry, and proxy controllers.

A rejection or unresolved promise in either earlier awaited step prevents execution from reaching `Runtime.dispose()`. `Runtime.dispose()` synchronously clears the child reference, destroys its streams, sends `SIGKILL`, then returns the child-exit promise.

## Clean candidate

The candidate at `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`:

1. removes the exit hook;
2. invokes `Runtime.dispose()` and retains its promise;
3. attaches an immediate rejection observer so an earlier cleanup failure cannot create an unhandled rejection;
4. awaits browser cleanup;
5. awaits proxy cleanup;
6. awaits the retained runtime-exit promise before closing dispatchers.

This starts the workerd kill request before independent awaits while preserving dispatcher shutdown after runtime exit.

## Exact changed-file fence

The clean branch is one commit over the base and contains exactly:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

Diff summary: `123` additions, `4` deletions. Temporary workflows, experiments, packet files, and carrier machinery are absent from the canonical source branch.

## Focused controls

1. proxy cleanup rejects and the first disposal still requests `SIGKILL` for workerd;
2. proxy cleanup remains pending and the workerd kill request occurs before the pending hook is released;
3. a later `DevRegistry.dispose()` rejection confirms the runtime had already been terminated.

The legacy fourth test covering initialization-error preservation belongs to a separate error-aggregation unit and remains excluded.

## Current execution

Owned-fork source PR `teamleaderleo/workers-sdk#5` opened at exact head `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`.

Repository workflows started for that head, including:

- CI — run `30690756068`;
- CI (Other Node Versions) — run `30690756037`;
- Changeset Review — run `30690756089`;
- Semgrep OSS scan — run `30690756086`;
- repository integration suites triggered by the target PR.

The focused package assertion still needs a retained job-level execution receipt. This is an execution task, so the current disposition is **EXECUTE**.

## Prior art and duplicate result

- The current base still contains the ordering gap.
- The legacy owned carrier combines this unit with adjacent lifecycle investigations; the clean candidate extracts only this unit.
- `cloudflare/miniflare#392` is repository-migration context and does not directly establish the fine-grained must-run ownership fix.
- `cloudflare/workers-sdk#12025`, `#13078`, and `#14727` establish adjacent runtime, temporary-directory, and browser teardown precedents.
- `cloudflare/workers-sdk#14903` remains a symptom match with an unresolved causal link. The packet makes no claim that this candidate fixes that report.

## Remaining work in strict order

1. Inspect exact-head CI results and job logs for source PR `#5`.
2. Confirm the focused lifecycle file actually executes and record its assertion count and result.
3. Run or obtain a baseline receipt for the same controls at `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.
4. Classify every failed or skipped target gate by source relevance.
5. Re-review browser-cleanup interaction and simultaneous runtime/earlier-hook failure precedence.
6. Synchronize `TESTS.md`, `REVIEW.md`, the source PR front page, and issue `#435` at the final exact head.
7. Obtain independent final review before promotion to `READY`.
8. Keep public issue and PR drafts dormant until explicit public-contact authority.

## Packet map

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — source trace, mechanism, evidence limits, compatibility concerns.
- [`APPROACHES.md`](./APPROACHES.md) — selected approach and rejected alternatives.
- [`TESTS.md`](./TESTS.md) — executed evidence, prepared controls, and remaining gates.
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — public issue draft only.
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — public PR draft only.
- [`REVIEW.md`](./REVIEW.md) — bounded self-review and continuation checklist.
