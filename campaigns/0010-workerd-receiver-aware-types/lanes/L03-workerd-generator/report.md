# L03 — workerd generator and implementation evidence

## In simple words

The runtime already knows which object may receive an ordinary JSG method. The generated declaration pipeline loses that information. Adding one `this` parameter at initial generation is easy, but a correct broad change must carry the policy through handwritten overrides, generic type parameters, inherited Worker globals, context-global receiver widening, and final declaration printing. The owned fork now implements that broader policy. Its code is credible by inspection and fixture design, but the current exact head still lacks an independent final review and retained target-native execution receipt.

## Ownership

- Workers: Flare/Kestrel source lane, Rook implementation continuation, materialized by campaign coordinator
- Parent: #230
- Claim scope: interface
- Target pin: `cloudflare/workerd` release commit `6aa890be9fa547e3907c805b312e39917a274221` (`2026-07-28`)
- Canonical fork candidate: `teamleaderleo/workerd#1`
- Canonical branch: `research/issue-474-receiver-aware-types`
- Canonical head at materialization: `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`
- Archival execution carrier: `teamleaderleo/stensibly#483`
- Upstream discussion: [workerd declaration issue](https://redirect.github.com/cloudflare/workerd/issues/6904)
- New upstream contact authorized: no

## Source trace

At the pinned workerd revision:

1. `src/workerd/api/global-scope.h` registers `ServiceWorkerGlobalScope::fetch` through `JSG_METHOD(fetch)`.
2. `src/workerd/jsg/resource.h` creates and attaches a V8 `Signature` for ordinary instance methods.
3. V8 API invocation converts nullish receivers and validates compatibility against that signature. The inspected V8 source pin was `66b7bf5e0ddc117ecfd04b8d79066fef3d9eaf2b`.
4. `types/src/generator/structure.ts#createMethodPartial()` already receives the fully qualified parent name, but historically emitted only declared arguments and return type.
5. `types/src/transforms/overrides/index.ts` can replace generated members with handwritten declarations.
6. `types/src/transforms/globals.ts` extracts members of `ServiceWorkerGlobalScope` and its ancestors into ambient functions.

The receiver exists at installation and disappears at declaration generation and transformation.

Relevant prior direction:

- [intentionally detachable JSG method proposal](https://redirect.github.com/cloudflare/workerd/pull/2352)
- [receiver-sensitive crypto precedent](https://redirect.github.com/cloudflare/workerd/issues/2716)
- [follow-up binding change](https://redirect.github.com/cloudflare/workerd/pull/2730)

These precedents support selective receiver policy rather than declaring every operation either universally strict or universally detachable.

## Candidate architecture

### Initial generation

For every generated non-static JSG method, prepend a marked receiver:

```ts
this: __JSG_GENERATED_RECEIVER__<OwningType>
```

Static methods receive no generated receiver.

### Internal provenance

Generated nodes are printed and reparsed before later transforms. The candidate therefore carries provenance through an internal wrapper type rather than relying on transient AST identity. A cleanup transform unwraps the marker before final declarations are printed.

### Override handling

- legacy override without `this` inherits the generated marked receiver;
- each override overload inherits it;
- explicit `this: void` remains receiver-free;
- explicit custom receiver unions remain authoritative;
- full-replacement overrides preserve the policy;
- override type parameters specialize the owner, producing forms such as `EventTarget<EventMap>` rather than raw `EventTarget`.

### Context-global handling

For marked generated members inherited into `ServiceWorkerGlobalScope`, the candidate widens the receiver to:

```ts
OwningType | typeof globalThis | null | void
```

It applies the same policy to the interface member and the extracted ambient function. Explicit handwritten receivers are not widened merely because the first parameter is named `this`.

### Global traversal

The candidate indexes declarations from the transformed source before recursively traversing inherited globals. This avoids resolving stale pre-override declarations through the original type checker.

### Static boundary

Static methods and properties remain on constructors and are excluded from ambient global extraction.

## Fixture coverage

The candidate contains tests for:

- generator → override → global extraction;
- partial and full-replacement override overloads;
- explicit `this: void`;
- explicit custom receivers;
- generic and inherited owners;
- static methods and properties;
- direct, detached, `self`, and `globalThis` fetch forms;
- legal and illegal `call`, `apply`, `Reflect.apply`, and `bind` receivers;
- unrelated property holders;
- a client field storing raw `fetch`.

The generated snapshot demonstrates:

```ts
addEventListener<Type extends keyof EventMap>(
  this: EventTarget<EventMap>,
  type: Type,
  handler: (event: EventMap[Type]) => void,
): void;

receiverFree(this: void, value: string): string;

customReceiver(
  this: EventTarget<EventMap> | WorkerGlobalScope,
  value: string,
): string;

interface ServiceWorkerGlobalScope {
  fetch(
    this: ServiceWorkerGlobalScope | typeof globalThis | null | void,
    ...args: FetchArgs
  ): Promise<Response>;
}
```

## Review and execution history

Kestrel's first generator-only patch established feasibility but left receiver loss through overrides and a stricter `self.fetch` interface type. Tess's reviews exposed those issues.

Rook replaced the simple patch with provenance-aware transforms. Tess's latest visible review at `d08e2e968b6db600c220e2babe0a07befa728ba2` found the remaining implementation paths correct by inspection but requested removal of two stale static ambient expectations.

Between that review and the canonical head, the branch:

- removed the stale static expectations;
- adjusted generator and override fixtures;
- expanded CI timeout and runner selection.

The old review is expired because the head moved.

At `e7b15f8…`:

- Lint completed successfully.
- The focused receiver workflow was cancelled.
- repository Tests, Coverage, and CodSpeed were cancelled.

Those cancellations are execution-harness outcomes. They do not establish either correctness or a product failure.

## Implementation-size interpretation

The core generation hook is small. The candidate diff is larger because it makes policy survive existing transforms and adds regression coverage. A hard-coded `fetch` override could be much smaller, but it would not repair ordinary receiver-sensitive JSG declarations and would duplicate runtime policy by hand.

## Evidence labels

- **Documented/source-read:** JSG installation, generator, override, and global extraction paths.
- **Observed:** native runtime matrix and existing fixture failures that shaped the design.
- **Target-test-prepared:** final candidate fixtures at the canonical head.
- **Unknown:** exact-head target-native completion and representative full API compatibility.

## Disposition

`EXECUTE` followed by independent exact-head review. The candidate is the only implementation worth continuing; the Stensibly prototype PR is archival and should not be merged.
