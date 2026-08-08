# Server body DSIH provenance — exact preservation requires an explicit policy

## Question

Can passive server markup plus client hydration both:

1. identify exactly which body DOM nodes came from server-rendered DSIH; and
2. preserve every third-party/outside node inserted anywhere in `document.body` before hydration?

## Conclusion

**Not from post-mutation DOM state alone.**

If HostSingleton keeps the strong founding invariant that outside style-related nodes must never be removed/reinserted/reordered by React regardless of where they appear in body, then a complete SSR opaque-content protocol needs provenance established before arbitrary outside mutation occurs.

Otherwise React must explicitly define a weaker DSIH-slot policy.

## Why a passive range is insufficient

Suppose server body DSIH produces:

```html
<!--react-start-->
<span>A</span>
<span>B</span>
<!--react-end-->
```

Before hydration, a third-party script or extension inserts:

```html
<style data-third-party></style>
```

between A and B.

At hydration time, passive start/end markers tell React the opaque slot boundaries, but not which nodes inside that slot were produced by the server.

The live DOM now contains three top-level nodes inside the range. Nothing in ordinary DOM identity/content says which two existed in server output and which one was inserted afterward.

A later opaque update that clears every node inside the passive range deletes the third-party style.

A matcher cannot reliably recover origin if outside code duplicates/moves equivalent nodes; the separate identical-node counterexample already proves content equality is not provenance.

## Strong HostSingleton reading

The original HostSingleton design explicitly says Head and Body should never reposition, reorder, or otherwise alter placement of style-related nodes outside React.

Under the strongest reading, a third-party style inserted between React-owned opaque nodes is still a node outside React and must survive.

If that invariant applies to DSIH too, passive boundary markers are not enough.

React needs one of these stronger families:

### Early runtime provenance

Mark the actual parser-created opaque nodes before later outside code can interleave new nodes, e.g. through runtime bookkeeping/expandos tied to Fizz output.

This has CSP, script-order, no-JS, external-runtime, and streaming costs and needs careful review.

### Parser-level provenance representation

Use a representation where the browser/parser itself preserves origin information for each opaque top-level node without changing user-observable DSIH semantics.

No existing browser primitive has been found that supplies this directly.

### Server-side parsing/tokenization

Parse the DSIH string on the server sufficiently to emit per-node ownership metadata.

This would add a major HTML-parser compatibility burden to React's server renderer and is not currently attractive.

## Weaker opaque-slot reading

React could instead specify that a body DSIH contribution owns a contiguous slot, analogous to ordinary `element.innerHTML` ownership.

Under that policy:

- nodes inserted **outside** the opaque slot are preserved;
- nodes inserted **inside** the opaque slot may be replaced on the next React DSIH update/release, regardless of origin.

Then passive start/end range provenance is enough for ownership, and the right-edge Range model becomes simpler.

This is a meaningful weakening of the strongest HostSingleton interoperability invariant and should be an explicit compatibility/product decision, not an accidental implementation consequence.

## Current evidence does not settle the policy

- Original HostSingleton tests strongly protect third-party stylesheet/style identity and placement.
- Historical insertion-edge research cared about outside nodes interleaved with React-managed children.
- 2026 DSIH lifecycle tests establish body DSIH support but do not insert outside child nodes inside the DSIH-owned region.
- PR 37112 discussion does not state an explicit child-list policy for third-party nodes added while DSIH is active.

Therefore Fieldwork should continue using adversarial outside-child tests to expose the choice, but should not claim the strong or weak policy is already publicly specified.

## Client-only distinction

For client-created DSIH, React can record the exact top-level nodes it inserted at write time. Exact provenance is therefore feasible without weakening policy.

The ambiguity is specifically server/hydration after outside mutation has already occurred.

This suggests a potentially asymmetric implementation:

- client writes: exact node provenance + right-edge slot Range;
- hydrated server writes: exact provenance only if a stronger Fizz/runtime protocol exists; otherwise require an explicit slot-ownership policy.

Do not silently give hydrated DSIH weaker outside-node guarantees than client-created DSIH without documenting/testing that difference.

## Disposition

**PRODUCT-POLICY FORK / HARD SERVER REQUIREMENT.**

No amount of content matching closes this gap. Before a complete SSR body-DISIH repair is promoted, decide whether DSIH inherits the strong HostSingleton outside-node invariant inside its slot or owns the slot like ordinary `innerHTML`.

## Evidence class

Original public HostSingleton contract + DOM identity counterexamples + current server/hydration source analysis. No public upstream interaction performed.
