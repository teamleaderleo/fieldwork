# Preamble cleanup — current client owner detach hypothesis

## Initial hypothesis

`clearSingletonPreambleContribution(instance)` ends by calling `detachDeletedInstance(instance)` even though the Fizz contribution marker has no HostSingleton Fiber handle of its own.

Current HostSingleton hydration still binds the persistent DOM node during complete work through `hydrateInstance()`, which immediately calls:

- `precacheFiberNode(internalInstanceHandle, instance)`;
- `updateFiberProps(instance, props)`.

So it is mechanically possible for later boundary cleanup to delete a Fiber/props mapping that was installed during the current render.

This led to a synthetic public-API control where a `<!--body-->` marker was manually placed inside a body whose HostSingleton Fiber sits outside the nested Suspense boundary. Current marker cleanup can detach that body's mapping, and a later click from the replacement child can miss the body's React event props.

## Critical lifecycle correction

**That synthetic arrangement is not the normal Fizz ownership shape.**

Fizz emits a body preamble contribution marker because the `<body>` itself came from the boundary-local preamble.

In a real errored/dehydrated boundary takeover:

1. the server fallback/body contribution owns the marker;
2. mutation cleanup can detach the old singleton association;
3. the client-rendered replacement body HostSingleton is part of that same boundary's new tree;
4. singleton acquisition can subsequently bind the persistent body to the replacement Fiber/props before the commit completes.

Therefore the synthetic event failure may demonstrate only that an arbitrary manually forged marker can detach an unrelated current body owner. It does **not** yet prove a real Fizz application loses final body event ownership.

## Current `bindInstance()` note

Current React DOM contains a `bindInstance()` helper with a comment that hydrated HostSingleton association should eventually happen only on commit because render may fail/restart and only one Fiber can own the singleton.

Current hydration still eagerly binds through `hydrateInstance()`, so the render-phase association concern remains real in source. But that concern is broader than marker cleanup and does not rescue the synthetic test as a valid product reproducer.

## React PR 43 reclassified

Owned React PR 43 is now a **falsification lane**, not a source-repair candidate.

The no-detach source patch remains on the branch only as historical experiment material. Its workflow no longer applies it.

Instead the workflow applies two tests to untouched source:

### Real-Fizz control — required pass

A Suspense boundary server-renders a fallback `<body>`. On the client the errored boundary renders a primary `<body onClick={...}>` with a button.

After takeover, a bubbling click from the primary button must still reach the body's React `onClick`.

If current source passes, the normal lifecycle successfully restores current owner association and the no-detach repair is unnecessary for this symptom.

### Synthetic marker control — required fail

The earlier manually constructed marker arrangement remains as a contrast. It is expected to expose the detach behavior because no replacement body acquisition occurs afterward.

That difference is the point of the verifier: distinguish raw helper behavior from a reachable Fizz lifecycle bug.

## Disposition

**HOLD / EXPECT FALSIFICATION.**

Do not use the synthetic event regression as load-bearing evidence for #708 unless the real-Fizz control also fails.

If current source passes the real lifecycle, close/reject PR 43 and remove “current client event association” from the active preamble repair requirements.

The following #708 problems remain independent regardless of PR 43:

- broad contributed attribute cleanup;
- per-style-property ownership;
- body DSIH child provenance;
- control-comment collisions for naive boundary-stream DSIH;
- qualified inline-marker adoption-authority risk.

## Evidence class

Current-main source/history read plus target-test-prepared real-Fizz falsification in PR 43. No semantic execution receipt yet. Public upstream interaction: none.
