# Unit 01 — Vite `watchChange` error isolation

## Current disposition

`REPAIR`

A second adversarial review invalidated the earlier environment-only `ACCEPT` fence. The old repair waited every environment, but each environment could still reject on the first plugin failure while slower sibling hooks remained live.

The clean three-file repair at `0cf30aa19e0ecf4053b7c6bf9be5d59e5733218b` fixes plugin-level settlement and passed formatting, full Vite build, an expanded 5/5 focused suite, and ESLint. One final source refinement is under execution: keep the watcher-only failure callback behind a stripped `@internal` method so the documented Environment API's public `watchChange(id, change)` signature remains unchanged.

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

- Inspected public Vite base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Last clean environment-only head: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Clean plugin-settlement head under API review: `0cf30aa19e0ecf4053b7c6bf9be5d59e5733218b`
- Canonical source branch: `fix/fieldwork-25-watchchange-error-isolation`
- Packet branch: `p0/435-unit-01-vite-watchchange-errors`

The source head will move once more only if the `@internal` declaration-leak control passes. Any source movement expires the current review fence and requires exact-head reconciliation.

## Failure model

### Public-base layer

A rejecting `watchChange` hook escapes the event worker before module invalidation, public-file/delete work, and HMR. The listener catches and logs the error after the worker has already aborted.

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
- retain the generic fail-fast path for direct compatibility calls.

The final refinement moves this specialized path to `watchChangeWithErrorHandler()` marked `/** @internal */`. Vite's node tsconfig uses `stripInternal: true`; execution additionally checks generated declarations and fails if the internal method leaks.

## Source scope

The clean plugin-settlement candidate contains exactly three files:

1. `packages/vite/src/node/server/index.ts`
2. `packages/vite/src/node/server/pluginContainer.ts`
3. `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`

No workflow, dependency, lockfile, generated output, research fixture, or Fieldwork-only file is allowed in the canonical source diff.

## Target-native tests

The focused suite now covers five cases:

1. change rejection still logs, invalidates the virtual-module cache, reaches HMR, and refreshes `alpha` to `beta`;
2. add rejection still reaches create-typed HMR;
3. unlink rejection still reaches delete-typed HMR;
4. two failing sibling hooks both settle and both errors are reported before a sequential barrier, later hook, and HMR;
5. a synchronous throw does not skip a later hook or HMR.

Execution on the clean plugin-settlement carrier:

- dependency install: success;
- formatting: success;
- full Vite build and type generation: success;
- focused suite: 5/5 passed;
- ESLint on implementation and tests: success;
- clean packaging: success.

The earlier source head also eventually passed the complete ordinary matrix, including the third Windows rerun. Those receipts remain valid for the original change/add/unlink behavior but do not replace exact-head ordinary validation after the API-boundary refinement.

## Prior art and duplicate result

Merged Vite PR `#22188` added listener-level catches and logging tests for add/change/unlink. It does not continue the inner event transaction after hook failure and does not settle sibling plugin hooks.

No inspected current issue or pull request provides the same plugin-level continuation repair. Repeat duplicate and current-main checks immediately before any authorized public submission.

## Compatibility limits

- Plugin failures remain visible but no longer veto sibling notifications or Vite-owned invalidation/HMR.
- Successful hooks retain parallel execution and sequential barriers.
- Simultaneous error ordering is not promised.
- A custom logger that throws can still interrupt reporting; logger-failure policy is separate.
- Separate filesystem events remain independently concurrent; Unit 01 does not serialize or coalesce them.
- The repair does not recover arbitrary partial state inside a failing plugin.
- Add/unlink controls prove event mapping and continuation, not every platform-specific graph or public-file side effect.

## Packet navigation

- [`ADVERSARIAL_AUDIT.md`](./ADVERSARIAL_AUDIT.md) — newly discovered plugin-level race and repair contract
- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — ownership, lifecycle, compatibility, and evidence model
- [`APPROACHES.md`](./APPROACHES.md) — selected, losing, rejected, and deferred approaches
- [`TESTS.md`](./TESTS.md) — exact execution ledger and classifications
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — optional issue route
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — public-facing draft
- [`REVIEW.md`](./REVIEW.md) — exact-head inspection guide
- [`receipts/current-head-2026-08-01.md`](./receipts/current-head-2026-08-01.md) — compact receipt, pending final-head rewrite

## Next transition

1. Complete the stripped-internal-method build, declaration-leak, focused, and lint run.
2. Inspect the resulting clean source diff and exact base relation.
3. Run and classify ordinary exact-head cross-platform gates.
4. Rewrite `TESTS.md`, `REVIEW.md`, the receipt, drafts, and PR bodies to one final source head.
5. Close temporary execution PR/branches.
6. Advance only after independent complete-diff review.
7. Await explicit authorization before any public upstream interaction.

## Continuation-ready handoff

Start with this file, then read `ADVERSARIAL_AUDIT.md`, `DEEP_DIVE.md`, `APPROACHES.md`, source PR `teamleaderleo/vite#4`, packet PR `teamleaderleo/fieldwork#438`, and the routing updates on `teamleaderleo/fieldwork#435`.

Do not treat queued runners, unrelated integration flakes, or temporary packaging commits as product blockers. Do treat source-head movement, public API leakage, failing target-native controls, or a real compatibility contradiction as evidence requiring repair and exact-head reconciliation.
