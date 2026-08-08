## In simple words

Body `dangerouslySetInnerHTML` is not only a cleanup/provenance problem. It also has no representation in React's host placement order.

React intentionally treats `<body>` and `<html>` HostSingletons as invisible for host positioning. Host nodes before `<html>`, managed children inside `<body>`, and host nodes after `</html>` can all be inserted into the same physical `document.body` in Fiber order. A body HostSingleton that uses `dangerouslySetInnerHTML` has no child Fibers, so the placement traversal contributes no host node for its opaque content. The content appears later through `setInitialProperties` / `updateProperties` as a whole-body `innerHTML` write.

That property-side-effect model cannot preserve the logical slot that the body Fiber occupies among other body-scope host nodes.

## Source mechanism

Current host positioning follows these rules:

- `isHostParent()` treats a HostSingleton as a placement parent only when `isSingletonScope(type)` is true;
- in React DOM, only `head` is a singleton placement scope;
- `getHostSibling()` descends through `body` and `html` HostSingletons while looking for real HostComponent/HostText siblings;
- `insertOrAppendPlacementNodeIntoContainer()` inserts HostComponent/HostText nodes, while a non-scope HostSingleton merely recurses into its child Fibers;
- a body DSIH Fiber has no managed child Fibers, therefore it contributes nothing to host placement.

Separately, the HostSingleton acquire/update path applies DSIH through generic DOM prop handling, which writes `body.innerHTML`.

So the current render has two independent models:

1. Fiber placement orders the actual host nodes in body scope;
2. body opaque HTML arrives as a later whole-container mutation that does not participate in that order.

## Same-tree collision

The Suspense-anywhere/document-root work explicitly supports host components in body scope outside the `<body>` Fiber.

Example logical tree:

```jsx
<>
  <div id="before" />
  <html>
    <head />
    <body dangerouslySetInnerHTML={{__html: '<span id="middle" />'}} />
  </html>
  <div id="after" />
</>
```

The intended physical order is conceptually:

```html
<body>
  <div id="before"></div>
  <span id="middle"></span>
  <div id="after"></div>
</body>
```

Current whole-body DSIH semantics can erase the before/after siblings or leave the opaque contribution without a stable placement relationship to them.

The same issue appears on managed -> opaque transition. Managed body child Fibers previously occupy a real slot between surrounding root/body-scope siblings. Replacing those children with DSIH removes the managed placement nodes, then the later whole-body write has no Fiber-visible insertion position to inherit.

## Consequence for the owned-range hypothesis

A private range stored only as HostConfig cleanup bookkeeping is insufficient.

The opaque contribution must also participate in **host sibling ordering** so that React can answer:

- where initial opaque content belongs among surrounding body-scope nodes;
- where a managed -> opaque transition inserts the new contribution;
- where opaque -> managed replacement children should be placed after retiring the opaque contribution;
- how a Suspense fallback opaque contribution coexists with mounted-but-hidden primary nodes;
- how keyed owner replacement transfers the slot without overwriting unrelated siblings.

This makes an opaque contribution closer to a host placement unit than an ordinary element property.

## Representation options to investigate

### Conditional HostSingleton placement unit

A body HostSingleton in opaque mode could expose an internal placement boundary to the existing placement traversal. This may avoid a new Fiber tag, but current `getHostSibling` intentionally looks through non-scope HostSingletons, so sibling discovery would need a way to observe the opaque boundary only when the singleton has an opaque contribution.

### Dedicated opaque-content Fiber / host terminal

Render the DSIH contribution as a reconciler-visible terminal child. This would naturally participate in Placement/deletion/sibling ordering, but it is a much larger semantic change and would need to preserve the existing rule that users cannot supply both children and DSIH.

### HostConfig-only range

A range attached to the body owner can solve selective cleanup, but without reconciler visibility it cannot fully solve initial/global ordering. Retain it as a possible storage primitive, not a complete placement model.

## Marker observability concern

Permanent comment/template sentinels would make internal boundaries observable through `body.innerHTML` and `childNodes`, changing current DSIH output. React already uses comments for Suspense/Activity boundaries, but adding them to every body DSIH contribution is still an observable compatibility change.

An in-memory DOM `Range` could potentially represent a client-side boundary without permanent marker nodes. That needs separate browser-semantics research, especially for empty ranges, surrounding-node deletion, outside insertions, and hydration recovery.

## New verifier controls

Owned React draft PR 27 now adds two body-scope placement controls on untouched source:

1. `keeps body direct HTML ordered between root body-scope siblings`
   - root host sibling before `<html>`;
   - body DSIH contribution;
   - root host sibling after `</html>`;
   - requires exact physical order and stable outside-node identity across DSIH update.

2. `keeps managed body children ordered when the body slot becomes opaque`
   - begins with a managed body child between root body-scope siblings;
   - transitions the body to DSIH;
   - requires the managed child to retire while surrounding nodes keep identity and the opaque contribution occupies the same middle slot.

These are source-free baseline controls. The verifier first runs the checked-in body-scope placement regression to validate the harness and then requires current source to fail the new controls.

## Decision

**REFINE THE BODY RANGE IDEA INTO A PLACEMENT-UNIT PROBLEM.**

Selective ownership and provenance remain necessary, but they are not sufficient. A complete body opaque-content repair must integrate the contribution with global `document.body` host ordering. Do not write a cleanup-only or HostConfig-only product candidate until that placement representation is explicit.