# Global receiver type design — unit 10

## In simple words

The current candidate uses `typeof globalThis` in legal Worker-global receiver unions. That precisely names the actual ambient global in a Worker project, but importable declarations evaluate `typeof globalThis` in the consumer's environment. A Node consumer importing Worker types could therefore get the Node global type accepted as a receiver even though workerd would reject that object.

A cleaner environment-independent option is `ServiceWorkerGlobalScope`, provided the generated ambient `globalThis` is structurally assignable to that interface. The generated snapshot and a direct compiler assertion must decide this before publication.

## Current candidate

Current implementation head `18a117c28773cd7aa0ee599e03439c5fbbf06584` widens generated context-global receivers to:

```ts
Owner | typeof globalThis | null | void
```

Advantages:

- directly accepts the actual ambient `globalThis` type;
- already passes the retained TypeScript direct-call model;
- works for direct and extracted global operations.

Limit:

- `typeof globalThis` is resolved in the consumer's compilation environment;
- importable types can be consumed under Node, browser DOM, or another host library;
- the union may therefore accept a host global object that is not the workerd Worker global at runtime.

Evidence label: **Inferred importable-type risk** pending generated-bundle execution.

## Alternative

Widen global-ancestry receivers to:

```ts
Owner | ServiceWorkerGlobalScope | null | void
```

For a direct `ServiceWorkerGlobalScope` method this reduces to the owner plus nullish forms. For inherited owners such as `EventTarget<EventMap>`, the root interface represents the legal Worker-global subtype without depending on the consumer's ambient host.

Advantages:

- environment-independent in importable output;
- more directly states the runtime condition: the receiver may be the ordinary owner or the Worker-global root;
- avoids accepting Node or browser globals merely because they are the consumer's `globalThis`;
- likely produces smaller and less recursive declaration output.

Required proof:

```ts
const ambientWorkerGlobal: ServiceWorkerGlobalScope = globalThis;
```

must compile against the generated ambient Workers bundle for latest and experimental entrypoints.

Potential issue:

- current Workers generation flattens global members into free declarations rather than explicitly declaring the TypeScript global object as `ServiceWorkerGlobalScope`;
- structural assignability may fail if `typeof globalThis` lacks one or more interface-only members or has incompatible overloads.

## Decision experiment

After PR #9 or PR #10 produces generated output:

1. compile the exact ambient latest snapshot plus:

   ```ts
   const latestGlobal: ServiceWorkerGlobalScope = globalThis;
   ```

2. compile the exact ambient experimental snapshot with the same assertion;
3. compile the importable bundle under a Node-oriented config and inspect the receiver type of representative methods;
4. compare the current `typeof globalThis` union with the root-interface alternative for:
   - `fetch`;
   - `EventTarget.addEventListener`;
   - a `WorkerGlobalScope`-declared method;
   - a direct `ServiceWorkerGlobalScope` method;
5. retain compiler diagnostics and output-size differences.

## Selection rule

Prefer `ServiceWorkerGlobalScope` if both generated ambient bundles assign `globalThis` to it without casts and the full type package remains green.

Retain `typeof globalThis` only if the root-interface form rejects the actual generated ambient global or causes a larger compatibility regression that cannot be repaired within this unit.

If `typeof globalThis` remains, the upstream compatibility section must disclose that importable types resolve it against the consumer host and can admit non-workerd global objects.

## Interaction with inherited-global repair

The ancestry repair and global receiver member are separate decisions:

- ancestry selection decides **which owner declarations** receive global/nullish permission;
- this file decides **which type represents the legal Worker global** in that union.

Do not materialize the ancestry repair on canonical source until both questions are settled or the chosen source explicitly records the remaining importable limitation.
