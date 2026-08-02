# Upstream pull-request draft — unit 10

> Internal draft. Public publication requires explicit human authorization, completed exact-head execution, settled inherited-global semantics, and committed generated snapshots.

## Proposed title

`Generate receiver-aware TypeScript declarations`

## Draft readiness

**Not ready to publish.**

The current implementation head is coherent, but three source-changing items remain:

1. inherited methods in the `ServiceWorkerGlobalScope` ancestry may need global/nullish widening on their original declarations;
2. the legal Worker-global receiver member must be selected between `typeof globalThis` and `ServiceWorkerGlobalScope` from generated ambient/importable evidence;
3. target-required latest and experimental snapshots must be generated and committed.

## Proposed body after those decisions settle

### Summary

- generate explicit TypeScript `this` parameters for ordinary non-static JSG methods;
- carry generated receiver provenance through declaration reparsing, handwritten overrides, full replacements, renames, and Worker-global extraction;
- preserve explicit `this: void` and custom handwritten receivers;
- specialize and rename replacement receivers from the replacement declaration;
- widen only generated methods whose owners are legal Worker-global receivers;
- keep static methods receiver-free and out of ambient function extraction while preserving generated ambient constants;
- leave callable resource call signatures and properties unchanged;
- regenerate and commit exact latest and experimental ambient/importable snapshots;
- add generator, override, heritage, static-constant, replacement, callback-erasure, inherited-global, and call-matrix coverage.

### Problem

JSG installs ordinary methods with an owning V8 signature. Generated declarations omit that receiver requirement, so TypeScript accepts some calls through unrelated objects that workerd rejects with `Illegal invocation`.

The inverse mismatch can also occur if only extracted global functions are widened: a function read from `self.addEventListener` still inherits an owner-only `EventTarget` receiver even though V8 converts nullish receivers to the compatible Worker global proxy before applying the signature.

This contribution changes declaration generation only. Runtime receiver enforcement remains unchanged.

### Implementation

Initial generation marks receivers internally as `__JSG_GENERATED_RECEIVER__<Owner>`. The marker survives print/reparse and lets later transforms distinguish generated ownership from explicit handwritten receiver contracts. Cleanup removes the marker before public output.

The final global policy will be selected from exact execution:

- ordinary non-global owner → `this: Owner`;
- owner in the exact transformed Worker-global ancestry → `this: Owner | <WorkerGlobalReceiver> | null | void`;
- explicit handwritten receiver → unchanged;
- static method → no receiver;
- static generated property/constant → existing ambient constant behavior;
- callable resource signature → unchanged.

Global heritage resolution uses the TypeScript checker for lexical identity and follows the corresponding transformed top-level declaration so override-added members and generated receiver markers survive.

### Runtime registration boundary

Current JSG registration uses the owning V8 signature for ordinary methods, iterator/async-iterator symbols, and disposal/async-disposal symbols. Callable resources use a separate instance call-handler surface. Current public source has no detached-method registration path.

### Tests

Final focused targets will include:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  //types:test/types/inherited-global-receiver \
  --test_output=errors
```

Ordinary gates:

```console
bazelisk test //types/... --test_output=errors
bazelisk test //types:types_lib@eslint --test_output=errors
bazelisk build //types
```

Native workerd coverage distinguishes bare, nullish, global, owning, and unrelated receivers for inherited `EventTarget` methods.

Generated output will be reviewed for marker leakage, owner resolution, recursive unions, static constant preservation, callable stability, latest/experimental differences, and unintended changes outside the Worker-global ancestry.

### Compatibility

Executed TypeScript models establish:

- implementations, object literals, and subclass overrides do not need to spell explicit `this` parameters;
- receiver-aware methods remain assignable to ordinary receiver-free callbacks;
- `OmitThisParameter` remains available;
- partial-holder property calls can now fail compilation when they would fail at runtime;
- structural typing cannot prove native identity;
- browser/Worker standard-library overload merging can reintroduce receiver-free overloads;
- importable output must avoid accepting an unrelated consumer-host global if a Worker-root receiver type can represent the legal global.

Current workerd source contains no detached-method registration path. Closed PR #2352 proposed a distinct detached macro, reinforcing the need for explicit runtime metadata before any generated method is treated as receiver-independent.

### Commit organization

Use two final commits:

1. one atomic implementation and target-native test commit;
2. one generator-produced snapshot commit matching `just generate-types` output.

This matches recent accepted workerd type-change history and keeps generated output auditable without hand edits.

### Review routing

Current CODEOWNERS routes `/types/` to the Wrangler team; experimental snapshot changes additionally route to runtime and Durable Objects teams. The final PR needs both TypeScript declaration compatibility review and JSG/runtime receiver-semantics review.

### AI assistance

This change was developed with AI assistance. The author remains responsible for every implementation detail, test, compatibility claim, generated snapshot, and submitted line.

## Exact internal state

- source PR: https://github.com/teamleaderleo/workerd/pull/5
- base: `813c31394b9909d8f557bba14324db275bc12720`
- current implementation head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- exact implementation carrier and native probe: https://github.com/teamleaderleo/workerd/pull/9 at `fbed6bc84e4de0051af069acb44d65776466f2d1`, run `30755965427`
- inherited-global repair carrier: https://github.com/teamleaderleo/workerd/pull/10 at `6d2d5fcc67523f75bf8e0589a291fc26576b3a35`, run `30756418899`
- final source head: pending semantic selection and snapshot materialization

## Publication checklist

- [ ] native inherited-global behavior established;
- [ ] repaired hierarchy policy passes focused and complete type gates;
- [ ] global receiver member selected from ambient/importable evidence;
- [ ] exact generated latest and experimental snapshots committed;
- [ ] static constants and callable signatures confirmed unchanged where expected;
- [ ] both carrier workflows absent from final source;
- [ ] independent types and runtime review recorded on the final exact head;
- [x] AI assistance disclosure prepared;
- [ ] human explicitly authorized public publication.
