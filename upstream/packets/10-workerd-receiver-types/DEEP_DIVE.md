# Deep dive — receiver-aware generated declarations

## Problem and runtime contract

Ordinary JSG instance methods are installed with a V8 holder signature. JavaScript property-call syntax supplies the object before the method as `this`; an unrelated holder therefore fails receiver validation before the C++ callback executes. Generated declarations currently describe parameters and return values while omitting the holder requirement.

Primary public record: https://github.com/cloudflare/workerd/issues/6904

Pinned runtime/source base used by the original investigation:

- workerd release commit: `6aa890be9fa547e3907c805b312e39917a274221`
- current public base used by the clean branch: `7cdc8c0e089287c8f3643f3a6f668ecdc221722a`
- base delta: three release commits; relevant source paths unchanged
- runtime registration: `src/workerd/api/global-scope.h`, `src/workerd/jsg/resource.h`
- declaration generation: `types/src/generator/structure.ts`
- handwritten merge: `types/src/transforms/overrides/index.ts`
- Worker-global extraction: `types/src/transforms/globals.ts`

Exact clean code links:

- generator hook: https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/src/generator/structure.ts
- provenance and cleanup: https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/src/receiver.ts
- override preservation: https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/src/transforms/overrides/index.ts
- global extraction and lexical resolution: https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/src/transforms/globals.ts
- transform ordering: https://github.com/teamleaderleo/workerd/blob/f167a283fc9f792c427eeded306c38602e60261d/types/src/index.ts

## Final declaration policy

```text
ordinary non-static generated JSG method
→ this: OwningType

context-global generated operation
→ this: OwningType | typeof globalThis | null | void
   on the Worker-global interface member and extracted ambient declaration

static method
→ no generated receiver and no ambient extraction

legacy handwritten override without `this`
→ inherit generated receiver policy

explicit handwritten receiver
→ preserve exactly

full class/interface replacement
→ specialize only with type parameters declared by the replacement
```

The internal type `__JSG_GENERATED_RECEIVER__<Owner>` carries origin through print/reparse and transformation. A final cleanup pass emits the owner type without exposing the marker.

## Why the diff extends beyond one parameter

The initial generator insertion is small. Correct behavior must survive:

- print-and-reparse boundaries;
- partial member overrides and overload replacement;
- full class/interface replacement;
- explicit `this: void` and custom receiver unions;
- generic owner specialization;
- inherited Worker-global traversal;
- same-named declarations in separate namespaces;
- global receiver widening;
- static member exclusion.

## Defect and repair history

### 1. Static ambient expectations

Review at carrier head `d08e2e968b6db600c220e2babe0a07befa728ba2` found fixtures still expecting static members to become ambient globals. The expectations were removed. Static methods receive no owning receiver and remain on constructors.

### 2. Ambiguous lexical heritage lookup

Review at carrier head `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a` found that a simple-name declaration map could choose `Other.Base` while resolving top-level `Base`. The repair resolves original heritage expressions through the TypeScript checker first, retains transformed type arguments, and uses generated declarations only as a unique fallback.

### 3. Generic full replacement

Review at carrier head `54926f86c95185a7b83b2bf1ea901c35876a9a58` found that a generated `Owner<T>` fully replaced by nongeneric `Owner` could emit `this: Owner<T>` without declaring `T`. Repair PR https://github.com/teamleaderleo/workerd/pull/2 changed specialization to use only `override.typeParameters` and added three controls:

- generic generated → nongeneric replacement;
- generic generated → generic replacement;
- nongeneric generated → generic replacement.

Current carrier head `0ecc0a6632747031a6650c49a401760e511c9f36` contains all three repairs. Review `4827890474` accepted the source repair and required exact-head execution.

## Runtime and application evidence

The reusable matrix on https://github.com/teamleaderleo/stensibly/pull/482 established:

- bare, detached, `undefined`, `null`, `globalThis`, and `self` receiver forms succeed in pinned native workerd;
- unrelated holder, `call`, `apply`, and `bind` receivers fail with `Illegal invocation`;
- Bun and Node accept the unrelated receiver forms as their server-global compatibility behavior;
- the real `HttpGitHubOAuthClient` default wrapper reaches a local outbound Worker under native workerd.

Merged safeguard: `f19c2c7aa09fc4d4fdb7e7ae2d4d727d0eedd091`.

## TypeScript boundary

TypeScript 5.8.3 supports one explicit union receiver and rejects an unrelated holder while the exact type is retained. Contextual assignment to a plain callback can erase the receiver. Therefore generated declarations improve early diagnostics while the runtime wrapper and native regression remain necessary.

Research branches and records:

- https://github.com/teamleaderleo/stensibly/issues/474
- `research/issue-474-lane-a`
- `research/issue-474-lane-b`
- archival execution carrier: https://github.com/teamleaderleo/stensibly/pull/483
- canonical workerd research carrier: https://github.com/teamleaderleo/workerd/pull/1

## Prior art

- https://github.com/cloudflare/workerd/issues/2716 — receiver-sensitive Web Crypto call reported as illegal invocation.
- https://github.com/cloudflare/workerd/pull/2730 — compatibility export binds `crypto.getRandomValues`, while `crypto.webcrypto.getRandomValues` remains receiver-sensitive.
- https://github.com/cloudflare/workerd/pull/2352 — unmerged selective `JSG_DETACHED_METHOD` proposal; supports distinguishing ordinary owning methods from deliberately detachable operations.
- https://github.com/microsoft/TypeScript/issues/15, https://github.com/microsoft/TypeScript/issues/3694, and https://github.com/microsoft/TypeScript/pull/6739 — explicit invocation-receiver checking precedent.
- https://github.com/oven-sh/bun/issues/36268 — Bun confirmed Node-compatible receiver-independent global `fetch` behavior.

## Compatibility questions for final review

1. Does broad generation annotate any operation that is intentionally detachable despite ordinary JSG registration?
2. Should the receiver be the declaring owner or leaf generated owner for every inherited API?
3. Do explicit receiver parameters cause unacceptable source breaks for callback assignment patterns, even though those patterns may fail at runtime?
4. Does `OwningType | typeof globalThis | null | void` introduce recursive or excessively large generated types on representative real output?
5. Should the change land as one coherent commit or as a test/provenance sequence, given workerd's preference for small reviewable commits?
