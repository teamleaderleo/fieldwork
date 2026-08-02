# Review — unit 10 workerd receiver-aware types

## Review subject

- Work class: upstream source contribution preparation
- Target repository: `cloudflare/workerd`
- Proposed upstream base: `813c31394b9909d8f557bba14324db275bc12720`
- Canonical clean source branch: `teamleaderleo/workerd:unit-10/receiver-aware-types`
- Exact source head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- Owned clean PR: https://github.com/teamleaderleo/workerd/pull/5
- Fieldwork packet branch: `p0/435-unit-10-workerd-receiver-types`
- Complete changed-file fence: ten `types/` source/test files, one commit
- Upstream-contact authority: no

## Exact diff

https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584

The branch excludes temporary workflows, publishers, Fieldwork-only files, and generated evidence artifacts.

## Current-main relation

Public main advanced from the August 1 release to the August 2 release commit. The only upstream changes were:

- `src/workerd/io/maximum-compatibility-date.txt`
- `src/workerd/io/release-version.txt`

The candidate was reconstructed as one commit on the exact August 2 base. The final head includes the static-global constant repair plus callback-erasure and renamed-replacement controls.

## Claims requiring judgment

| Claim | Evidence | Reviewer challenge |
| --- | --- | --- |
| Ordinary JSG methods require an owning receiver | public issue #6904 source trace and native matrix | find a current ordinary `JSG_METHOD` whose runtime registration deliberately omits the owning signature |
| Iterator and disposal symbols are owning method surfaces | current `registerIterable`, `registerAsyncIterable`, `registerDispose`, and `registerAsyncDispose` use `MethodCallback` with `signature` | find a symbol registration that emits a generated method but does not carry the signature |
| Callable resource instances are outside this change | `registerCallable` uses an instance call handler and the generator models a call signature | identify a named method declaration incorrectly omitted by this boundary |
| Receiver-independent instance methods need distinct metadata | closed unmerged PR #2352 proposed a separate macro and registration path | identify equivalent current runtime support absent from the source search |
| Marker provenance is required | print/reparse pipeline plus override/global transforms | propose a smaller durable identity mechanism that survives reparse |
| Context-global receiver union matches workerd | native matrix and type fixture | inspect `globalThis`, `self`, nullish, detached, callback-widened, and recursive output |
| Full replacements must use replacement generics and emitted names | four standalone controls including `RenamedOwner<U>` | find another type-parameter or rename ownership case |
| Checker plus transformed top-level lookup is required | same-name lexical regression and discriminating end-to-end failure | inspect qualified nested heritage or generated declarations lacking checker symbols |
| Static methods are excluded while constants remain ambient | exact-head review `4834296945`, `createConstantPartial()`, and strict global output control | find another static property category whose prior extraction differs from constants |
| One commit is the correct presentation | transform ordering and per-commit invariant analysis | produce a split where every intermediate commit preserves legal globals, override receivers, constants, and green tests |

## Source review history

- `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`: repaired simple-name lexical heritage resolution.
- `54926f86c95185a7b83b2bf1ea901c35876a9a58`: repaired generic full-replacement receiver specialization.
- `0ecc0a6632747031a6650c49a401760e511c9f36`: technical review `4827890474` accepted the repaired source and required execution.
- validation run `30690050452`: end-to-end target failed while three focused transform targets passed; failure showed inherited global receiver loss.
- repaired validation run `30690396598`: four focused targets passed after transformed top-level heritage lookup was added.
- PR #5 review `4834296945`: found blanket static exclusion removed generated ambient constants; requested method-only exclusion and a retained constant control.
- `cde837e5ba5b1ecc5295ec9957146feaf1160707`: reconstructed on August 2 base with method-only static exclusion and constant preservation.
- `18a117c28773cd7aa0ee599e03439c5fbbf06584`: final current source adding renamed generic replacement ownership control.

