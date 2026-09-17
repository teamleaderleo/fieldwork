## In simple words

The removed HostSingleton insertion-edge implementation is useful precedent for the reconciler half of the current body opaque-content problem, but its renderer half does not solve opaque ownership.

The old packet made HostSingleton itself participate in Placement and sibling discovery. That is directly relevant because current body DSIH has no host-positioning identity. However, old singleton placement still reapplied the singleton props through ordinary DOM property initialization, so `dangerouslySetInnerHTML` still reached a whole-element `innerHTML` assignment.

Decision: salvage the placement-unit concept and insertion-edge reasoning; reject copying the old singleton reset/property writer.

## Historical reconciler behavior

The early HostSingleton implementation added all of the following:

- HostSingleton counted as a host parent;
- `getHostSibling()` stopped when it reached a HostSingleton instead of always looking through it;
- `commitReconciliationEffects()` used a dedicated `commitSingletonPlacement()` path when placing a HostSingleton;
- HostSingleton insertion was skipped by generic recursive placement because it was placed independently;
- when placing ordinary children into a persistent singleton, the renderer's `getInsertionEdge(parent)` supplied a fallback position around non-React nodes;
- root/container placement could also consult an insertion edge when the physical parent was itself a persistent singleton.

This is strong evidence that React previously recognized a persistent singleton as a meaningful placement boundary rather than only as a DOM property target.

## Historical renderer behavior

The corresponding DOM host config did two different things:

1. `getInsertionEdge(parent)` scanned persistent singleton children and DOM-to-Fiber ownership to choose a safe insertion point around non-React nodes;
2. `commitSingletonPlacement()` reset singleton state and reapplied the new singleton props.

The reset path tried to retain style and stylesheet nodes when clearing a persistent head/body. But `resetProperties()` then called ordinary `setInitialProperties()` with the singleton's props.

The old `ReactDOMComponent` patch still handled `dangerouslySetInnerHTML` using the ordinary direct HTML setter. Therefore a singleton DSIH prop could still assign whole-element `innerHTML` after the sparse reset and remove the supposedly retained nodes.

The old packet was designed primarily around Fiber-managed singleton children/resources, not raw opaque child provenance.

## What remains reusable

### Placement identity

A body singleton in opaque mode needs some reconciler-visible terminal/boundary so that surrounding body-scope host nodes can find it as a sibling.

The old packet proves this can be integrated into `commitPlacement` / `getHostSibling` without requiring the persistent body DOM node itself to be moved.

### Outside-node insertion reasoning

The old `getInsertionEdge` demonstrates a policy React has already explored: append relative to sibling React trees while avoiding unnecessary movement of outside nodes in the persistent singleton.

A new opaque contribution still needs more precise ownership than DOM-to-Fiber scanning because its raw children have no child Fibers, but the edge is useful for placing a newly created contribution around existing outside state.

## What must change for opaque content

A future body DSIH experiment cannot finish by calling ordinary singleton `setInitialProperties` / `updateProperties` for the child-content prop.

It needs to split singleton **property state** from singleton **opaque child contribution**:

- ordinary attributes/property-backed state can use existing singleton acquire/update ownership machinery;
- opaque child content must be parsed/inserted as its own contribution at the reconciler-computed slot;
- updates must retire only the prior contribution's top-level nodes;
- opaque -> managed must retire the contribution before child Placement;
- managed -> opaque must delete managed child Fibers first, then place the opaque contribution at the same logical slot;
- initial mount must place opaque content during mutation or equivalent host-placement work, before layout acquisition can overwrite sibling placements;
- layout acquisition must skip the child-content write once the opaque contribution has been placed independently.

## Top-level node ownership hypothesis

For client-created opaque HTML, the smallest provenance unit may be the exact array of top-level DOM nodes parsed for the contribution rather than a permanent DOM range marker.

Benefits:

- removing an owned top-level node retires its whole opaque subtree, including nested mutations;
- later sibling nodes inserted outside the contribution remain independent;
- a React-owned `<style>` inside DSIH can be removed while an externally appended sibling `<style>` survives;
- no permanent comment/template sentinel changes `body.innerHTML`.

Remaining gaps:

- empty DSIH has no physical node to act as a stable sibling edge;
- a stable nonempty contribution needs sibling discovery to return its first owned node;
- an empty contribution that later becomes nonempty must recompute its logical insertion edge from Fiber order;
- hydration still needs a server-to-client provenance protocol to identify the server-created top-level nodes;
- hidden/reappearing opaque owners need explicit retirement/restoration semantics.

## Current recommendation

For the next source experiment, prefer a **body-only opaque placement/contribution prototype** that reuses the historical reconciler concept but bypasses ordinary DSIH property writes.

Keep it experimental until it passes the PR 27 contract matrix plus Trusted Types, script parsing, custom-element timing, hydration provenance, and Suspense reappearance controls.

Do not revive the historical sparse singleton reset as the opaque cleanup mechanism.