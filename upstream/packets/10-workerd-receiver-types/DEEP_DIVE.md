# Deep dive — receiver-aware generated declarations

## In simple words

Ordinary JSG methods already carry an owning runtime receiver. The generated declarations describe their arguments and return values while omitting that receiver, so TypeScript permits some rebindings that workerd rejects with `Illegal invocation`. The selected change carries an internal receiver marker through generation, handwritten overrides, and Worker-global extraction, then removes the marker from public output.

## Exact current source

- public base: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b` (`Release 2026-08-01`)
- clean owned source: `teamleaderleo/workerd:unit-10/receiver-aware-types`
- exact head: `8f41da276852ad48735c1d817b7c1a3699ac8beb`
- compare: https://github.com/teamleaderleo/workerd/compare/d82c2a45a8695aac30d4d24828ce1ee7fb11909b...8f41da276852ad48735c1d817b7c1a3699ac8beb
- source fence: one commit, ten `types/` source/test files, no workflows

The August 1 release changed only compatibility-date and release-version metadata relative to the prior July 31 base.

## Problem and runtime contract

Ordinary JSG instance methods are installed with a V8 holder signature. JavaScript property-call syntax supplies the object before the method as `this`; an unrelated holder therefore fails receiver validation before the C++ callback executes. Generated declarations currently omit this holder requirement.

Primary public discussion record: `cloudflare/workerd#6904`.

Relevant source boundaries:

- runtime registration: `src/workerd/api/global-scope.h`, `src/workerd/jsg/resource.h`
- declaration generation: `types/src/generator/structure.ts`
- handwritten merge: `types/src/transforms/overrides/index.ts`
- Worker-global extraction: `types/src/transforms/globals.ts`
- transform ordering and cleanup: `types/src/index.ts`, `types/src/receiver.ts`

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

