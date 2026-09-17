# Body HostSingleton — persistent slot Range model

## Refinement

The strongest client design no longer treats the live Range as opaque-DISIH-only metadata.

**Every body HostSingleton Fiber can own a persistent logical body-scope slot, represented by a collapsed live right-edge Range.**

Managed children, empty content, and opaque DSIH are different content modes inside the same Fiber-owned slot.

This turns the historical insertion-edge concept into explicit per-Fiber state rather than repeated DOM scanning heuristics.

## Why body needs a slot object at all

`body` is intentionally invisible to host positioning. Its descendants and root-level siblings share physical `document.body`.

The Fiber tree nevertheless has a precise logical point where the body contribution belongs:

```text
root content before body
<body> contribution slot
root content after body
```

A persistent Range lets that point survive:

- outside DOM insertions;
- empty body content;
- managed child deletion/reinsertion;
- managed <-> opaque transitions;
- hidden Activity owners coexisting with another visible owner.

## Initial placement

When a body HostSingleton is first placed, `getHostSibling(bodyFiber)` already finds the next stable Fiber-owned host node after the body contribution.

Conceptually:

1. resolve `before` using normal Fiber host-sibling search;
2. establish the body slot at that position;
3. insert this body's managed children or opaque contribution before `before`;
4. collapse/reset the Range to the right edge of the finished body contribution.

If body content is empty, no DOM child needs to be inserted; the Range alone records the slot.

This is exactly the case historical insertion-edge heuristics could not represent explicitly.

## Managed children

Managed body children remain ordinary HostComponent/Text Fibers.

The Range is **not** their ownership list. Their existing Fiber/DOM mappings remain authoritative.

The Range only supplies the end-of-body-contribution insertion edge.

### Placement before an internal body sibling

Normal `getHostSibling(child)` can return the stable later managed child. The live Range automatically shifts when insertion occurs before its right edge.

### Placement at the end of the body contribution

When host-sibling search climbs out through the body Fiber without finding a later managed child inside that body contribution, it should stop at the body slot and use the Range's current right-hand anchor rather than continuing to an unrelated root sibling / append edge.

This is the key replacement for historical `getInsertionEdge(parent)` DOM scanning.

After such an end placement, reset/recompute the body's collapsed Range to the new right edge. Equality insertion semantics otherwise leave a live Range on the left side of a node inserted exactly at its current offset.

### Deletion

Removing managed nodes before the right-edge Range naturally shifts the live boundary left.

If the last managed child disappears, the body contribution becomes empty while the Range preserves its logical position relative to outside/root siblings.

## Recompute versus incremental bookkeeping

The safest first implementation may recompute the right edge at the end of a body mutation pass rather than trying to update the Range perfectly for every Placement path.

For managed mode:

- find the last connected HostComponent/Text terminal that belongs to this body Fiber subtree;
- collapse Range immediately after it;
- if there is no managed terminal, retain the previously tracked empty-slot position / known right anchor.

For opaque mode:

- collapse immediately after the last owned opaque top-level node;
- if opaque content is empty, keep the existing slot position.

This scan should skip portals and physical nodes owned elsewhere such as Hoistables.

HostSingleton count is tiny, so correctness matters more than micro-optimizing the first design.

## Outside-node behavior

### Outside node inserted after body contribution

Insertion at the exact right-edge offset leaves the Range before the new outside node.

A later body end-placement/replacement therefore still occurs before that outside node.

### Outside node inserted before body contribution

Insertion before the Range shifts the Range right. The outside node remains before this body contribution.

### Outside node inserted among managed body children

Managed child Fiber ownership continues to identify React nodes. The right-edge slot remains after the contribution's last React-managed terminal.

Whether an interstitial outside node is considered before/inside the logical body contribution for future large replacements remains governed by the same HostSingleton outside-node policy; no Range-based deletion should accidentally delete it.

## Opaque DSIH mode

DSIH becomes another content implementation for the same body slot.

