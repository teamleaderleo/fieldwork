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

This gives the renderer enough information to distinguish a legitimate update/release from stale work belonging to a previously released owner.

## Proposed containment predicate

Conceptually:

```js
function isCurrentSingletonOwner(instance, internalInstanceHandle) {
  const owner = getInstanceFromNodeDOMTree(instance);
  return (
    owner === internalInstanceHandle ||
    owner === internalInstanceHandle.alternate
  );
}
```

For a HostSingleton `commitUpdate`, return without DOM/property bookkeeping when that predicate is false.

For `releaseSingletonInstance`, pass the releasing Fiber handle into the host config and return without clearing/detaching when the predicate is false.

A null DOM owner also means the singleton was already released, so repeated hidden updates/releases naturally become no-ops until reacquisition.

## Why this is better than the current partial Offscreen guards

The existing experiment guards two call sites with `offscreenSubtreeWasHidden`:

- skip HostSingleton update under an already-hidden subtree;
- skip eager HostSingleton release when deleting an already-hidden subtree.

Those guards encode one known stale-owner route in reconciler traversal.

An ownership check instead protects the shared persistent host node itself. It also covers future stale call paths that reach update/release after ownership has moved, without requiring every reconciler path to reproduce the same hidden-state condition.

## Expected behavior against the existing Activity matrix

The existing verifier controls imply:

1. **First hide releases previous props** — still allowed because the DOM association points to that owner or its alternate.
2. **Hidden update after visible owner acquisition** — skipped because the body association points to the visible owner's different Fiber pair.
3. **Delete already-hidden owner while visible owner remains** — repeated release skipped for the same reason.
4. **Reappear after hidden prop updates** — hidden updates changed Fiber memoized props even though host mutation was skipped; reacquisition applies those latest props and replaces the DOM association.
5. **Restore children detached by another owner's DSIH** — still unresolved. This guard cannot synthesize Placement for surviving child Fibers.
6. **Hidden descendant Placement** — still unresolved. Child Placement can mutate the shared body even when the HostSingleton's own update is rejected.

So this is a containment repair, not a complete Activity/opaque-child ownership repair.

## Keyed replacement compatibility

The current deletion path eagerly releases an old HostSingleton before a keyed replacement can acquire the persistent DOM node. In that healthy ordering the DOM association still points to the deleting owner, so the guard allows release.

Once a different owner has already acquired the node, an old owner's later cleanup no longer has authority to clear the new owner's properties or detach its Fiber/props mapping.

## Event / props benefit

Skipping stale `commitUpdate` also prevents `updateFiberProps(instance, hiddenProps)` from overwriting the visible owner's current event-handler props while the DOM Fiber pointer still belongs to the visible owner.

Skipping stale release prevents `detachDeletedInstance(instance)` from deleting the visible owner's Fiber/props mapping.

These were two independently observed corruption modes in the Activity review.

## Limits

- descendant Placement/deletion below the stale HostSingleton still needs an ownership-aware rule;
- managed children physically detached by another owner still need preservation/restoration;
- opaque content needs node + slot provenance;
- reappearance acquisition still occurs in layout and has its existing phase-order TODO;
- the Fiber/alternate match should be implemented in reconciler-visible code or through a renderer helper with deliberate typing, rather than relying on an undocumented Object field casually.

## Public overlap

Read-only public PR searches for HostSingleton stale-owner / hidden-owner containment found no direct matching owner in the current search. Public interaction remains unauthorized and none was performed.

## Disposition

**Worth an isolated verifier-only experiment.**

This appears strictly better scoped than the two Offscreen-specific guards for the update/release corruption subset, while making no claim to solve child ownership.

## Evidence class

Source-read and existing-test-matrix reasoning. Target-test-prepared experiment recommended; no execution receipt yet.
