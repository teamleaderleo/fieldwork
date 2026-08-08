## In simple words

Fizz preamble contribution cleanup needs three independent ownership channels:

1. **singleton property ownership** for attributes/style state moved into the document preamble;
2. **opaque child ownership** when a boundary-contributed body uses `dangerouslySetInnerHTML`;
3. **current singleton Fiber/props ownership** so retiring an old server contribution does not detach the client HostSingleton that now owns the same persistent DOM node.

The opaque child problem has a promising small split: keep boundary body DSIH in the boundary stream after the existing body contribution marker instead of moving it into root `bodyChunks`. That lets existing Suspense boundary deletion own the raw DOM. React draft PR 34 tests this server-only experiment.

Property cleanup still needs marker metadata because the persistent singleton attributes live outside the boundary DOM range.

## Current source behavior

For a singleton in a boundary preamble:

- `pushStartBody()` writes `<!--body-->` into the boundary target;
- the actual `<body ...>` start tag is serialized into `preamble.bodyChunks`;
- `pushStartSingletonElement()` serializes explicit props with `pushAttribute()` and generated ViewTransition attributes with `pushViewTransitionAttributes()`;
- current `clearSingletonPreambleContribution()` receives only the persistent DOM element, clears every attribute, calls `detachDeletedInstance(instance)`, and therefore has no way to distinguish the old server contribution from a client HostSingleton that may already be bound to the persistent element.

The checked-in source TODO already states that the marker identifies the singleton but does not carry enough contributed-property information to preserve imperative state.

## Current-owner association gap

HostSingleton hydration makes this more than an attribute problem.

`prepareToHydrateHostInstance()` runs during complete work and calls the DOM host config's `hydrateInstance()`. `hydrateInstance()` immediately calls both:

- `precacheFiberNode(internalInstanceHandle, instance)`;
- `updateFiberProps(instance, props)`.

So by the time mutation commit later clears a nested dehydrated Suspense boundary, the persistent `body` / `head` / `html` node can already be associated with the **current client HostSingleton Fiber and props**.

If that boundary contains a preamble contribution marker, current `clearSingletonPreambleContribution()` ends by calling `detachDeletedInstance(instance)`. That deletion is not scoped to an old server owner; it removes whatever Fiber/props association is currently on the persistent node.

A correct preamble cleanup protocol must therefore preserve a current client owner association when retiring the old boundary contribution.

React PR 29 now includes a public-API control: after a synthetic body preamble marker is cleared and the boundary client-renders a replacement button, a bubbling click must still invoke the current body's React `onClick` prop. This exercises the props/Fiber association through normal event dispatch rather than inspecting private maps directly.

Do **not** assume unconditional `detachDeletedInstance()` remains correct after attribute metadata is added.

## Descriptor requirements

A useful marker descriptor should carry ownership metadata only; arbitrary prop values are unnecessary and should stay out of comment payloads.

### Explicit emitted props

Inside `pushStartSingletonElement`, the server can determine whether an explicit prop actually serialized by recording `target.length` before and after `pushAttribute()`.

If the chunk count did not change, that prop produced no server attribute and must not be claimed by the contribution. This naturally excludes ignored event handlers, null values, invalid value types, and other serializer no-ops.

Store the React prop key, not the rendered value. The client can then reuse React's existing property-clearing semantics where that path is safe instead of maintaining a second complete alias/namespaced-property table.

### Style

`style` needs per-property ownership.

The server should record only style keys that actually emitted CSS. `pushStyleAttribute()` skips properties whose values are null, boolean, or empty string; claiming one of those skipped keys would allow cleanup to erase a later imperative style value that React never emitted.

The client can reconstruct a minimal previous style object containing only those keys and use the existing style clearing path. Values can be inert sentinels because style cleanup depends on previous keys, not on reproducing the serialized CSS values.

### Props whose previous value kind matters

Before source work, audit every singleton-relevant `setProp` branch that inspects `prevValue` rather than only the prop key.

Known categories to treat deliberately include:

- `style` — needs previous keys;
- function-valued `action` / `formAction` — previous type can affect cleanup of generated form state;
- `is` — client update has development-only previous-value behavior;
- `autoFocus` — ordinary client property updates intentionally do not manipulate the attribute, so server-contribution cleanup may require direct attribute removal if it can appear on a singleton.

The descriptor may need a tiny value-kind tag for these cases, or the cleanup path can special-case the small set that cannot be reconstructed safely.

### Generated ViewTransition attributes

Singleton serialization also calls `pushViewTransitionAttributes()`.

These `vt-*` attributes are generated from `FormatContext`; they do not correspond one-for-one with explicit element props and therefore will not be discovered by wrapping `pushAttribute()`.

A complete descriptor must record every generated ViewTransition attribute that was emitted by the contribution and remove only those slots during cleanup.

Do not leave them out merely because the initial gated regression uses `data-*` attributes.

