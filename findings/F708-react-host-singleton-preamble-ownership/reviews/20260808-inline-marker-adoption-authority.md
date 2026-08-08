# Inline preamble markers — cleanup authority can precede adoption

## Question

Does the current inline `<!--html-->` / `<!--head-->` / `<!--body-->` marker prove that the containing Suspense/Activity boundary actually supplied that singleton's root preamble state?

## Historical protocol

The original Suspense-anywhere hydration implementation used a boundary-end contribution code.

A boundary-local `PreambleState` accumulated a bitset. Crucially, `hoistPreambleState()` set a contribution bit **only when** that boundary's singleton chunks were actually adopted into the root preamble:

```text
if root body is empty and local body exists:
  root body = local body
  local contribution |= BODY
```

The contribution code was serialized immediately before the boundary's real closing marker. Client cleanup therefore interpreted only a contribution that had already won root adoption.

## Inline optimization

Public change #32850 moved preamble contribution markers inline so they could be written early in render.

The change:

- removed the `PreambleState.contribution` bitset;
- removed adoption-time bit setting from `hoistPreambleState()`;
- emits static `<!--head-->`, `<!--body-->`, `<!--html-->` comments directly in `pushStartHead/Body/Html` whenever `preambleState !== null`;
- changed the client scanner to act on those comments wherever they occur inside the boundary.

The change's safety rationale focused on DOM placement: document-scope singleton markers remain flat in body and can be discovered by the scanner.

It did not preserve the old protocol's **adoption proof**.

## Source-level authority mismatch

Fizz creates separate preamble states for Suspense content/fallbacks and calls `hoistPreambleState()` as completed/client-rendered boundary subtrees are prepared.

Current DOM `hoistPreambleState()` adopts each singleton slot only when the root slot is still null:

```text
if rootPreamble.bodyChunks === null && local.bodyChunks:
  rootPreamble.bodyChunks = local.bodyChunks
```

If the root body slot is already occupied, a later boundary-local body is not adopted into root `bodyChunks`.

But its inline `<!--body-->` marker was emitted earlier when the local `<body>` was encountered.

Therefore marker presence and singleton adoption are no longer equivalent facts at the protocol level.

## Simplest target counterexample

Conceptual server tree:

```jsx
<html>
  <head />
  <body data-adopted-body="">
    <div>stable</div>
  </body>
  <Suspense
    fallback={
      <body data-losing-body="">
        <div id="losing-body-child">losing child</div>
      </body>
    }>
    <ServerError />
    <span id="client">client</span>
  </Suspense>
</html>
```

Mechanically, the root body already owns `renderState.preamble.bodyChunks`, while the fallback has a separate boundary-local preamble state. If the fallback reaches the parsed boundary stream:

- `pushStartBody()` emitted `<!--body-->` into that boundary;
- fallback `bodyChunks` contain `data-losing-body`;
- `hoistPreambleState()` sees the root body already occupied and does not adopt those fallback body chunks;
- managed fallback children can still be ordinary boundary segment content;
- later boundary cleanup can interpret the losing marker as authority over the real document body.

With current broad marker cleanup that would erase the adopted body's attributes.

## Important reachability qualification

The simple target above has two active body candidates in one server render: the root body plus a fallback body sibling. That may already violate React's singleton usage contract.

So the current evidence proves a **protocol authority mismatch**, but it does not yet prove that a losing marker can flush from a valid application tree whose singleton alternatives are properly mutually exclusive.

Do not overstate this as a normal-valid-app production bug until one of these is established:

1. the prepared Fizz regression executes and React accepts the tree far enough to expose the marker behavior without an earlier duplicate-singleton failure; or
2. a mutually-exclusive/nested Suspense configuration is found where a boundary-local singleton candidate loses root adoption yet its inline marker still reaches the DOM.

If every reachable losing-adoption case necessarily comes from already-invalid concurrent singleton usage, this remains useful protocol-hardening evidence but drops in product severity.

## Verifier

React PR 29 carries the target control:

`does not clear the adopted body for an unadopted preamble marker`

The test requires:

- server document body retains the root-adopted attribute;
- the losing fallback body's attribute never becomes the document body's attribute;
- the losing fallback's managed child/marker can still exist in the boundary stream;
- after client takeover of the losing boundary, the adopted body attribute still survives.

Interpret execution carefully:

- failure at duplicate-singleton validation / server render before the marker reaches DOM means the simple target is not a valid reachability proof;
- reaching hydration and losing the adopted body attribute confirms the protocol bug is observable at least in this invalid/edge tree;
- a separate valid-tree reproducer remains preferable before promotion.

## Design consequence if reachable

Property descriptors alone would be insufficient.

A marker protocol would need to prove both:

1. what singleton properties/content a boundary contributed;
2. that this boundary's contribution is the one actually adopted into the current document singleton.

Possible repair families include restoring adoption-time/end-marker authority or associating inline candidates with an adoption identity.

## Relationship to other #708 findings

This is distinct from:

- broad attribute/style cleanup;
- current client Fiber/props detachment;
- opaque DSIH child provenance;
- raw-comment control namespace collision.

Those remain independently actionable regardless of whether losing-adoption marker authority is reachable in a valid tree.

## Disposition

**PROTOCOL RISK / EXECUTE REACHABILITY REGRESSION.**

Do not make adoption identity a hard blocker for a marker metadata repair until valid-tree reachability is proven. Do preserve the historical distinction in the design review so a future protocol does not accidentally broaden authority further.

## Evidence class

Public history/source control-flow read plus target-test-prepared Fizz reachability regression in React PR 29. Normal-valid-app reachability remains uncertain. No public upstream interaction performed.
