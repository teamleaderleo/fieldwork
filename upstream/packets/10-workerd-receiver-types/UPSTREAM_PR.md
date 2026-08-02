# Upstream pull-request draft — unit 10

> Internal draft. Public publication requires explicit human authorization, completed exact-head execution, and committed generated snapshots.

## Proposed title

`Generate receiver-aware TypeScript declarations`

## Draft readiness

**Not ready to publish yet.** The implementation head is coherent, but target policy requires regenerated `types/generated-snapshot/` files. Exact carrier PR #9 is producing those outputs for review and later materialization onto source PR #5.

## Proposed body

### Summary

- generate explicit TypeScript `this` parameters for ordinary non-static JSG methods;
- carry generated receiver provenance through declaration reparsing, handwritten overrides, and Worker-global extraction;
- preserve explicit `this: void` and custom handwritten receivers;
- specialize and rename full-replacement receivers from the replacement declaration;
- widen generated context-global operations to their legal owner/global/nullish receiver set;
- keep static methods receiver-free and out of ambient function extraction while preserving generated ambient constants;
- regenerate and commit the affected Workers type snapshots;
- add generator, override, global, generic-replacement, renamed-replacement, lexical-resolution, transformed-heritage, static-constant, callback-erasure, and call-matrix coverage.

### Problem

JSG installs ordinary methods with an owning V8 signature. Generated declarations omit that receiver requirement, so TypeScript can accept calls through unrelated objects that workerd rejects with `Illegal invocation`.

This changes declaration generation only. Runtime receiver enforcement remains unchanged.

### Implementation

Initial generation marks receivers internally as `__JSG_GENERATED_RECEIVER__<Owner>`. The marker survives print/reparse, allows override and global passes to distinguish generated policy from explicit handwritten receivers, and is removed before final declaration output.

Ordinary methods emit `this: Owner`. Context-global generated operations emit `this: Owner | typeof globalThis | null | void`. Static methods emit no receiver. Full replacements use the replacement's declared generics and emitted name.

Global heritage lookup uses the TypeScript checker to establish lexical identity, then follows the corresponding transformed top-level declaration so override-added members and generated receiver markers survive extraction.

Static method exclusion is applied only to method declarations/signatures. Generated static readonly constants retain the existing ambient `const` extraction path.

### Runtime registration boundary

Current JSG registration uses the owning V8 signature for ordinary methods, iterator/async-iterator symbols, and disposal/async-disposal symbols. Callable resource instances use a separate call-handler surface and are unchanged by this patch. Current public source has no detached-method registration path.

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

Ordinary gates:

```console
bazelisk test //types/... --test_output=errors
bazelisk test //types:types_lib@eslint --test_output=errors
bazelisk build //types
```

The fixtures cover legal bare/global/nullish/detached calls, invalid unrelated receivers, ordinary callback assignment, explicit receiver preservation, overloads, full replacement, renamed replacement generics, inherited globals, same-name namespaces, transformed heritage, static method exclusion, and static constant preservation.

The generated snapshot diff will be included in the final source branch and reviewed for marker leakage, owner resolution, recursive global unions, callable stability, and unexpected declaration churn.

### Compatibility

The change reveals source errors where code retains the receiver-aware method type and rebinds a host method to an unrelated object. Those calls already fail at runtime.

Assignment to an ordinary receiver-free callback type remains accepted and erases the explicit `this` parameter under TypeScript's existing function assignability rules. Runtime validation therefore remains necessary.

Current workerd source contains no detached-method registration path. Closed PR #2352 proposed a distinct `JSG_DETACHED_METHOD` macro, reinforcing the distinction between ordinary owning methods and deliberate receiver-independent instance operations. A future detached registration would need an RTTI flag and generator branch.

Generated constants and callable resource signatures remain unchanged by design.

### Commit organization

Generation, override preservation, global widening, cleanup, and their fixtures form one atomic implementation invariant. Required generated snapshots may be folded into that commit or retained as one adjacent generated-output commit, provided each final commit satisfies target review expectations and the complete exact head is retested.

### AI assistance

This change was developed with AI assistance. The author remains responsible for every implementation detail, test, compatibility claim, generated snapshot, and submitted line.

## Exact internal source

- source PR: https://github.com/teamleaderleo/workerd/pull/5
- implementation base: `813c31394b9909d8f557bba14324db275bc12720`
- implementation head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- implementation compare: https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584
- snapshot carrier: https://github.com/teamleaderleo/workerd/pull/9 at `c232e306a796c4d9d43c9a72b5fd810f6f150082`
- final source head: pending snapshot materialization

## Publication checklist

- [ ] focused exact-head target command passed;
- [ ] complete `//types/...` and types lint passed;
- [ ] representative ambient and importable generated output reviewed;
- [ ] required `types/generated-snapshot/` files committed on source PR #5;
- [ ] static constants and callable signatures confirmed unchanged where expected;
- [ ] snapshot carrier closed and workflow absent from final source;
- [ ] independent complete-diff acceptance recorded on the final source-and-snapshot head;
- [x] issue and PR text synchronized to current source direction;
- [x] commit and PR draft include current AI-assistance disclosure;
- [ ] human explicitly authorized public publication.
