# L02 — TypeScript and typed-tooling evidence

## In simple words

TypeScript can express the direct legal receiver set with an explicit `this` union. It rejects wrong property receivers while the function keeps that type. The protection can disappear when code widens the value to a plain callback. Existing `unbound-method` lint catches some method extraction but misses important bare-global assignments and reports at least one legal Worker-global detachment pattern. A small complementary rule worked in a synthetic matrix, but it needs reliable host-function provenance before production use.

## Ownership

- Worker: Tess lane, materialized by campaign coordinator
- Parent: #230
- Claim scope: interface
- Source branch: `teamleaderleo/stensibly:research/issue-474-lane-b`
- Primary owned records: `teamleaderleo/stensibly#474` and the Tess review packet on `teamleaderleo/stensibly#483`
- Upstream contact authorized: no

## Tested environment

- TypeScript `5.8.3`
- ESLint `10.7.0`
- typescript-eslint `8.65.0`
- Node `22.23.1`

Representative declaration:

```ts
interface WorkerGlobalReceiver {
  fetch(
    this: void | null | WorkerGlobalReceiver,
    input: string,
  ): Promise<string>;
}

type ReceiverAwareFetch = WorkerGlobalReceiver["fetch"];
```

The synthetic receiver owner used a nominal `unique symbol` member so unrelated objects could not satisfy it structurally.

## Direct TypeScript result

The explicit receiver type accepts:

- bare invocation;
- invocation through the legal owner;
- `call(undefined, ...)`;
- `call(null, ...)`;
- `call(owner, ...)`;
- corresponding legal `bind` forms.

It rejects:

- a precise unrelated property holder;
- `call({} as unrelated, ...)`;
- `bind({} as unrelated)`;
- wrong receiver forms preserved through precise inference.

The extended generated-shape fixture covered 22 cases across assignments, object literals, destructuring, callback parameters, widening, `bind`, and `call`.

## Receiver erasure

TypeScript permits a receiver-aware function to be widened to a plain callback:

```ts
const widened: (input: string) => Promise<string> = fetch;
({ fetch: widened }).fetch("x");
```

Once widened, the call-site receiver requirement is gone. Similar erasure occurs through:

- class-property assignment to a plain callback type;
- contextually typed object literals;
- plain callback parameters;
- explicit plain variable annotations;
- `OmitThisParameter`;
- assertions or `any`.

This is ordinary TypeScript assignability behaviour rather than a narrow demonstrated language defect. No TypeScript language issue is recommended.

## Existing lint result

`@typescript-eslint/unbound-method` reported owner-member extraction cases, including destructuring and widening from an ordinary member. It did not report equivalent bare ambient `fetch` assignments such as:

```ts
this.fetchImpl = fetch;
acceptsPlain(fetch);
const widened: PlainFetch = fetch;
```

It also reported legal destructuring of the mixed global receiver because the rule treats exact syntactic `this: void` as safely detachable, while a union containing `void`, `null`, and an owner still appears receiver-dependent.

## Complementary rule prototype

A typed proof-of-concept rule visited bare identifier value references and compared source and contextual callable types. It reported exactly the intended bare-global contextual erasures in the synthetic matrix.

The prototype deliberately ignored:

- direct calls;
- declaration positions and property names;
- inference without a contextual target;
- receiver-aware callback targets;
- `bind` and `call` operations.

A production rule would need one of:

1. generated JSDoc such as `@receiverSensitive`;
2. machine-readable declaration metadata;
3. a very small Worker host-symbol allowlist.

Without provenance, a general rule risks false positives against application callbacks. No typescript-eslint issue or general lint proposal is recommended from the current evidence.

## Review findings contributed to the candidate

Tess identified and required fixes for:

- handwritten overrides deleting generated receiver parameters;
- every override overload inheriting legacy receiver policy;
- explicit `this: void` and custom receiver preservation;
- generic owner specialization such as `EventTarget<EventMap>`;
- inherited global traversal using transformed declarations rather than stale checker nodes;
- `self.fetch` receiving the same context-global call set as ambient `fetch`;
- static members remaining receiver-free and unextracted;
- complete generator → overrides → global extraction coverage.

The latest visible independent disposition was `REPAIR` on workerd head `d08e2e968b6db600c220e2babe0a07befa728ba2` because two static ambient expectations were stale. The canonical candidate has moved and the old disposition is expired.

## Evidence labels

- **Observed:** compiler and lint diagnostics under the pinned tool versions.
- **Observed:** the custom rule's exact synthetic diagnostic set.
- **Inferred:** generated provenance could make a narrow complement production-worthy.
- **Unknown:** false-positive rate across the complete generated Workers API surface.

## Disposition

Complete as research. Keep explicit receiver declarations as the first diagnostic layer; retain the wrapper and native test as the final layer; defer a lint proposal until provenance or a narrow allowlist is justified.
