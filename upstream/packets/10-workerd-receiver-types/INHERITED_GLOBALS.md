# Inherited Worker-global receivers — unit 10

## In simple words

The current candidate widens methods declared directly on `ServiceWorkerGlobalScope` and the free ambient functions copied from its ancestors. It does not widen the original ancestor declarations themselves.

That means the generated free `addEventListener` type accepts a bare or nullish call, but a function obtained from `self.addEventListener` still has `this: EventTarget<...>` and TypeScript rejects the same legal runtime call. This file records the source proof, a TypeScript reproduction, the native probe, and the bounded repair design.

## Exact question

For a generated ordinary method whose owning type is in the `ServiceWorkerGlobalScope` inheritance chain, should its original declaration accept:

```text
Owner | typeof globalThis | null | void
```

rather than limiting that widening to the extracted ambient free function?

This is not a question about unrelated objects. They remain illegal.

## Source-read evidence

### V8 receiver conversion

Current V8 `Builtins::InvokeApiFunction()` performs receiver conversion before calling the API callback when the supplied receiver is not already a JavaScript receiver:

- `src/builtins/builtins-api.cc`
- inspected revision: `v8/v8@bf3d02947968c33781ad7a74e5e0234d9ac5d748`

The relevant sequence is:

1. for a non-constructor API call, if the receiver is not a `JSReceiver`, call `Object::ConvertReceiver()`;
2. `Object::ConvertReceiver()` maps `null` and `undefined` to the isolate's global proxy and boxes other primitives;
3. `HandleApiCallHelper()` then checks the converted receiver against the function template's signature;
4. a compatible global proxy proceeds; an unrelated object throws `Illegal invocation`.

Evidence labels: **Documented source behavior** and **Inferred application to all owning API callbacks**.

### workerd registration

Current workerd ordinary methods, iterator/async-iterator symbols, and dispose/async-dispose symbols use `MethodCallback` with the owning V8 signature. `ServiceWorkerGlobalScope` inherits from `WorkerGlobalScope`, which inherits from `EventTarget<WorkerGlobalScopeEventMap>`.

Therefore a bare or nullish call to an `EventTarget` method function converts to the Worker global proxy, which is compatible with the `EventTarget` signature. The same conversion applies whether the function value was read from `self` or from another `EventTarget` instance.

Callable resource instances remain a separate call-handler surface and are outside this question.

Evidence label: **Source-read mechanism** pending native execution.

## Current candidate declaration shape

Implementation head: `teamleaderleo/workerd@18a117c28773cd7aa0ee599e03439c5fbbf06584`.

The candidate emits approximately:

```ts
declare class EventTarget<EventMap extends Record<string, Event>> {
  addEventListener<Type extends keyof EventMap>(
    this: EventTarget<EventMap>,
    type: Type,
    handler: EventListenerOrEventListenerObject<EventMap[Type]>,
  ): void;
}

interface ServiceWorkerGlobalScope
  extends WorkerGlobalScope {
  // addEventListener remains inherited from EventTarget
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

Consequences:

- `const f = addEventListener; f(...)` is accepted;
- `const f = self.addEventListener; f(...)` is rejected;
- both function values reach the same owning V8 callback at runtime.

## Executed TypeScript model

Environment:

```text
TypeScript 5.8.3
Node 22.16.0
--strict --noEmit --lib es2022
```

The model declared owner-only `EventTarget` methods, a widened free global, and `self: ServiceWorkerGlobalScope`.

Observed diagnostics:

```text
TS2684: The 'this' context of type 'void' is not assignable to method's 'this' of type 'EventTarget<WorkerGlobalScopeEventMap>'.
TS2345: Argument of type 'undefined' is not assignable to parameter of type 'EventTarget<WorkerGlobalScopeEventMap>'.
```

The failures were produced by:

```ts
const fromSelf = self.addEventListener;
fromSelf("fetch", handler);
fromSelf.call(undefined, "fetch", handler);
```

A second model widened the ancestor method itself to:

```ts
this: EventTarget<EventMap> | typeof globalThis | null | void
```

It accepted:

- bare calls;
- `undefined` and `null` receivers;
- `globalThis` and `self` receivers;
- the actual owning `EventTarget` instance;

and continued rejecting `{}` through `@ts-expect-error` controls. The widened model completed with exit code `0`.

Evidence label: **Model-executed**.

## Native workerd probe

Owned execution carrier:

- PR: `teamleaderleo/workerd#9`
- carrier head: `fbed6bc84e4de0051af069acb44d65776466f2d1`
- custom run: `30755965427`
- product candidate pinned by workflow: `18a117c28773cd7aa0ee599e03439c5fbbf06584`

