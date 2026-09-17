## In simple words

Tracking the top-level DOM nodes produced by body `dangerouslySetInnerHTML` is useful provenance for non-empty content, but it cannot represent an empty opaque contribution.

`dangerouslySetInnerHTML={{__html: ''}}` still establishes a logical body-content slot. If an outside system inserts a sibling after that empty contribution and React later changes the contribution to managed or non-empty opaque content, React needs to insert at the original slot rather than after the later outside node.

With zero produced nodes there is no physical owned node that can serve as the insertion edge.

## Counterexamples

### Empty opaque -> managed

1. render an empty body DSIH contribution;
2. an outside script appends a style node to body;
3. update body to a managed `<span>`;
4. expected order is `[managed span, outside style]` because the outside node was appended after React's existing empty slot.

A design that stores only the contribution's produced nodes has an empty node list. Ordinary sibling discovery reaches the end of body and appends the managed child after the outside style, reversing the logical order.

### Empty opaque -> non-empty opaque

The same sequence with a later non-empty DSIH update should produce `[new opaque node, outside style]`.

A node-list-only design has no old first node to insert before and therefore appends the new opaque contribution after the outside style.

## Consequence

A complete body opaque contribution needs two separate pieces of state:

1. **provenance:** which top-level DOM nodes belong to this contribution;
2. **position:** an insertion token that remains meaningful even when the contribution has zero nodes.

Permanent DOM comments could supply the token but would become observable through `childNodes` / `innerHTML`.

A live DOM `Range` is worth investigating specifically as the invisible position token. Live ranges update boundary offsets as surrounding DOM is mutated and can represent a collapsed zero-node position. The exact mutation-at-boundary behavior still needs browser-level proof before relying on it.

## Verifier

React PR 27 now carries two source-free red-baseline controls:

- `keeps the empty direct HTML slot before a later outside node when becoming managed`;
- `keeps the empty direct HTML slot before a later outside node when becoming nonempty`.

React PR 32 intentionally requires both controls to remain red. That experiment tests top-level node provenance and placement for non-empty client contributions only; it is not accepted as a complete body design.

## Decision

**REQUIRE AN EMPTY-CAPABLE POSITION TOKEN.**

Keep the top-level-node contribution prototype because it can still validate the non-empty ownership/placement half. Do not promote it until an invisible empty-slot representation and hydration provenance are both solved.