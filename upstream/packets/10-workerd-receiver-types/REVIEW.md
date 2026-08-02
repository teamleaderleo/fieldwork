# Review — unit 10 workerd receiver-aware types

## Review subject

- Work class: upstream source contribution preparation
- Target: `cloudflare/workerd`
- Public base: `813c31394b9909d8f557bba14324db275bc12720`
- Canonical implementation branch: `teamleaderleo/workerd:unit-10/receiver-aware-types`
- Current implementation head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- Owned source PR: https://github.com/teamleaderleo/workerd/pull/5
- Exact implementation/native carrier: https://github.com/teamleaderleo/workerd/pull/9 at `fbed6bc84e4de0051af069acb44d65776466f2d1`, run `30755965427`
- Exact inherited repair carrier: https://github.com/teamleaderleo/workerd/pull/10 at `6d2d5fcc67523f75bf8e0589a291fc26576b3a35`, run `30756418899`
- Fieldwork packet branch: `p0/435-unit-10-workerd-receiver-types`
- Current implementation fence: ten source/test files, one commit, no workflows
- Missing final source: settled ancestry/global receiver policy plus generated snapshots
- Upstream-contact authority: no

## Current disposition

**REPAIR**

The current implementation is not the final review subject. It remains the exact source fence from which two independent decisions are being executed:

1. whether generated receiver widening must apply to original declarations throughout the exact Worker-global ancestry;
2. whether the global member in that union should be `typeof globalThis` or `ServiceWorkerGlobalScope`.

The final review begins only after those decisions are materialized and generator-produced snapshots are committed.

## Current implementation diff

https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584

Current source contains no workflows, Fieldwork files, dependency churn, or hand-edited snapshots.

## Required final history

Recent merged workerd type changes support this two-commit shape:

1. atomic implementation plus target-native tests;
2. CI-generated latest and experimental ambient/importable snapshots.

Every snapshot file must match generator output. Carrier workflows must be closed and absent from both commits.

## Active technical decisions

### Inherited Worker-global declarations

Current source widens extracted ambient functions but leaves original ancestor declarations owner-only. The TypeScript model rejects detached `self.addEventListener` calls that V8 source predicts are legal after nullish-to-global-proxy conversion.

Review must require agreement between:

- PR #9 native workerd probe;
- PR #10 ancestry repair model;
- exact generated output.

If confirmed, only declarations in the transformed `ServiceWorkerGlobalScope` ancestry should widen. Non-ancestry owners remain strict.

### Global receiver member

Current source uses `typeof globalThis`. Importable output resolves that against the consumer host, which can admit Node or browser globals unrelated to workerd.

Prefer `ServiceWorkerGlobalScope` if generated latest and experimental ambient bundles prove:

```ts
const workerGlobal: ServiceWorkerGlobalScope = globalThis;
```

Retain `typeof globalThis` only with explicit evidence that the root-interface form rejects the real Workers global or causes a larger regression.

## Claims requiring judgment

| Claim | Current evidence | Reviewer challenge |
| --- | --- | --- |
| Ordinary JSG methods require an owner | JSG registration and native matrix | find an ordinary registration that omits the owning signature |
| Iterator and disposal symbol methods are owning | current `resource.h` registration | find a generated symbol method with different receiver semantics |
| Callable resource signatures are separate | instance call-handler registration | identify a named method incorrectly excluded |
| Detached instance operations need metadata | no current detached path; closed PR #2352 | identify current equivalent runtime support |
| Receiver provenance must survive reparse | generator/override/global pipeline | propose a smaller durable mechanism |
| Transformed heritage must be followed | discriminating failed and repaired runs | find a transformed hierarchy still resolved to stale source |
| Static methods and constants have different global behavior | review `4834296945` and strict fixture | identify another static property category with different prior behavior |
| Replacement owners use emitted names/generics | four replacement controls | find an unresolved rename or generic ownership case |
| Worker-global ancestors need widening | V8 source and TS model; native run pending | produce a native counterexample |
| Root interface can replace host `globalThis` | generated assertion pending | show missing or incompatible Worker-global members |
| Snapshots are mandatory | target instructions, just recipe, check-snapshot | show accepted generator work without matching snapshots |
| Two-commit packaging is acceptable | recent merged type PR history | identify target policy requiring one squashed commit |

## Executed evidence retained

- downstream native/runtime matrix and production wrapper passed;
- TypeScript direct receiver and callback-erasure models passed;
- implementation ergonomics model passed for classes, literals, overrides, callbacks, `OmitThisParameter`, and partial-holder rejection;
- mixed `lib.dom` overload model demonstrated that receiver-free merged overloads can neutralize diagnostics;
- pre-repair transformed-heritage run failed on the discriminating assertion;
- repaired transformed-heritage focused run passed;
- repaired-head lint passed;
- static constant regression was found by exact-diff review and repaired in source/test expectations.

Queued carrier jobs remain execution state only.

## Final source cleanliness checklist

- [ ] ancestry/global receiver decisions materialized on source PR #5;
- [ ] implementation commit contains only source and target-native tests;
- [ ] generated snapshot commit contains only exact generator output;
- [ ] no workflow or evidence-only files;
- [ ] no Fieldwork terminology in public source or snapshots;
- [ ] no dependency or lockfile churn;
- [ ] commit and PR AI disclosure current;
- [ ] public base current and relevant paths reconciled;
- [ ] carrier PRs closed and clearly superseded.

## Final execution checklist

- [ ] native inherited-global probe passed or produced a retained counterexample;
- [ ] focused generator, override, globals, replacement, fetch, and inherited-global targets passed;
- [ ] complete `//types/...` passed;
- [ ] types lint passed;
- [ ] `bazelisk build //types` passed;
- [ ] latest and experimental ambient/importable bundles type-checked;
- [ ] `check-snapshot` passed on the committed snapshot tree;
- [ ] no `__JSG_GENERATED_RECEIVER__` leakage;
- [ ] every receiver owner resolves;
- [ ] static constants and callable signatures unchanged where expected;
- [ ] no duplicate inherited overloads;
- [ ] output size and `typeof globalThis`/root-interface complexity reviewed.

## Compatibility review checklist

- [ ] direct unrelated-holder calls rejected;
- [ ] bare/nullish/global/owning calls accepted only where runtime permits;
- [ ] non-global owners remain strict;
- [ ] explicit handwritten `this: void` and custom unions unchanged;
- [ ] user implementations and overrides remain source-compatible;
- [ ] receiver-free callback assignment and `OmitThisParameter` remain valid;
- [ ] partial-holder rejection documented;
- [ ] structural fake limitation documented;
- [ ] mixed DOM/Web overload limitation documented;
- [ ] importable consumer-host global limitation eliminated or disclosed;
- [ ] no nominal-safety claim made.

## Review routing

Current CODEOWNERS routes `/types/` to the Wrangler team. Experimental snapshots additionally route to runtime and Durable Objects teams.

Final acceptance should include independent judgment from:

1. a Workers types/declaration-generation reviewer;
2. a JSG/runtime reviewer;
3. runtime/Durable Objects reviewers when experimental output changes materially.

No review request is authorized yet.

## Clearing condition

Choose and execute the inherited ancestry and global receiver designs, materialize one implementation commit plus one generated snapshot commit, run the complete exact-head gates, close both carriers, then obtain independent `ACCEPT` or a concrete new `REPAIR` finding on the final source-and-snapshot head.
