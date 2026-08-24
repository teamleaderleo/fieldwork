# Review — Vite `watchChange` error isolation

## Review fence

- Work class: owned-fork source candidate
- Public base and current public main: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical source head: `ba8ac979ee91c77fdd91304ccde38942e9752133`
- Canonical branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source PR: `teamleaderleo/vite#4`
- Expected changed files: exactly three
- Public upstream contact authorized: `no`

Any source or material base movement expires this review fence.

## Decision under review

Should watcher-driven plugin notification failures be reported without allowing one plugin to veto sibling notifications or Vite-owned invalidation and HMR?

Selected contract:

- every applicable hook that belonged to the event is invoked;
- synchronous throws and asynchronous rejections are reported per plugin;
- parallel groups and sequential barriers retain their existing ordering;
- Vite waits for all notifications before later watcher work;
- the direct public plugin-container method remains fail-fast;
- infrastructure failures remain observable through environment-level settle-all.

## Exact diff inventory

### `packages/vite/src/node/server/pluginContainer.ts`

- adds a watcher-specific parallel runner with per-plugin error handling;
- tracks asynchronous hook promises through the existing close-time set;
- preserves `sequential: true` barriers;
- factors the existing per-environment watch condition into a strictly boolean helper;
- adds internal `watchChangeWithErrorHandler()`;
- leaves direct `watchChange()` on generic fail-fast `hookParallel()`.

### `packages/vite/src/node/server/index.ts`

- adds one server-local `notifyWatchChange()` helper;
- settles every environment;
- reports environment-level infrastructure rejection;
- routes change/add/unlink notification through the helper;
- leaves later invalidation, public-file/deletion, restart, and HMR ordering in place.

### `packages/vite/src/node/__tests__/server/watchChange-error-isolation.spec.js`

- proves refreshed content after a change rejection;
- proves create/delete event mapping after add/unlink rejection;
- proves two sibling failures both settle and are both reported;
- proves HMR cannot overtake a blocked sibling;
- proves a sequential barrier and later hook retain order;
- proves a synchronous throw does not skip later hooks or HMR;
- uses bounded waits and registered cleanup.

## Complete-diff pre-review result

`ACCEPT`

No blocking source defect was found.

### Ownership and lifecycle

- [x] Watcher/server orchestration owns continuation into invalidation and HMR.
- [x] Per-plugin handling prevents one plugin from ending the current notification set.
- [x] Environment-level settle-all prevents one environment from ending server fanout.
- [x] Sequential barriers wait for all earlier parallel hooks.
- [x] Later Vite-owned work begins only after all applicable hooks settle.
- [x] Close-time hook tracking includes watcher-specific async hooks.

### Compatibility

- [x] Hook arguments and successful-path order are unchanged.
- [x] Direct `pluginContainer.watchChange()` remains fail-fast.
- [x] The specialized method is internal and absent from generated declarations.
- [x] Plugin failures remain visible.
- [x] No documented plugin contract grants a rejecting hook veto authority over Vite-owned cache/HMR work.
- [x] A throwing custom logger remains an explicit separate limit.

### Error handling

- [x] Sync throws are caught inside hook invocation.
- [x] Async rejections are caught after close-time tracking is installed.
- [x] Each plugin failure is passed to the configured logger.
- [x] Unexpected environment rejection is still logged by the outer layer.
- [x] Later invalidation or HMR errors are not swallowed by this helper.

### Tests

- [x] Change proves cache invalidation and refreshed output, not only hook reachability.
- [x] Add and unlink assert both Rollup event and HMR type.
- [x] Dual rejection proves every failure is reported.
- [x] Blocking control proves HMR waits.
- [x] Barrier control proves ordering.
- [x] Sync-throw control proves later invocation.
- [x] Temporary projects and servers are cleaned up.

## Exact execution

- [x] Zizmor `30753769710`: success.
- [x] CI `30753769684`: success.
- [x] Lint, formatting, typecheck, docs, and workflow checks: success.
- [x] Ubuntu Node 20 Build&Test: success.
- [x] Ubuntu Node 22 Build&Test: success.
- [x] Ubuntu Node 24 Build&Test: success.
- [x] Ubuntu Node 26 Build&Test: success.
- [x] macOS Node 24 Build&Test: success.
- [x] Windows Node 24.15.0 Build&Test: success.
- [x] Final success aggregate: success.
- [x] Failure aggregate: skipped.

Every Build&Test job completed build, unit, ordinary serve, bundled-development serve, and build tests.

## Source hygiene

- [x] Exactly three changed files.
- [x] No workflow or restart trigger.
- [x] No dependency or lockfile change.
- [x] No generated output.
- [x] No Fieldwork file in the target source.
- [x] Current public main remains the exact tested base.
- [x] Fresh overlap search found no open matching repair.

## Known limits

- Error ordering between simultaneous failures is not promised.
- Logger failure can interrupt reporting and remains separate.
- Filesystem events are not serialized or coalesced by this change.
- Plugin-owned partial state is not rolled back.
- Add/unlink tests do not enumerate every downstream platform-specific state transition.

## Human inspection path

1. Review the three-file comparison `e6b6b167...ba8ac979`.
2. Confirm the public-base abort point in watcher handlers.
3. Trace one failing hook through the specialized runner.
4. Trace parallel-group settlement and a sequential barrier.
5. Confirm the direct public `watchChange()` path is unchanged.
6. Read the stale-cache, add/unlink, dual-rejection, barrier, and sync-throw controls.
7. Confirm CI `30753769684` and Zizmor `30753769710` are terminal success.
8. Check public wording and contribution policy again before any authorized filing.

## Recommended disposition

`ACCEPT`

The source is technically ready for human review. Acceptance here does not authorize merge or public submission.
