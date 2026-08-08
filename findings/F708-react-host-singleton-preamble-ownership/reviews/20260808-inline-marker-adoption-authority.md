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

## Why a boundary-local candidate can lose adoption

Fizz creates separate preamble states for Suspense content/fallbacks and calls `hoistPreambleState()` as completed/client-rendered boundary subtrees are prepared.

Current DOM `hoistPreambleState()` adopts each singleton slot only when the root slot is still null:

```text
if rootPreamble.bodyChunks === null && local.bodyChunks:
  rootPreamble.bodyChunks = local.bodyChunks
```

If the root body slot is already occupied, a later boundary-local body is simply not adopted into root `bodyChunks`.

But its inline `<!--body-->` marker was emitted earlier when the local `<body>` was encountered.

Therefore marker presence and singleton adoption are no longer equivalent facts.

## Minimal counterexample

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

The root body already owns `renderState.preamble.bodyChunks`.

The fallback has its own boundary-local preamble state:

- `pushStartBody()` emits `<!--body-->` into that boundary;
- fallback `bodyChunks` contain `data-losing-body`;
- later `hoistPreambleState()` sees the root body already occupied and does not adopt those fallback body chunks;
- managed fallback children can still render into the normal boundary stream.

The parsed document therefore keeps the actual root body's `data-adopted-body` attribute, while the losing fallback boundary still contains a `<!--body-->` marker.

When hydration client-renders that errored boundary, current `clearHydrationBoundary()` sees the marker and calls `clearSingletonPreambleContribution(document.body)`. That cleanup has authority over the real body even though this boundary never supplied its singleton opening/attributes.

With current broad marker cleanup it clears the adopted root body's attributes. Even after property-aware marker cleanup is implemented, the same authority bug remains unless the marker proves which contribution was actually adopted.

## Verifier

React PR 29 now carries the real-Fizz control:

`does not clear the adopted body for an unadopted preamble marker`

The test requires:

- server document body retains the root-adopted attribute;
- the losing fallback body's attribute never becomes the document body's attribute;
- the losing fallback's managed child/marker can still exist in the boundary stream;
- after client takeover of the losing boundary, the adopted body attribute still survives.

Current source is expected to fail at the final ownership assertion.

## Design consequence

Property descriptors alone are insufficient.

A future marker protocol must prove **both**:

1. what singleton properties/content a boundary contributed;
2. that this boundary's contribution is the one actually adopted into the current document singleton.

Possible repair families:

### Restore adoption-time/end-marker authority

Return to the original model where `hoistPreambleState()` records contribution ownership and the authoritative cleanup marker is emitted only after adoption is known.

This is historically proven but partially reverses the early-inline optimization and needs a performance/streaming review.

### Keep inline candidates, add an adoption identity

Give boundary preamble contributions an ID and make singleton cleanup conditional on that ID matching an authoritative owner token associated with the adopted root preamble.

This could potentially compose with opaque DSIH range provenance, but requires a clean server/client identity channel.

### Other equivalent proof

Any design is acceptable if a losing boundary's marker cannot clear state adopted from another boundary.

## Relationship to other #708 findings

This is distinct from:

- broad attribute/style cleanup;
- current client Fiber/props detachment;
- opaque DSIH child provenance;
- raw-comment control namespace collision.

Those can all be fixed and an unadopted marker would still have incorrect cleanup authority unless adoption is encoded.

## Disposition

**HIGH-CONFIDENCE PROTOCOL BUG / EXECUTE REGRESSION.**

Do not promote a marker metadata patch that preserves current inline marker authority without addressing adoption.

## Evidence class

Public history/source control-flow read plus target-test-prepared real-Fizz regression in React PR 29. No public upstream interaction performed.
