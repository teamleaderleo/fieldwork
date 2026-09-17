# Opaque body contribution visibility under Activity/Suspense

## Question

If body DSIH becomes a per-Fiber child contribution instead of a whole-body property write, how can an owning Activity/Suspense primary hide that opaque contribution when DSIH has no child Fibers for normal Offscreen traversal?

## Existing React precedent

React DOM already has two connected-node visibility mechanisms.

### Managed HostComponent / HostText

`hideInstance()` applies `display: none !important` to the element.

`hideTextInstance()` clears the Text node value.

Unhide uses the React props/text value to restore the visible state.

These nodes remain physically connected; React does not detach the subtree merely to hide it.

### Dehydrated Suspense/Activity boundary payload

`hideOrUnhideDehydratedBoundary()` walks the top-level DOM inside the serialized boundary while tracking nested boundary depth.

For top-level Elements it stashes the element's current display value and sets `display: none`.

For Text nodes it stashes the node value and clears it.

On unhide it restores those stashed values.

Again, the payload stays connected.

This is a close precedent for opaque DSIH: a DOM payload with no ordinary child Fibers still has explicit visibility handling.

## Opaque contribution state has enough information

The leading client representation already stores:

- exact top-level nodes produced by the opaque write;
- the Fiber-owned body slot Range;
- contribution mode/state.

So a renderer hook can hide only this contribution's owned top-level nodes.

Conceptual opaque visibility snapshot:

```text
Element -> previous inline display value + priority if needed
Text    -> previous nodeValue
Comment -> no visual state
```

Then:

### Hide

- Element: set display none using the same semantics as normal HostComponent hiding;
- Text: set nodeValue to empty string;
- Comment: leave in place;
- do not remove/reinsert any node.

### Unhide

- Element: restore the exact previously stashed inline display state;
- Text: restore the stashed value;
- Comment: no-op.

The snapshot should live in the Fiber-owned singleton contribution state rather than ad-hoc DOM expandos when possible.

## Why connectedness matters

Detaching opaque nodes to a DocumentFragment would fire custom-element `disconnectedCallback`, potentially unload/reload iframe/media/resource state, and diverge sharply from existing Offscreen semantics.

Display/text hiding preserves connectedness and aligns with React's managed/dehydrated hidden-tree behavior.

This is particularly valuable for the earlier detached-child problem: hidden primary contributions can remain physically present rather than being erased and later reconstructed.

## Top-level styles/scripts/resources

Some raw DSIH elements are non-visual or have behavior independent of CSS display:

- `<style>` rules can remain active even if the style element itself has `display:none`;
- stylesheet links can remain active;
- scripts created by client `innerHTML` remain inert under the existing DSIH semantics;
- server scripts may already have executed before hydration.

This is not obviously inconsistent with React's current hidden-tree behavior: managed Hoistables/resources have their own lifecycle and are not simply equivalent to visual HostComponents.

Before promotion, add explicit policy/regressions for opaque style/link/script content under hidden Activity if React wants stronger semantics than “hide visible DOM while preserving connected resource effects.”

Do not solve that question by detaching the whole contribution.

## Mutation-phase integration

Opaque contribution visibility belongs with Offscreen/Activity mutation visibility, not with HostSingleton property release in layout.

When Activity hides:

1. mutation phase hides managed descendants and the opaque contribution payload;
2. layout disappear releases exclusive body singleton properties/events;
3. contribution remains in its Fiber-owned body slot.

When Activity reappears:

1. mutation phase unhides the contribution;
2. layout reappearance reacquires exclusive singleton properties;
3. layout effects run against already-connected visible descendants.

If exact ordering between unhide and singleton acquisition matters for layout/style observation, reuse the existing HostSingleton TODO analysis rather than moving child contribution deletion back into release.

## Hidden opaque updates

A hidden opaque owner can update its own DSIH contribution while another owner has exclusive body properties.

Preferred sequence:

1. retain the hidden body's slot Range;
2. retire old hidden opaque owned nodes;
3. parse/insert replacement opaque nodes into that same slot;
4. immediately apply hidden visibility snapshot to the replacement top-level nodes;
5. leave the visible owner's body attributes/events untouched through the stale-owner property guard.

This is the opaque counterpart to allowing managed hidden descendant Placement into its own hidden contribution.

## Server/hydration

A guarded server opaque contribution can use the same visibility concept once hydration has established contribution ownership/state.

Before hydration commits, dehydrated boundary hiding already knows how to hide serialized boundary DOM. After conversion to Fiber-owned contribution state, use the opaque contribution hook instead.

## Host-config shape

A complete body slot API may need renderer hooks conceptually like:

```text
hideSingletonContribution(state)
unhideSingletonContribution(state)
```

The generic reconciler invokes them for HostSingleton contribution state when traversing a hidden/reappearing Offscreen subtree.

Renderers without singleton contribution semantics can use no-op shims.

## Disposition

**FEASIBLE / NOT A FUNDAMENTAL BLOCKER.**

Opaque Activity visibility can reuse React's existing connected hide/unhide model. The remaining design work is API placement and explicit resource/style behavior, not basic DOM feasibility.
