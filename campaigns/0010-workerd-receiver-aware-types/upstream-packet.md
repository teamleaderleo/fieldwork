# Draft upstream packet — workerd receiver-aware generated declarations

> **Status: internal draft. Do not publish.**
>
> This packet records a possible future pull request against `cloudflare/workerd`. Publication requires explicit human approval after Campaign #230's clearing conditions pass.

## In simple words

workerd already rejects ordinary native methods called through the wrong object. Generated Worker TypeScript declarations usually omit that receiver rule, so invalid rebinding can compile and even pass under Bun or Node before failing in workerd. The candidate teaches the generator to preserve the runtime receiver policy through handwritten overrides and Worker-global extraction. The local production incident is already fixed independently.

## Proposed title

```text
Generate receiver-aware TypeScript declarations for JSG methods
```

## Proposed summary

- generate explicit TypeScript `this` parameters for receiver-sensitive non-static JSG methods;
- preserve generated receiver policy through handwritten override overloads and replacements;
- keep explicit receiver-free and custom handwritten receivers authoritative;
- specialize generic owner receivers;
- widen generated context-global operations to the nullish/global receiver set accepted by workerd;
- exclude static members from owning receiver generation and ambient global extraction;
- add generator, override, global-transform, and fetch call-matrix coverage.

## Problem statement

JSG installs ordinary methods with an owning V8 signature. Current workerd rejects an unrelated receiver with `Illegal invocation`, but generated declarations present the method as receiver-free.

A representative failure is:

```ts
class Client {
  fetchImpl = fetch;

  run() {
    return this.fetchImpl("data:text/plain,ok");
  }
}
```

Property-call syntax supplies the `Client` instance as `this`. TypeScript accepts the declaration today. Bun and Node also execute the call because their server-global fetch wrappers ignore the receiver. workerd and Chromium reject it before outbound I/O.

The already-submitted [declaration-fidelity issue](https://redirect.github.com/cloudflare/workerd/issues/6904) contains the original source and runtime trace.

## Runtime contract established

For Worker-global `fetch`, workerd accepts:

```js
fetch(url);
globalThis.fetch(url);
self.fetch(url);

const operation = self.fetch;
operation(url);
operation.call(undefined, url);
operation.call(null, url);
operation.call(globalThis, url);
operation.call(self, url);
```

It rejects unrelated objects and unrelated property holders across direct property calls, `call`, `apply`, and `bind`.

This proposal changes declarations only. It does not relax JSG/V8 runtime enforcement.

## Proposed declaration policy

```text
ordinary non-static JSG method
→ this: OwningType

context-global JSG operation
→ this: OwningType | typeof globalThis | null | void
   on the interface and ambient declaration

static method
→ no generated owning receiver

legacy handwritten override without this
→ inherit generated receiver

explicit handwritten this
→ preserve exactly
```

## Candidate implementation

The owned-fork prototype uses an internal generated-receiver wrapper because generated declarations are printed and reparsed before override and global transforms run:

```ts
this: __JSG_GENERATED_RECEIVER__<OwningType>
```

The marker:

1. is emitted during initial non-static method generation;
2. survives reparsing;
3. is inherited by old overrides that omit `this`;
4. is specialized with override type parameters;
5. is widened only for generated context-global operations;
6. is unwrapped by a cleanup transform before final output.

This avoids treating every leading parameter named `this` as generated policy and therefore preserves explicit `this: void` and custom receiver unions.

Canonical owned-fork candidate:

- `teamleaderleo/workerd#1`
- branch `research/issue-474-receiver-aware-types`
- campaign materialization head `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`
- pinned base `6aa890be9fa547e3907c805b312e39917a274221`

## Test plan

### Small generator/compiler gate

Construct synthetic RTTI covering:

- ordinary method;
- static method and property;
- legacy override and overloads;
- explicit `this: void`;
- explicit custom receiver;
- generic inherited owner;
- context-global fetch-like method.

Run the real declaration transforms in memory, capture emitted text, and compile a legal/illegal receiver matrix with TypeScript.

### Target-native focused gate

Run:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  --test_output=errors
```

### Compatibility review

Inspect the complete generated declaration diff and representative APIs for:

- source breaks from explicit receivers;
- intentional detachable operations;
- generic owner changes;
- global type recursion;
- static and inherited member handling;
- handwritten override policy.

## Existing evidence

- Native workerd and Chromium reject unrelated Worker `fetch` receivers.
- Bun and Node intentionally accept them.
- TypeScript 5.8.3 represents the direct call set with an explicit receiver union.
- The owned application wrapper and native-workerd regression are merged through `teamleaderleo/stensibly#482`.
- The candidate includes broad generator and call-matrix fixtures.
- Lint passed at the materialized candidate head.

## Evidence still required before publication

- retained small exact-head generator/compiler receipt;
- completed focused target-native receipt or documented feasibility limit;
- independent complete-diff acceptance at the final head;
- representative generated-output compatibility measurement;
- current workerd contribution-policy review;
- appropriate AI-assistance disclosure.

## Compatibility and limits

- Explicit receiver parameters do not exist at runtime and do not change generated JavaScript.
- Legal nullish and Worker-global fetch calls remain represented.
- Callbacks widened to plain function types can still erase receiver information.
- A declaration change does not remove the need for runtime tests.
- Intentionally detachable operations need an explicit policy boundary rather than silent inheritance from legacy receiver-free overrides.

## Rejected alternatives

### Hard-code only Worker `fetch`

Smaller, but duplicates one runtime policy by hand and leaves other receiver-sensitive JSG methods receiver-free.

### Add an unmarked `this: OwningType` and stop

Incorrect because handwritten overrides can replace the parameter list, generic owners can lose type arguments, and global operations need a different receiver set.

### Widen every explicit `this` in global extraction

Incorrect because explicit `this: void` and custom handwritten receivers are deliberate policy.

### Solve with lint only

Incomplete. Existing lint misses bare ambient receiver erasure, and a custom rule needs provenance or a narrow allowlist.

### Change runtime semantics

Out of scope and unnecessary. The runtime behaviour is intentional and compatible with browser host-operation enforcement.

## Rollback

The change is confined to declaration generation and tests. Reverting the generator/provenance transforms restores current declarations. The owned Stensibly wrapper and native-workerd regression remain valid regardless of upstream disposition.

## AI assistance

AI systems assisted with source navigation, fixture generation, candidate implementation, compatibility analysis, and review. Before submission, the human author must review and be able to defend every claim and line, and the disclosure must be adjusted to workerd's current contribution policy.