assignment to a receiver-free callback type
→ allowed by normal TypeScript function assignability; receiver requirement erased
```

The internal type `__JSG_GENERATED_RECEIVER__<Owner>` carries origin through print/reparse and transformation. A final cleanup pass emits the owner type without exposing the marker.

## Why provenance is required

The generated AST is printed and reparsed before later transformations. Object identity and transient node metadata disappear at that boundary. Later passes need to distinguish two semantically different declarations:

- a receiver generated from ordinary JSG ownership, which may be inherited, specialized, or widened for a context global;
- a handwritten receiver such as `this: void` or a custom union, which is an intentional public contract and must remain authoritative.

The internal wrapper is durable TypeScript syntax during the private pipeline and disappears before public output.

## Transform interaction

### Generation

`createMethodPartial()` prepends a marked owner receiver to every non-static method. Static methods remain receiver-free.

### Handwritten overrides

Partial overrides written before receiver generation inherit a generated receiver when they replace a generated method and omit their own `this` parameter. Explicit receivers remain unchanged.

Full replacements use the replacement declaration's type parameters. This prevents a generic generated owner such as `Owner<T>` from leaking undeclared `T` into a nongeneric replacement.

### Worker-global extraction

Global extraction runs after overrides. Generated context-global receivers widen to:

```ts
Owner | typeof globalThis | null | void
```

This accepts bare, detached, actual-global, and nullish calls while rejecting unrelated holders when the exact method type is retained.

Heritage lookup uses the pre-transform TypeScript checker to establish lexical identity. For a top-level declaration, extraction then follows the corresponding transformed declaration so override-added members and receiver markers survive.

### Cleanup

The cleanup transformer unwraps every remaining internal receiver marker before class-to-interface, ambient, and importable output passes.

## Defect and repair history

### 1. Static ambient expectations

Early fixtures still expected static members to become ambient globals. Those expectations were removed. Static methods live on constructors, receive no owning receiver, and are excluded from ambient extraction.

### 2. Ambiguous lexical heritage lookup

A simple-name declaration map could select `Other.Base` while resolving top-level `Base`. The repair uses the checker for lexical identity and retains transformed type arguments.

### 3. Generic full replacement

A generated `Owner<T>` fully replaced by nongeneric `Owner` could emit `this: Owner<T>` without declaring `T`. Replacement specialization now uses only `override.typeParameters`, with generic-to-nongeneric, generic-to-generic, and nongeneric-to-generic controls.

### 4. Stale pre-transform heritage declaration

The checker points at the original source tree. After overrides transformed a superclass, global extraction followed that original declaration and discarded transformed members and generated receiver markers.

Validation run `30690050452` distinguished the defect:

- globals, override, and replacement-generic focused targets passed;
- the end-to-end generator target failed because inherited global methods lost their receiver;
- emitted `addEventListener` and `plain` declarations lacked the expected `this` parameter.

The repair keeps checker-guided lexical identity, then follows the corresponding transformed top-level declaration. Repaired validation run `30690396598` passed all four focused targets.

## Detachability research

Closed unmerged workerd PR #2352 proposed `JSG_DETACHED_METHOD` and a separate runtime registration path without an owning V8 signature. Current public source contains no equivalent detached-method registration implementation.

This gives a clean policy boundary:

- current ordinary `JSG_METHOD` registration is receiver-owning;
- current static registration remains receiver-free on the constructor;
- any future receiver-independent instance operation needs explicit runtime/RTTI metadata and a generator branch.

The generated declaration layer should follow runtime registration metadata once such a distinction exists. It should not guess detachability from method names.

## TypeScript compatibility boundary

Explicit `this` parameters improve diagnostics while the receiver-aware method type is retained. TypeScript intentionally allows assignment to a receiver-free callback type, erasing the receiver requirement. The final fixture records both sides:

- exact `typeof fetch` values reject unrelated holders, `.call()`, `.apply()`, and `.bind()` receivers;
- assignment to `(...args: Parameters<typeof fetch>) => ReturnType<typeof fetch>` remains accepted;
- property calls through that widened callback remain accepted by TypeScript and rely on runtime validation.

`Reflect.apply()` also types its receiver as `any`, leaving that path runtime-checked.

This compatibility behavior reduces source breakage for callback APIs while preserving earlier diagnostics in direct receiver-aware use.

## Runtime and application evidence

The retained native matrix established:

- bare, detached, `undefined`, `null`, `globalThis`, and `self` receiver forms succeed in pinned native workerd;
- unrelated holder, `call`, `apply`, and `bind` receivers fail with `Illegal invocation`;
- Bun and Node accept unrelated receiver forms as their server-global compatibility behavior;
- the owned production OAuth wrapper reaches a local outbound Worker under native workerd.

The downstream wrapper and runtime-parity regression remain useful because TypeScript receiver information can be widened away.

## Commit organization

Keep one atomic source commit.

A generator-only commit leaks incomplete semantics through later transforms. Adding override preservation without global widening makes legal Worker-global calls type-invalid. Global widening and cleanup depend on the generated marker. Matching fixtures must accompany each behavior under workerd's per-commit test discipline.

One commit preserves the invariant across generation, transformation, and public output. A file-based three-part split would produce intermediate revisions a reviewer could not safely merge or bisect as complete behavior.

## Current prior-art and overlap result

- public issue #6904 remains the discussion record;
- current search found no competing public implementation pull request;
- issue #2716 and merged PR #2730 demonstrate receiver-sensitive Web Crypto behavior and selective binding at a compatibility boundary;
- closed PR #2352 documents the unmerged separate detached-method design;
- TypeScript explicit-`this` precedent establishes the language mechanism used here.

## Compatibility and review questions

1. How many ambient and importable methods gain receivers in representative generated output?
2. Does any current ordinary JSG method intentionally tolerate an unrelated receiver at runtime?
3. Do owner/global/nullish unions create recursive expansion or editor-performance regression?
4. Are explicit handwritten receiver declarations byte-for-byte unchanged after the full pipeline?
5. Does every receiver owner resolve in ambient and importable output, including replacement generics?
6. Does standalone workerd generation require additional snapshot changes when consumed as a submodule of the larger Workers repository?

## Known limits

- callback widening and `Reflect.apply()` can erase or bypass static receiver checking;
- qualified heritage resolving to a transformed nested declaration remains outside the current top-level generated source model;
- generated-output size and editor impact remain unmeasured until the compatibility build completes;
- exact final-head execution remains required because the last source revision adds the callback-erasure type control.

## Rollback

Revert the one clean source commit to restore receiver-free generated declarations. The downstream wrapper and runtime-parity regression remain independently valid.