## Marker encoding

Use a versioned encoding that is provably safe inside an HTML comment.

Working requirements:

- old bare `<!--html-->`, `<!--head-->`, and `<!--body-->` markers remain parseable for older server output;
- new markers identify singleton type plus descriptor version;
- payload contains names/kinds only, no arbitrary attribute or HTML values;
- the serialized comment data can never contain `--` or terminate the comment;
- malformed or unknown-version payloads fail safely and predictably rather than partially clearing guessed state.

A prior note suggested ordinary percent-encoded JSON. That is insufficient as stated: JavaScript's `encodeURIComponent()` leaves `-` unescaped, so payload strings can still contain consecutive hyphens.

Viable experiment encodings include:

- JSON whose serialized output is post-processed so every literal `-` becomes the JSON escape `\u002d` (and other chosen delimiter-sensitive characters are escaped deliberately);
- another compact alphabet that entirely excludes `-` and other comment-dangerous sequences.

The important requirement is a proof about the emitted alphabet, not a preference for a particular codec.

Conceptual payload, not a committed wire format:

```text
body:v1:<comment-safe descriptor bytes>
```

## Client cleanup direction

For a new descriptor marker:

1. reconstruct the minimal previous-props ownership packet from explicit prop keys and style keys;
2. reuse the normal singleton property clear path where its previous-value semantics are adequate;
3. directly clear generated `vt-*` attributes;
4. special-case the audited server-emitted props whose client update semantics cannot remove the serialized attribute correctly;
5. preserve any current client HostSingleton Fiber/props association on the persistent DOM node instead of unconditionally detaching it.

Exactly how to distinguish a stale association from a current client owner remains a reconciler/host ownership question. The stale-owner work in React PR 41 demonstrates that React already has a useful DOM -> Fiber ownership signal, but #708 should establish its own lifecycle contract before sharing an implementation helper.

For an old bare marker, preserve deterministic compatibility behavior unless policy explicitly changes it. Old streamed HTML cannot retroactively contain ownership metadata, so the legacy path may necessarily remain broader; that limitation should be documented rather than hidden.

## Opaque child split

Do not encode raw DSIH values or arbitrary child fingerprints into this property descriptor.

Source review found a smaller body-only mechanism:

- the body start tag and attributes remain in `preamble.bodyChunks`;
- the existing `<!--body-->` marker remains in the Suspense boundary target;
- if the boundary-contributed body has DSIH, emit those raw bytes into the boundary target after the marker instead of `bodyChunks`;
- existing Suspense boundary removal can then retire the opaque DOM naturally.

This is React PR 34's experiment. If it passes the focused Fizz regression while attribute/association controls remain red, child ownership and property/current-owner ownership can be repaired independently.

Head/html are intentionally excluded from that body DSIH split because their parser/resource/document semantics differ.

## Rejected shortcuts retained

1. **Clear every attribute.** Already erases later imperative state.
2. **Read current HostSingleton Fiber props and treat them as the old server contribution.** The marker describes an older server boundary contribution; current client props can differ.
3. **Unconditionally detach the singleton after marker cleanup.** Hydration may already have bound the persistent DOM node to the current client HostSingleton.
4. **Record only attribute names and clear the whole style attribute.** This erases later imperative style properties.
5. **Record every input style key.** Keys skipped by the server serializer were never owned and must not be cleared later.
6. **Ignore generated `vt-*` attributes.** They are server-emitted singleton state even though they are not explicit props.
7. **Serialize arbitrary prop values into comments.** Cleanup does not need them and this enlarges the wire/security surface unnecessarily.
8. **Assume `encodeURIComponent()` alone makes arbitrary descriptor JSON comment-safe.** Hyphens remain literal.
9. **Use the property descriptor to solve DSIH child provenance.** Body DSIH can remain inside the boundary's existing DOM ownership range instead.

## Verification lanes

React PR 29 is the source-free contract verifier:

- old contributed attribute disappears while later external attribute survives;
- contributed `style.color` disappears while later external `backgroundColor` survives;
- current body event props remain live after nested marker cleanup;
- Fizz opaque fallback body content disappears on boundary client takeover while a later outside style survives.

During this refinement, the hand-built PR 29 contract patch was also found to have incorrect existing unified-diff hunk counts. Those counts were repaired before semantic execution. Preserve any preflight failure from an older run as verifier-packet evidence, not product evidence.

React PR 34 is the server-only DSIH stream experiment. It intentionally leaves the attribute/style/current-owner controls unresolved.

## Decision

**SPLIT THE PROTOCOL, INCLUDING CURRENT-OWNER ASSOCIATION.**

Advance body preamble DSIH streaming as an independent small experiment. Keep marker property/current-owner metadata in research until the prev-value audit, generated ViewTransition coverage, owner-preservation rule, and comment-safe encoding are complete. Do not combine them merely because they share the same contribution marker.
