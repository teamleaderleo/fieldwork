# Preamble cleanup — preserve the current client HostSingleton owner

## Narrow question

Should clearing an old Fizz singleton preamble contribution call `detachDeletedInstance(instance)` on the persistent singleton DOM node after hydration may already have associated that node with the current client HostSingleton Fiber and props?

## Source/history result

**The current detach has no boundary-specific owner token and was inherited from the old broad singleton release implementation.**

Before public PR 37112, `releaseSingletonInstance(instance)` cleared every singleton attribute and then called `detachDeletedInstance(instance)`.

PR 37112 made normal HostSingleton release props-aware and split marker cleanup into `clearSingletonPreambleContribution(instance)`. The new marker helper retained the same clear-all-attributes plus `detachDeletedInstance(instance)` behavior because the server marker has no HostSingleton Fiber/props payload.

No separate server-contribution Fiber handle was introduced for that detach.

## Hydration ordering

HostSingleton hydration binds the persistent singleton during complete work:

`prepareToHydrateHostInstance(fiber, hostContext)` calls the renderer's `hydrateInstance(...)`.

React DOM `hydrateInstance()` immediately calls:

- `precacheFiberNode(internalInstanceHandle, instance)`;
- `updateFiberProps(instance, props)`.

Nested dehydrated-boundary cleanup occurs later during commit.

Therefore the DOM -> Fiber/props association present when `clearSingletonPreambleContribution()` runs may be the **freshly hydrated current client owner**, not an old server contribution.

Calling `detachDeletedInstance(instance)` at that point can erase the current client's event/props/Fiber association.

## Experiment

Owned React draft PR 43 is a child of the source-free preamble ownership contract.

Source experiment: remove only `detachDeletedInstance(instance)` from `clearSingletonPreambleContribution()`.

Normal `releaseSingletonInstance()` keeps its detach unchanged.

### Required green

A public-API event control:

1. model a body preamble contribution marker inside a dehydrated Suspense boundary;
2. hydrate a current body HostSingleton with `onClick`;
3. let the nested boundary client-render a replacement button;
4. dispatch a bubbling click from that replacement;
5. require the current body's React `onClick` to fire.

This exercises the current DOM -> Fiber/props association through React event dispatch rather than inspecting private expandos.

### Required remaining red

The experiment deliberately must **not** solve:

- server-owned attribute versus later external attribute;
- contributed `style.color` versus later imperative `backgroundColor`;
- body DSIH bytes that escaped from the boundary into the root preamble.

Those remain separate property/child ownership lanes.

## Why unconditional detach looks conceptually wrong

A server preamble marker tells the client that a boundary contributed state to a persistent singleton, but there is no corresponding HostSingleton Fiber object representing that old server contribution on the client.

If no client owner is bound, omitting detach is effectively a no-op for ownership state.

If a client owner is bound, unconditional detach removes state that belongs to a different lifecycle owner.

Actual HostSingleton deletion/release still has its normal reconciler Fiber and should continue using normal release semantics.

## Remaining questions

- Verify whether any recovery path intentionally relies on marker cleanup detaching a stale current association before another singleton acquisition. The current experiment's focused and broader hydration tests should catch the obvious case.
- Verify event mapping in development and production if the first experiment passes.
- If property metadata is later added to markers, preserve this owner rule rather than reintroducing detach as a cleanup epilogue.

## Disposition

**EXECUTE as a narrow child experiment.**

A pass would justify treating current-client-owner preservation as an independent preamble repair. It would still leave marker property metadata and opaque child ownership unresolved.

## Evidence class

Source/history read plus target-test-prepared React PR 43. No semantic execution receipt yet. Public upstream interaction: none.
