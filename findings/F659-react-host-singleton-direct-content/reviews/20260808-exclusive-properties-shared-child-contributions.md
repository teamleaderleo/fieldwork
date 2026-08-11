# Body HostSingleton ownership — exclusive properties, shared child contributions

## Working model

The cleanest model found so far separates two kinds of ownership on the persistent `document.body`:

1. **singleton property/event ownership is exclusive** — one current HostSingleton Fiber owns body attributes, styles, event props, refs, and the DOM -> Fiber/props association;
2. **body child ownership is compositional** — multiple React subtrees, root-level body-scope siblings, external DOM, and hidden singleton owners may have distinct ordered child contributions in the same persistent body.

This model fits existing React behavior more closely than treating a visible `<body>` Fiber as owner of the entire physical body child list.

## Existing source already supports the managed-child half

`body` is intentionally not a singleton placement scope. Host children before `<html>`, descendants of `<body>`, and host children after `</html>` can all resolve into the same physical `document.body` in Fiber order.

Activity/Offscreen visibility handling also traverses **through** HostSingleton and hides the nearest HostComponent / HostText descendants.

For a managed body subtree, hiding therefore leaves its actual DOM nodes connected in `document.body` and applies the normal hidden state to those nodes. The HostSingleton disappear path separately releases the singleton's properties.

This is important: React's existing Activity semantics do not require hidden managed body descendants to be detached or reconstructed.

## Why the current DSIH writer breaks this model

A visible owner that acquires body with non-null `dangerouslySetInnerHTML` currently performs a whole-body `innerHTML` write.

That operation does not understand child contributions. It deletes:

- hidden managed nodes from another still-mounted Activity/Suspense owner;
- root-level body-scope siblings;
- third-party nodes;
- any other child contribution not encoded in the new DSIH string.

The later reappearance bug is therefore downstream of the writer's ownership error. The hidden Fiber has no Placement because its DOM node was supposed to remain mounted; the visible owner's whole-body write violated that assumption.

## Prevention instead of restoration

If body DSIH is changed to a contribution-aware writer:

- hidden managed owner A can keep its HostComponent/Text nodes connected and hidden;
- visible owner B can insert only B's opaque contribution at B's logical body slot;
- B's release removes only B's opaque nodes;
- A's reappearance reacquires singleton properties and normal Offscreen unhide restores A's already-connected managed nodes.

The exact same DOM node identity survives without synthesizing Placement or reconstructing A's subtree.

This is a materially cleaner target than trying to restore children after a whole-body wipe.

## Consequence for hidden descendant Placement

Earlier review correctly identified that a descendant Placement below an already-hidden singleton can currently mutate the same physical body while a different visible owner is active.

Under the current whole-body DSIH model, that is dangerous because the visible owner implicitly claims the entire child list.

Under a contribution-aware model, blanket suppression is no longer obviously correct.

Suppose hidden owner A precedes visible owner B in Fiber order. A new managed child can be placed into `document.body` **before B's contribution**, then hidden by normal Offscreen visibility handling. That is a valid update to A's own still-mounted hidden contribution, provided:

- host-sibling search can see B's opaque contribution as an ordering unit;
- A's placement does not mutate B-owned nodes;
- stale HostSingleton property updates are still rejected by the exclusive-owner guard.

So the long-term fix should make hidden placements ownership-aware and correctly ordered, rather than simply suppress every hidden descendant mutation.

## Opaque contribution representation

For body DSIH, the current best client-side representation remains two-part:

- **owned node provenance:** exact top-level DOM nodes produced by this Fiber's opaque write;
- **slot provenance:** an empty-capable logical position token, with a collapsed live DOM Range currently the strongest candidate.

The HostSingleton/contribution must also participate in host-sibling ordering so sibling placements can position relative to opaque content that has no child Fibers.

Historical insertion-edge work is useful precedent for this part of the reconciler design.

## Transition ordering