The fork-only probe builds workerd and executes a temporary `.wd-test` covering a method value read from:

1. `self.addEventListener`;
2. `new EventTarget().addEventListener`.

For each, it checks:

- bare call;
- `.call(undefined, ...)`;
- `.call(null, ...)`;
- `.call(globalThis, ...)`;
- `.call(self, ...)`;
- actual owning receiver;
- unrelated `{}` receiver.

Expected source-derived result:

- bare/nullish/global/owning forms succeed;
- unrelated object throws `Illegal invocation`.

The native result is pending. A queued job is not evidence.

## Bounded repair design if the native probe confirms

Do not copy inherited methods onto `ServiceWorkerGlobalScope`. Redeclaration would duplicate overload sets and make `.call()` behavior dependent on overload ordering.

Instead, widen marked generated receivers on every transformed top-level declaration in the `ServiceWorkerGlobalScope` heritage chain:

1. collect transformed top-level declarations after override processing;
2. find `ServiceWorkerGlobalScope`;
3. resolve its heritage recursively using the existing checker-guided lexical identity plus transformed-declaration lookup;
4. replace each declaration in that exact ancestry with a version whose marked generated method receivers use the context-global union;
5. leave explicit handwritten receivers unchanged;
6. leave static methods, properties, constants, call signatures, and declarations outside the global ancestry unchanged;
7. use the same widened declaration map for ambient global extraction.

Expected examples:

```ts
// Global ancestry: widened.
declare class EventTarget<EventMap extends Record<string, Event>> {
  addEventListener<Type extends keyof EventMap>(
    this: EventTarget<EventMap> | typeof globalThis | null | void,
    type: Type,
    handler: EventListenerOrEventListenerObject<EventMap[Type]>,
  ): void;
}

// Not in the global ancestry: remains owner-only.
declare class CryptoKey {
  someMethod(this: CryptoKey): void;
}
```

Why this boundary is selected:

- V8 nullish conversion is callback-wide, not tied to the property from which the function value was read;
- the global proxy is compatible only with owners in the Worker-global inheritance chain;
- widening every generated method would incorrectly accept nullish calls for owners the global proxy does not implement;
- widening only copied free functions creates the reproduced false positive.

## Required source controls

If repaired, add or update:

1. `types/test/index.spec.ts`
   - `EventTarget` generated receivers in the global ancestry widen;
   - unrelated `ReplacementTarget` remains owner-only;
   - extracted free globals remain widened.
2. `types/test/transforms/globals.spec.ts`
   - transformed root and ancestor declarations both widen;
   - explicit `this: void` and custom receivers remain unchanged;
   - static method exclusion and static constant preservation remain intact.
3. `types/test/types/inherited-global-receiver.ts`
   - `self.addEventListener` detachment accepts bare/nullish/global/owning forms;
   - a method detached from `new EventTarget()` accepts the same forms;
   - unrelated object receivers remain rejected.
4. Generated snapshot review
   - only declarations in the exact Worker-global ancestry receive the broader union;
   - no unrelated owner type is widened;
   - no duplicate inherited overloads are introduced;
   - ambient and importable output type-check.

## Reversal conditions

Do not widen ancestor declarations if the native probe shows any of the following:

- a bare or nullish function read from `self.addEventListener` throws;
- the result differs from the same callback read from a fresh `EventTarget`;
- workerd configures these methods as strict API functions that bypass `Object::ConvertReceiver`;
- widening creates an unresolved or recursive output that cannot be bounded without a larger design change.

In that case retain the current source direction, record the TypeScript limitation, and keep the free-global widening only.

## Current disposition impact

This question is independently capable of changing the source. Unit 10 remains `REPAIR` even before snapshot materialization because exact runtime/type alignment for inherited Worker-global methods is not yet settled.
