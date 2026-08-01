# Upstream pull-request draft — unit 10

> Internal draft. Public publication requires explicit human authorization and completed exact-head execution.

## Proposed title

`Generate receiver-aware TypeScript methods`

## Proposed body

### Summary

- generate explicit TypeScript `this` parameters for ordinary non-static JSG methods;
- carry generated receiver provenance through declaration reparsing, handwritten overrides, and Worker-global extraction;
- preserve explicit `this: void` and custom handwritten receivers;
- bind full-replacement receivers only to type parameters declared by the replacement;
- widen generated context-global operations to their legal owner/global/nullish receiver set;
- exclude static members from owning receiver generation and ambient extraction;
- add generator, override, global, generic-replacement, lexical-resolution, transformed-heritage, static, callback-erasure, and call-matrix coverage.

### Problem

JSG installs ordinary methods with an owning V8 signature. Generated declarations omit that receiver requirement, so TypeScript can accept calls through unrelated objects that workerd rejects with `Illegal invocation`.

This changes declaration generation only. Runtime receiver enforcement remains unchanged.

### Implementation

Initial generation marks receivers internally as `__JSG_GENERATED_RECEIVER__<Owner>`. The marker survives print/reparse, allows override and global passes to distinguish generated policy from explicit handwritten receivers, and is removed before final declaration output.

Ordinary methods emit `this: Owner`. Context-global generated operations emit `this: Owner | typeof globalThis | null | void`. Static methods emit no receiver. Full replacements specialize receivers from replacement-declared type parameters only.

Global heritage lookup uses the TypeScript checker to establish lexical identity, then follows the corresponding transformed top-level declaration so override-added members and generated receiver markers survive extraction.

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

The fixtures cover legal bare/global/nullish/detached calls, invalid unrelated receivers, ordinary callback assignment, explicit receiver preservation, overloads, full replacement, generics, inherited globals, same-name namespaces, transformed heritage, and static exclusion.

### Compatibility

The change reveals source errors where code retains the receiver-aware method type and rebinds a host method to an unrelated object. Those calls already fail at runtime.

Assignment to an ordinary receiver-free callback type remains accepted and erases the explicit `this` parameter under TypeScript's existing function assignability rules. Runtime validation therefore remains necessary.

Current workerd source contains no detached-method registration path. Closed PR #2352 proposed a distinct `JSG_DETACHED_METHOD` macro, reinforcing the distinction between ordinary owning methods and deliberate receiver-independent instance operations. A future detached registration would need an RTTI flag and generator branch.

### Commit organization

The implementation is one commit because generation, override preservation, global widening, cleanup, and their fixtures form one atomic declaration invariant. Splitting them would create intermediate commits that either lose receivers through overrides or reject legal Worker-global calls.

### AI assistance

This change was developed with AI assistance. The author remains responsible for every implementation detail, test, compatibility claim, and submitted line.

## Exact internal source

- owned PR: https://github.com/teamleaderleo/workerd/pull/5
- base: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b`
- head: `8f41da276852ad48735c1d817b7c1a3699ac8beb`
- compare: https://github.com/teamleaderleo/workerd/compare/d82c2a45a8695aac30d4d24828ce1ee7fb11909b...8f41da276852ad48735c1d817b7c1a3699ac8beb

## Publication checklist

- [ ] focused exact-head target command passed;
- [ ] ordinary target gates passed;
- [ ] representative ambient and importable generated output reviewed;
- [ ] independent complete-diff acceptance recorded;
- [x] issue and PR text synchronized to current source direction;
- [x] commit and PR draft include current AI-assistance disclosure;
- [ ] human explicitly authorized public publication.
