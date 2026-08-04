# Worker-global inherited method surface — unit 10

## Purpose

This record describes the narrow repair that replaces the rejected ancestry-wide receiver rewrite.

Source candidate before the localized repair:

- repository: `teamleaderleo/workerd`;
- branch: `unit-10/receiver-aware-types`;
- head after stale fixture repair: `a1628283d6160c1b8ebbfcc34b50cd5e73945977`;
- clean experimental output branch: `unit-10/worker-global-surface-repair`;
- guarded carrier: `teamleaderleo/workerd#13`.

## Runtime boundary

The native workerd matrix establishes two distinct method surfaces:

1. `self.addEventListener` supports the Worker-global bare/nullish/global fallback and rejects unrelated objects.
2. `new EventTarget().addEventListener` remains an ordinary owning method and rejects detached calls.

The same shared `EventTarget` declaration cannot be widened without admitting runtime-invalid ordinary-object calls.

## Selected declaration model

Keep the generated shared ancestor strict:

```ts
declare class EventTarget<EventMap extends Record<string, Event>> {
  addEventListener<Type extends keyof EventMap>(
    this: EventTarget<EventMap>,
    type: Type,
    handler: EventListenerOrEventListenerObject<EventMap[Type]>,
  ): void;
}
```

Add inherited generated methods locally to the transformed `ServiceWorkerGlobalScope` surface:

```ts
interface ServiceWorkerGlobalScope extends WorkerGlobalScope {
  addEventListener<Type extends keyof WorkerGlobalScopeEventMap>(
    this:
      | EventTarget<WorkerGlobalScopeEventMap>
      | typeof globalThis
      | null
      | void,
    type: Type,
    handler: EventListenerOrEventListenerObject<
      WorkerGlobalScopeEventMap[Type]
    >,
  ): void;
}
```

The original owner remains in the union. This preserves legal explicit EventTarget receivers while adding only the Worker-global fallback forms demonstrated by runtime execution.

## Repository-style implementation

The repair stays inside `types/src/transforms/globals.ts` and reuses existing mechanisms:

- transformed top-level declaration lookup;
- checker-backed lexical heritage resolution;
- generic type-argument inlining;
- the existing generated receiver marker;
- the existing context-global receiver rewrite;
- immutable TypeScript factory updates;
- receiver cleanup after global transformation.

It does not modify the printer, generator marker format, override compiler, importable transformer, or ambient transformer.

The intended transform sequence is:

1. widen direct generated methods declared on `ServiceWorkerGlobalScope`;
2. walk its transformed heritage declarations;
3. copy only generated, non-static, identifier-named inherited methods onto the local Worker-global surface;
4. preserve the nearest declaration's overload set and type-argument specialization;
5. leave shared ancestor declarations unchanged;
6. extract ambient free globals from the pre-shadow declaration so functions are not emitted twice;
7. clean the generated marker before comments, ambient, and importable output are finalized.

## Output scope

The current generated hierarchy contributes three inherited EventTarget methods:

- `addEventListener`;
- `removeEventListener`;
- `dispatchEvent`.

No properties, accessors, constructors, static methods, static constants, call signatures, or symbol-named methods are copied by this repair.

## Receiver type choice

Retain `typeof globalThis` in the Worker-global fallback union.

A TypeScript 5.8.3 consumer model shows that the generated ambient bundle declares:

```ts
declare const self: ServiceWorkerGlobalScope;
```

but does not narrow the consumer's `globalThis` to `ServiceWorkerGlobalScope`. Replacing `typeof globalThis` with only `ServiceWorkerGlobalScope` therefore rejects the actual `globalThis` expression in ordinary consumer compilation.

This host-global reference is an existing limitation of direct Worker-global methods as well as the new inherited shadows. Changing the complete global typing model is outside this unit.

## Target tests

### Exact transform output

`types/test/transforms/globals.spec.ts` must show:

- strict methods retained on `EventTarget<EventMap>`;
- local widened inherited signatures appended to `ServiceWorkerGlobalScope`;
- one ambient function per inherited method;
- no duplicated ambient functions;
- static method exclusion and static constant extraction unchanged.

### Generated declaration type fixture

`types/test/types/inherited-global-receiver.ts` must prove:

- `self.dispatchEvent` supports bare, undefined, null, `globalThis`, and `self` calls;
- an unrelated receiver is rejected;
- an ordinary `EventTarget` detached method remains rejected;
- the ordinary owner remains accepted;
- `self.addEventListener("fetch", ...)` retains `FetchEvent` inference;
- an incompatible keyed handler is rejected.

`dispatchEvent` is the primary receiver discriminator because it avoids generic overload ambiguity. `addEventListener` separately protects keyed event-map behavior.

## Review risks

Review the generated source-and-snapshot diff for:

1. duplicate inherited overloads;
2. loss of nearest-declaration hiding;
3. accidental static method or property copying;
4. copied inherited methods appearing on shared ancestors;
5. receiver-marker leakage;
6. ambient/importable disagreement;
7. consumer-host `globalThis` broadening beyond the already accepted global-method model;
8. generated comments appearing in unstable or duplicated positions.

## Acceptance rule

Accept the localized shadow only if focused transform/type tests, complete `//types/...`, lint, build, ambient/importable generation, snapshot checks, and exact native invariants all pass.

If the local shadow creates unstable overloads or declaration incompatibilities, remove it and retain the strict inherited declaration. Do not fall back to hierarchy-wide widening.