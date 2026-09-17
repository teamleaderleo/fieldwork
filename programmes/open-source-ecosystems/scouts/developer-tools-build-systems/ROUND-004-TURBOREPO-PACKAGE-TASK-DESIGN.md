# Developer tools scout round 004 — Turborepo package-task composition design

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `source-reviewed candidate boundary; execution pending`  
Upstream contact authorized: `false`

## In simple words

Turborepo has an established rule: an explicitly requested package-qualified task remains selected even when an unrelated package filter scopes the unqualified tasks.

The combined task-filter path preserves that rule through `always_include`. The separate `affectedUsingTaskInputs` path appears to remove the explicit task while pruning affected entrypoints, before later entrypoint handling can restore it.

A paired target-native test is queued. This note records the smallest candidate boundary if the paths produce different results.

## Established contract

Maintainer PR `vercel/turborepo#13398` added explicit package-task preservation across package filters. The current combined task-filter implementation follows that contract:

1. resolve selector matches;
2. intersect affected constraints;
3. apply exclude selectors;
4. remove excluded entrypoints;
5. extend the task set with `TaskFilterConstraints.always_include`;
6. retain selected tasks and required dependencies.

Package-qualified task requests populate `always_include`.

## Separate task-input-affected path

At merged fix `0b1f46670fc4ea8687416549fb583585846c80a5`, the separate path:

1. builds an all-package engine;
2. computes directly affected tasks and affected dependents;
3. intersects those entrypoints with package scope;
4. expands `with` siblings;
5. retains selected tasks and required dependencies;
6. later applies ordinary entrypoint selection to the already-pruned engine.

An explicitly requested package task outside package scope can disappear at step 3. Once removed, later entrypoint selection cannot restore the node.

## Paired characterization

Owned PR:

- repository: https://github.com/teamleaderleo/turborepo
- pull request: https://github.com/teamleaderleo/turborepo/pull/3
- head: `e8bdd25fdf7db5de27b33524d215f6fad5fbd429`

Command:

```text
turbo run test alpha#build --affected --filter=beta --dry=json
```

Fixture:

- alpha and beta are independent packages;
- only beta changes;
- beta provides `test`;
- alpha provides `build`;
- `alpha#build` is explicitly requested;
- beta is the reported package scope.

Expected executable tasks under the established rule:

- `alpha#build`;
- `beta#test`.

The test runs once through `filterUsingTasks` and once through the separate `affectedUsingTaskInputs` path.

## Candidate boundary if the paths diverge

Reuse the already-computed set of explicitly requested package task IDs.

Pass that set into `filter_engine_to_affected_tasks` as an inclusion set. Inside the successful SCM path:

1. compute and package-scope the affected entrypoints;
2. derive `selected_packages` from those scoped affected entrypoints, before explicit additions;
3. extend entrypoints with explicit package tasks that exist in the engine;
4. expand `with` siblings;
5. retain the filtered task graph and required dependencies.

Conceptual order:

```rust
let selected_packages = affected_entrypoints
    .iter()
    .map(|task| PackageName::from(task.package()))
    .collect();

affected_entrypoints.extend(
    always_include
        .iter()
        .filter(|task| engine.task_definition(task).is_some())
        .cloned(),
);
```

This ordering preserves beta-only package reporting while retaining explicit `alpha#build` execution.

The fail-open invalid-range branch should apply the same explicit-task inclusion after package scoping and before dependency closure.

## Reversing controls

A candidate must preserve:

- package reporting remains the package-selected affected entrypoints, not every explicit task package;
- exclude-only filters retain their existing meaning for unqualified work;
- package-qualified tasks retain the established override behavior;
- strict and legacy entrypoint policies remain separately gated;
- required dependency closure remains intact;
- no-filter task-input affectedness remains driven by affected tasks across all packages.

## Current disposition

`EXECUTION PENDING`

Do not select or write the production change until the paired exact-head test distinguishes the two paths.

No public upstream interaction was performed.
