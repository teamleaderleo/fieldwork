# Body HostSingleton slot state — Fiber-owned opaque renderer state

## Question

Where should a per-body logical slot live when multiple HostSingleton Fibers all resolve to the same persistent `document.body` DOM node?

## Requirements

The state must be:

- per HostSingleton Fiber, not per DOM body;
- stable across current/work-in-progress alternates;
- retained while an Activity/Suspense owner is hidden;
- available during mutation/placement;
- collectible when the Fiber is permanently deleted;
- renderer-specific enough to contain a DOM `Range` without teaching generic Fiber about DOM types;
- compatible with empty, managed, and opaque body content modes.

## Reject DOM-element global state

`document.body` cannot own one global slot object because multiple HostSingleton Fibers may coexist during Suspense/Activity overlap.

A body-level expando can represent only the currently acquired singleton property owner, not every hidden/visible child contribution slot.

## WeakMap keyed by Fiber — workable but awkward

The PR 32 prototype uses renderer bookkeeping keyed by Fiber handles and checks the alternate when reading state.

This can work, but it creates recurring questions:

- which alternate owns the canonical state;
- when to copy/move/delete WeakMap entries;
- how generic `getHostSibling` asks a renderer for a slot keyed by an internal Fiber object;
- how to avoid stale mappings after deletion/remount.

It is useful experimental machinery, but not the cleanest final representation.

## Fiber `memoizedState` is a better carrier

`createWorkInProgress(current, pendingProps)` explicitly copies:

```js
workInProgress.memoizedState = current.memoizedState;
```

So a mutable renderer-owned slot object placed on a committed HostSingleton Fiber naturally survives double buffering by identity.

HostSingleton has no current independent `memoizedState` contract in the reconciler source reviewed here.

That gives a natural representation:

```text
HostSingleton.memoizedState -> opaque renderer singleton state
```

For React DOM body, conceptually:

```js
{
  slotRange: Range,
  mode: 'managed' | 'opaque' | 'empty',
  opaqueNodes: null | Array<Node>,
  ...renderer bookkeeping
}
```

Exact fields belong to the DOM renderer; generic reconciler should not inspect them directly.

## Host-config boundary

The custom reconciler host config already defines renderer-opaque types and optional singleton functions.

A complete implementation can add an opaque singleton-state type/function family, conceptually:

```text
SingletonInstanceState
create/initializeSingletonState(...)
getSingletonInsertionAnchor(state, instance, ...)
updateSingletonSlotAfterMutation(state, ...)
deleteSingletonState(state, ...)
```

Exact API should stay minimal.

The generic reconciler needs only the operations required for:

- HostSingleton placement;
- descendant end-placement through a non-scoped body;
- contribution transitions;
- deletion / visibility.

It should never depend on DOM `Range` methods directly.

Renderers that do not support singletons can extend `ReactFiberConfigWithNoSingletons` with matching shims; third-party custom reconciler config can expose opaque `SingletonInstanceState = mixed` similarly to existing host-config types.

## Initialization timing

Do not create/mutate a live DOM Range during speculative render merely because complete work resolves a singleton.

Preferred timing:

- render/complete determines flags and content mode;
- mutation/commit initializes the slot when placement becomes real;
- successful hydration commit initializes/converts server provenance into the slot state;
- later work-in-progress Fibers inherit the committed state object through normal `memoizedState` copying.

This avoids retaining live DOM position state from abandoned renders.

Current React's `bindInstance()` TODO/comment points in the same general lifecycle direction for singleton Fiber/props binding: persistent singleton host ownership should ideally become authoritative at commit, not speculative render.

## Mutation safety

The state object can be mutable during commit even though current/WIP alternates may share the same pointer, because renderer code must only mutate it during committed host effects, never speculative render.

If a mutation effect throws midway, this is comparable to partially applied DOM host mutations generally; error recovery still needs review but is not unique to the slot object.

## Hidden/reappear benefit

A hidden body Fiber retains `memoizedState` while its singleton properties are released.

Its slot Range and contribution metadata therefore survive:

- another body owner acquiring the persistent body element;
- hidden managed child updates;
- reappearance;
- opaque hide/unhide.

This is exactly the lifetime required by the exclusive-properties/shared-contributions model.

## Deletion

Permanent HostSingleton deletion should:

1. remove managed/opaque contribution content through its normal contribution lifecycle;
2. detach/release exclusive singleton state if still owned;
3. release/drop renderer slot state;
4. set/allow Fiber state to become unreachable for GC.

No global DOM expando cleanup protocol is needed for per-owner slot metadata.

## DevTools / Fiber-state caution

Using `memoizedState` on a HostSingleton is an internal reconciler representation change. Before implementation, verify no DevTools/test utility assumes HostSingleton `memoizedState === null`.

Current code search found no dedicated HostSingleton memoized-state semantics, but this should still be covered by type/test review.

## Disposition

**PREFER FIBER-OWNED OPAQUE `memoizedState` OVER DOM GLOBALS OR FIBER-KEYED WEAKMAPS.**

This is the cleanest state lifetime found so far for the per-body slot model, provided all DOM Range mutation remains commit-only behind host-config functions.
