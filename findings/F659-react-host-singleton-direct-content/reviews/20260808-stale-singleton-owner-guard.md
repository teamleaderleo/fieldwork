# HostSingleton stale-owner containment guard

## Question

Can React prevent a previously released / hidden HostSingleton Fiber from mutating or releasing a persistent singleton after another Fiber has acquired the same DOM node, without coupling the renderer to Offscreen traversal state?

## Existing ownership signal

React DOM already stores the HostSingleton Fiber that most recently acquired or hydrated the persistent DOM node.

- `precacheFiberNode(internalInstanceHandle, instance)` installs the DOM -> Fiber association during singleton acquisition/hydration.
- `updateFiberProps(instance, props)` updates only the props association; ordinary host updates do **not** replace the DOM -> Fiber association.
- `detachDeletedInstance(instance)` removes the Fiber/props association on release.

Because Fiber alternates are reused, a healthy visible owner update can see the DOM association pointing to either the finished Fiber or `finishedWork.alternate`.

If a competing visible singleton owner acquires the same body/head/html node, acquisition calls `precacheFiberNode` with that different owner's Fiber pair.

This gives React enough information to distinguish a legitimate update/release from stale work belonging to a previously released owner **when the DOM association itself is trustworthy**.

## Implementation refinement

The generic reconciler host config already exposes `getInstanceFromNode`; no new DOM-only API and no `releaseSingletonInstance` signature expansion are required for the experiment.

The containment helper can live in `ReactFiberCommitHostEffects.js`:

```js
function isCurrentHostSingletonOwner(fiber) {
  const owner = getInstanceFromNode(fiber.stateNode);
  return owner === fiber || owner === fiber.alternate;
}
```

Before a HostSingleton `commitHostUpdate`, return when this predicate is false.

Before `commitHostSingletonRelease`, return when this predicate is false.

A props-identity-only variant was considered and rejected. `updateFiberProps` preserves useful current-owner props, but distinct Fibers can theoretically share the same props object when a React element is reused; the DOM -> Fiber association is the stronger ownership token.

## Why this is better than the current partial Offscreen guards

The earlier experiment guards two call sites with `offscreenSubtreeWasHidden`:

- skip HostSingleton update under an already-hidden subtree;
- skip eager HostSingleton release when deleting an already-hidden subtree.

Those guards encode one known stale-owner route in reconciler traversal.

An ownership check instead protects the shared persistent host node itself. It also covers future stale call paths that reach update/release after ownership has moved, without requiring every reconciler path to reproduce the same hidden-state condition.

## Existing Activity matrix

Expected behavior:

1. **First hide releases previous props** — allowed because the DOM association points to that owner or its alternate.
2. **Hidden update after visible owner acquisition** — skipped because the body association points to the visible owner's different Fiber pair.
3. **Delete already-hidden owner while visible owner remains** — repeated release skipped for the same reason.
4. **Reappear after hidden prop updates** — hidden work still updates Fiber memoized props; reacquisition applies those latest props and replaces the DOM association.
5. **Restore children detached by another owner's DSIH** — unresolved by the guard alone. The newer contribution-aware body model aims to prevent this detachment instead.
6. **Hidden descendant Placement** — not globally suppressed by the leading contribution model; it can be valid if correctly ordered into the hidden owner's own child contribution.

So this is a containment repair for exclusive singleton state, not a complete child-ownership repair.

## Public Suspense reachability

The public Suspense-anywhere Fiber regression `can render a Suspense boundary above the <html> tag` provides a production-feature version of the same ownership overlap.

Its checked-in behavior explicitly demonstrates:

- a primary document/body is visible;
- the primary suspends;
- a fallback document/body acquires the same persistent singleton nodes;
- the primary managed children remain mounted and hidden in the physical document;
- later resolution reacquires the primary document.

That is exactly the lifecycle in which stale hidden primary singleton properties could race with the visible fallback owner.

### New PR 41 public control

PR 41 now adds a test derived from that public harness:

