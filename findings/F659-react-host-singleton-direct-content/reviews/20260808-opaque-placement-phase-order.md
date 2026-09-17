## In simple words

The body opaque-content defect is enforced by commit ordering, not merely by an over-broad cleanup helper.

On a new HostSingleton mount, React resolves the persistent body during render and marks the singleton for update, but it does not apply the singleton props then. During commit, normal host Placement effects run in the mutation phase. The new HostSingleton is acquired later in the layout phase, where `acquireSingletonInstance()` applies `setInitialProperties()`. If body props contain `dangerouslySetInnerHTML`, that late acquisition writes the whole `body.innerHTML` after sibling/body-scope Placements already happened.

On an existing HostSingleton update, child mutation effects run first and then `commitHostUpdate()` applies the new singleton props. A managed -> opaque transition therefore removes/places ordinary host children before the later whole-body DSIH update overwrites the current body child list.

This proves that selective release/reset cannot make the full lifecycle correct. Opaque content must participate in commit placement/update semantics rather than arriving as an unrelated whole-container property side effect.

## New mount path

`ReactFiberCompleteWork` HostSingleton mount does the following when it is not hydrating:

1. call `resolveSingletonInstance(type, props, rootContainer, hostContext, true)`;
2. store the persistent DOM node in `workInProgress.stateNode`;
3. `markUpdate(workInProgress)`.

It deliberately does not call `setInitialProperties()` during render.

During the mutation phase, `commitMutationEffectsOnFiber` for HostSingleton:

1. traverses child mutation effects;
2. runs `commitReconciliationEffects`, including Placement;
3. only runs `commitHostUpdate` when `current !== null && flags & Update`.

Therefore a newly mounted singleton does not apply its props in mutation.

During regular layout effects, HostSingleton has a special mount path:

```js
if (current === null && flags & Update) {
  commitHostSingletonAcquisition(finishedWork);
}
```

The adjacent TODO explicitly says acquisition should ideally move to the mutation phase but currently remains in layout because disappear must precede appear.

`commitHostSingletonAcquisition` reaches `acquireSingletonInstance`, which clears/reapplies singleton props through `setInitialProperties`.

### Consequence

Given Fiber order:

```jsx
<>
  <div id="before" />
  <html>
    <head />
    <body dangerouslySetInnerHTML={{__html: '<span id="opaque" />'}} />
  </html>
  <div id="after" />
</>
```

normal host Placement can first produce the surrounding body-scope nodes. Later layout acquisition writes whole-body `innerHTML`, deleting them.

No release/reset logic participates in this failure.

## Existing update path

For an existing HostSingleton, mutation commit does:

1. `recursivelyTraverseMutationEffects(root, finishedWork, lanes)`;
2. `commitReconciliationEffects(finishedWork, lanes)`;
3. if `current !== null && flags & Update`, call `commitHostUpdate(finishedWork, newProps, oldProps)`.

`commitHostUpdate` ultimately calls renderer `commitUpdate`, which invokes `updateProperties` and therefore the generic DSIH `innerHTML` setter.

For managed -> opaque body:

- old managed child deletion executes during recursive child mutation effects;
- surrounding body-scope siblings remain mounted;
- HostSingleton update then assigns the entire body `innerHTML`;
- those surrounding siblings are erased even though their Fibers were unchanged.

For opaque -> opaque:

- there may be no child Fibers at all;
- `commitHostUpdate` directly replaces the whole body list, again erasing outside nodes inserted after the previous opaque write.

## Suspense fallback path

A newly visible fallback document owner compounds the mount ordering issue.

The primary document can remain mounted but hidden. The fallback HostSingleton is a new owner. Its layout acquisition occurs after mutation-phase hide/placement work and can then write whole-body DSIH, detaching hidden primary host nodes that are supposed to remain mounted for reappearance.

This explains the opaque Suspense fallback counterexample without relying on a speculative Activity-specific interaction.

## Representation consequence

A correct body opaque contribution needs a mutation-phase representation that can answer both ownership and host ordering.

Two implementation families remain plausible:

### Reconciler-visible opaque terminal

Represent raw opaque content as a terminal contribution that participates in Placement, sibling discovery, deletion, and hidden ownership. This gives the reconciler an explicit unit to order among body-scope host nodes, but it is a larger internal semantic addition.

### HostSingleton-owned placement boundary visible to commit host effects

Keep HostSingleton as the Fiber but teach placement/sibling logic that a body singleton in opaque mode contributes a host boundary/range. The boundary would need to exist early enough in mutation to establish its slot, survive updates/empty HTML, and be addressable on release/reappearance/hydration.

A HostConfig-only cleanup range that is created during layout acquisition is too late for initial placement ordering.

## Rejected consequence

The following can no longer be considered complete repairs for body non-null DSIH:

- release-only child cleanup;
- ContentReset-only transition cleanup;
- selective range bookkeeping created only inside `acquireSingletonInstance` / `commitUpdate`;
- any implementation that still writes `body.innerHTML` after ordinary body-scope Placements.

They can correct local symptoms but leave initial acquisition and same-tree ordering broken.

## Decision

**REQUIRE MUTATION-PHASE PLACEMENT SEMANTICS FOR OPAQUE BODY CONTENT.**

Continue the narrow unset-wrapper release fix independently. For actual non-null DSIH, do not revive a source candidate until the opaque contribution has an explicit mutation-phase placement representation.