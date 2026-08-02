# Unit 10 — workerd receiver-aware TypeScript declarations

## In simple words

`workerd` rejects ordinary native methods called through the wrong JavaScript object, but its generated TypeScript declarations omit that receiver rule. The current implementation adds explicit `this` parameters and preserves them through overrides and Worker-global extraction.

Further review found two publication-changing gaps: required generated snapshots are not yet on the source branch, and methods inherited by the Worker global can still produce false TypeScript errors when detached even though V8 converts nullish receivers to the compatible Worker global proxy. Both are being resolved on owned execution carriers; public upstream contact remains unauthorized.

## Current disposition

**REPAIR.**

The clean implementation candidate is coherent but not yet the final proposed source head because:

1. workerd requires regenerated `types/generated-snapshot/` files for type-generation changes;
2. inherited Worker-global method declarations may need hierarchy-wide global/nullish receiver widening;
3. the final global receiver member must be selected between host-dependent `typeof globalThis` and environment-independent `ServiceWorkerGlobalScope`;
4. the resulting source plus snapshots needs exact-head execution and independent review.

## Exact current implementation

- repository: `teamleaderleo/workerd`
- source branch: `unit-10/receiver-aware-types`
- owned draft PR: https://github.com/teamleaderleo/workerd/pull/5
- public base: `813c31394b9909d8f557bba14324db275bc12720` (`Release 2026-08-02`)
- implementation head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- compare: https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584
- current fence: one implementation commit, ten source/test files, no workflow files
- missing required source: generated snapshot commit
- AI assistance: disclosed in the commit and owned PR body

The August 2 public release differs from the prior August 1 base only in:

- `src/workerd/io/maximum-compatibility-date.txt`
- `src/workerd/io/release-version.txt`

## Owned execution and repair carriers

### Final implementation and snapshot carrier

- PR: https://github.com/teamleaderleo/workerd/pull/9
- branch: `unit-10/final-validation-18a117c`
- carrier head: `fbed6bc84e4de0051af069acb44d65776466f2d1`
- custom run: `30755965427`
- pinned product candidate: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- only committed carrier file: `.github/workflows/unit-10-final-validation.yml`

Jobs:

- five focused receiver targets;
- complete `//types/...` package;
- types lint;
- generated latest and experimental ambient/importable snapshots;
- native inherited-global receiver probe.

### Inherited-global repair model

- PR: https://github.com/teamleaderleo/workerd/pull/10
- branch: `unit-10/inherited-global-repair-validation`
- carrier head: `6d2d5fcc67523f75bf8e0589a291fc26576b3a35`
- custom run: `30756418899`
- pinned product candidate: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- only committed carrier file: `.github/workflows/unit-10-inherited-global-repair.yml`

The job applies an assertion-heavy ancestry repair only in its worktree, adds a dedicated type fixture, runs focused and complete type gates, builds declarations, and uploads the patched source plus generated-output review packet.

Neither carrier workflow may enter the final source branch.

## Established mechanism

- Ordinary `JSG_METHOD` callbacks use an owning V8 signature and reject unrelated receivers before C++ execution.
- Iterator, async-iterator, dispose, and async-dispose symbol methods use the same owning signature.
- Callable resource instances use a separate instance call-handler surface and remain outside ordinary method generation.
- Static methods are constructor members and remain receiver-free.
- Generated static readonly properties/constants retain existing ambient `const` extraction.
- Closed unmerged public PR #2352 proposed a separate detached-method registration path; current public source contains no equivalent receiver-independent instance registration.
- No competing public implementation PR was found; public issue #6904 remains the discussion record.

## Current implementation behavior

At head `18a117c…`:

- ordinary non-static generated method → `this: Owner`;
- direct `ServiceWorkerGlobalScope` method and extracted ambient copy → `this: Owner | typeof globalThis | null | void`;
- generated receiver provenance survives print/reparse, overrides, full replacements, renames, and global extraction;
- explicit handwritten receivers remain authoritative;
- generic and renamed full replacements use the replacement declaration's parameters and emitted owner name;
- static methods are not extracted as ambient functions;
- static generated constants remain ambient constants;
- callback assignment can intentionally erase the receiver through normal TypeScript assignability.

## Repairs already completed

### Transformed heritage

A pre-repair run showed inherited globals lost receiver parameters because the checker pointed to the original superclass declaration. The repair uses checker-guided lexical identity and follows the corresponding transformed top-level declaration. Repaired validation run `30690396598` passed the four focused targets.

### Static constants

Review `4834296945` found blanket static-member filtering removed generated global constants. The current implementation excludes only static methods and requires `static readonly CONSTANT: 42` to remain `declare const CONSTANT: 42`.

### Generic and renamed replacements

The source prevents undeclared replacement generics and includes a direct control requiring `Owner` replaced by `RenamedOwner<U>` to emit a receiver owned by `RenamedOwner<U>` with no stale original owner.

## Active inherited-global finding

The current implementation widens free ambient functions copied from ancestor declarations, but leaves the original ancestor declaration owner-only.

Example consequence:

```ts
const fromSelf = self.addEventListener;
fromSelf("fetch", handler); // current candidate reports a `this` error
```

