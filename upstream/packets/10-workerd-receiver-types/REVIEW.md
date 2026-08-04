# Review — unit 10 workerd receiver-aware types

## Review subject

- Work class: upstream source contribution preparation
- Target: `cloudflare/workerd`
- Public base: `813c31394b9909d8f557bba14324db275bc12720`
- Canonical implementation branch: `teamleaderleo/workerd:unit-10/receiver-aware-types`
- Current implementation head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- Owned source PR: https://github.com/teamleaderleo/workerd/pull/5
- Exact validation/native carrier: https://github.com/teamleaderleo/workerd/pull/9 at `159fe1e87253ae79f5b2b767d49074f1ebeb447d`, run `30857633684`
- Rejected broad repair carrier: https://github.com/teamleaderleo/workerd/pull/10 at `6d2d5fcc67523f75bf8e0589a291fc26576b3a35`
- Fieldwork packet branch: `p0/435-unit-10-workerd-receiver-types`
- Current implementation fence: ten source/test files, one commit, no workflows
- Upstream-contact authority: no

## Current disposition

**REPAIR**

The receiver mechanism is viable, but the current source is not publication-complete. Two stale generator exact-output fixtures must be repaired, generated snapshots must be materialized, and the final exact-head gates must pass.

The native probe has now settled the inherited-global question. The former proposal to widen every declaration in the `ServiceWorkerGlobalScope` ancestry is rejected as unsound.

## Decisive native finding

Run `30857633684`, job `91832245048`, built workerd and passed the receiver characterization matrix.

For a function value read from `self.addEventListener`:

- bare call succeeds;
- `.call(undefined, ...)` succeeds;
- `.call(null, ...)` succeeds;
- `.call(globalThis, ...)` succeeds;
- `.call(self, ...)` succeeds;
- `.call({}, ...)` throws `Illegal invocation`.

For a function value read from `new EventTarget().addEventListener`:

- the owning `EventTarget` receiver succeeds;
- a bare call throws `Illegal invocation`;
- an unrelated receiver throws `Illegal invocation`.

The ordinary `EventTarget` declaration therefore must remain owner-strict. Widening the shared ancestor would admit calls the runtime rejects.

## Accepted receiver invariants

1. Generated ordinary instance methods carry an owning receiver.
2. Static methods remain receiver-free.
3. Explicit handwritten receivers remain authoritative.
4. Direct Worker-global methods and extracted ambient globals may accept their owner, the Worker global, `null`, and `undefined` where runtime evidence supports that behavior.
5. Shared ancestor declarations such as ordinary `EventTarget` remain owner-strict.
6. If inherited methods are exposed with Worker-global fallback, the widening must be localized to the transformed Worker-global surface; it must not mutate the shared ancestor declaration.
7. If a localized shadow cannot be expressed without duplicate or unstable overloads, retain the strict inherited declaration and document the TypeScript false positive rather than introduce a runtime false negative.

## Rejected repair

The PR #10 hierarchy-wide approach is rejected.

It proposed finding every declaration in the transformed `ServiceWorkerGlobalScope` ancestry and widening marked generated receivers on all of them. Native execution disproved its central assumption: a method read from a separate `EventTarget` does not acquire Worker-global fallback. Applying that patch would make ordinary `EventTarget` detachment type-check even though workerd throws.

Do not revive or merge the ancestry-wide patch. Any follow-up must be a Worker-global-local shadow/redeclaration design with separate tests for the global surface and the ordinary owner surface.

## Current implementation diff

https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584

Current source contains no workflows, Fieldwork files, dependency churn, or hand-edited snapshots.

## Exact executed validation

Carrier run `30857633684` is pinned to implementation head `18a117c28773cd7aa0ee599e03439c5fbbf06584` and differs only by its fork-only workflow.

| Gate | Result | Review meaning |
| --- | --- | --- |
| focused receiver targets | PASS | marker, override, global, replacement-generic, and fetch receiver behavior remains intact |
| native inherited-global matrix | PASS | rejects ancestry-wide widening and establishes the Worker-global-local boundary |
| generated declarations and artifact | PASS | four expected snapshot files produced; no marker leakage |
| complete `//types/...` | FAIL | two stale generator exact-output fixtures still expect receiver-free generated methods |
| lint in latest combined job | SKIPPED | skipped after full package failure; earlier exact candidate lint passed |

The full package failure is not a semantic receiver failure. The stale expectations are in:

- `types/test/generator/structure.spec.ts`;
- `types/test/generator/index.spec.ts`.

They must expect the internal generated receiver marker on generated non-static methods. Static methods must remain receiver-free.

## Generated-output review already completed

The artifact contains exactly:

- `types/generated-snapshot/index.d.ts`;
- `types/generated-snapshot/index.ts`;
- `types/generated-snapshot/experimental/index.d.ts`;
- `types/generated-snapshot/experimental/index.ts`.

Observed summary:

- changed files: 4;
- added lines: 2478;
- removed lines: 1044;
- receiver lines: 1504;
- generated marker lines: 0.

Most broad textual churn is receiver insertion plus mechanical Prettier reflow. Snapshot files must still be regenerated or verified against the repaired exact source head before committing.

## Global receiver type decision

Current source uses `typeof globalThis`. In importable output this can resolve against a consumer host and may be broader than the workerd global.

Before changing it, test both ambient and importable generated output and prove whether:

```ts
const workerGlobal: ServiceWorkerGlobalScope = globalThis;
```

is valid. Prefer `ServiceWorkerGlobalScope` only if it preserves the actual generated global and does not create compatibility or declaration-order regressions. Do not change the public type on aesthetic grounds alone.

## Required final history

Repository precedent supports:

1. implementation and target-native tests;
2. exact generator-produced latest and experimental snapshots.

Carrier workflow files must remain absent from both commits.

## Final source cleanliness checklist

- [ ] stale generator exact-output fixtures repaired;
- [ ] inherited-global policy remains localized and runtime-backed;
- [ ] implementation commit contains only source and target-native tests;
- [ ] generated snapshot commit contains only exact generator output;
- [ ] no workflow or evidence-only files;
- [ ] no Fieldwork terminology in public source or snapshots;
- [ ] no dependency or lockfile churn;
- [ ] commit and PR AI disclosure current;
- [ ] public base current and relevant paths reconciled;
- [ ] carrier PRs closed or clearly marked as execution-only/superseded.

## Final execution checklist

- [x] native inherited-global characterization completed;
- [x] focused generator, override, globals, replacement, and fetch receiver targets passed on `18a117c…`;
- [x] snapshot generation completed on `18a117c…`;
- [x] no `__JSG_GENERATED_RECEIVER__` leakage in generated output;
- [ ] complete `//types/...` passes after fixture repair;
- [ ] types lint passes on final exact head;
- [ ] `bazelisk build //types` passes on final exact head;
- [ ] latest and experimental ambient/importable bundles type-check;
- [ ] `check-snapshot` passes on the committed snapshot tree;
- [ ] no duplicate inherited overloads;
- [ ] ordinary `EventTarget` remains owner-strict;
- [ ] final source-and-snapshot diff receives independent review.

## Review routing

Current CODEOWNERS routes `/types/` to the Wrangler team. Experimental snapshots additionally route to runtime and Durable Objects teams. No public review request is authorized yet.

## Clearing condition

Repair the stale generator fixtures, decide whether a narrow Worker-global shadow is technically sound, materialize exact generated snapshots, run the complete exact-head gates, and obtain a final `ACCEPT` or a concrete new `REPAIR` finding on the source-and-snapshot head.