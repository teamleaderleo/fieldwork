# Playwright deferred dependency safety run 2 — 2026-07-30

## Result

The strengthened exact control confirmed that equal per-fixture recovery allocation starts a child finalizer, closes its root dependency, and exits without the child completing.

| Field | Value |
|---|---|
| Repository | `teamleaderleo/playwright` |
| Safety probe | PR `#8` |
| Execution PR | `#9` |
| Workflow run | `30478752594` |
| Job | `90666996997` |
| Equal-share safety CI head | `744fb5054852bad70fcd795e8e4301894152b4a4` |
| Safety probe head | `c6e2c58935f4e5d7c22c4e277ad8e49000393145` |
| Runner | Ubuntu 24.04.4, Node 22, one worker |
| Outcome | expected failure |

No upstream contact occurred.

## Required order

```text
child-finalizer-started
child-finished-root-open
root-closed
```

## Observed order

```text
child-finalizer-started
root-closed
```

The child completion marker was absent.

## Exact conclusion

Equal per-fixture allocation is unsafe for connected fixture dependency chains in the tested case:

1. the child teardown callback starts;
2. its temporary allocation expires;
3. `_runWithTimeout` rejects, but the child callback itself is not cancelled;
4. fixture usage tracking is force-cleared;
5. the root dependency teardown callback runs and closes the resource;
6. the worker exits before the child callback reaches completion.

This is stronger than ordinary starvation. The scheduler can violate the semantic teardown guarantee that dependents finish before dependencies are released.

## Candidate status

| Candidate | Status |
|---|---|
| One shared fallback slot | rejected: starves independent finalizers before `testEnd` |
| Equal per-fixture shares | rejected as production policy: unsafe for dependency chains |
| Dependency-group shares | lead intervention pending exact run |

The equal-share branch remains valuable as a cross-platform positive control for independent fixture fairness. It passed seven tests on Ubuntu, macOS, and Windows, proving the mechanism works where fixtures are independent. It should not be promoted as a general scheduler.

## Required scheduler property

Connected deferred fixtures must share one recovery allowance. If a child exhausts that allowance, its dependency callback must not begin concurrently. Independent connected components can receive separate bounded opportunities.

An exhausted group also needs explicit completion accounting because preserving dependency safety may leave a root callback unstarted.
