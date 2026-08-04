# Inherited Worker-global receivers — unit 10

## Decision

Do not widen generated receivers on the shared `ServiceWorkerGlobalScope` ancestry.

Native workerd execution shows that Worker-global fallback depends on the Worker-global method surface, not merely on the method's shared ancestor type. Ordinary `EventTarget` instances remain strict.

The former hierarchy-wide repair design is rejected.

## Current candidate shape

Implementation head: `teamleaderleo/workerd@18a117c28773cd7aa0ee599e03439c5fbbf06584`.

The candidate currently does two different things:

1. generated declarations retain an internal owner marker until the final receiver transform;
2. direct Worker-global methods and extracted ambient global functions receive a context-global receiver union;
3. inherited methods remain declared only on their ordinary ancestor owner.

Approximate output:

```ts
declare class EventTarget<EventMap extends Record<string, Event>> {
  addEventListener<Type extends keyof EventMap>(
    this: EventTarget<EventMap>,
    type: Type,
    handler: EventListenerOrEventListenerObject<EventMap[Type]>,
  ): void;
}

declare function addEventListener<Type extends keyof WorkerGlobalScopeEventMap>(
  this:
    | EventTarget<WorkerGlobalScopeEventMap>
    | typeof globalThis
    | null
    | void,
  type: Type,
  handler: EventListenerOrEventListenerObject<WorkerGlobalScopeEventMap[Type]>,
): void;
```

This means the ambient free global reflects Worker-global fallback, while `self.addEventListener` still inherits the strict `EventTarget` declaration.

## Exact native evidence

Owned carrier:

- PR: `teamleaderleo/workerd#9`;
- carrier head: `159fe1e87253ae79f5b2b767d49074f1ebeb447d`;
- product candidate: `18a117c28773cd7aa0ee599e03439c5fbbf06584`;
- run: `30857633684`;
- job: `91832245048`;
- conclusion: success.

The probe builds workerd and characterizes function values obtained from:

- `self.addEventListener`;
- `new EventTarget().addEventListener`.

Observed and asserted Worker-global-derived behavior:

| Invocation | Result |
| --- | --- |
| bare | success |
| `.call(undefined, ...)` | success |
| `.call(null, ...)` | success |
| `.call(globalThis, ...)` | success |
| `.call(self, ...)` | success |
| `.call({}, ...)` | `Illegal invocation` |

Observed and asserted separate-`EventTarget` behavior:

| Invocation | Result |
| --- | --- |
| bare | `Illegal invocation` |
| owning target | success |
| unrelated object | `Illegal invocation` |

This is the runtime discriminator the previous TypeScript model lacked.

## Why the ancestry-wide model is unsound

The rejected design recursively found `ServiceWorkerGlobalScope`, `WorkerGlobalScope`, and `EventTarget`, then widened marked receivers on every declaration in that ancestry.

That would emit an ordinary shared declaration similar to:

```ts
declare class EventTarget<EventMap extends Record<string, Event>> {
  addEventListener<Type extends keyof EventMap>(
    this: EventTarget<EventMap> | typeof globalThis | null | void,
    type: Type,
    handler: EventListenerOrEventListenerObject<EventMap[Type]>,
  ): void;
}
```

It would then accept a bare function detached from `new EventTarget()`, even though native workerd throws `Illegal invocation`. That is a runtime false negative and is worse than the current Worker-global TypeScript false positive.

The PR #10 patch and its hierarchy-wide acceptance theory must remain preserved as a rejected experiment, not applied to the canonical source branch.

## Correct repair boundary

The shared ancestor remains owner-strict.

A more accurate type model, if it can be expressed without destabilizing overloads, is a Worker-global-local shadow:

```ts
interface ServiceWorkerGlobalScope extends WorkerGlobalScope {
  addEventListener<Type extends keyof WorkerGlobalScopeEventMap>(
    this: ServiceWorkerGlobalScope | null | void,
    type: Type,
    handler: EventListenerOrEventListenerObject<WorkerGlobalScopeEventMap[Type]>,
  ): void;
}
```

The exact receiver may include the emitted Worker-global owner and/or the selected global type. It must be proven against generated ambient and importable output rather than assumed.

Required properties:

1. `self.addEventListener` gets Worker-global fallback behavior;
2. `new EventTarget().addEventListener` remains owner-strict;
3. inherited overload/event-map specificity is preserved;
4. no duplicate or order-dependent overload set is introduced;
5. explicit handwritten receivers remain untouched;
6. static members and constants remain unchanged;
7. ambient extracted globals retain their current legal call forms.

## Repository-compatible implementation direction

Use the existing transformed declaration map and heritage lookup in `types/src/transforms/globals.ts`.

Do not change the low-level printer or add a second receiver-marker system. If implemented, the global transform should:

1. resolve the transformed `ServiceWorkerGlobalScope` declaration;
2. identify inherited generated methods visible on the Worker-global surface;
3. synthesize only the minimum local method declarations needed for that surface;
4. apply the existing context-global receiver rewrite to those local declarations;
5. leave ancestor declarations unchanged;
6. use the same local surface for ambient global extraction;
7. avoid copying properties, constructors, call signatures, static methods, or constants.

Before implementation, use a small TypeScript 5.8.3 model to test explicit-`this` override compatibility and overload selection.

## Test design

Start with `dispatchEvent` because it is not overloaded by event-map key and produces a clean receiver diagnostic.

Then test `addEventListener` separately for overload and event-map behavior.

Required compile controls:

```ts
const fromSelf = self.dispatchEvent;
fromSelf(new Event("x"));
fromSelf.call(undefined, new Event("x"));
fromSelf.call(null, new Event("x"));
fromSelf.call(globalThis, new Event("x"));
fromSelf.call(self, new Event("x"));
// @ts-expect-error unrelated receiver
fromSelf.call({}, new Event("x"));

const target = new EventTarget();
const fromTarget = target.dispatchEvent;
// @ts-expect-error detached ordinary owner
fromTarget(new Event("x"));
fromTarget.call(target, new Event("x"));
// @ts-expect-error global is not the separate owner
fromTarget.call(globalThis, new Event("x"));
```

For `addEventListener`, additionally verify keyed event inference and handler type remain intact.

## Fallback if local shadowing is not sound

Do not widen the shared ancestor.

If TypeScript inheritance rules, overload ordering, generated declaration merging, or snapshot compatibility make a local shadow unreliable, retain the current strict inherited declaration and document the remaining false positive:

- native workerd permits detachment from `self`;
- TypeScript cannot distinguish a method function by the object from which it was read when the only declaration lives on a shared ancestor;
- ambient extracted globals remain correctly widened;
- ordinary owner safety remains correct.

A bounded false positive is preferable to accepting calls that workerd rejects.

## Current disposition impact

The runtime policy is settled. The unit remains `REPAIR` for stale generator fixtures, the optional local-shadow investigation, snapshot materialization, and final exact-head validation.