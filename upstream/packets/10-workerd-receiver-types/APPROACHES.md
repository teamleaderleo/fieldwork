# Approaches — unit 10

## Selected approach: generated receiver provenance through transforms

Generate a marked owning receiver for every non-static generated JSG method, preserve or deliberately replace that policy during handwritten override and Worker-global transforms, then remove the marker before final declaration output.

Why selected:

- follows the runtime's ordinary owning-signature model;
- uses the parent type context already present in the generator;
- keeps explicit handwritten receiver choices authoritative;
- supports inherited, generic, and renamed declarations;
- makes global widening an explicit transformation;
- preserves static global constants while excluding static methods from ambient function extraction;
- supports targeted regression fixtures;
- preserves ordinary callback assignment compatibility when TypeScript widens the method to a receiver-free function type.

Exact source: https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584

## Selected runtime boundary

Annotate generated method surfaces whose runtime callbacks use the owning V8 signature:

- ordinary methods;
- iterator and async-iterator symbol methods;
- synchronous and asynchronous disposal symbol methods.

Do not change:

- static methods on constructors;
- callable resource call signatures, which use an instance call handler rather than ordinary method registration;
- properties and accessors, which have no explicit TypeScript invocation receiver.

Retain pre-existing ambient extraction for generated static properties/constants.

## Selected commit presentation: one atomic commit

Keep the source and target-native tests in one commit.

The seams are coupled:

1. The generator marker and cleanup must land together or internal receiver types leak into output.
2. Override preservation must land with generation or handwritten replacements silently erase receiver policy.
3. Worker-global widening must land with generation or legal bare/global/nullish calls become type-invalid.
4. Static method exclusion must retain static property/constant extraction in the same transform revision.
5. The end-to-end and type fixtures must land with the implementation to satisfy workerd's per-commit build/test discipline.

A generator / overrides / globals split creates knowingly incomplete intermediate semantics and repeated output churn. The one-commit diff is larger, yet it represents one declaration-fidelity invariant and every changed file participates in that invariant.

## Current detachability conclusion

Current public workerd contains no `JSG_DETACHED_METHOD` or `registerDetachedMethod` implementation. Closed unmerged PR #2352 proposed a separate macro and runtime registration path for receiver-independent instance operations.

This supports the selected default:

- ordinary `JSG_METHOD` → owning receiver;
- `JSG_ITERABLE`, `JSG_ASYNC_ITERABLE`, `JSG_DISPOSE`, `JSG_ASYNC_DISPOSE` → owning receiver;
- `JSG_STATIC_METHOD` → static receiver-free member;
- callable resource instance → unchanged call signature;
- any future detached instance registration → new RTTI flag and generator branch, outside this unit until such runtime support exists.

Reopen broad-generation policy only if current source identifies an ordinary owning registration whose runtime callback deliberately omits the V8 signature.

## Considered alternatives

### Hard-code only Worker `fetch`

Smallest visible patch, yet it duplicates one runtime policy by hand and leaves other ordinary receiver-sensitive JSG methods receiver-free. Rejected as incomplete.

### Add an unmarked `this: OwningType` only at generation

Receiver origin disappears when declarations are printed and reparsed. Later overrides cannot distinguish generated policy from explicit handwritten `this`. Rejected after override and global tests exposed loss.

### Use transient AST identity or side tables

The pipeline reparses generated text, so object identity cannot survive. A side table would need stable cross-pass keys and would duplicate declaration matching. The internal wrapper is simpler and reviewable.

### Preserve every first parameter named `this`

This would treat explicit `this: void` and custom receiver unions as generated policy. Rejected because handwritten declarations are intentional source contracts.

### Widen every global receiver

Broad widening could weaken explicit custom receiver policy and hide invalid rebinding. Selected implementation widens only marked generated receivers during context-global extraction.

### Use generated owner parameters for full replacements

A replacement emits its own type parameters. Inheriting hidden generated parameters can create undeclared identifiers. Rejected by the `Owner<T>` → nongeneric `Owner` counterexample.

### Specialize replacement generics but ignore type renames

A full replacement may emit `RenamedOwner<U>` while the inherited receiver still references `Owner` or `Owner<U>`. Rejected because that creates a dangling or semantically wrong owner. The selected pipeline applies the replacement's type parameters and then runs the existing rename visitor over the receiver owner. A direct regression requires `RenamedOwner<U>` in the final marker.

### Resolve inherited globals from a simple-name map

Same-named declarations in separate namespaces make the lookup ambiguous. Rejected after exact source review. The selected implementation uses the checker for lexical identity and the transformed top-level declaration for post-override members.

### Use only the pre-transform checker declaration

The checker points at the original source tree. After an override transforms a superclass, following the old declaration discards transformed members and generated receiver markers. Rejected by the end-to-end failure reproduced in validation run `30690050452` and repaired by transformed top-level lookup.

### Exclude every static member from global extraction

Rejected after exact-head review `4834296945`. JSG constants are represented as static readonly properties, and the blanket return removed their existing ambient `const` declarations. The selected implementation excludes only static methods; static properties/constants preserve prior extraction.

### Keep extracting static methods as ambient globals

Rejected. Static methods live on constructors, are not inherited by global-scope instances, and should not become free global functions. The fixture now distinguishes them from static constants.

### Annotate callable resource signatures as ordinary methods

Rejected. Callable resources use an instance call-handler registration and are represented as call signatures, not named methods. This unit follows ordinary method ownership and leaves callable semantics unchanged.

### Rely on runtime checks alone

The application wrapper and native regression remain required, though runtime-only detection gives later feedback. Rejected as the sole solution.

### Rely on `@typescript-eslint/unbound-method`

The rule catches ordinary member extraction but misses bare ambient assignments and can report legal mixed-global receiver detachment. Rejected as the primary remedy.

### Add a broad custom lint rule

A model rule can detect receiver erasure, but production use needs provenance or a narrow host-symbol list and adds tooling cost. Deferred.

### Propose a TypeScript language change

Existing explicit-`this` semantics express the direct call matrix. Receiver information can still be widened away, which is ordinary assignability behavior. No language proposal recommended.

### Change Bun or Node

Both intentionally use receiver-independent server-global `fetch` behavior. Rejected; the target contract is workerd declaration fidelity.

### Relax JSG/V8 receiver enforcement

The runtime behavior follows ordinary host-operation ownership and browser-compatible precedent. Rejected and outside unit scope.

## Known boundary

Qualified heritage that resolves to a transformed nested declaration is outside the current generated source model. The globals transformer preserves checker-resolved nested lexical identity but only substitutes transformed top-level declarations. Reopen this boundary if workerd begins generating namespace-nested classes used in `ServiceWorkerGlobalScope` heritage.

## Rollback

Revert the clean source commit to restore receiver-free generated declarations. The merged Stensibly wrapper and runtime-parity regression remain valid independently.
