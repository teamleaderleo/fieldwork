# Approaches — Vite `watchChange` error isolation

## In simple words

The retained repair changes only the server's environment fanout: collect every `watchChange` outcome, log failures, then continue existing Vite work. Broader hook-runner changes and listener-only catches either alter too much or leave the stale-cache failure intact.

## Selected approach

### Server-local settle-and-log helper

Current source: [`a2ab7ca6183ad74d64066d6706e57a546e355224`](https://github.com/teamleaderleo/vite/commit/a2ab7ca6183ad74d64066d6706e57a546e355224)

Implementation:

- add `notifyWatchChange(file, event)` inside server creation;
- invoke each current environment plugin container in parallel;
- await `Promise.allSettled`;
- log every rejection through the configured server logger;
- return to the existing change/add/unlink worker;
- retain later graph, public-file, deletion, and HMR logic unchanged.

Why it wins:

- it sits at the boundary that owns cross-environment fanout and later Vite work;
- it preserves current successful ordering;
- it avoids changing generic Rollup/Vite hook semantics;
- it gives complete environment-level error visibility;
- it keeps the source diff to one implementation file and one target-native test file;
- it serves all three watcher event kinds through one policy.

Reopening trigger:

- evidence that server environment snapshots can change during `watchChange` and require an explicit stale-transaction guard at this earlier boundary;
- a documented plugin contract granting a rejecting hook veto authority over Vite-owned invalidation/HMR;
- a target-native failure showing that settle-all creates an unsupported lifecycle interaction.

## Retained viable alternative

### Per-environment catch inside the mapped promise

Example direction:

```ts
await Promise.all(
  environments.map(async (environment) => {
    try {
      await environment.pluginContainer.watchChange(file, { event })
    } catch (error) {
      logger.error(error)
    }
  }),
)
```

This can deliver the same observable policy. The selected `Promise.allSettled` form separates hook execution from result reporting and makes the complete result set explicit.

Reopening trigger:

- project style strongly prefers local `try/catch` over inspecting settled results;
- typing or lint rules make the selected result handling awkward;
- maintainers want environment identity included in each log and a mapped wrapper provides that context more cleanly.

## Executed losing approach

### Listener-level `.catch()` only

Prior art: [`vitejs/vite#22188`](https://github.com/vitejs/vite/pull/22188)

Result:

- prevents dropped or unhandled watcher rejections;
- reports `watchChange` failures for add, change, and unlink;
- leaves the inner handler fail-fast;
- logs only after invalidation/HMR has already been skipped.

Why it loses for unit 01:

The retained runtime reproduction shows stale transformed content even though the exact error reaches the logger. Error visibility alone cannot restore the aborted server work.

Reopening trigger:

None for this unit. Listener catches remain useful and should stay; they solve a different failure boundary.

## Rejected easy answer

### Wrap each whole event worker in `try/finally`

A `finally` block could force selected later work after an error, but the event workers contain several distinct stages and potential failures beyond `watchChange`.

Why rejected:

- it risks continuing after failures in public-file lookup, deletion handling, or HMR itself;
- it blurs which failure is intentionally isolated;
- it can duplicate or reorder existing logic;
- unit 01 concerns one known plugin-notification boundary.

Reopening trigger:

A wider audited transaction design that classifies every stage and states which failures permit continuation. That is outside this unit.

## Rejected broad answer

### Change generic plugin hook scheduling or `hookParallel`

Why rejected:

- generic hook execution is shared by unrelated plugin APIs;
- changing it can alter hook ordering, rejection semantics, and callers outside dev-server file events;
- the defect exists in server orchestration after environment notifications;
- current source needs no generic abstraction change.

Reopening trigger:

Independent evidence of the same required settle-and-continue contract across several generic hook callers, with a reviewed compatibility plan. That would be a separate contribution.

## Rejected narrow answer

### Catch only the first rejected environment notification

Possible forms include one outer `try/catch` around `Promise.all` or attaching one catch to the aggregate promise.

Why rejected:

- the first rejection ends aggregate waiting;
- later environment outcomes are unavailable to the server;
- only one rejection is reported;
- the helper needs a complete settlement boundary before later Vite work.

Reopening trigger:

A Vite policy that intentionally reports only one plugin failure and permits proceeding before other environment hooks settle. No such policy was found.

## Test approaches

### Selected change control

A virtual module reads a watched text file. The test proves:

- initial transform contains `alpha`;
- rejecting `watchChange` error is logged;
- `hotUpdate` runs;
- transform cache becomes invalid;
- next transform contains `beta`.

This directly distinguishes stale-cache behavior from successful continuation.

### Selected add/unlink controls

Parameterized watcher events prove:

- `add` maps to `create` for both hooks;
- `unlink` maps to `delete` for both hooks;
- the rejecting hook error remains visible;
- event-typed HMR still runs.

Why selected:

They close the explicit packet gap without inventing filesystem fixtures whose platform timing could obscure the orchestration property.

### Deferred stronger add/unlink controls

Potential additions:

- add a newly resolvable module and prove failed-resolution recovery still occurs;
- unlink a real imported module and prove graph relations are removed;
- exercise public-directory add and verify same-path transform etag removal;
- assert emitted HMR payloads rather than hook reachability.

Why deferred:

The current controls discriminate continuation at the exact shared helper boundary. Stronger state assertions may be requested after current-head execution or review, and should stay bounded to a concrete acceptance concern.

## Packaging approaches

### Selected

- packet branch: `p0/435-unit-01-vite-watchchange-errors`
- clean target branch: `fix/fieldwork-25-watchchange-error-isolation`
- exact public-base mirror: `upstream/unit-01-vite-main-e6b6b167`
- canonical target PR: `teamleaderleo/vite#4`

### Executed carrier

`teamleaderleo/vite#15` replayed the reviewed two-file candidate onto current public main and was squash-merged into a temporary work branch. The canonical branch was then moved to the current-base result and received the add/unlink test commit.

The carrier is retained as rebase history, not proposed upstream source.

## Adjacent questions intentionally excluded

- late post-transform import graph reconciliation;
- experimental bundled-development `hotUpdate` support;
- CSS graph publication after post transforms;
- watcher event serialization across concurrent files;
- generic plugin error policy;
- HMR error payload handling inside `handleHMRUpdate`;
- server restart transactions triggered by config or environment files.

These lanes have separate records under Fieldwork #25 or the #435 parking lot. They do not alter unit 01's source or disposition.
