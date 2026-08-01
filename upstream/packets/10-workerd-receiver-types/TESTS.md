# Tests — unit 10

## Exact clean source

- base: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b`
- head: `8f41da276852ad48735c1d817b7c1a3699ac8beb`
- compare: https://github.com/teamleaderleo/workerd/compare/d82c2a45a8695aac30d4d24828ce1ee7fb11909b...8f41da276852ad48735c1d817b7c1a3699ac8beb
- owned draft PR: https://github.com/teamleaderleo/workerd/pull/5
- fence: one commit, ten source/test files, no workflow files

The August 1 upstream base differs from the prior July 31 base only in two release metadata files. The final head adds one accepted callback-erasure compatibility control to the repaired product/test blobs.

## Test inventory in the clean diff

- `types/test/index.spec.ts`
  - generator snapshot and end-to-end transform ordering;
  - ordinary, explicit, generic, static, inherited, and global receiver output.
- `types/test/transforms/globals.spec.ts`
  - context-global widening;
  - static exclusion;
  - lexical superclass selection when another namespace contains the same unqualified name;
  - transformed top-level heritage lookup after an earlier transformer replaces superclass members.
- `types/test/transforms/overrides/index.spec.ts`
  - partial and full override behavior;
  - explicit receiver preservation and overload handling.
- `types/test/transforms/overrides/replacement-receiver-generics.spec.ts`
  - generic generated owner → nongeneric replacement;
  - generic generated owner → generic replacement;
  - nongeneric generated owner → generic replacement.
- `types/test/types/fetch-receiver.ts`
  - legal bare, detached, nullish, `globalThis`, `self`, `call`, `apply`, and `bind` forms;
  - expected diagnostics for unrelated holders and unrelated explicit receivers;
  - raw host function stored on an unrelated client;
  - accepted assignment to a receiver-free callback type, documenting normal TypeScript receiver erasure and source compatibility.

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

### Target-executed — lint

Repaired-head lint run `30690346721`: passed.

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

Run at `8f41da276852ad48735c1d817b7c1a3699ac8beb`:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  --test_output=errors
```

The final-head delta from the green repaired source is the callback-erasure acceptance control plus upstream release metadata outside the diff. This still requires exact execution before publication.

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
2. examples from `fetch`, `EventTarget`, `Crypto`, streams, URL, Headers, FormData, WebSocket, and iterator-bearing APIs;
3. legal global receiver unions;
4. explicit handwritten `this: void` and custom unions unchanged;
5. static methods unchanged and absent from ambient extraction;
6. no `__JSG_GENERATED_RECEIVER__` leakage;
7. no undeclared generic receiver parameters;
8. no unexpected recursive expansion from `typeof globalThis`;
9. ambient and importable outputs both type-check;
10. any intentionally detachable current API, or an explicit negative result.

## Remaining evidence gap

- final-head focused command;
- final-head ordinary `types` package and lint/generation gates;
- representative generated-output compatibility review;
- independent complete-diff acceptance.

Queued, pending, or skipped jobs are execution state only and provide no pass or failure evidence.
