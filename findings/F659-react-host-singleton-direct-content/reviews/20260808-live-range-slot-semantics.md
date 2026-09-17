# Body opaque ownership — live Range slot semantics

## Question

Can an in-memory live DOM `Range` represent the logical position of a body opaque contribution even when `dangerouslySetInnerHTML` produces zero top-level nodes?

## Standards result

**Yes, as a position token, with a deterministic boundary policy. A collapsed Range at the contribution's right edge is preferable to the earlier left-edge idea.**

The DOM Standard's insertion algorithm updates a live range boundary in a parent only when that boundary's offset is **greater than** the reference child's index. Equality does not shift it.

For append-before-null, the reference-child offset adjustment does not run.

The removal algorithm decreases a parent boundary offset when the boundary is greater than the removed node's index.

These rules make a live Range useful for remembering a child-list position while outside code mutates siblings.

## Why the earlier left-edge model is insufficient

A collapsed Range before the first React-owned opaque node solves the empty-at-end example, but it has an undesirable nonempty edge case.

Suppose the contribution begins with owned node A and the Range sits immediately before A. If outside code later calls `insertBefore(X, A)`, insertion occurs at exactly the Range offset, so the Range does not move. The Range now sits before X.

On React's next opaque replacement, inserting at that left Range would place the new React content before X. The outside node that was deliberately inserted **before the old React content** would migrate to the other side of the replacement.

That is a poor default preservation rule.

## Prefer a right-edge Range

For a contribution whose owned top-level nodes end immediately before some outside node R, store the collapsed Range **after the owned contribution / before R**.

If the contribution is at the end of body, store the Range at `(body, body.childNodes.length)`.

This behaves better for ordinary outside insertions.

### Outside insertion before the contribution

If outside code inserts before an owned node, that insertion index is less than the right-edge Range offset. The live Range shifts right with the insertion and therefore remains after the React contribution.

When React later removes its owned nodes, the Range shifts left appropriately but remains after the outside node. Replacement inserted at the captured right edge stays **after** the outside-before node.

### Outside insertion after the contribution

If outside code inserts at the exact right edge — for example before R, or appends when the Range is at body end — equality means the Range does not shift.

The new outside node therefore lands to the **right** of React's remembered slot. A later replacement inserted at the slot stays before that outside-after node.

This gives the intuitive behavior for the two common adjacency cases:

- insert before React -> remains before React after replacement;
- insert after React -> remains after React after replacement.

## Empty-at-end example still works

Suppose body has `N` children and React owns an empty opaque contribution at the logical end.

The right edge and left edge are the same collapsed point: `(body, N)`.

If outside code later appends a node:

- append occurs before `null`;
- the Range remains at offset `N`;
- body length becomes `N + 1`;
- the Range is now immediately before the newly appended outside node.

So empty -> managed or empty -> nonempty still returns to React's old logical slot rather than jumping after the later append.

## Interstitial outside nodes remain a policy question, but do not require per-gap identity mapping

If outside code inserts a node **between two React-owned top-level opaque nodes**, no single boundary can preserve a meaningful one-to-one gap when the next DSIH string may contain a completely different number/kind of top-level nodes.

Ownership must still preserve that outside node, but replacement policy has to choose which side of the new opaque contribution it lands on.

A right-edge policy naturally leaves surviving interstitial outside nodes before the replacement after old owned nodes are removed. A left-edge policy would put them after the replacement.

Neither can infer author intent from arbitrary replacement markup.

However, the original HostSingleton contract helps bound what must be preserved. Its key constraint says Head and Body must never reposition, reorder, or otherwise alter the placement of style-related nodes **outside React**. The core interoperability concern was physically unmounting/reinserting those outside stylesheet/style nodes and triggering reload/unload behavior.

A right-edge opaque replacement can satisfy that ownership constraint without inventing a mapping from old opaque nodes to new opaque nodes:

- remove only React-owned old opaque nodes;
- leave an interstitial external style node physically attached where it is;
- insert the new React-owned fragment on the chosen side of that surviving node.

The external node's sibling index may change as React-owned nodes disappear/appear, but React never removes, reinserts, or directly moves that outside node itself.

This is a plausible reading of the founding invariant, not a fully specified cascade-order guarantee. Keep an explicit regression for an interstitial external style node and document which side of replacement content it remains on.

Do not add per-gap mutation tracking unless a stronger compatibility requirement demands it.

## Ownership versus position

The Range must **not** define which DOM nodes React owns.

Ownership remains explicit, e.g. the exact top-level nodes produced by the opaque write. Otherwise an outside node inserted between React-owned nodes could accidentally become part of a range-based delete operation.

The useful split remains:

- **node provenance:** exact React-produced top-level nodes;
- **slot provenance:** one collapsed live right-edge Range.

## Replacement mechanics

Do not use `Range.insertNode()` as the primary insertion primitive. Its collapsed-range semantics expand the Range around the inserted node, which is different bookkeeping from what the contribution model needs.

Instead:

1. derive a fixed `before` node from `range.startContainer.childNodes[range.startOffset]` (or `null` at end);
2. retire old React-owned nodes;
3. insert a parsed `DocumentFragment` once before that fixed node, preserving fragment child order;
4. re-establish the collapsed Range **after the newly inserted opaque contribution / before the same outside right anchor**.

Using a single fragment insertion also avoids reversing nodes when multiple parsed top-level nodes are installed at one slot.

### Opaque -> managed

Before removing the opaque contribution, snapshot the right-hand `before` node from the Range. Retire opaque owned nodes, then make replacement child Placements use that fixed `before` node for the transition commit. Once the tree becomes managed, opaque Range metadata can be discarded.

### Managed -> opaque

Capture a right-edge Range after the managed contribution before child deletions. Normal mutation effects retire the old managed children. Then insert the new opaque fragment at the remembered right edge and reset the Range after the new owned nodes.

### Opaque -> opaque

Keep the right edge, retire only old owned nodes, insert replacement fragment before the fixed right anchor, then reset the Range after the new contribution.

This preserves the retire-before-install lifecycle ordering required for custom elements.

## Activity relevance

The Range model fits the stronger body ownership synthesis: hidden managed contributions can remain connected and hidden while another owner's opaque contribution occupies a separate ordered slot.

For opaque contributions owned by a hidden Activity, additional explicit hide/unhide bookkeeping is still required because DSIH nodes have no child Fibers for normal Offscreen traversal.

## Server/hydration relevance

A live Range solves only client position tracking. Hydrated server DSIH still needs a collision-proof provenance protocol that identifies its owned nodes and initial right edge.

The rejected PR 34 direct-stream experiment cannot provide that because arbitrary DSIH comments collide with React's boundary-control comment namespace.

## Cost / risk

Live ranges are updated by DOM tree mutations, and the DOM Standard notes the maintenance cost. HostSingleton count is tiny, but this should still be measured/reviewed before promotion.

## Disposition

**Retain a collapsed right-edge live Range as the leading client slot primitive. Reject the earlier left-edge recommendation for nonempty contributions.**

This strengthens the placement/contribution direction but does not make PR 32 promotable. PR 32 still lacks Range state, correct replacement order, hydration provenance, opaque Activity visibility, and explicit interstitial-node policy.

## Evidence class

Standards-read against the current DOM Standard plus React source/control-flow analysis and the original HostSingleton contract. No public upstream interaction performed.
