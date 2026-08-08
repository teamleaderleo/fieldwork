# Fizz body DSIH — preamble hoisting breaks body-scope order

## Question

Does server-rendered `<body dangerouslySetInnerHTML>` occupy the same logical body-scope position as the body HostSingleton in Fiber/client rendering?

## Conclusion

**No. Current Fizz serialization hoists body DSIH into the document preamble, so its raw nodes are emitted before ordinary body-scope segment content regardless of the body's Fiber position.**

This is a server-side counterpart to the client body-placement defect and conflicts with explicit public Fizz/Fiber Suspense-anywhere semantics.

## Public contract

### Fizz

Public Suspense-anywhere server change #32069 defines the document preamble as:

- the three singleton tags;
- plus contents of `document.head`.

Its PR description then states that **anything that is not part of the preamble is implicitly in body scope**.

Body child content is therefore intended to be ordinary body-scope stream content rather than document preamble payload.

### Fiber

Public Suspense-anywhere Fiber change #32163 deliberately made most HostSingletons invisible from host positioning. Its PR description says:

- `body` and `html` do not directly participate in host positioning;
- `head` is the special singleton scope.

The same change added a document-root regression whose expected physical body order is explicitly:

```text
root sibling before
body child inside
root sibling after
```

The test evolves insertions/deletions around all three regions and repeatedly asserts that body descendants remain interleaved with root-level body-scope siblings in Fiber order.

So current client React has a public regression contract for body child positioning relative to siblings outside `<body>`, and the Fizz design says such content belongs in ordinary body scope.

## Fizz source path

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

This directly contradicts the conceptual Fizz preamble boundary: DSIH child content is being treated as part of the body start/preamble packet even though equivalent managed body content is ordinary body scope.

### Flush order

Fizz flushes the document preamble before the ordinary shell/root segment. So anything serialized directly into `bodyChunks` is physically earlier in the body than ordinary root segment nodes.

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

This follows the same body-scope model tested by the public Fiber regression: host nodes outside the singleton are routed into physical `document.body` and are ordered around the body contribution according to React tree position.

Expected client/Fiber host order:

```text
before
opaque body contribution
after
```

Current Fizz output must flush the body preamble before the ordinary segment containing `before` and `after`.

Physical server order becomes:

```text
opaque body contribution
before
after
```

The DSIH contribution has been hoisted out of its React-tree body-scope position.

The existing React DOM nesting warning for arbitrary host nodes at the document root does not invalidate the host-order contract: the public Fiber regression intentionally exercises exactly this root/body-scope behavior while carrying the warning as a TODO until nesting validation is loosened.

## Managed-body reversing control

With managed body children instead of DSIH:

```jsx
<body><span id="managed" /></body>
```

`pushStartSingletonElement()` returns that child instead of serializing it into `bodyChunks`.

Fizz renders the managed child through the ordinary task/segment traversal, so it can participate in the same body-scope ordering as root-level siblings.

This makes the server asymmetry specific to direct HTML, not to the existence of a body singleton itself.

## Narrow root-body repair experiment

Owned React draft PR 48 isolates the common root/non-boundary case on current main `2042572329425f9ebf35ae6287ea5bab72b2c497`.

The experiment leaves the `<body ...>` start tag in `preamble.bodyChunks` but gives `pushStartSingletonElement()` an optional `innerHTMLTarget`.

For `pushStartBody()` only when `preambleState === null`:

```text
body opening/attributes -> preamble.bodyChunks
body DSIH bytes         -> ordinary current render target
```

For boundary-local bodies (`preambleState !== null`), DSIH remains in the existing preamble path because raw arbitrary comments cannot safely enter the Suspense/Activity control-comment sibling stream without a stronger protocol.

### Verifier design

PR 48's workflow deliberately proves both defect and experiment in one job:

1. apply only the order tests;
2. require the managed body-order control to pass on untouched current source;
3. require the root body DSIH order control to fail on untouched current source;
4. apply the server experiment;
5. require both order controls to pass;
6. rerun an existing matching root-body DSIH hydration control;
7. run `yarn linc`.

This is a much stronger execution carrier than a patch that only demonstrates its own happy path.

## Cross-renderer consequence

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

PR 34 tried to move **boundary-contributed** body DSIH from `bodyChunks` into the ordinary boundary target. That incidentally restores body-scope placement and gives the boundary normal deletion ownership.

That implementation is rejected because arbitrary DSIH comments then collide with React's direct-sibling Suspense/Activity/preamble control-comment namespace.

PR 48 avoids that specific collision by changing only root/non-boundary body DSIH, where the ordinary target is not nested inside a preamble-contributing Suspense boundary.

So PR 48 is a narrow repair candidate; PR 34 remains useful negative evidence for the harder boundary case.

## Design consequence

A complete server representation has to satisfy all three:

1. opaque body content occupies its normal body-scope React order rather than being blindly hoisted in preamble chunks;
2. arbitrary raw DSIH cannot be parsed as React's Suspense/Activity control comments;
3. server/client hydration retains exact opaque-node provenance, including empty content.

The root case may be repaired independently with ordinary segment placement. Boundary-contributed DSIH still requires an explicit provenance/control protocol.

## Disposition

**HIGH-CONFIDENCE CROSS-RENDERER CONTRACT DEFECT. EXECUTE PR 48 AS A NARROW ROOT-BODY REPAIR EXPERIMENT.**

Do not infer from a PR 48 pass that boundary DSIH or client opaque ownership is solved.

## Evidence class

Fizz source/control-flow read plus public Fizz/Fiber PR/test contract; target-test-prepared PR 48. No public upstream interaction performed.
