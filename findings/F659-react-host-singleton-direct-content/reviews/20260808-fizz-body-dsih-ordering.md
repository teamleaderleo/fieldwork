# Fizz body DSIH — preamble hoisting breaks body-scope order

## Question

Does server-rendered `<body dangerouslySetInnerHTML>` occupy the same logical body-scope position as the body HostSingleton in Fiber/client rendering?

## Conclusion

**No. Current Fizz serialization hoists body DSIH into the document preamble, so its raw nodes are emitted before ordinary body-scope segment content regardless of the body's Fiber position.**

This is a server-side counterpart to the client body-placement defect.

## Source path

### Body singleton serialization

For a document-scope `<body>`, `pushStartBody()` chooses the request/root preamble and initializes `preamble.bodyChunks`.

It then calls:

```js
pushStartSingletonElement(
  preamble.bodyChunks,
  props,
  'body',
  formatContext,
)
```

`pushStartSingletonElement()`:

- writes the `<body ...>` start tag into `bodyChunks`;
- captures `children` separately;
- captures `dangerouslySetInnerHTML` separately;
- calls `pushInnerHTML(target, innerHTML, children)` using the same target;
- returns managed `children` to ReactFizzServer for normal recursive rendering.

Therefore:

- body DSIH bytes become **preamble body chunks**;
- managed body children remain **ordinary render-segment content**.

### Flush order

Fizz treats the preamble as document-opening content and flushes it before the ordinary shell/root segment. The Suspense-anywhere server design explicitly relies on this: document singleton openings plus head contents are preamble, while normal body-scope content follows inside the physical body.

So anything serialized directly into `bodyChunks` is physically earlier in the body than ordinary root segment nodes.

## Minimal ordering counterexample

Conceptual tree:

```jsx
<>
  <div id="before" />
  <html>
    <head />
    <body
      dangerouslySetInnerHTML={{
        __html: '<span id="opaque">opaque</span>',
      }}
    />
  </html>
  <div id="after" />
</>
```

Fiber/client body-scope semantics intentionally treat `body` as invisible to host positioning. The logical host order is:

```text
before
opaque body contribution

after
```

Current Fizz output instead has to flush the body preamble before the ordinary segment containing `before` and `after`.

The physical order is therefore:

```text
opaque body contribution
before
after
```

The DSIH contribution has been hoisted out of its React-tree body-scope position.

## Managed-body reversing control

With managed body children instead of DSIH:

```jsx
<body><span id="managed" /></body>
```

`pushStartSingletonElement()` returns that child instead of serializing it into `bodyChunks`.

Fizz renders the managed child through the ordinary task/segment traversal, so it can participate in the same body-scope ordering as root-level siblings.

This makes the asymmetry specific to direct HTML, not to the existence of a body singleton itself.

## Why this matters beyond aesthetics

The same React tree can have different document-body order between:

- server/Fizz output;
- fresh client Fiber rendering.

That can affect:

- CSS/style ordering when raw HTML contains style-related nodes;
- script/data-block/document query order;
- hydration cursor expectations;
- subsequent contribution placement and outside-node preservation.

It also means a complete body DSIH repair cannot be a client-only HostConfig change. Fizz needs a representation that lets opaque body content participate in normal body-scope order while preserving preamble/Suspense ownership semantics.

## Relationship to rejected PR 34

PR 34 tried to move boundary-contributed body DSIH from `bodyChunks` into the ordinary boundary target. That incidentally moves the opaque bytes back toward the correct body-scope position and gives the boundary normal deletion ownership.

That implementation is still rejected because arbitrary DSIH comments then collide with React's direct-sibling Suspense/Activity/preamble control-comment namespace.

So this ordering result strengthens the **goal** behind PR 34 while leaving its implementation falsified.

## Design consequence

A complete server representation has to satisfy all three:

1. opaque body content occupies its normal body-scope React order rather than being blindly hoisted in preamble chunks;
2. arbitrary raw DSIH cannot be parsed as React's Suspense/Activity control comments;
3. server/client hydration retains exact opaque-node provenance, including empty content.

This strongly favors treating body DSIH as a first-class contribution/placement unit in both Fizz and Fiber, with an explicit server provenance protocol rather than ordinary `innerHTML` property serialization.

## Test to add when execution capacity is useful

A focused Fizz regression should assert the physical body order for:

```text
root sibling before -> body DSIH -> root sibling after
```

and use the equivalent managed-body case as a reversing control.

No separate execution PR is opened from this note yet; the mechanism is source-deterministic and the current runner queue is already saturated.

## Evidence class

Fizz source/control-flow read plus established preamble flush semantics. Public upstream interaction: none.
