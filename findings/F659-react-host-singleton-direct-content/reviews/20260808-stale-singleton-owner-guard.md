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

This gives React enough information to distinguish a legitimate update/release from stale work belonging to a previously released owner.

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

A null DOM owner means the singleton was already released, so repeated hidden updates/releases naturally become no-ops until reacquisition.

A props-identity-only variant was considered and rejected. `updateFiberProps` preserves useful current-owner props, but distinct Fibers can theoretically share the same props object when a React element is reused; the DOM -> Fiber association is the stronger ownership token.

## Why this is better than the current partial Offscreen guards

The earlier experiment guards two call sites with `offscreenSubtreeWasHidden`:

- skip HostSingleton update under an already-hidden subtree;
- skip eager HostSingleton release when deleting an already-hidden subtree.

Those guards encode one known stale-owner route in reconciler traversal.

An ownership check instead protects the shared persistent host node itself. It also covers future stale call paths that reach update/release after ownership has moved, without requiring every reconciler path to reproduce the same hidden-state condition.

## Expected behavior against the existing Activity matrix

1. **First hide releases previous props** — allowed because the DOM association points to that owner or its alternate.
2. **Hidden update after visible owner acquisition** — skipped because the body association points to the visible owner's different Fiber pair.
3. **Delete already-hidden owner while visible owner remains** — repeated release skipped for the same reason.
4. **Reappear after hidden prop updates** — hidden work still updates Fiber memoized props; reacquisition applies those latest props and replaces the DOM association.
5. **Restore children detached by another owner's DSIH** — unresolved. This guard cannot synthesize Placement for surviving child Fibers.
6. **Hidden descendant Placement** — unresolved. Child Placement can mutate the shared body even when the HostSingleton's own update is rejected.

So this is a containment repair, not a complete Activity/opaque-child ownership repair.

## Keyed replacement compatibility

The current deletion path eagerly releases an old HostSingleton before a keyed replacement can acquire the persistent DOM node. In that healthy ordering the DOM association still points to the deleting owner, so the guard allows release.

Once a different owner has already acquired the node, an old owner's later cleanup no longer has authority to clear the new owner's properties or detach its Fiber/props mapping.

## Event / props benefit

Skipping stale `commitHostUpdate` prevents `updateFiberProps(instance, hiddenProps)` from overwriting the visible owner's current event-handler props while the DOM Fiber pointer belongs to the visible owner.

Skipping stale release prevents `detachDeletedInstance(instance)` from deleting the visible owner's Fiber/props mapping.

These were two independently observed corruption modes in the Activity review.

## Executable lane

Owned React draft PR 41 is the verifier-only experiment.

- Base at PR creation: current fork/public main `2042572329425f9ebf35ae6287ea5bab72b2c497`.
- Source packet: one reconciler host-effect patch using existing `getInstanceFromNode`.
- Contract: the existing five-test Activity ownership matrix.
- Expected pass subset: first hide, stale hidden update containment, repeated hidden release containment, reappear with latest props.
- Required remaining red: detached managed-child restoration after another owner used direct HTML.

The workflow also preflights the hand-built patches before installation/tests so patch-packet errors are kept separate from semantic failures.

## Limits

- descendant Placement/deletion below the stale HostSingleton still needs an ownership-aware rule;
- managed children physically detached by another owner still need preservation/restoration;
- opaque content needs node + slot provenance;
- reappearance acquisition still occurs in layout and has its existing phase-order TODO;
- a third-party renderer that advertises singleton support must have `getInstanceFromNode` semantics compatible with returning its internal instance handle; React DOM satisfies this.

## Public overlap

Read-only public PR searches for HostSingleton stale-owner / hidden-owner containment found no direct matching owner in the current search. Public interaction remains unauthorized and none was performed.

## Disposition

**EXECUTE as a narrow containment experiment; never treat it as complete Activity ownership.**

This is more general and cleaner than the two Offscreen-specific guards for the update/release corruption subset.

## Evidence class

Source-read plus target-test-prepared PR 41. No execution receipt yet.
