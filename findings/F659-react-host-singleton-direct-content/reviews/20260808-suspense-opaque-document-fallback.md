## In simple words

The hidden-owner problem is broader than the experimental Activity verifier.

React's public Suspense document-fallback support intentionally allows one `<html>/<body>` singleton owner to remain mounted but hidden while a fallback `<html>/<body>` owner becomes visible. The checked-in regression verifies this with ordinary managed children: primary DOM nodes remain physically present with `display: none`, fallback children coexist beside them, and the same primary nodes are unhidden when Suspense resolves.

A fallback body using `dangerouslySetInnerHTML` breaks that coexistence model because the fallback acquisition/update can replace the entire persistent body's child list. That can physically detach the hidden primary owner's mounted nodes. When the primary tree reappears, those Fibers already exist and do not receive ordinary Placement solely because they reappear.

This moves the retained-child/reappearance problem from an Activity-only research edge into an intended Suspense document-fallback feature.

## Historical contract

Public React commit `c492f97541486458ce21653d2669d53d380f0538` / PR 32163 added Fiber support for Suspense boundaries above document singletons.

Its commit message states that:

- most HostSingletons became invisible for host positioning;
- `head` remained the special singleton placement scope;
- `body` and `html` do not directly participate in host positioning;
- Offscreen hiding/unhiding was changed to pierce through singletons so React can flip between primary and fallback html/head/body owners.

The regression added by that change renders a Suspense boundary above `<html>` with a primary document and a fallback document.

After the primary document has mounted, a synchronous suspension expects output equivalent to:

```html
<html data-fallback>
  <head>
    <meta ... style="display: none">
  </head>
  <body data-fallback>
    <div style="display: none">primary</div>
    <div>fallback</div>
  </body>
</html>
```

The key invariant is that the primary managed DOM remains mounted in the persistent singleton while hidden; the fallback owner coexists with it rather than replacing it.

When the promise resolves, the same primary content becomes visible again.

## Opaque fallback counterexample

Change only the fallback body from managed children to opaque HTML:

```jsx
const fallback = (
  <html data-fallback="">
    <head />
    <body
      data-fallback=""
      dangerouslySetInnerHTML={{
        __html: '<div id="opaque-fallback">fallback</div>',
      }}
    />
  </html>
);
```

Sequence:

1. primary document mounts with a managed body child;
2. synchronous suspension hides that primary child;
3. fallback body acquires the same persistent `document.body`;
4. generic singleton property initialization writes the fallback `innerHTML` to the whole body;
5. the hidden primary DOM node is detached even though its Fiber remains mounted;
6. resolving Suspense reacquires the primary singleton and runs reappearance effects, but the retained primary child Fiber has no ordinary Placement caused by reappearance;
7. without an explicit restoration mechanism, the primary DOM identity cannot be restored to the body.

The release side is problematic too: whole-body cleanup of the opaque fallback can remove hidden primary nodes if a future acquisition path preserved them initially.

## Relation to the body opaque-range direction

A body-owned opaque range would address this case naturally if it obeys the existing Suspense coexistence contract:

- the fallback's raw HTML is inserted into its own owned range;
- hidden primary DOM remains outside that range;
- releasing the fallback retires only the fallback range;
- primary reappearance can unhide the same retained primary DOM nodes.

This is stronger motivation for range ownership than the third-party-style cases alone: the outside nodes here are **React-owned by another mounted Fiber tree**, and the existing Suspense regression requires them to survive fallback takeover.

## Relation to the Activity guards

The prior Activity verifier found two classes of failures:

- hidden owner updates/releases can mutate or detach the visible owner's singleton association;
- hidden descendant Placement/deletion can still target the shared persistent singleton.

This Suspense case is complementary. Even if hidden-owner updates and descendant mutations are guarded, the **visible fallback owner's own opaque write** can destroy the hidden primary owner's retained DOM.

Therefore an Activity-only mutation guard cannot complete persistent singleton ownership. The visible owner's child-content semantics must also preserve hidden owner content when Suspense intentionally overlaps them.

## New verifier

Owned React draft PR 27 now carries a source-free baseline control:

`preserves primary document children across an opaque body fallback`

It first mounts the primary document, stores the primary DOM child identity, synchronously suspends into an opaque body fallback, and requires:

- fallback opaque HTML becomes visible;
- the exact primary child remains contained in `document.body` with `display: none`;
- resolving Suspense removes the opaque fallback;
- the same primary child identity is still in body, becomes visible, and receives the resolved content update.

The PR workflow validates the existing checked-in Suspense document test first and then requires untouched current source to fail this new control. Until CI executes, this is target-test-prepared/source-read evidence.

## Decision

**EXPAND BODY OWNERSHIP CONTRACT; DO NOT TREAT ACTIVITY AS THE ONLY HIDDEN-OWNER PROBLEM.**

The complete body opaque-content design must preserve three distinct classes of children outside the current opaque owner's authority:

1. third-party/extension state;
2. separately managed React content sharing persistent body placement;
3. hidden primary React content intentionally retained by Suspense while a fallback singleton owner is active.

The body opaque-range hypothesis is compatible with all three. Whole-body `innerHTML` / `textContent` ownership is compatible with none of them.