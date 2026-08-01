# Unit 15 — Miniflare runtime-first disposal

Current disposition: **HOLD**

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
| Current clean target head | `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d` — base only while materialization is queued |
| Packet branch | `teamleaderleo/fieldwork:upstream/15-miniflare-runtime-first-disposal` |
| Initial packet head | [`920f87cb25dd0cc7901d59ea2019cd4b4a193b94`](https://github.com/teamleaderleo/fieldwork/commit/920f87cb25dd0cc7901d59ea2019cd4b4a193b94) |
| Legacy carrier PR | [`teamleaderleo/workers-sdk#1`](https://github.com/teamleaderleo/workers-sdk/pull/1) |
| Legacy carrier head | [`7d51105349020151c2efd0a961706c59228ca9fd`](https://github.com/teamleaderleo/workers-sdk/commit/7d51105349020151c2efd0a961706c59228ca9fd) |
| Accepted A001 evidence point | [`fa39841a98d71edd2df7561beb877f4dacbc6b7c`](https://github.com/teamleaderleo/workers-sdk/commit/fa39841a98d71edd2df7561beb877f4dacbc6b7c) |
| Legacy source base | [`161443215fba3ac77407ba30f6996aa9963a0276`](https://github.com/teamleaderleo/workers-sdk/commit/161443215fba3ac77407ba30f6996aa9963a0276) |
| Durable review hub | [`teamleaderleo/fieldwork#88`](https://github.com/teamleaderleo/fieldwork/issues/88) |
| A001 result PR | [`teamleaderleo/fieldwork#98`](https://github.com/teamleaderleo/fieldwork/pull/98) |
| Coordinator synthesis | [`teamleaderleo/fieldwork#112`](https://github.com/teamleaderleo/fieldwork/pull/112) |
| Owned execution carrier | [`teamleaderleo/workers-sdk#4`](https://github.com/teamleaderleo/workers-sdk/pull/4) |
| Carrier head | [`92eeb04c7866775351e184085cc53c0b9d3b1446`](https://github.com/teamleaderleo/workers-sdk/commit/92eeb04c7866775351e184085cc53c0b9d3b1446) |
| Materialization run / job | [`30674559186`](https://github.com/teamleaderleo/workers-sdk/actions/runs/30674559186) / `91299001548` |

## Current-source observation

At exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`, [`packages/miniflare/src/index.ts`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/packages/miniflare/src/index.ts) still awaits cleanup in this order inside `Miniflare.dispose()`:

1. `#closeBrowserProcesses()`;
2. `#proxyClient?.dispose()`;
3. `#runtime?.dispose()`;
4. later dispatchers, loopback server, WebSockets, temporary files, registry, and proxy controllers.

A rejection or unresolved promise in either earlier awaited step prevents execution from reaching `Runtime.dispose()`. `Runtime.dispose()` synchronously clears the child reference, destroys its streams, sends `SIGKILL`, then returns the child-exit promise. Starting that operation first discharges runtime ownership before later awaits can interrupt control flow.

## Candidate source inventory

The clean branch is intended to contain exactly these three files over the current base:

- `packages/miniflare/src/index.ts`
- `packages/miniflare/test/teardown-lifecycle.spec.ts`
- `.changeset/fuzzy-cats-dispose.md`

Prepared controls:

1. proxy cleanup rejects and the first disposal still requests `SIGKILL` for workerd;
2. proxy cleanup remains pending and the workerd kill request occurs before the pending hook is released;
3. a later `DevRegistry.dispose()` rejection confirms the runtime had already been terminated.

The legacy fourth test covering initialization-error preservation belongs to a separate error-aggregation unit and is deliberately excluded.

## Why the packet is held

- The clean branch currently points to the exact base without the candidate commit.
- Owned-fork carrier run `30674559186`, job `91299001548`, remains queued.
- The target-native Miniflare controls have therefore not run on the current base or candidate.
- Ordinary Miniflare type, format, lint, and package-test gates have not run for the candidate.
- The Workers SDK contribution guide requests prior issue/discussion engagement for a non-trivial change; public upstream contact is unauthorized.

## Clearing conditions

1. Materialize one source-only commit on `upstream/miniflare-runtime-first-disposal` over exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.
2. Verify the diff contains exactly the three files listed above.
3. Run the three focused controls on baseline and candidate, retaining both receipts.
4. Run the applicable Miniflare checks and retain exact run/job links.
5. Re-review error precedence and browser-cleanup ordering.
6. Keep the public issue and PR as drafts until upstream contact is explicitly authorized.

## Packet map

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — source trace, mechanism, evidence limits, compatibility concerns.
- [`APPROACHES.md`](./APPROACHES.md) — selected approach and rejected alternatives.
- [`TESTS.md`](./TESTS.md) — executed evidence, prepared controls, and remaining gates.
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — public issue draft only.
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — public PR draft only.
- [`REVIEW.md`](./REVIEW.md) — bounded self-review and continuation checklist.
