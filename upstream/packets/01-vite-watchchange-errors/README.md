# Unit 01 — Vite `watchChange` error isolation

## In simple words

A Vite plugin can reject its `watchChange` hook after the dev server observes a real filesystem event. Vite logs that error, then exits the event transaction before its own cache invalidation and HMR work. A virtual module can therefore keep serving old content after its backing file changed.

The selected repair collects every environment-level `watchChange` outcome, logs each rejection, and then continues Vite's existing change, add, or unlink path. The clean owned source is rebased onto current public Vite main and has target-native controls for all three event kinds.

## Current disposition

`REPAIR`

The source is current and bounded. Current-head Zizmor and the CI lint job passed. Promotion requires the remaining cross-platform Build&Test matrix, final receipt reconciliation, and independent exact-head review.

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
- Canonical draft PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)
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

The helper is shared by change, add, and unlink. Generic plugin hook scheduling, hook order, and the semantics of successful hooks remain unchanged.

## Durable evidence and history

- Original scout and handoff: [`teamleaderleo/fieldwork#25`](https://github.com/teamleaderleo/fieldwork/issues/25)
- Research and runtime reproduction: [`teamleaderleo/vite#1`](https://github.com/teamleaderleo/vite/pull/1), exact head [`882e62169e2cc4a8ac91d63aca2337fda4f69e1e`](https://github.com/teamleaderleo/vite/commit/882e62169e2cc4a8ac91d63aca2337fda4f69e1e)
- Reviewed predecessor source: [`8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78`](https://github.com/teamleaderleo/vite/commit/8b5d1ae237bf61031a7436ed8fb0fc1e436b6d78)
- Predecessor exact-head review: [`teamleaderleo/vite#4` review `4822979298`](https://github.com/teamleaderleo/vite/pull/4#pullrequestreview-4822979298)
- Current-base replay carrier: [`teamleaderleo/vite#15`](https://github.com/teamleaderleo/vite/pull/15), squash commit [`5f513983f155a1bb59671b5eb9bc78b76f4ad889`](https://github.com/teamleaderleo/vite/commit/5f513983f155a1bb59671b5eb9bc78b76f4ad889)
- Add/unlink controls: [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224)
- Current exact-head self-review: [`teamleaderleo/vite#4` comment `5148481573`](https://github.com/teamleaderleo/vite/pull/4#issuecomment-5148481573)

## Duplicate and prior-art result

The merged upstream repair [`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188) added listener-level catches and tests requiring `watchChange` errors to be logged for add, change, and unlink. It leaves the inner file-event transaction fail-fast: rejection still prevents later invalidation and HMR.

Searches of current Vite issues and pull requests for `watchChange`, invalidation, HMR, and error combinations found no separate current proposal that continues Vite-owned work after the hook failure. Unit 01 is a follow-up to #22188, not a duplicate of its error-reporting repair.

## Tests and gates

See [`TESTS.md`](./TESTS.md) for exact commands, revisions, environments, workflow runs, classifications, and gaps.

Current-head workflow runs:

- CI: [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447) — lint job [`91298285154`](https://github.com/teamleaderleo/vite/actions/runs/30674314447/job/91298285154) passed; six Build&Test jobs remain queued
- Zizmor: [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445) — success
- Preview release: [`30674314449`](https://github.com/teamleaderleo/vite/actions/runs/30674314449) — skipped as expected for this internal source PR

## Compatibility and evidence limits

- The repair changes failure handling only after a plugin `watchChange` rejection.
- All environments are allowed to settle, so multiple rejections can be logged instead of only the first one.
- Vite-owned invalidation and HMR continue even when plugin notification failed; this is the intended invariant and the main behavior change.
- A plugin that relied on throwing to suppress Vite's later cache/HMR work would observe different behavior. That reliance conflicts with the server's ownership of cache coherence, but it remains the principal compatibility risk.
- The change-path test proves refreshed virtual-module content. Add/unlink tests prove error visibility and continuation into event-typed `hotUpdate`; they do not claim every public-file or module-deletion side effect across every platform.
- Current-head cross-platform Build&Test execution and independent exact-head acceptance remain pending.

## Packet navigation

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — current behavior, ownership, failure model, and selected design
- [`APPROACHES.md`](./APPROACHES.md) — selected, losing, rejected, and excluded approaches
- [`TESTS.md`](./TESTS.md) — exact execution record and gaps
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — issue-first disposition and optional issue text
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — polished upstream pull-request draft
- [`REVIEW.md`](./REVIEW.md) — exact-head review and human inspection guide

## Remaining work in strict order

1. Inspect the six queued Build&Test jobs in CI run `30674314447`.
2. Classify any failure before changing unit 01 source or tests.
3. Run the focused test directly at the final head if the ordinary jobs do not expose an unambiguous focused receipt.
4. Reconcile `TESTS.md`, `REVIEW.md`, the source PR, and this README with final job conclusions.
5. Obtain independent complete-diff review at the unchanged source head.
6. Change disposition to `READY` only when the acceptance criteria are met.
7. Await explicit authority for the exact public upstream action.

## Continuation-ready handoff

Start from this file, then read the linked packet files, `teamleaderleo/vite#4`, `teamleaderleo/vite#1`, Fieldwork #25, upstream Vite #22188, and current-head CI/Zizmor runs. Treat `a2ab7ca6183ad74d64066d6706e57a546e355224` as the source fence until the branch moves. The immediate action is to inspect CI run `30674314447`; any source-head movement expires the current disposition and requires test, diff, draft, and review reconciliation.
