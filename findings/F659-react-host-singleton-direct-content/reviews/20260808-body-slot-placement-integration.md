# Body slot integration with host-sibling placement

## Concrete current failure the slot must address

Consider a managed body contribution followed by a stable root Fiber sibling:

```text
Fiber order:
  <body>
    A
  </body>
  R
```

Physical body initially:

```text
A, R
```

Outside code inserts X after A / before R:

```text
A, X, R
```

Now React appends managed child B to the end of the **same body Fiber**.

Current body is not a host-parent scope, so `getHostSibling(B)` can climb out through `<body>` and find root sibling R.

Placement inserts B before R:

```text
A, X, B, R
```

The outside node X has effectively moved from after the body contribution to between the body's managed children, even though React never moved X itself.

The historical HostSingleton insertion-edge work existed to prevent exactly this class of tail interleaving.

## Per-body slot rule

When host-sibling search for a descendant climbs out through a body HostSingleton, that body Fiber's slot is the **terminal end edge for that contribution**.

Do not keep searching to unrelated root siblings merely to obtain a DOM anchor.

The slot state can supply its current physical right anchor:

- next DOM node at the Range offset;
- or null if the body contribution's slot is at physical body end.

In the example, the body slot sits before X, so B is inserted before X:

```text
A, B, X, R
```

Outside X remains after the body contribution.

## Initial body placement is straightforward

On initial HostSingleton Placement:

1. normal root-level `getHostSibling(bodyFiber)` finds the next stable Fiber host node after the body contribution, e.g. R;
2. existing recursive placement inserts all managed body terminals before R;
3. initialize the body slot Range immediately before R, or at body end if R is null.

For an empty body, step 2 inserts nothing but step 3 still records the Fiber position.

So the slot can be initialized from the exact `before` anchor placement already computes.

## End-placement needs post-insertion Range reset

A live Range at the right edge has left-sticky equality semantics.

If B is inserted **at exactly the Range offset**, the browser leaves the Range before B.

But after a body-end placement the slot must be after B.

Therefore body-end placement needs:

1. snapshot the slot's right anchor before mutation;
2. insert the entire host subtree before that anchor (or append if null);
3. reset/collapse the body Range immediately before the same right anchor, or at new body end.

This updates the contribution's right edge without moving outside DOM.

## Root-level placement before an empty body slot

An empty body has no physical host node.

Suppose root Fiber S is logically inserted immediately before empty body A.

Both S and A can map to the same DOM offset.

Host-sibling search should treat A as a **virtual stable sibling** and return:

- the body's current physical slot anchor;
- metadata saying this insertion crosses body slot A from the left.

After S's host terminals are inserted, placement advances A's Range to the right side of S.

This preserves Fiber order even though A has no DOM node.

## Root-level placement after an empty body slot

If S is logically after body A, host-sibling search starts after A and does not use A as the insertion target.

Insertion at the same physical DOM offset naturally leaves A's left-sticky Range before S, which is correct.

This is the Fiber-affinity distinction recorded separately.

## Placement result likely needs richer internal metadata

Current `getHostSibling()` returns only `?Instance`.

That is insufficient to encode virtual empty body slots that need post-placement affinity updates.

A cleaner internal abstraction is conceptually:

```text
HostPlacementEdge = {
  before: ?Instance,
  advanceSingletonSlots: null | Array<Fiber-or-state>,
}
```

For ordinary placement:

```text
before = normal stable DOM sibling
advanceSingletonSlots = null
```

For body descendant end-placement:

```text
before = body's slot right anchor
advanceSingletonSlots = [that body slot]
```

For a root insertion before one or more empty body slots:

```text
before = shared physical anchor
advanceSingletonSlots = [empty slots crossed from left]
```

After insertion, generic placement calls a host-config hook to advance/reset those opaque renderer slot states.

Exact type/API naming is open; the important point is that a physical DOM sibling alone cannot represent the virtual ordering information.

## Non-empty body as root sibling

When a stable body contribution has managed child Fibers, root-level `getHostSibling(S)` before that body can still descend into the body and return its first stable HostComponent/Text node. The live right-edge Range automatically shifts when S inserts before that content.

For opaque body mode with no child Fibers, host-sibling search needs a host-config helper to expose the opaque contribution's first owned top-level node.

For empty body mode, use the virtual slot edge above.

This yields a three-mode host-sibling behavior while keeping one persistent slot state.

## External node between body children

If host-sibling search finds a later stable React-managed child C inside the same body contribution, normal placement before C remains correct. An outside node X already interleaved before C stays physically in place; React does not need to move it.

The slot abstraction is specifically required when placement reaches the **end of this body Fiber's contribution**, where current search would otherwise escape to unrelated root siblings.

## Historical relation

The removed insertion-edge implementation solved body/head tails by scanning the singleton DOM for an edge around React-owned nodes.

The new model preserves the useful concept but replaces repeated DOM scans with explicit per-Fiber slot state and Fiber-affinity metadata.

This is more robust for:

- empty bodies;
- multiple hidden/visible body owners;
- opaque DSIH contributions with no child Fibers;
- outside DOM inserted after a contribution.

## Disposition

**REQUIRED RECONCILER INTEGRATION FOR THE BODY SLOT MODEL.**

A body Range stored on Fiber is not enough unless `getHostSibling`/placement stops at that contribution boundary for descendant end-placement and can update virtual empty-slot affinity after insertion.
