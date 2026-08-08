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

## Expected behavior against the existing Activity matrix

1. **First hide releases previous props** — allowed because the DOM association points to that owner or its alternate.
2. **Hidden update after visible owner acquisition** — skipped because the body association points to the visible owner's different Fiber pair.
3. **Delete already-hidden owner while visible owner remains** — repeated release skipped for the same reason.
4. **Reappear after hidden prop updates** — hidden work still updates Fiber memoized props; reacquisition applies those latest props and replaces the DOM association.
5. **Restore children detached by another owner's DSIH** — unresolved by the guard alone. The newer contribution-aware body model aims to prevent this detachment instead.
6. **Hidden descendant Placement** — not globally suppressed by the leading contribution model; it can be valid if correctly ordered into the hidden owner's own child contribution.

So this is a containment repair for exclusive singleton state, not a complete child-ownership repair.

## Keyed replacement compatibility

The current deletion path eagerly releases an old HostSingleton before a keyed replacement can acquire the persistent DOM node. In that healthy ordering the DOM association still points to the deleting owner, so the guard allows release.

Once a different owner has already acquired the node, an old owner's later cleanup no longer has authority to clear the new owner's properties or detach its Fiber/props mapping.

## Event / props benefit

Skipping stale `commitHostUpdate` prevents `updateFiberProps(instance, hiddenProps)` from overwriting the visible owner's current event-handler props while the DOM Fiber pointer belongs to the visible owner.

Skipping stale release prevents `detachDeletedInstance(instance)` from deleting the visible owner's Fiber/props mapping.

These were two independently observed corruption modes in the Activity review.

## Critical integration dependency: preamble marker cleanup

A strict DOM-owner guard cannot be promoted independently while current Fizz preamble cleanup can destroy a legitimate current owner association.

Current `clearSingletonPreambleContribution(instance)` calls `detachDeletedInstance(instance)` without any old HostSingleton Fiber handle. HostSingleton hydration can already have associated the persistent node with the current client Fiber/props before nested dehydrated-boundary cleanup runs.

If marker cleanup deletes that association, a later legitimate HostSingleton update sees no matching body owner. React DOM's generic `getInstanceFromNode(body)` may then return a nearest ancestor Fiber (for example the html singleton) or null rather than the current body Fiber. The strict guard classifies the body update as stale and skips it.

So the guard currently depends on one of two things:

1. fix preamble cleanup so it preserves the current client singleton association (React PR 43 is the narrow experiment); or
2. introduce a richer ownership state than the raw DOM -> Fiber map so a missing association can be distinguished from an intentionally released owner.

Simply treating a missing owner as authorized is insufficient: after a real singleton release, null/missing ownership is exactly what should make repeated hidden updates/releases lose authority.

This is a real integration dependency, not a reason to return to Offscreen-specific guards.

## Executable lane

Owned React draft PR 41 is the verifier-only experiment.

- Base at PR creation: current fork/public main `2042572329425f9ebf35ae6287ea5bab72b2c497`.
- Source packet: one reconciler host-effect patch using existing `getInstanceFromNode`.
- Contract: the existing five-test Activity ownership matrix.
- Expected pass subset: first hide, stale hidden update containment, repeated hidden release containment, reappear with latest props.
- Required remaining red: detached managed-child restoration after another owner used direct HTML.

The workflow also preflights the hand-built patches before installation/tests so patch-packet errors are kept separate from semantic failures.

A future integration verifier should add a preamble-cleanup-then-body-update control before any owner guard is promoted beyond the isolated Activity experiment.

## Limits

- the guard depends on correct lifecycle ownership of the DOM association itself;
- body child contributions still need the separate contribution/range semantics;
- opaque content needs node + slot provenance;
- opaque Activity visibility needs explicit top-level-node hide/unhide handling;
- reappearance acquisition still occurs in layout and has its existing phase-order TODO;
- a third-party renderer that advertises singleton support must have `getInstanceFromNode` semantics compatible with returning its internal instance handle; React DOM satisfies this.

## Public overlap

Read-only public PR searches for HostSingleton stale-owner / hidden-owner containment found no direct matching owner in the current search. Public interaction remains unauthorized and none was performed.

## Disposition

**EXECUTE as a narrow containment experiment; do not promote independently of current-owner association correctness.**

This is more general and cleaner than the two Offscreen-specific guards for the update/release corruption subset, but PR 43 (or equivalent owner-preservation work) is now an explicit dependency for production use.

## Evidence class

Source-read plus target-test-prepared PR 41, with a source-read integration dependency on #708/PR 43. No execution receipt yet.
