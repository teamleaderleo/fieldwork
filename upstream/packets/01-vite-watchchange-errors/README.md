# Unit 01 — Vite `watchChange` error isolation

## In simple words

A Vite plugin can reject its `watchChange` hook after the dev server observes a real filesystem event. The rejection is logged, but the current inner event transaction exits before Vite performs its own cache invalidation and HMR work. A virtual module can therefore keep serving old content after its backing file changed.

The selected repair collects every environment-level `watchChange` outcome, logs each rejection, and then continues Vite's existing change, add, or unlink path. The clean owned source is based on the inspected public Vite main head and has target-native controls for all three event kinds.

## Current disposition

`ACCEPT`

The exact source candidate is suitable for independent final review. Complete-diff self-review found no blocking product defect. Current-head workflow security, lint/build/type/format/docs checks, Linux Node 20/22/24/26 Build&Test, macOS Node 24 Build&Test, and the Windows unit/focused regression paths passed. Two Windows attempts failed only in the pre-existing HMR/SSR integration playground after the Unit 01 regression passed; those failures are classified as unrelated Windows integration flakiness.

This disposition does not authorize merge or public upstream submission. The author is not the sole eligible final accepter.

## Assignment

- Unit: `01`
- Backlog: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Target: [`vitejs/vite`](https://github.com/vitejs/vite)
- Proposed destination: pull request to Vite `main`
- Proposed title: `fix(dev): continue invalidation after watchChange errors`
- Upstream contact authorized: `no`
- Public upstream interaction during this unit: `none`

## Exact source

- Exact inspected public base: [`e6b6b167afa0a80548829d1f24a0712f9194389a`](https://github.com/vitejs/vite/commit/e6b6b167afa0a80548829d1f24a0712f9194389a)
- Owned base mirror: [`upstream/unit-01-vite-main-e6b6b167`](https://github.com/teamleaderleo/vite/tree/upstream/unit-01-vite-main-e6b6b167)
- Canonical owned branch: [`fix/fieldwork-25-watchchange-error-isolation`](https://github.com/teamleaderleo/vite/tree/fix/fieldwork-25-watchchange-error-isolation)
- Exact canonical head: [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224)
- Canonical internal draft PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)
- Current relation: two commits ahead, zero behind the exact base; exactly two changed files

### Changed files

1. [`packages/vite/src/node/server/index.ts`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/server/index.ts)
2. [`packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`](https://github.com/teamleaderleo/vite/blob/a2ab7ca6183ad74d64066d6706e57a546e355224/packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js)

No temporary workflow, publisher, research fixture, lockfile, dependency, generated output, or Fieldwork vocabulary is present in the canonical source diff.

## Contribution synopsis

The current watcher handlers await `Promise.all(...)` over environment `watchChange` hooks. Any rejection reaches the outer listener catch and logger, but skips later Vite-owned work.

The candidate introduces one server-local `notifyWatchChange` helper that:

1. invokes each environment's plugin container;
2. awaits all outcomes with `Promise.allSettled`;
3. logs every rejected outcome;
4. returns normally so the existing invalidation, public-file bookkeeping, deletion handling, and HMR path continues.

The helper is shared by change, add, and unlink. Generic plugin-hook scheduling, hook order, and successful-hook semantics remain unchanged.

## Durable evidence and history

- Original scout and handoff: [`teamleaderleo/fieldwork#25`](https://github.com/teamleaderleo/fieldwork/issues/25)
- Research and runtime reproduction: [`teamleaderleo/vite#1`](https://github.com/teamleaderleo/vite/pull/1), exact head [`882e62169e2cc4a8ac91d63aca2337fda4f69e1e`](https://github.com/teamleaderleo/vite/commit/882e62169e2cc4a8ac91d63aca2337fda4f69e1e)
- Reviewed predecessor source: [`8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78`](https://github.com/teamleaderleo/vite/commit/8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78)
- Predecessor exact-head review: [`teamleaderleo/vite#4` review `4822979298`](https://github.com/teamleaderleo/vite/pull/4#pullrequestreview-4822979298)
- Current-base replay carrier: [`teamleaderleo/vite#15`](https://github.com/teamleaderleo/vite/pull/15), squash commit [`5f513983f155a1bb59671b5eb9bc78b76f4ad889`](https://github.com/teamleaderleo/vite/commit/5f513983f155a1bb59671b5eb9bc78b76f4ad889)
- Add/unlink controls: [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224)
- Current exact-head self-review: [`teamleaderleo/vite#4` comment `5148481573`](https://github.com/teamleaderleo/vite/pull/4#issuecomment-5148481573)
- Current receipt: [`receipts/current-head-2026-08-01.md`](./receipts/current-head-2026-08-01.md)

## Duplicate and prior-art result

The merged upstream repair [`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188) added listener-level catches and tests requiring `watchChange` errors to be logged for add, change, and unlink. It leaves the inner file-event transaction fail-fast: rejection still prevents later invalidation and HMR.

Searches of current Vite issues and pull requests for `watchChange`, invalidation, HMR, and error combinations found no separate current proposal that continues Vite-owned work after the hook failure. Unit 01 is a follow-up to #22188, not a duplicate of its error-reporting repair. Repeat the search immediately before any authorized public submission.

## Tests and gates

See [`TESTS.md`](./TESTS.md) for exact commands, revisions, jobs, classifications, and limits.

Current-head workflow summary:

- CI: [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447)
  - lint/build/type/format/docs/workflow checks: success
  - Linux Node 20/22/24/26 Build&Test: success
  - macOS Node 24 Build&Test: success
  - Windows build/unit/focused Unit 01 test: success
  - Windows ordinary serve: success on rerun
  - two failures confined to the existing Windows `playground/hmr-ssr` integration family; classified unrelated to Unit 01
  - a further Windows full-job rerun was requested as supplementary evidence
- Zizmor: [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445) — success
- Preview release: [`30674314449`](https://github.com/teamleaderleo/vite/actions/runs/30674314449) — skipped as expected for this internal source PR

The CI pull-request checkout used a synthetic merge containing source head `a2ab7ca6` on the owned repository's current default branch. The canonical review fence remains the explicit public-base comparison `e6b6b167...a2ab7ca6`; the merge ref is compatibility evidence, not the source revision.

## Compatibility and evidence limits

- The repair changes failure handling only after a plugin `watchChange` rejection.
- All environments are allowed to settle, so multiple rejections can be logged instead of only the first one.
- Vite-owned invalidation and HMR continue even when plugin notification failed; this is the intended invariant and main behavior change.
- A plugin that relied on throwing to suppress Vite's later cache/HMR work would observe different behavior. No inspected supported contract grants that veto authority.
- The change-path test proves refreshed virtual-module content. Add/unlink tests prove error visibility and continuation into event-typed `hotUpdate`; they do not claim every public-file or module-deletion side effect across every platform.
- Windows HMR/SSR integration timing remains noisy outside the changed files. Unit 01's focused regression remained green in those jobs.

## Packet navigation

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — current behavior, ownership, failure model, and selected design
- [`APPROACHES.md`](./APPROACHES.md) — selected, losing, rejected, and deferred options
- [`TESTS.md`](./TESTS.md) — exact execution record and limits
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — issue-first disposition and optional issue text
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — polished upstream pull-request draft
- [`REVIEW.md`](./REVIEW.md) — exact-head self-review and human inspection guide
- [`receipts/current-head-2026-08-01.md`](./receipts/current-head-2026-08-01.md) — compact current-head receipt

## Next transition

1. Obtain independent complete-diff review at the unchanged source head.
2. Re-read live checks and repeat duplicate/current-main/contribution-policy checks immediately before any public submission.
3. Rebase and rerun only if current Vite `main` or the source head changes materially.
4. Await explicit authority for the exact public upstream interaction.

## Continuation-ready handoff

Treat `a2ab7ca6183ad74d64066d6706e57a546e355224` as the source fence until the branch moves. Start with this file, then read the linked packet files, `teamleaderleo/vite#4`, `teamleaderleo/vite#1`, Fieldwork #25, upstream Vite #22188, and workflow run `30674314447`. The source is accepted for independent review; ordinary Windows HMR/SSR flake data is classified and must not trigger unrelated source churn. Any source-head movement expires this disposition and requires test, diff, draft, and review reconciliation.