The renderer records exact top-level opaque nodes created by this Fiber on client writes.

The slot Range persists independently.

### Managed -> opaque

1. retain the body's right-edge slot;
2. normal mutation effects retire managed child Fibers;
3. parse DSIH through a detached body `innerHTML` sink;
4. insert one DocumentFragment at the body slot;
5. store opaque node provenance;
6. reset Range to the resulting right edge.

### Opaque -> opaque

1. retain slot/right anchor;
2. remove only old opaque owned nodes;
3. insert replacement fragment at the same slot;
4. replace opaque provenance;
5. reset Range.

### Opaque -> managed

1. retain slot/right anchor;
2. remove old opaque owned nodes before replacement custom elements can connect;
3. child Placements use the body slot as their end insertion edge;
4. opaque provenance is discarded;
5. Range remains the managed body's right edge.

This removes most of the transition-specific insertion-edge machinery in PR 32.

## Activity / overlapping body owners

Each body HostSingleton Fiber can retain its own slot Range even though all resolve to the same persistent `document.body` instance.

This cleanly separates:

- **exclusive singleton state:** only the currently acquired owner controls body attributes/events/Fiber props;
- **per-Fiber child slot:** hidden and visible body owners can each retain ordered child contributions in the physical body.

### Hidden managed owner

Its managed descendants remain connected and are hidden by existing Offscreen traversal. Its slot Range remains around that contribution.

### Visible competing owner

Its body slot is inserted/maintained at its own Fiber position. Its managed or opaque content does not need to delete the hidden owner's contribution.

### Reappear

The hidden owner reacquires exclusive singleton properties and normal unhide operates on already-connected managed descendants. Detached-child restoration is prevented.

### Hidden child updates

A new hidden managed child may be inserted into that hidden body's own slot and then hidden normally. This is preferable to globally suppressing descendant Placement merely because another body owner currently has exclusive singleton properties.

## Opaque Activity visibility

Opaque DSIH still needs a renderer-level hide/unhide operation because it has no child Fibers.

The body slot Range makes location/ownership stable, but visibility must explicitly hide/show the owned opaque top-level nodes while preserving connectedness where possible.

This remains an independent acceptance requirement.

## Host-sibling integration

The clean reconciler question becomes:

> When host-sibling search climbs out through a non-scoped body HostSingleton, should that Fiber's slot Range act as the terminal insertion edge for descendants that belong to this body contribution?

For body, likely yes.

For root-level siblings outside the body Fiber, normal search continues around the body contribution as usual; the body slot itself can also act as a sibling unit when another Fiber needs to insert relative to it.

This is conceptually close to the old HostSingleton placement/insertion-edge implementation, but uses explicit per-Fiber position state instead of scanning DOM ownership every time.

## Server/hydration mirror

The guarded Fizz protocol can instantiate the same abstraction on hydration:

- server opaque guards identify the initial body content slot/range;
- body-scope hydration cursor establishes Fiber order;
- after successful hydration, remove/retire serialized guards and create the in-memory body slot Range;
- future client updates use the same slot model regardless of whether initial content was server-rendered.

For managed server body children, existing child hydration plus a commit-time slot initialization can establish the Range after the final hydrated managed terminal.

## Head/html exclusion

A persistent slot Range is a **body-scope** mechanism.

`head` is a singleton host scope with resource/Hoistable ownership. `html` carries document identity constraints. Do not generalize this model by tag symmetry.

## Disposition

**LEADING CLIENT POSITION MODEL.**

The strongest complete body architecture now looks like:

1. persistent per-Fiber body slot Range for all content modes;
2. normal Fiber ownership for managed children;
3. explicit node provenance for client-created opaque content;
4. exclusive current owner for singleton properties/events;
5. contribution-aware opaque visibility under Activity;
6. guarded Fizz server ranges that hydrate into the same slot abstraction;
7. an explicit SSR policy for third-party nodes inserted inside opaque server ranges.

This is a design result, not yet a clean source candidate.