A TypeScript 5.8.3 model reproduced the false positive. A widened ancestor receiver accepted bare, nullish, global, and owning receivers while still rejecting unrelated objects.

V8 source at `bf3d02947968c33781ad7a74e5e0234d9ac5d748` shows non-JavaScript receivers are converted before signature validation: `null` and `undefined` become the global proxy, then the owning signature accepts that proxy for owners in the Worker-global inheritance chain.

PR #9 carries a native workerd probe for methods read from both `self.addEventListener` and `new EventTarget().addEventListener`. PR #10 validates the bounded repair algorithm:

- identify the exact transformed `ServiceWorkerGlobalScope` ancestry;
- widen only marked generated receivers on declarations in that ancestry;
- leave unrelated owners strict;
- use the same widened declaration map for ambient extraction;
- preserve explicit receivers, static behavior, properties, constants, and call signatures.

The guarded repair script is retained at [`patches/apply-inherited-global-ancestry-repair.py`](./patches/apply-inherited-global-ancestry-repair.py).

## Global receiver type decision

The current union uses `typeof globalThis`. This directly names the Worker ambient global, but importable declarations resolve it against the consumer host. A Node consumer could therefore get Node's global object accepted as a receiver.

The preferred alternative is:

```ts
Owner | ServiceWorkerGlobalScope | null | void
```

provided the generated ambient bundles prove:

```ts
const workerGlobal: ServiceWorkerGlobalScope = globalThis;
```

The generated latest and experimental outputs will decide this. See [`GLOBAL_RECEIVER_TYPE.md`](./GLOBAL_RECEIVER_TYPE.md).

## Compatibility established by executed models

TypeScript 5.8.3 models established:

- classes can implement receiver-aware interfaces without spelling an explicit `this` parameter;
- object literal implementations remain valid;
- subclass overrides remain valid without repeating `this`;
- receiver-aware methods remain assignable to ordinary receiver-free callbacks;
- `OmitThisParameter` remains an explicit escape hatch;
- `Pick<Owner, "method">` property calls are intentionally rejected because the partial holder is not the owner;
- structural typing cannot prove hidden native identity, so a complete structural fake remains a known false negative.

See [`TYPE_COMPATIBILITY.md`](./TYPE_COMPATIBILITY.md).

## Mixed ambient-library limit

The supported Workers package configuration recommends `lib: ["esnext"]` plus Workers-generated types. A TypeScript model with `lib.dom` showed receiver-free DOM overloads merge into `fetch` and `EventTarget`, allowing unrelated-holder calls to compile again.

This is a mixed-environment effectiveness limit, not a reason to weaken the Workers declarations. See [`DOM_MERGING.md`](./DOM_MERGING.md).

## Required generated snapshots

Current workerd policy and `check-snapshot` require generator-produced snapshots. The bounded output tree contains:

- `types/generated-snapshot/index.d.ts`
- `types/generated-snapshot/index.ts`
- `types/generated-snapshot/experimental/index.d.ts`
- `types/generated-snapshot/experimental/index.ts`

Recent merged type work confirms an acceptable final history shape:

1. one atomic implementation commit;
2. one CI-generated snapshot commit whose files match generator output and pass `check-snapshot`.

Do not hand-edit snapshot files.

## Review routing

Current CODEOWNERS routes `/types/` to the Wrangler team. Experimental snapshots additionally route to runtime and Durable Objects teams. Final human review should cover:

- TypeScript declaration compatibility, snapshot integrity, and editor behavior;
- JSG/V8 runtime ownership and global-proxy semantics;
- experimental surface changes when material.

No review request is authorized yet.

## Remaining work in strict order

1. Complete the native inherited-global probe and PR #10 repair-model execution.
2. Select the ancestry policy and global receiver member from executed results.
3. Materialize the accepted repair on source PR #5 as a new exact implementation head.
4. Generate, inspect, and commit the exact latest/experimental ambient/importable snapshots as a second commit.
5. Run focused, complete-types, lint, generation, and snapshot gates on the source-plus-snapshot head.
6. Close PRs #9 and #10 and prove their workflow files are absent from source.
7. Obtain independent complete-diff review from types and runtime perspectives.
8. Human decides whether to authorize a public issue follow-up and upstream PR.

Queued jobs are execution state only and provide no pass or failure evidence. Research, source review, and packet work continue independently.

## Packet

- branch: `p0/435-unit-10-workerd-receiver-types`
- directory: `upstream/packets/10-workerd-receiver-types/`
- routing board: https://github.com/teamleaderleo/fieldwork/issues/435
- campaign record: https://github.com/teamleaderleo/fieldwork/issues/230

## Reading order

1. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
2. [`INHERITED_GLOBALS.md`](./INHERITED_GLOBALS.md)
3. [`GLOBAL_RECEIVER_TYPE.md`](./GLOBAL_RECEIVER_TYPE.md)
4. [`TYPE_COMPATIBILITY.md`](./TYPE_COMPATIBILITY.md)
5. [`DOM_MERGING.md`](./DOM_MERGING.md)
6. [`APPROACHES.md`](./APPROACHES.md)
7. [`TESTS.md`](./TESTS.md)
8. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
9. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)
10. [`REVIEW.md`](./REVIEW.md)
