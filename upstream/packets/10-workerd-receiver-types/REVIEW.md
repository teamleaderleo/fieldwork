# Review — unit 10 workerd receiver-aware types

## Review subject

- Work class: upstream source contribution preparation
- Target repository: `cloudflare/workerd`
- Proposed upstream base: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b`
- Canonical clean source branch: `teamleaderleo/workerd:unit-10/receiver-aware-types`
- Exact source head: `8f41da276852ad48735c1d817b7c1a3699ac8beb`
- Owned clean PR: https://github.com/teamleaderleo/workerd/pull/5
- Fieldwork packet branch: `p0/435-unit-10-workerd-receiver-types`
- Complete changed-file fence: ten `types/` source/test files, one commit
- Upstream-contact authority: no

## Exact diff

https://github.com/teamleaderleo/workerd/compare/d82c2a45a8695aac30d4d24828ce1ee7fb11909b...8f41da276852ad48735c1d817b7c1a3699ac8beb

The branch excludes temporary workflows, publishers, Fieldwork-only files, and generated evidence artifacts.

## Current-main relation

Public main advanced from the prior July 31 base to the August 1 release commit. The only upstream changes were:

- `src/workerd/io/maximum-compatibility-date.txt`
- `src/workerd/io/release-version.txt`

The candidate was reconstructed as one commit on the exact August 1 base. Product source blobs remain identical to the repaired reviewed candidate. The final head adds one type-test control documenting callback receiver erasure.

## Claims requiring judgment

| Claim | Evidence | Reviewer challenge |
| --- | --- | --- |
| Ordinary JSG methods require an owning receiver | public issue #6904 source trace and native matrix | find a current ordinary `JSG_METHOD` whose runtime registration deliberately omits the owning signature |
| Receiver-independent instance methods need distinct metadata | closed unmerged PR #2352 proposed a separate macro and registration path | identify equivalent current runtime support absent from the source search |
| Marker provenance is required | print/reparse pipeline plus override/global transforms | propose a smaller durable identity mechanism that survives reparse |
| Context-global receiver union matches workerd | native matrix and type fixture | inspect `globalThis`, `self`, nullish, detached, callback-widened, and recursive output |
| Full replacements must use replacement generics | three-case standalone control | find another type-parameter ownership case |
| Checker plus transformed top-level lookup is required | same-name lexical regression and discriminating end-to-end failure | inspect qualified nested heritage or generated declarations lacking checker symbols |
| Static members stay receiver-free and unextracted | generator/global tests | identify a static API represented as an ambient global by design |
| One commit is the correct presentation | transform ordering and per-commit invariant analysis | produce a split where every intermediate commit preserves legal globals, override receivers, and green tests |

## Source review history

- `d08e2e968b6db600c220e2babe0a07befa728ba2`: repaired stale static ambient expectations.
- `e7b15f8014e8ed49255d2f0c6774f0b3bfe1714a`: repaired simple-name lexical heritage resolution.
- `54926f86c95185a7b83b2bf1ea901c35876a9a58`: repaired generic full-replacement receiver specialization.
- `0ecc0a6632747031a6650c49a401760e511c9f36`: technical review `4827890474` accepted the repaired source and required execution.
- validation run `30690050452`: end-to-end target failed while three focused transform targets passed; failure showed inherited global receiver loss.
- repaired validation run `30690396598`: four focused targets passed after transformed top-level heritage lookup was added.
- `8f41da276852ad48735c1d817b7c1a3699ac8beb`: one-commit exact-August-1 source with callback-erasure compatibility control and AI disclosure.

## Staleness and duplicate check

- Current public head checked: `d82c2a45a8695aac30d4d24828ce1ee7fb11909b`.
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
- [x] Repaired-head generator, globals, overrides, and replacement-generic targets passed.
- [x] Discriminating old-code failure retained and explained.
- [ ] Final-head callback-erasure type fixture executed.
- [ ] Final-head complete `//types/...` package executed.
- [ ] Final-head generation and formatting gates executed.
- [ ] Representative ambient/importable output compatibility measured.
- [ ] Independent complete-diff acceptance at exact final head.

## Compatibility review focus

1. Count changed methods and declaration files in both ambient and importable output.
2. Confirm no `__JSG_GENERATED_RECEIVER__` marker leakage.
3. Confirm every receiver owner type resolves and no replacement generic is undeclared.
4. Inspect global unions for recursion or editor-performance growth.
5. Sample receiver output across `fetch`, `EventTarget`, Web Crypto, URL, Headers, FormData, streams, WebSocket, SQL, and iterator-bearing APIs.
6. Verify explicit handwritten `this: void` and custom unions remain byte-for-byte stable.
7. Verify static members remain receiver-free and are not extracted as ambient globals.
8. Search for any current API intentionally detachable despite ordinary owning registration; retain a negative result if none exists.
9. Confirm ordinary callback assignment remains accepted and exact receiver-aware property calls reject unrelated holders.
10. Check standalone workerd output requirements against any additional snapshot obligations when the repository is consumed as a submodule of the larger Workers tree.

## Known limits

- receiver widening can be erased by plain callback types;
- `Reflect.apply()` accepts an `any` receiver in TypeScript and remains runtime-checked only;
- a future detached-method registration path would need RTTI and generator support;
- qualified heritage resolving to a transformed nested declaration is outside the current generated source model;
- generated-output size and editor impact remain unmeasured;
- target execution on the exact final test blob remains pending.

## Reviewer disposition

**HOLD**

Reviewed source head: `8f41da276852ad48735c1d817b7c1a3699ac8beb`  
Reason: source cleanup, current-main reconciliation, duplicate search, commit atomicity, AI disclosure, and prior-art analysis are coherent. Exact final-head execution, representative output review, and independent acceptance remain.  
Clearing condition: run the final focused and ordinary type gates, retain generated-output compatibility results, then obtain independent complete-diff `ACCEPT` or a concrete repair.  
Reviewer eligibility: this file is coordinator/self-review; final acceptance should come from an independent reviewer familiar with workerd type generation.
