# Empty body slot — Range position needs Fiber affinity

## Correction / refinement

A collapsed live DOM Range can remember an empty body HostSingleton slot across outside DOM mutations, but **Range gravity alone cannot represent both logical sides of an empty Fiber position**.

The reconciler must combine:

- DOM Range position;
- Fiber ordering/affinity.

## Counterexample

Suppose body contribution A is currently empty and its collapsed Range sits at DOM child offset `i`.

A later Fiber placement can target the exact same physical DOM offset while being logically either:

1. before body A; or
2. after body A.

DOM has no node representing A, so both insertions are `insertBefore(child, childNodes[i])`.

The DOM Range insertion rule uses a strict `offset > insertionIndex` adjustment. If insertion occurs at exactly `i`, the Range does not move.

That native behavior means the Range stays **before** the newly inserted node.

This is correct when the new Fiber belongs **after** empty body A.

It is wrong when the new Fiber belongs **before** body A: after insertion, A's virtual slot should be after the newly inserted subtree.

## React already has a virtual-position precedent

Empty Fragment refs solve a closely related problem.

`compareDocumentPositionForEmptyFragment()` cannot compare a physical Fragment node because none exists. Instead it:

- inspects the parent host instance;
- asks Fiber reflection for the next sibling host Fiber;
- derives whether an external node is preceding/following the empty Fragment from that Fiber sibling position;
- marks the result implementation-specific.

This proves React already accepts the idea that an empty Fiber-owned position needs **Fiber-order semantics in addition to physical DOM state**.

## Body slot rule

For an empty body HostSingleton slot:

- the live Range remembers the current physical offset relative to outside DOM;
- Fiber host-sibling search determines whether a new placement is logically before or after that body Fiber;
- when an insertion occurs at the Range's exact DOM offset **before** the body Fiber, React must manually move/reset the body Range to the right side of the newly inserted host subtree;
- when an insertion occurs at the exact offset **after** the body Fiber, leave the Range on its native left-sticky side.

This gives the Range an explicit Fiber affinity.

## Non-empty body contribution

When the body contribution has connected managed or opaque nodes, its physical right edge usually disambiguates ordinary before/after placements.

The explicit affinity rule is most important when:

- body content is empty;
- all managed/opaque nodes were just deleted;
- a transition temporarily has zero physical contribution nodes;
- outside code has inserted nodes at the same remembered boundary.

## Placement API consequence

A plain `getHostSibling(): ?Instance` return value may be too weak for this body-specific case because it carries only a DOM anchor.

Possible implementation families:

### Virtual sibling result

Return/propagate an internal placement descriptor containing:

- physical `before` node;
- optional body-slot Fiber whose empty position is being crossed;
- side/affinity information.

After insertion, placement code updates affected body slot Range(s).

### Body-slot side effect during sibling search

Keep the current return type but record that host-sibling search crossed an empty body slot and whether the inserted Fiber precedes/follows it. Placement then resets the relevant Range after mutation.

This is more implicit and therefore less attractive for reviewability.

### Recompute affected slot(s) from Fiber order after placement

After a root/body-scope placement, recompute the empty body Range using:

- next stable Fiber sibling position;
- surviving outside DOM anchor remembered by the previous Range.

This may be simpler initially but needs care not to move outside nodes.

## Multiple body slots

Suspense/Activity overlap can produce multiple body HostSingleton Fibers sharing physical `document.body`.

Each slot Range has its own Fiber position. A placement may cross more than one empty slot in theory.

Do not model body position as one global `document.body` insertion edge. Slot state is per HostSingleton Fiber.

## Server mirror

Fizz does not have live DOM Ranges while rendering, but Fiber/server tree order already supplies the affinity side.

The guarded opaque protocol serializes physical contribution guards at the proper segment position; matching hydration then reconstructs the client Range + Fiber-affinity model.

## Disposition

**RETAIN Range + Fiber affinity.**

This fixes a real weakness in the earlier “Range alone is the body slot” description without requiring permanent client comment markers.

The existing empty Fragment positioning code is the strongest in-tree precedent for this kind of virtual host position.
