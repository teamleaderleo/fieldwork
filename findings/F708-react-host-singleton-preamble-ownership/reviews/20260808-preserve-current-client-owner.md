# Preamble cleanup — preserve the current client HostSingleton owner

## Narrow question

Should clearing an old Fizz singleton preamble contribution call `detachDeletedInstance(instance)` on the persistent singleton DOM node after hydration may already have associated that node with the current client HostSingleton Fiber and props?

## Source/history result

**The current detach has no boundary-specific owner token and was inherited from the old broad singleton release implementation.**

Before public PR 37112, `releaseSingletonInstance(instance)` cleared every singleton attribute and then called `detachDeletedInstance(instance)`.

PR 37112 made normal HostSingleton release props-aware and split marker cleanup into `clearSingletonPreambleContribution(instance)`. The new marker helper retained the same clear-all-attributes plus `detachDeletedInstance(instance)` behavior because the server marker has no HostSingleton Fiber/props payload.

No separate server-contribution Fiber handle was introduced for that detach.

## Current hydration ordering confirmed

Current public main `2042572329425f9ebf35ae6287ea5bab72b2c497` still binds the persistent singleton during render/complete work.

The HostSingleton complete-work path calls:

`prepareToHydrateHostInstance(workInProgress, currentHostContext)`

when `popHydrationState()` reports a hydrated singleton.

Current `prepareToHydrateHostInstance()` directly calls the renderer's:

`hydrateInstance(instance, type, props, hostContext, fiber)`

and React DOM's current `hydrateInstance()` immediately executes:

- `precacheFiberNode(internalInstanceHandle, instance)`;
- `updateFiberProps(instance, props)`.

Only after that does it run `hydrateProperties(...)`.

So nested dehydrated-boundary cleanup during commit can indeed encounter a persistent body/head/html node already associated with the current render's HostSingleton Fiber and props.

### `bindInstance()` does not invalidate this conclusion

Current React DOM also contains a `bindInstance()` helper with a comment saying HostSingleton hydration association should eventually happen only on commit because render can fail/restart and only one Fiber can own the singleton.

That helper is evidence that the current render-phase binding is itself recognized as a lifecycle concern. It is **not** the active replacement for `hydrateInstance()` yet: the current hydration path above still performs the eager association.

If a future public change actually moves singleton binding to commit, reevaluate this entire lane before promotion. At current main, the eager-binding premise is real.

## Consequence

The DOM -> Fiber/props association present when `clearSingletonPreambleContribution()` runs may be the **freshly hydrated current client owner**, not an old server contribution.

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

## Mirror-image risk: abandoned hydration work

The eager binding itself means render failure/restart can transiently associate a persistent singleton with work that never commits. That is exactly the concern called out by the `bindInstance()` comment.

Do not assume deleting marker-path detach is the final global answer to eager-binding cleanup.

The narrow claim is only that a **server contribution marker has no old Fiber token proving authority to detach whatever mapping currently exists**.

If abandoned hydration work needs cleanup, it should be handled by a lifecycle path that knows which Fiber association it is retiring, or by the planned commit-time binding move, rather than by an unrelated marker unconditionally deleting the singleton's current mapping.

## Remaining questions

- Verify whether any recovery path intentionally relies on marker cleanup detaching a stale association before another singleton acquisition.
- If PR 43 passes, add a forced hydration restart/client-render control so preserving current mapping is tested against abandoned-work cleanup too.
- Verify event mapping in development and production if the first experiment passes.
- If property metadata is later added to markers, preserve this owner rule rather than reintroducing detach as a cleanup epilogue.
- Revalidate immediately if public React moves HostSingleton hydration binding to the existing commit-time `bindInstance()` helper.

## Disposition

**EXECUTE as a narrow child experiment.**

A pass would justify treating current-client-owner preservation as an independent preamble repair under the current eager-binding implementation. It would still leave marker property metadata, opaque child ownership, and the broader render-phase binding lifecycle unresolved.

## Evidence class

Current-main source/history read plus target-test-prepared React PR 43. No semantic execution receipt yet. Public upstream interaction: none.
