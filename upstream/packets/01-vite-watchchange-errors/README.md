# Unit 01 — Vite `watchChange` error isolation

## Current disposition

`REPAIR`

A second adversarial review invalidated the earlier environment-only `ACCEPT` fence. The old repair waited every environment, but each environment could still reject on the first plugin failure while slower sibling hooks remained live.

The canonical three-file source head is now `79fa097750158790ec9bf03d74e6f83d702dd4c2`. It settles sibling plugin hooks, preserves sequential barriers, keeps the specialized path out of generated declarations, and has passed the expanded focused suite and source gates. Exact-head ordinary CI and Zizmor are running.

Both canonical PRs remain draft. No merge or public upstream interaction is authorized.

## Assignment

- Unit: `01`
- Routing board: `teamleaderleo/fieldwork#435`
- Target: `vitejs/vite`
- Proposed title: `fix(dev): continue invalidation after watchChange errors`
- Source PR: `teamleaderleo/vite#4`
- Packet PR: `teamleaderleo/fieldwork#438`
- Public upstream contact authorized: `no`
- Public upstream interactions: `zero`

## Exact revisions

- Inspected public Vite base and current public main: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Last clean environment-only head: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Canonical plugin-settlement head: `79fa097750158790ec9bf03d74e6f83d702dd4c2`
- Canonical source branch: `fix/fieldwork-25-watchchange-error-isolation`
- Packet branch: `p0/435-unit-01-vite-watchchange-errors`

Any source movement expires this fence and requires exact-head reconciliation.

## Failure model

### Public-base layer

A rejecting `watchChange` hook escapes the event worker before module invalidation, public-file/delete work, and HMR. The listener catches and logs the error only after the worker has aborted.

### First repair layer

Server-level `Promise.allSettled` across environments allows Vite-owned work to continue after an environment rejection.

### Deeper plugin layer

Inside each environment, generic `hookParallel()` still uses fail-fast `Promise.all` for ordinary parallel hook groups.

With fast and slow sibling failures:

```text
fast:start
slow:start
fast:reject
logged:fast
vite:continues
slow:reject
```

That permits HMR to overtake a pending hook, hides later failures, and can skip later hooks or `sequential: true` barriers.

## Selected repair

For watcher-driven server events only:

- run every applicable plugin notification;
- catch synchronous throws and asynchronous rejections per plugin;
- report each failure individually;
- preserve ordinary parallel groups and `sequential: true` barriers;
- wait all applicable hooks before invalidation/HMR;
- track asynchronous hook promises so environment close waits them;
- retain the generic fail-fast path for direct compatibility calls;
- retain environment-level `Promise.allSettled` as the outer infrastructure guard.

The specialized path is `watchChangeWithErrorHandler()` marked `/** @internal */`. Vite's node tsconfig uses `stripInternal: true`, and the repair carrier verified that the name is absent from generated declarations. The documented `environment.pluginContainer.watchChange(id, change)` method retains its original public signature and fail-fast path.

## Source scope

The canonical source diff contains exactly three files:

1. `packages/vite/src/node/server/index.ts`
2. `packages/vite/src/node/server/pluginContainer.ts`
3. `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`

It contains no workflow, dependency, lockfile, generated output, research fixture, trigger marker, or Fieldwork-only source file.

## Target-native tests

The focused suite covers five cases:

1. change rejection logs, invalidates the virtual-module cache, reaches HMR, and refreshes `alpha` to `beta`;
2. add rejection reaches create-typed HMR;
3. unlink rejection reaches delete-typed HMR;
4. two failing sibling hooks both settle and both errors are reported; HMR cannot overtake a blocked sibling; a sequential barrier and later hook retain their order;
5. a synchronous throw does not skip a later hook or HMR.

Exact product-content carrier execution passed:

- dependency installation;
- formatting;
- full Vite build and type generation;
- generated-declaration leak check;
- focused suite, 5/5;
- ESLint on all three changed files;
- clean three-file packaging.

Current exact-head ordinary runs:

- CI `30694603635`: in progress;
- Zizmor `30694603632`: queued;
- Preview `30694603631`: skipped as expected.

At the latest snapshot, macOS Node 24 is fully green. Windows Node 24.15 has passed build, unit, ordinary serve, and bundled development and is finishing build tests. Linux jobs and lint remain queued.

The earlier environment-only head eventually passed the complete ordinary matrix, including a third Windows rerun. Those receipts remain historical and do not replace current exact-head validation.

## Prior art and duplicate result

Merged Vite PR `#22188` added listener-level catches and logging tests for add/change/unlink. It does not continue the inner event transaction after hook failure and does not settle sibling plugin hooks.

Fresh issue and pull-request searches for `watchChange`, sibling rejection, sequential barriers, invalidation, and HMR found no overlapping current repair. Repeat duplicate and current-main checks immediately before any authorized public submission.

## Compatibility limits

- Plugin failures remain visible but no longer veto sibling notifications or Vite-owned invalidation/HMR.
- Successful hooks retain parallel execution and sequential barriers.
- Simultaneous error ordering is not promised.
- A custom logger that throws can interrupt reporting, matching existing Vite watcher-listener assumptions; logger-failure policy is separate.
- Separate filesystem events remain independently concurrent; Unit 01 does not serialize or coalesce them.
- The repair does not recover arbitrary partial state inside a failing plugin.
- Add/unlink controls prove event mapping and continuation, not every platform-specific graph or public-file side effect.

The explored settle-before-log variant was rejected as unnecessary scope expansion for a throwing custom logger. Source decision record: `teamleaderleo/vite#4` comment `5150908165`.

## Packet navigation

- [`ADVERSARIAL_AUDIT.md`](./ADVERSARIAL_AUDIT.md) — sibling-plugin race and repair contract
- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — ownership, lifecycle, compatibility, and evidence model
- [`APPROACHES.md`](./APPROACHES.md) — selected, losing, rejected, and deferred approaches
- [`TESTS.md`](./TESTS.md) — exact execution ledger and classifications
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — optional issue route
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — public-facing draft
- [`REVIEW.md`](./REVIEW.md) — exact-head inspection guide
- [`receipts/current-head-2026-08-01.md`](./receipts/current-head-2026-08-01.md) — compact receipt, pending final ordinary reconciliation

## Next transition

1. Complete and classify exact-head CI and Zizmor.
2. Decide whether multi-environment and close-while-blocked controls add material confidence without widening the patch.
3. Rewrite `TESTS.md`, `REVIEW.md`, the receipt, and public drafts to the final exact source head.
4. Close temporary execution PR/branches.
5. Advance only after independent complete-diff review.
6. Await explicit authorization before any public upstream interaction.

## Continuation-ready handoff

Start with this file, then read `ADVERSARIAL_AUDIT.md`, `DEEP_DIVE.md`, `APPROACHES.md`, source PR `teamleaderleo/vite#4`, packet PR `teamleaderleo/fieldwork#438`, and the routing updates on `teamleaderleo/fieldwork#435`.

Do not treat queued runners, unrelated integration flakes, or temporary packaging commits as product blockers. Do treat source-head movement, public API leakage, failing target-native controls, or a real compatibility contradiction as evidence requiring repair and exact-head reconciliation.