The contribution model also gives a precise transition order.

### Managed -> opaque

1. capture a live Range at the managed contribution's logical slot before child deletions;
2. normal mutation effects delete the old managed children;
3. parse/insert the new opaque contribution at the retained Range;
4. update only this Fiber's contribution metadata.

This preserves current custom-element lifecycle ordering: old React-owned nodes are retired before replacement custom elements connect.

### Opaque -> managed

1. retain the opaque contribution's Range;
2. retire only the old opaque owned nodes before replacement child Placement;
3. child Placement inserts managed nodes at the retained slot;
4. discard opaque node provenance while the normal managed Fiber tree becomes the contribution.

### Opaque -> opaque

1. retain the slot Range;
2. retire old opaque owned nodes;
3. parse/insert replacement nodes at that same slot.

No whole-body clearing is necessary.

## Activity with opaque DSIH needs one extra mechanism

Opaque DSIH descendants have no child Fibers, so ordinary `hideOrUnhideAllChildren()` cannot see or hide their top-level nodes.

A complete contribution implementation therefore needs explicit visibility handling for an **opaque contribution** when its owning Activity disappears/reappears.

Possible renderer behavior mirrors existing HostComponent/Text hide semantics on the contribution's top-level nodes:

- Elements: stash/restore display state and hide while inactive;
- Text nodes: stash/restore node value;
- Comments: already non-visible;
- nested content is hidden by its top-level element ancestor where applicable.

This preserves DOM connectedness better than detaching the contribution to a DocumentFragment, which would fire custom-element `disconnectedCallback` and diverge from normal Offscreen semantics.

This visibility hook must be associated with Activity disappear/reappear rather than ordinary permanent HostSingleton deletion.

## Property ownership still remains exclusive

Child contribution coexistence does not imply concurrent body attribute/event ownership.

When A hides and B acquires the persistent body:

- A's singleton properties are released;
- B becomes the DOM -> Fiber/props owner;
- hidden A host updates to body attributes/events must be ignored while B owns it;
- A may still update its hidden child contribution if those mutations are correctly routed/ordered.

The stale-owner guard experiment in React PR 41 is therefore complementary to the contribution model, not a competing approach.

## Server/hydration gap

Client-only node/Range provenance does not recover which server DOM nodes belong to a hydrated opaque body contribution.

A server-to-client range protocol is still required for matching hydration and preamble contributions. The simple PR 34 idea of moving arbitrary DSIH into the existing Suspense comment stream is rejected because raw author comments collide with React's control-comment namespace.

A future server range protocol must be collision-proof and should ideally hydrate into the same client contribution representation.

## Head/html boundary

This model is body-specific.

`head` has separate Hoistable/resource ownership, and `html` has hard persistent head/body identity constraints. Do not generalize this contribution protocol to head/html merely for tag symmetry.

## What this changes in prior review

- **Detached-child restoration:** still a valid current regression, but the preferred fix is now prevention via contribution-aware DSIH rather than synthetic restoration.
- **Hidden descendant Placement:** still a current conflict, but global suppression is no longer the preferred complete solution. Correct contribution ordering may make it valid.
- **Two Offscreen guards:** remain partial; the stale-owner property guard is cleaner for the exclusive singleton state subset.

## Disposition

**Promote this as the leading body ownership model for further research.**

A plausible complete body design is now:

1. exclusive current owner for singleton attributes/events/Fiber association;
2. ordered per-Fiber child contributions in the shared body scope;
3. opaque contributions represented by owned nodes + live slot Range;
4. HostSingleton/opaque contribution visible to host-sibling ordering;
5. retire-before-install transition ordering;
6. opaque visibility handling for Activity;
7. server/hydration provenance that instantiates the same contribution representation.

This is a design direction, not a source candidate yet.

## Evidence class

Current-source control-flow read plus synthesis across existing regressions and rejected experiments. No public upstream interaction performed.
