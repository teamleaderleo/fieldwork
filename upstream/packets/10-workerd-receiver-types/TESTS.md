# Tests — unit 10

## Exact implementation source

- base: `813c31394b9909d8f557bba14324db275bc12720`
- implementation head: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- compare: https://github.com/teamleaderleo/workerd/compare/813c31394b9909d8f557bba14324db275bc12720...18a117c28773cd7aa0ee599e03439c5fbbf06584
- owned draft source PR: https://github.com/teamleaderleo/workerd/pull/5
- current fence: one implementation commit, ten source/test files, no workflow files

The source PR is not publication-complete. Generated snapshots are required for type-generation changes, and two generator exact-output fixtures are stale.

## Exact validation carrier

- owned draft PR: https://github.com/teamleaderleo/workerd/pull/9
- branch: `unit-10/final-validation-18a117c`
- carrier head: `159fe1e87253ae79f5b2b767d49074f1ebeb447d`
- run: `30857633684`
- product candidate pinned by workflow: `18a117c28773cd7aa0ee599e03439c5fbbf06584`
- carrier-only file: `.github/workflows/unit-10-final-validation.yml`

The carrier is execution machinery only. Its workflow must never enter source PR #5 or a public upstream diff.

## Latest exact results

Run `30857633684`:

| Job | Result | Details |
| --- | --- | --- |
| `generated-snapshot` | PASS | built `//types`, produced the expected four files, diff/report uploaded, marker check passed |
| `inherited-global-runtime` | PASS | built workerd and passed the Worker-global versus separate-`EventTarget` receiver matrix |
| `focused-and-types` | FAIL | focused receiver targets passed; complete `//types/...` failed on two stale generator expectations; lint step was skipped after the failure |

The latest run is exact-head evidence because the workflow checks that the carrier differs from the candidate only by its workflow file.

## Focused receiver targets

The following command passed on the exact candidate:

```console
bazelisk test \
  //types:test/index.spec \
  //types:test/transforms/overrides/index.spec \
  //types:test/transforms/overrides/replacement-receiver-generics.spec \
  //types:test/transforms/globals.spec \
  //types:test/types/fetch-receiver \
  --test_output=errors
```

Covered behavior includes:

- ordinary generated instance receiver insertion;
- static method exclusion;
- explicit handwritten receiver preservation;
- transformed heritage lookup;
- static constant extraction preservation;
- full replacement owner rename and generic specialization;
- legal direct Worker-global receiver forms;
- rejection of unrelated direct receivers;
- receiver erasure when assigning to a receiver-free callback type.

## Complete package failure classification

The complete package failure is a fixture-maintenance defect, not a new semantic failure.

Stale files:

1. `types/test/generator/structure.spec.ts`
   - expected generated non-static methods without an internal receiver marker;
   - actual generator structure now correctly includes `this: __JSG_GENERATED_RECEIVER__<Resource>`.
2. `types/test/generator/index.spec.ts`
   - expected generated ordinary, iterator, async-iterator, dispose, async-dispose, abort, and fetch methods without the marker;
   - actual output includes the marker on generated non-static methods;
   - generated static methods must remain receiver-free.

Repair rule: update only generated non-static method expectations. Do not add the marker to static methods, constructors, properties, call signatures, or explicit handwritten receivers.

## Native inherited-global receiver matrix

Run `30857633684`, job `91832245048`, conclusion: success.

For a method value obtained from `self.addEventListener`:

- bare: success;
- undefined receiver: success;
- null receiver: success;
- `globalThis`: success;
- `self`: success;
- unrelated object: `Illegal invocation`.

For a method value obtained from `new EventTarget().addEventListener`:

- bare: `Illegal invocation`;
- owning target: success;
- unrelated object: `Illegal invocation`.

This result rejects the PR #10 hierarchy-wide widening patch. Ordinary `EventTarget` declarations must remain owner-strict. Any inherited Worker-global typing repair must be localized to the Worker-global surface.

## Generated snapshot artifact

The generated tree contains exactly:

- `types/generated-snapshot/index.d.ts`;
- `types/generated-snapshot/index.ts`;
- `types/generated-snapshot/experimental/index.d.ts`;
- `types/generated-snapshot/experimental/index.ts`.

Artifact summary from the exact candidate:

```text
changed_files=4
added_lines=2478
removed_lines=1044
receiver_lines=1504
generated_marker_lines=0
```

Review observations:

- no `__JSG_GENERATED_RECEIVER__` marker leaks;
- the broad line count is mostly explicit receiver insertion plus mechanical formatting reflow;
- static global constants remain present;
- snapshot files are generator output and must not be hand-edited.

The snapshots must be regenerated or byte-verified after the fixture/source repair head is chosen, then committed separately from implementation changes.

## Local inherited-surface investigation tests

Before adding a Worker-global-local shadow, execute a TypeScript 5.8.3 model that proves:

1. a derived interface may redeclare an inherited method with a wider explicit `this` without breaking assignability;
2. `self.dispatchEvent` accepts bare/nullish/global/self forms;
3. `new EventTarget().dispatchEvent` remains strict;
4. an unrelated receiver remains rejected;
5. `addEventListener` keyed overload inference remains intact;
6. ambient and importable generated outputs agree;
7. the selected global receiver type does not accidentally resolve to a consumer host global.

Use `dispatchEvent` as the first discriminating fixture because it avoids `addEventListener` overload-order ambiguity.

## Final required gates

After canonical repair and snapshot materialization:

```console
bazelisk test //types/... --test_output=errors
bazelisk test //types:types_lib@eslint --test_output=errors
bazelisk build //types
```

Also require:

- exact generated snapshot diff is clean;
- latest and experimental ambient/importable bundles type-check;
- no marker leakage;
- every receiver owner resolves;
- no duplicate inherited overloads;
- ordinary `EventTarget` remains strict;
- source branch contains no workflow files;
- independent final diff review.

## Evidence status

### Passed

- focused receiver targets on exact candidate;
- native Worker-global/separate-owner characterization;
- generated declaration build;
- four-file artifact production;
- marker leakage check;
- earlier exact-candidate lint run.

### Failed and classified

- complete `//types/...`: two stale generator exact-output fixtures.

### Remaining

- fixture repair committed to canonical source;
- optional localized Worker-global shadow decision;
- regenerated snapshots committed;
- complete package, lint, build, and snapshot checks on final exact head;
- independent source-and-snapshot review.