1. render primary document/body with `data-owner="primary"` and a primary click handler;
2. suspend so fallback document/body becomes visible with `data-owner="fallback"` and its own click handler;
3. while the same promise is still pending, re-render the app with the hidden primary body changed to `data-owner="hidden-update"`;
4. require the physical body to remain `fallback` and a click to reach only the fallback handler;
5. resolve the promise;
6. require the reappearing primary body to use `hidden-update` and its primary event props.

The workflow applies the test **before** the source experiment and requires untouched current source to fail. It then applies the ownership guard and requires the same public Suspense control to pass.

If this executes as expected, stale singleton property ownership is reachable through the public Suspense document feature, not only through direct Activity API usage.

If untouched current source unexpectedly passes, downgrade the owner-guard case back to Activity-only and inspect why the Suspense hidden tree does not commit the body property update while fallback remains visible.

## Keyed replacement compatibility

The current deletion path eagerly releases an old HostSingleton before a keyed replacement can acquire the persistent DOM node. In that healthy ordering the DOM association still points to the deleting owner, so the guard allows release.

Once a different owner has already acquired the node, an old owner's later cleanup no longer has authority to clear the new owner's properties or detach its Fiber/props mapping.

## Event / props benefit

Skipping stale `commitHostUpdate` prevents `updateFiberProps(instance, hiddenProps)` from overwriting the visible owner's current event-handler props while the DOM Fiber pointer belongs to the visible owner.

Skipping stale release prevents `detachDeletedInstance(instance)` from deleting the visible owner's Fiber/props mapping.

These were two independently observed corruption modes in the Activity review.

## Integration dependency: DOM ownership association lifecycle

A strict DOM-owner guard cannot be promoted if another lifecycle can erase a legitimate current singleton association without making that owner actually stale.

The preamble-marker detach hypothesis initially looked like such a dependency, but the first event regression used a synthetic marker arrangement that real Fizz does not normally emit. React PR 43 now falsifies that hypothesis against a real Fizz fallback-body takeover before it is allowed to become a production dependency.

Interpret the dependency conservatively:

- if PR 43 real-Fizz takeover passes current source, remove that specific preamble concern from the owner-guard blocker list;
- if it fails, the owner guard needs the corresponding association repair or a richer owner token;
- independent render-phase HostSingleton hydration binding remains a broader lifecycle concern because current `hydrateInstance()` still eagerly binds during complete work and `bindInstance()` documents a future commit-time direction.

Do not solve a hypothetical missing-association case by treating `owner == null` as automatically authorized: after a real release, missing ownership is precisely what should make repeated hidden updates/releases stale.

## Executable lane

Owned React draft PR 41 is the verifier-only experiment.

- Base: current fork/public main `2042572329425f9ebf35ae6287ea5bab72b2c497`.
- Source packet: one reconciler host-effect patch using existing `getInstanceFromNode`.
- Contracts: five-test Activity matrix plus public Suspense hidden-primary/fallback-owner control.
- Current-source public Suspense control is required red before the experiment is applied.
- Expected experiment pass subset: first hide, stale hidden update containment, repeated hidden release containment, reappear with latest props, public Suspense fallback authority.
- Required remaining red: detached managed-child restoration after another owner used direct HTML.

The workflow preflights every hand-built patch before installation/tests so packet errors remain separate from semantic failures.

## Limits

- the guard depends on correct lifecycle ownership of the DOM association itself;
- body child contributions still need the separate slot/range semantics;
- opaque content needs node provenance;
- opaque Activity visibility needs explicit top-level-node hide/unhide handling;
- reappearance acquisition still occurs in layout and has its existing phase-order TODO;
- a third-party renderer that advertises singleton support must have `getInstanceFromNode` semantics compatible with returning its internal instance handle; React DOM satisfies this.

## Public overlap

Read-only public PR searches for HostSingleton stale-owner / hidden-owner containment found no direct matching owner in the current search. Public interaction remains unauthorized and none was performed.

## Disposition

**EXECUTE as a narrow containment experiment. Public Suspense reachability is now the key discriminator.**

Do not promote it as complete body ownership; it protects exclusive singleton properties/events only. The contribution model remains responsible for children.

## Evidence class

Current-source/history read plus target-test-prepared PR 41. Public Suspense reachability remains unexecuted until the custom workflow runs. No public upstream interaction performed.
