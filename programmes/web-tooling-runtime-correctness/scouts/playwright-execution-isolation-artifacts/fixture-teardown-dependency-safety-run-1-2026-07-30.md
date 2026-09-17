# Playwright deferred dependency safety run 1 — 2026-07-30

## Result

The equal per-fixture budget prototype failed the dependency cleanup safety invariant.

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Safety probe | PR `#8` |
| Execution PR | `#9` |
| Workflow run | `30477923500` |
| Job | `90664199744` |
| Merge ref | `5ce0aab5b703384a0216a32f6ada12ccf29eb4b1` |
| Prototype | equal per-fixture budget PR `#4` |
| Runner | Ubuntu 24.04.4, Node 22, one worker |
| Outcome | expected safety failure |

No upstream contact occurred.

## Scenario

- a deferred child fixture depends on a resource-owning root fixture;
- the child finalizer requires 80ms;
- total worker-cleanup recovery budget is 120ms;
- equal per-fixture allocation gives child and root roughly 60ms each;
- the safety requirement is child completion while root is open, followed by root close.

Expected output order:

```text
child-saw-root-open
root-closed
```

Observed filtered output:

```text
root-closed
```

The child completion marker never appeared.

## What run 1 establishes

- the root dependency teardown callback ran;
- the child finalizer did not reach completion before worker shutdown;
- equal per-fixture allocation can allow a dependency to finalize while its child cleanup remains incomplete;
- independent fairness alone is not a safe scheduling policy for dependency chains.

Run 1 did not include a marker before the child delay, so it does not independently prove whether the child finalizer started before it was abandoned. Source control flow predicts that it started and timed out at its scheduler allocation, but that point requires the strengthened exact rerun.

## Strengthened probe

The test now emits:

```text
child-finalizer-started
child-finished-root-open
root-closed
```

The equal-share control is expected to produce:

```text
child-finalizer-started
root-closed
```

The dependency-group intervention is expected to produce all three lines in the required order.

Updated heads:

| Layer | Head |
|---|---|
| Strengthened safety probe | `c6e2c58935f4e5d7c22c4e277ad8e49000393145` |
| Equal-share safety CI | `744fb5054852bad70fcd795e8e4301894152b4a4` |
| Dependency-group intervention | `47c3cd328728b292fd630af0688b3e1826460479` |
| Dependency-group CI | `39ad6a2d9f215a5ef2b8826d827bfd887b624a47` |

## Policy consequence

Recovery fairness should be allocated across independent fixture dependency groups, not blindly across individual fixtures.

A group must share one slot so that:

- a child that completes leaves remaining group time for its root;
- a child that exhausts the group allowance prevents the root callback from starting concurrently;
- independent groups still receive separate bounded opportunities.

An exhausted group still needs an explicit incomplete-cleanup receipt because preserving ordering can mean leaving the root finalizer unstarted.
