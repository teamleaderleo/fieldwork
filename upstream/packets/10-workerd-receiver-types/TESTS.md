# Tests — unit 10

## Exact clean source

- base: `813c31394b9909d8f557bba14324db275bc12720`
- head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- compare: https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584
- owned draft PR: https://github.com/teamleaderleo/workerd/pull/5
- fence: one commit, ten source/test files, no workflow files

The August 2 upstream base differs from the prior August 1 base only in two release metadata files. The final head adds three controls beyond the last green semantic source: callback receiver erasure, static-global constant preservation, and renamed full-replacement receiver ownership.

## Test inventory in the clean diff

- `types/test/index.spec.ts`
  - generator snapshot and end-to-end transform ordering;
  - ordinary, explicit, generic, static, inherited, iterator-transformed, and global receiver output.
- `types/test/transforms/globals.spec.ts`
  - context-global widening;
  - static method exclusion;
  - static readonly property/constant preservation as ambient `const`;
  - lexical superclass selection when another namespace contains the same unqualified name;
  - transformed top-level heritage lookup after an earlier transformer replaces superclass members.
- `types/test/transforms/overrides/index.spec.ts`
  - partial and full override behavior;
  - explicit receiver preservation and overload handling;
  - existing type rename behavior across generated references.
- `types/test/transforms/overrides/replacement-receiver-generics.spec.ts`
  - generic generated owner → nongeneric replacement;
  - generic generated owner → generic replacement;
  - nongeneric generated owner → generic replacement;
  - renamed generic replacement updates the receiver owner and leaves no marker referencing the original name.
- `types/test/types/fetch-receiver.ts`
  - legal bare, detached, nullish, `globalThis`, `self`, `call`, `apply`, and `bind` forms;
  - expected diagnostics for unrelated holders and unrelated explicit receivers;
  - raw host function stored on an unrelated client;
  - accepted assignment to a receiver-free callback type, documenting normal TypeScript receiver erasure and source compatibility.

## Source-read registration controls

Current public `resource.h` shows the following use the owning `signature` with `MethodCallback`:

- ordinary methods;
- synchronous and asynchronous iterator symbol registrations;
- synchronous and asynchronous disposal symbol registrations.

Callable resources use `SetCallAsFunctionHandler` and are not ordinary generated method declarations. Static methods use the constructor registration path and remain receiver-free. These source-read distinctions define the output review matrix.

## Evidence classes

### Target-executed — repaired semantic source

Validation run `30690396598` checked out the repaired source fence and verified the carrier differed only by its workflow.

Focused command:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  --test_output=errors
```

Result: four of four targets passed after the transformed-heritage repair.

The immediately preceding run `30690050452` is a discriminating negative receipt:

- override, replacement-generic, and globals targets passed;
- `//types:test/index.spec` failed because inherited global methods lost receiver parameters;
- the output showed `addEventListener` and `plain` emitted without their expected receiver;
- source review traced this to global extraction following the pre-transform checker declaration;
- the current `getHeritageDeclaration()` repair selects the corresponding transformed top-level declaration.

This failure and repair provide stronger evidence than a green-only receipt because they distinguish the old and new implementations on the exact behavior under review.

### Review-executed — static constant negative result

Owned PR #5 review `4834296945` found that blanket static-member exclusion removed generated global constants. The review traced the behavior through `createConstantPartial()`, which represents JSG constants as static readonly class members.

Final-head repair:

- static check moved inside the method extraction branch;
- static methods remain unextracted;
- static properties/constants retain extraction;
- strict expected output now includes `declare const CONSTANT: 42`.

This is prepared test evidence until the final exact head executes.

### Target-executed — lint

Repaired-head lint run `30690346721`: passed. The final head contains the same implementation plus the bounded static repair and two additional test controls; exact-head lint remains required.

### Model-executed — downstream/runtime

Stensibly PR https://github.com/teamleaderleo/stensibly/pull/482 at exact head `2c42d8041b0cbe5fbccbe87202381361da2bc6ef`:

```console
bun install
bun run typecheck
bun run test
bun run test:convex
bun run worker:check
bun run test:runtime-parity
```

Exact-head run `30449733862`: all passed. Final restored PR-head run `30449840120`: ordinary `test` and `runtime-parity` passed.

Versions:

```text
Bun 1.3.14
Node v26.5.0
workerd 2026-07-22
```

The native matrix accepted bare, detached, nullish, `globalThis`, and `self` receiver forms and rejected unrelated holder, `call`, `apply`, and `bind` forms. The production `HttpGitHubOAuthClient` wrapper completed through a local outbound Worker.

Merged revision: `f19c2c7aa09fc4d4fdb7e7ae2d4d727d0eedd091`.

### Model-executed — TypeScript/tooling

Environment:

- TypeScript `5.8.3`
- ESLint `10.7.0`
- typescript-eslint `8.65.0`
- Node `22.23.1`

The retained model established:

- one explicit union receiver accepts the intended direct set;
- unrelated holders fail while the precise function type is retained;
- assignment to a plain receiver-free callback type erases the receiver requirement;
- a runtime wrapper and native regression remain useful because TypeScript cannot preserve receiver provenance through every widening path.

## Final-head focused command

Run at `18a117c28773cd7aa0ee599e03439c5fbbf06584`:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  --test_output=errors
```

The final-head-only assertions are:

- receiver-free callback assignment remains accepted;
- static generated constants remain ambient globals while static methods do not;
- renamed generic replacements update their receiver owner.

## Ordinary target gate

Current workerd instructions identify these relevant commands:

```console
just format
just generate-types
just test //types/...
just lint
```

Equivalent Bazel targets may be retained when the workflow uses Bazel directly. Record exact runner image, toolchain, command, target count, duration, and result.

## Generated-output review

Build both ambient and importable output and retain a compact compatibility report covering:

1. changed declaration files and changed method count;
2. examples from `fetch`, `EventTarget`, `Crypto`, streams, URL, Headers, FormData, WebSocket, iterator-bearing APIs, and disposal symbols;
3. legal global receiver unions;
4. explicit handwritten `this: void` and custom unions unchanged;
5. static methods unchanged and absent from ambient extraction;
6. static global constants preserved;
7. no `__JSG_GENERATED_RECEIVER__` leakage;
8. no undeclared or stale renamed receiver owners;
9. no unexpected recursive expansion from `typeof globalThis`;
10. ambient and importable outputs both type-check;
11. callable resource call signatures unchanged;
12. any intentionally detachable current API, or an explicit negative result.

## Remaining evidence gap

- final-head focused command;
- final-head ordinary `types` package and lint/generation gates;
- representative generated-output compatibility review;
- independent complete-diff acceptance.

Queued, pending, or skipped jobs are execution state only and provide no pass or failure evidence.