The previous packet statement that static ambient expectations were stale was wrong. Static method extraction was stale; static property/constant extraction remains required.

## Staleness and duplicate check

- Current public head checked: `813c31394b9909d8f557bba14324db275bc12720`.
- Relevant source paths changed upstream since the prior base: no.
- Open duplicate search: issue #6904 only; no competing public implementation PR found.
- Current project guidance checked: `AGENTS.md`, `types/AGENTS.md`, and `.opencode/agent/submit.md`.
- Guidance implications applied:
  - exact current-main base;
  - source and target-native tests only;
  - one atomic commit with no fixups;
  - AI assistance disclosed in commit and PR text;
  - type-level tests included;
  - ambient and importable generated output still require review.

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers.
- [x] No stale execution artifacts.
- [x] No dependency or lockfile churn.
- [x] One clean commit against current public main.
- [x] Commit message contains current AI-assistance disclosure.
- [x] Owned PR description contains current AI-assistance disclosure.
- [x] Commit-pinned code and test links recorded in the packet.

## Test review

- [x] Runtime/application matrix executed and merged in the owned testbed.
- [x] TypeScript receiver and erasure model executed.
- [x] Repaired-head lint passed.
- [x] Repaired-head generator, globals, overrides, and replacement-generic targets passed before the final controls.
- [x] Discriminating pre-transform-heritage failure retained and explained.
- [x] Static constant regression found through complete-diff review and repaired in source plus expected output.
- [ ] Final-head static constant and static method control executed.
- [ ] Final-head renamed replacement control executed.
- [ ] Final-head callback-erasure type fixture executed.
- [ ] Final-head complete `//types/...` package executed.
- [ ] Final-head generation and formatting gates executed.
- [ ] Representative ambient/importable output compatibility measured.
- [ ] Independent complete-diff acceptance at exact final head.

## Compatibility review focus

1. Count changed methods and declaration files in both ambient and importable output.
2. Confirm no `__JSG_GENERATED_RECEIVER__` marker leakage.
3. Confirm every receiver owner type resolves and no replacement generic or original renamed owner remains.
4. Inspect global unions for recursion or editor-performance growth.
5. Sample receiver output across `fetch`, `EventTarget`, Web Crypto, URL, Headers, FormData, streams, WebSocket, SQL, iterator-bearing APIs, and disposal symbols.
6. Verify explicit handwritten `this: void` and custom unions remain byte-for-byte stable.
7. Verify static methods remain receiver-free and absent from ambient function extraction.
8. Verify static generated constants remain present and unchanged.
9. Verify callable resource call signatures remain unchanged.
10. Search for any current API intentionally detachable despite ordinary owning registration; retain a negative result if none exists.
11. Confirm ordinary callback assignment remains accepted and exact receiver-aware property calls reject unrelated holders.
12. Check standalone workerd output requirements against any additional snapshot obligations when the repository is consumed as a submodule of the larger Workers tree.

## Known limits

- receiver widening can be erased by plain callback types;
- `Reflect.apply()` accepts an `any` receiver in TypeScript and remains runtime-checked only;
- callable resources and property accessors are separate declaration surfaces;
- a future detached-method registration path would need RTTI and generator support;
- qualified heritage resolving to a transformed nested declaration is outside the current generated source model;
- generated-output size and editor impact remain unmeasured;
- target execution on the exact final test blobs remains pending.

## Reviewer disposition

**HOLD**

Reviewed source head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`  
Reason: current-main reconciliation, static constant repair, renamed replacement control, duplicate search, commit atomicity, AI disclosure, and runtime registration analysis are coherent. Exact final-head execution, representative output review, and independent acceptance remain.  
Clearing condition: run the final focused and ordinary type gates, retain generated-output compatibility results, then obtain independent complete-diff `ACCEPT` or a concrete repair.  
Reviewer eligibility: this file is coordinator/self-review; final acceptance should come from an independent reviewer familiar with workerd type generation.
