## In simple words

Fizz preamble contribution cleanup needs two independent ownership channels:

1. **singleton property ownership** for attributes/style state moved into the document preamble;
2. **opaque child ownership** when a boundary-contributed body uses `dangerouslySetInnerHTML`.

The opaque child problem has a promising small split: keep boundary body DSIH in the boundary stream after the existing body contribution marker instead of moving it into root `bodyChunks`. That lets existing Suspense boundary deletion own the raw DOM. React draft PR 34 tests this server-only experiment.

Property cleanup still needs marker metadata because the persistent singleton attributes live outside the boundary DOM range.

## Current source behavior

For a singleton in a boundary preamble:

- `pushStartBody()` writes `<!--body-->` into the boundary target;
- the actual `<body ...>` start tag is serialized into `preamble.bodyChunks`;
- `pushStartSingletonElement()` serializes explicit props with `pushAttribute()` and generated ViewTransition attributes with `pushViewTransitionAttributes()`;
- current `clearSingletonPreambleContribution()` receives only the persistent DOM element and therefore clears every attribute.

The checked-in source TODO already states that the marker identifies the singleton but does not carry enough contributed-property information to preserve imperative state.

## Descriptor requirements

A useful marker descriptor should carry ownership metadata only; arbitrary prop values are unnecessary and should stay out of comment payloads.

### Explicit emitted props

Inside `pushStartSingletonElement`, the server can determine whether an explicit prop actually serialized by recording `target.length` before and after `pushAttribute()`.

If the chunk count did not change, that prop produced no server attribute and must not be claimed by the contribution. This naturally excludes ignored event handlers, null values, invalid value types, and other serializer no-ops.

Store the React prop key, not the rendered value. The client can then reuse React's existing property-clearing semantics instead of maintaining a second alias/namespaced-property table.

### Style

`style` needs per-property ownership.

The server should record only style keys that actually emitted CSS. `pushStyleAttribute()` skips properties whose values are null, boolean, or empty string; claiming one of those skipped keys would allow cleanup to erase a later imperative style value that React never emitted.

The client can reconstruct a minimal previous style object containing only those keys and use the existing style clearing path. Values can be inert sentinels because cleanup depends on previous keys, not on reproducing the serialized CSS values.

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

Use a versioned, comment-safe payload.

Working requirements:

- old bare `<!--html-->`, `<!--head-->`, and `<!--body-->` markers remain parseable for older server output;
- new markers identify singleton type plus descriptor version;
- payload contains names/kinds only, no arbitrary attribute or HTML values;
- encoding cannot allow `--` / `-->` injection into comment syntax;
- malformed or unknown-version payloads must fail safely and predictably rather than partially clearing guessed state.

A percent-encoded compact JSON payload is an adequate experiment format because it is comment-safe and easy to version. Production encoding can be reconsidered after size measurements.

Example conceptual payload, not a committed wire format:

```text
body:v1:<encoded {
  props: [...],
  styles: [...],
  generatedAttributes: [...]
}>
```

## Client cleanup direction

For a new descriptor marker:

1. reconstruct the minimal previous-props ownership packet from explicit prop keys and style keys;
2. reuse the normal singleton property clear path where its previous-value semantics are adequate;
3. directly clear generated `vt-*` attributes;
4. special-case the audited server-emitted props whose client update semantics cannot remove the serialized attribute correctly;
5. detach the singleton association exactly as current marker cleanup does.

For an old bare marker, preserve the old clear-all fallback unless compatibility policy explicitly chooses otherwise. Same-version server/client output will use the new descriptor; old streamed HTML remains deterministic.

## Opaque child split

Do not encode raw DSIH values or arbitrary child fingerprints into this property descriptor.

Source review found a smaller body-only mechanism:

- the body start tag and attributes remain in `preamble.bodyChunks`;
- the existing `<!--body-->` marker remains in the Suspense boundary target;
- if the boundary-contributed body has DSIH, emit those raw bytes into the boundary target after the marker instead of `bodyChunks`;
- existing Suspense boundary removal can then retire the opaque DOM naturally.

This is React PR 34's experiment. If it passes the focused Fizz regression while attribute controls remain red, child ownership and property ownership can be repaired independently.

Head/html are intentionally excluded from that body DSIH split because their parser/resource/document semantics differ.

## Rejected shortcuts retained

1. **Clear every attribute.** Already erases later imperative state.
2. **Read current HostSingleton Fiber props during cleanup.** The marker describes an older server boundary contribution; the current client owner can have different or empty props.
3. **Record only attribute names and clear the whole style attribute.** This erases later imperative style properties.
4. **Record every input style key.** Keys skipped by the server serializer were never owned and must not be cleared later.
5. **Ignore generated `vt-*` attributes.** They are server-emitted singleton state even though they are not explicit props.
6. **Serialize arbitrary prop values into comments.** Cleanup does not need them and this enlarges the wire/security surface unnecessarily.
7. **Use the property descriptor to solve DSIH child provenance.** Body DSIH can remain inside the boundary's existing DOM ownership range instead.

## Verification lanes

React PR 29 is the source-free contract verifier:

- old contributed attribute disappears while later external attribute survives;
- contributed `style.color` disappears while later external `backgroundColor` survives;
- Fizz opaque fallback body content disappears on boundary client takeover while a later outside style survives.

React PR 34 is the server-only DSIH stream experiment. It intentionally leaves the attribute/style controls red.

## Decision

**SPLIT THE PROTOCOL.**

Advance body preamble DSIH streaming as an independent small experiment. Keep marker property metadata in research until the prev-value audit and generated ViewTransition coverage are complete. Do not combine the two into one source packet merely because they share the same contribution marker.