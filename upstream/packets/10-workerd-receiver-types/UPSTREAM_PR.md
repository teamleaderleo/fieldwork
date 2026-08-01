# Upstream pull-request draft — unit 10

> Internal draft. Public publication requires explicit human authorization and completed exact-head execution.

## Proposed title

`fix(types): generate receiver-aware TypeScript declarations`

## Proposed body

### Summary

- generate explicit TypeScript `this` parameters for ordinary non-static JSG methods;
- carry generated receiver provenance through declaration reparsing, handwritten overrides, and Worker-global extraction;
- preserve explicit `this: void` and custom handwritten receivers;
- bind full-replacement receivers only to type parameters declared by the replacement;
- widen generated context-global operations to their legal owner/global/nullish receiver set;
- exclude static members from owning receiver generation and ambient extraction;
- add generator, override, global, generic-replacement, lexical-resolution, static, and call-matrix coverage.

### Problem

JSG installs ordinary methods with an owning V8 signature. Generated declarations omit that receiver requirement, so TypeScript can accept calls through unrelated objects that workerd rejects with `Illegal invocation`.

This changes declaration generation only. Runtime receiver enforcement remains unchanged.

### Implementation

Initial generation marks receivers internally as `__JSG_GENERATED_RECEIVER__<Owner>`. The marker survives print/reparse, allows override/global passes to distinguish generated policy from explicit handwritten receivers, and is removed before final declaration output.

Ordinary methods emit `this: Owner`. Context-global generated operations emit `this: Owner | typeof globalThis | null | void`. Static methods emit no receiver. Full replacements specialize receivers from replacement-declared type parameters only.

### Tests

Focused targets:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  --test_output=errors
```

The fixtures cover legal bare/global/nullish/detached calls, invalid unrelated receivers, explicit receiver preservation, overloads, full replacement, generics, inherited globals, same-name namespaces, and static exclusion.

### Compatibility

Explicit receiver parameters can reveal source errors in code that rebinds native host methods. Callback widening can erase the receiver, so runtime validation remains necessary. Representative generated output should be reviewed before publication for intentional detachable APIs and recursive/global-type effects.

### Prior art

- workerd issue #6904 records the declaration mismatch;
- workerd issue #2716 and PR #2730 preserve receiver-sensitive Web Crypto behavior while binding a compatibility export;
- closed PR #2352 proposed selective detached JSG methods, reinforcing the distinction between ordinary owning methods and deliberate detachability.

### AI assistance

AI systems assisted with source navigation, fixture preparation, implementation, compatibility analysis, and review. The human author must review and be able to defend each claim and line and should adjust this disclosure to the target's current policy.

## Exact internal source

- owned PR: https://github.com/teamleaderleo/workerd/pull/5
- base: `7cdc8c0e089287c8f3643f3a6f668ecdc221722a`
- head: `f167a283fc9f792c427eeded306c38602e60261d`
- compare: https://github.com/teamleaderleo/workerd/compare/7cdc8c0e089287c8f3643f3a6f668ecdc221722a...f167a283fc9f792c427eeded306c38602e60261d

## Publication checklist

- [ ] focused exact-head target command passed;
- [ ] ordinary target gates passed;
- [ ] representative generated-output compatibility reviewed;
- [ ] independent complete-diff acceptance recorded;
- [ ] issue and PR text synchronized to final head;
- [ ] AI disclosure checked against current target expectations;
- [ ] human explicitly authorized public publication.
