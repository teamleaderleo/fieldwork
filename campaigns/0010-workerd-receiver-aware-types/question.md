# Campaign 0010 Question

## In simple words

workerd already rejects native host methods called with an unrelated JavaScript receiver. Its generated TypeScript declarations often describe those methods as freely reusable. We are deciding whether workerd can expose its existing runtime receiver policy in generated declarations without breaking static methods, handwritten overrides, generic owners, inherited globals, or legal Worker-global calls.

## Exact question

Can workerd generate receiver-aware TypeScript declarations that accurately represent installed JSG/V8 method policy across ordinary methods, context-global operations, handwritten overrides, inheritance, generics, and static methods, with bounded compatibility cost?

## Change thesis

### Current behaviour

Ordinary JSG methods are installed with an owning V8 signature. The runtime converts nullish receivers where Web IDL requires, accepts compatible global receivers, and rejects unrelated receivers. The declaration generator retains method arguments and results but does not normally expose the owning receiver.

### Consequence

An application can assign raw Worker `fetch` to a client field and later invoke it as a property. TypeScript accepts the property call, Bun and Node accept it at runtime, and workerd rejects it before network I/O. Local tests can therefore miss a production-only compatibility failure.

### Proposed improvement

- ordinary non-static JSG method: generate `this: OwningType`;
- context-global operation: generate the runtime-accepted owner/global/nullish receiver union on the interface and ambient declaration;
- static or explicitly receiver-free operation: preserve receiver independence;
- handwritten override without `this`: inherit generated policy;
- explicit handwritten receiver: preserve it;
- carry provenance through generator reparsing and override/global transforms.

### Evidence required

1. source trace from JSG registration to generated declarations;
2. native runtime matrix;
3. direct TypeScript call matrix;
4. override, generic, inheritance, static, and global-transform fixtures;
5. one exact-head target-native focused receipt or an honest feasibility limit;
6. representative compatibility measurement;
7. independent exact-head review.

### Boundary

TypeScript permits receiver information to be erased when a value is contextually widened to a plain callback type. Generated declarations can reject preserved-receiver mistakes earlier, but they cannot replace a native runtime regression or solve every TypeScript assignability path.

## Competing directions

1. **General generator policy with internal provenance.** Current owned-fork candidate; strongest fidelity, highest transform complexity.
2. **RTTI receiver metadata.** Cleaner long-term cross-consumer model, but widens schema and implementation scope.
3. **Handwritten `fetch` override only.** Smallest patch, but leaves ordinary receiver-sensitive JSG methods incorrect.
4. **Application wrapper and runtime test only.** Already protects Stensibly; leaves ecosystem diagnostic gap.
5. **Typed lint rule.** Useful only with reliable provenance or a tiny allowlist; existing generic lint is incomplete.

## Stop condition

Stop after recording a defensible decision on whether the general generator candidate is ready for upstream review, requires maintainer direction, should be reduced to a narrower patch, or should remain a published finding plus local mitigation.
