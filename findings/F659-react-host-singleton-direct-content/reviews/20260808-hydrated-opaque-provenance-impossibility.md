# Hydrated body opaque content — content matching cannot recover ownership

## Question

Can client hydration avoid a new server provenance protocol by parsing the current body's expected `dangerouslySetInnerHTML.__html` value and matching those parsed top-level nodes against the live `document.body` around the existing hydration cursor?

## Useful source fact

For a non-scoped `body` HostSingleton, hydration already retains the body-scope cursor rather than entering `body` as a separate child scope.

`claimHydratableSingleton()` resolves the persistent body and then calls `getFirstHydratableChildWithinSingleton(type, instance, nextHydratableInstance)`.

Because DOM `isSingletonScope('body')` is false, that helper returns the incoming `nextHydratableInstance` unchanged.

So when Fiber reaches a body singleton, React already knows the body's logical position relative to managed/root-level body-scope siblings.

The current gap is that body DSIH has no child Fibers, so it consumes zero DOM nodes from that cursor and records no owned child provenance.

## Tempting approach

1. Parse `props.dangerouslySetInnerHTML.__html` through a detached body element.
2. Compare the expected top-level parsed nodes with live body nodes around the hydration cursor.
3. Mark matching live nodes as this Fiber's opaque contribution.
4. Initialize the right-edge live Range after the claimed contribution.

This could work for pristine DOM and some simple outside insertions.

## Hard counterexample: indistinguishable duplicate insertion

Server output contains a body opaque contribution:

```html
<span class="x"></span>
```

Before React hydrates, an extension/script inserts an **identical** node immediately before the server-owned node:

```html
<span class="x"></span> <!-- outside -->
<span class="x"></span> <!-- server-owned -->
```

Both nodes have the same:

- tag name;
- attributes;
- child structure;
- `outerHTML`;
- `isEqualNode()` result;
- parser-normalized representation.

The React Fiber tree and body-scope hydration cursor know the logical slot but contain no server node identity token saying which identical DOM node came from the DSIH serialization.

A content matcher that chooses the first identical node can claim the outside node as React-owned. On a later React update/release it deletes that outside node and leaves the actual server-rendered DSIH node stale.

Choosing the last identical node merely reverses the counterexample: outside code can insert the duplicate after the server-owned node.

A subsequence matcher that tolerates interstitial outside nodes has the same ambiguity when expected nodes repeat or when outside code duplicates one expected node exactly.

## Consequence

**DOM content alone cannot provide the provenance required for destructive future cleanup.**

This is an identity problem, not a better-diff-algorithm problem.

The client expected DSIH value is useful for validation/mismatch diagnostics, but it cannot safely grant ownership authority over live nodes after arbitrary pre-hydration mutation.

Current `diffHydratedGenericElement` already normalizes and compares DSIH using the singleton's `innerHTML`; that is warning/validation information, not provenance.

## What the hydration cursor can still provide

The cursor remains valuable as a **slot anchor** for a server-carried contribution identity.

A future protocol can use:

- the existing body-scope cursor to place/validate the contribution relative to surrounding managed Fibers;
- server/runtime provenance to identify the exact owned DOM nodes;
- the client contribution representation (owned top-level nodes + right-edge live Range) after hydration commits.

So the cursor reduces how much the server protocol must encode: it need not describe global body ordering from scratch.

## Required server/runtime property

A complete solution needs a provenance signal that survives parsing and cannot be confused with arbitrary outside DOM purely by content equality.

Possible protocol families still under research:

- paired internal range markers around the preamble DSIH contribution, with a contribution-specific identity;
- a Fizz/runtime step that converts temporary parser markers into client-side ownership metadata before hydration;
- another server-carried range representation that identifies the exact contribution boundaries without placing arbitrary DSIH inside React's existing Suspense control-comment stream.

The simple PR 34 stream split is rejected because raw DSIH comments collide with the boundary scanner's `$`/`/$`/`html`/`head`/`body` control namespace.

## Security / compatibility note

This is primarily a correctness/interoperability problem. `dangerouslySetInnerHTML` already represents trusted application markup, but third-party scripts/extensions can mutate the parsed DOM before hydration. A provenance protocol should be robust to ordinary accidental collisions and outside insertions; do not rely on content uniqueness.

## Disposition

**REJECT content-only hydration ownership recovery.**

Keep expected-DOM parsing as a validation tool, not as the source of destructive ownership authority.

## Evidence class

Current React hydration source-read plus identity counterexample. No public upstream interaction performed.
