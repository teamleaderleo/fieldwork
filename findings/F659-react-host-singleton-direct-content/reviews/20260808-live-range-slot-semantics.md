# Body opaque ownership — live Range slot semantics

## Question

Can an in-memory live DOM `Range` represent the logical position of a body opaque contribution even when `dangerouslySetInnerHTML` produces zero top-level nodes?

## Standards result

**Yes, as a position token, with a deterministic boundary policy.**

The DOM Standard's insertion algorithm updates a live range boundary in a parent only when that boundary's offset is **greater than** the reference child's index. Equality does not shift it.

For append-before-null, the insertion algorithm does not run that reference-child offset adjustment at all.

The removal algorithm decreases a parent boundary offset when the boundary is greater than the removed node's index.

These rules give a collapsed Range useful left-sticky behavior.

## Empty-at-end example

Suppose body has `N` children and React owns an empty opaque contribution at the logical end.

Store a collapsed range at `(body, N)`.

If outside code later appends a node:

- the append occurs before `null`;
- the Range remains at offset `N`;
- the body length becomes `N + 1`;
- the Range is now immediately **before** the newly appended outside node.

So a later empty -> managed or empty -> nonempty transition can still insert at React's old logical slot instead of jumping after the outside append.

## Insertions before the slot

If outside code inserts before a child whose index is less than the Range offset, the Range offset increases with the insertion. It therefore continues pointing at the same logical place relative to the pre-existing content.

## Insertions exactly at the slot

If outside code inserts before the child currently at the exact Range offset, the Range does not shift because the update condition is `offset > child.index`, not `>=`.

That means the new outside node lands after the conceptual React slot.

A live Range cannot infer whether outside code intended that exact-boundary insertion to mean "before React" or "inside/after React". A repair using this primitive must choose and document a deterministic policy. Left-sticky behavior naturally gives exact-boundary outside insertions to the **right** of React's slot.

## Ownership versus position

The Range should not define which DOM nodes React owns.

Ownership should remain explicit, e.g. a list/set of top-level nodes produced by the opaque write. Otherwise an outside node inserted between React-owned top-level nodes could become accidentally included in a range-based delete operation.

The useful split is therefore:

- **node provenance:** exact React-produced top-level nodes;
- **slot provenance:** one collapsed live Range.

## Replacement order

The Range also allows the corrected lifecycle order identified separately:

1. retain the collapsed slot Range;
2. remove previous React-owned nodes;
3. insert the replacement at the Range boundary.

For insertion, avoid `Range.insertNode()` if the intent is to keep the Range collapsed and left-sticky: the Range algorithm expands a collapsed range's end after insertion. Instead, derive the reference child from `range.startContainer/startOffset` and insert a `DocumentFragment` with the ordinary DOM insertion operation. The live Range remains at the left edge because its offset equals the insertion index.

## Hide / reappear

A per-Fiber Range is also potentially useful across singleton release/reacquire:

- release can remove the owned nodes while leaving the Range state associated with the still-retained hidden Fiber;
- reappearance can reconstitute opaque nodes at the remembered slot;
- if the Fiber is permanently deleted, a WeakMap keyed by the Fiber/alternate pair can let the Range state become collectible without a DOM marker.

This does not by itself solve commit-phase timing or stale-owner singleton mutations.

## Cost / risk

Live ranges are updated by DOM tree mutations, and the DOM Standard explicitly notes that maintaining them has mutation-time cost. The expected HostSingleton count is tiny, but this should still be measured/reviewed before promotion.

## Disposition

**Retain as a viable body-slot primitive.**

This raises confidence in the placement-unit direction but does not rescue the current PR 32 implementation. PR 32 still has wrong replacement ordering, no empty Range state, hydration provenance gaps, and hide/reappear work.

## Evidence class

Standards-read against the current DOM Standard plus React source-read. No public upstream interaction performed.
