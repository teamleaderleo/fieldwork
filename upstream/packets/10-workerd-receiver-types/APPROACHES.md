# Approaches — unit 10

## Selected approach: generated receiver provenance through transforms

Generate a marked owning receiver for every non-static JSG method, preserve or deliberately replace that policy during handwritten override and Worker-global transforms, then remove the marker before final declaration output.

Why selected:

- follows the runtime's ordinary owning-signature model;
- uses the parent type context already present in the generator;
- keeps explicit handwritten receiver choices authoritative;
- supports inherited and generic declarations;
- makes global widening an explicit transformation;
- supports targeted regression fixtures.

Exact source: https://github.com/teamleaderleo/workerd/compare/7cdc8c0e089287c8f3643f3a6f668ecdc221722a...f167a283fc9f792c427eeded306c38602e60261d

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

### Resolve inherited globals from a simple-name map

Same-named declarations in separate namespaces make the lookup ambiguous. Rejected after exact source review. The selected implementation uses the checker first and a unique generated fallback.

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

## Commit-series recommendation

The current clean branch uses one commit so the exact semantically reviewed carrier blobs remain easy to verify. Before public publication, a human may choose to split it into reviewable commits while preserving green tests at every commit:

1. receiver marker, generator hook, cleanup, and direct generator fixture;
2. override preservation plus generic replacement controls;
3. global extraction, lexical heritage resolution, static controls, and fetch call matrix.

Any split creates new exact heads and requires rerunning the target gates and complete-diff review.

## Rollback

Revert the clean source commit to restore receiver-free generated declarations. The merged Stensibly wrapper and runtime-parity regression remain valid independently.
