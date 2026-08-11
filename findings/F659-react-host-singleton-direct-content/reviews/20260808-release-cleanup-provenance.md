## In simple words

The current HostSingleton child cleanup on release was introduced by public React commit `b685b40d870b90a975da28c8d22ecf0ba910b1a1` (PR 37112), whose stated goal was to stop release from destroying third-party singleton state.

That change made attribute/property cleanup ownership-aware by clearing only props from the releasing Fiber, but its special `dangerouslySetInnerHTML` cleanup still assigns `instance.textContent = ''`, which clears the entire current child list.

The accompanying release regression simulates third-party attributes, inline style properties, and an imperative click handler. It does not insert a third-party child node. That missing dimension explains why the child-list ownership conflict survived a change explicitly intended to preserve external singleton state.

## Provenance

PR 37112 is titled `[Fiber] only remove properties from singletons on release`.

Its body says that removing every attribute both fails to reset all property-backed state and wipes attributes/properties set by third-party scripts and extensions. The replacement release path therefore receives the singleton type and last committed props and calls `clearSingletonProperties(instance, type, props)`.

The release implementation added in that same change then special-cases state that ordinary property clearing does not remove:

```js
if (props.dangerouslySetInnerHTML != null) {
  instance.textContent = '';
}
```

The comment immediately above calls out that `dangerouslySetInnerHTML` is not cleared by `updateProperties` when its next value is null, and separately notes the unresolved ordinary-update path.

## Tests added by the same change

The change added the current HostSingleton DSIH controls, including:

- release resets a body that had non-null dangerous HTML;
- direct HTML -> unset wrapper controls as gated TODOs;
- direct HTML -> different direct HTML;
- managed singleton children -> direct HTML;
- direct HTML -> managed children as a gated TODO.

This is useful contract evidence: body dangerous HTML is explicitly exercised by the current singleton suite, including updates and managed-to-opaque transitions.

The release regression also deliberately mutates outside state while React owns body:

- a `data-external` attribute;
- an additional background style property;
- an imperative `onclick` handler.

After release it requires that outside state to survive while React-owned state disappears.

It does **not** add an outside child node such as `<style>` or `<link rel="stylesheet">`.

## Ownership inconsistency exposed by the second review

At property level, PR 37112 follows this rule:

> remove only state represented by the releasing Fiber's props; preserve later imperative state.

At child-list level, the DSIH special case currently follows a different rule:

> if the Fiber ever had a non-null `dangerouslySetInnerHTML` wrapper, clear every child currently present.

Those rules diverge as soon as an outside system inserts a child after React's opaque write.

For example:

1. React commits body dangerous HTML;
2. an extension appends a `<style>` to the persistent body;
3. the body singleton releases;
4. `textContent = ''` removes both React opaque content and the later outside style.

This is the same external-state class PR 37112 was designed to preserve, but applied to child nodes rather than attributes/properties.

## Narrow unset-wrapper repair

The release implementation also has a separate false positive.

A committed prop shaped as:

```js
dangerouslySetInnerHTML={{__html: null}}
```

or

```js
dangerouslySetInnerHTML={{__html: undefined}}
```

contains a non-null wrapper object but performs no opaque DOM write. The current release condition still clears the singleton child list because it tests the wrapper rather than whether direct content was actually supplied.

The renderer's existing direct-content predicate can distinguish these cases:

```js
props.children == null && shouldSetTextContent(type, props)
```

For HostSingleton DOM types, this remains false for null/undefined `__html` and true for actual non-null direct HTML, including empty string and other accepted values.

This narrow correction changes no actual non-null DSIH release behavior and does not attempt to solve child provenance. It is therefore independent from the broader opaque-range redesign.

The owned verifier for this split is React draft PR 24 at head `12c05f7e7d147721a359070f0c9edb3faa5c1176` until CI provides an executed receipt.

## Rejected conclusion

Do not use PR 37112's DSIH tests as evidence that whole-child-list release cleanup is intended external-state behavior. The change's stated preservation rule points in the opposite direction, and its release regression simply omitted external child insertion.

Likewise, do not treat the narrow unset-wrapper condition fix as completion of non-null DSIH ownership. Actual opaque content still needs a child-level authority/provenance design.

## Decision

**SPLIT / ADVANCE NARROW RELEASE FALSE POSITIVE; HOLD NON-NULL OPAQUE CLEANUP.**

The historical provenance strengthens both decisions:

- null/undefined wrapper release is a local condition bug with a minimal correction;
- non-null opaque content belongs in the broader ownership redesign because whole-container clearing conflicts with the external-state intent of the release cleanup that introduced it.