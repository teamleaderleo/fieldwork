# Developer tools scout round 004 — Turborepo package-task results

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `executed defect; owned-fork candidate authorized`  
Upstream contact authorized: `false`

## In simple words

The merged task-input affectedness repair passes the owned compatibility controls for package filters, parallel mode, exclusion, dependency closure, and entrypoint policy.

It does not preserve Turborepo's established rule for explicitly requested package-qualified tasks. The combined task-filter path keeps the explicit task; the separate `affectedUsingTaskInputs` path drops it before later entrypoint logic can restore it.

This is an executed future-flag-dependent precedence defect.

## Exact identity

- repository: https://github.com/teamleaderleo/turborepo
- owned pull request: https://github.com/teamleaderleo/turborepo/pull/3
- merged-fix base: `0b1f46670fc4ea8687416549fb583585846c80a5`
- executed head: `e8bdd25fdf7db5de27b33524d215f6fad5fbd429`
- workflow: `Round 004 affected-filter controls`
- run: `30981301116`
- job: `92226109918`
- production source changes: none

## Executed controls

The job completed repository setup successfully and passed:

1. package-scope controls;
2. package filtering through the `--parallel` engine rebuild;
3. exclude-only package selectors;
4. same-name cross-package dependency closure;
5. legacy non-strict entrypoint behavior;
6. explicit strict entrypoint behavior.

Only the paired package-task authority step failed.

## Paired characterization

Test file:

```text
crates/turborepo/tests/affected_task_filter_package_task_test.rs
```

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
- beta is the package-filter scope.

Established expected contract:

```text
packages: [beta]
tasks: [alpha#build, beta#test]
```

The paired tests run the same fixture through:

1. `filterUsingTasks = true`;
2. `filterUsingTasks = false`, selecting the separate `affectedUsingTaskInputs` path.

The combined task-filter test passed. The separate task-input affected test failed.

The isolated failure and source ordering establish the missing task as `alpha#build`: package scoping retains affected `beta#test`, while the explicit alpha task is removed before later entrypoint handling. The surviving executable task is `beta#test`.

## Contract basis

Maintainer change `vercel/turborepo#13398` explicitly preserved package-qualified tasks alongside unrelated package-filtered work.

The combined task-filter implementation follows that rule through `TaskFilterConstraints.always_include`:

1. resolve selector tasks;
2. intersect affected tasks;
3. apply exclusions;
4. add explicitly requested package tasks;
5. retain those roots and required dependencies.

The separate task-input affected path does not receive the explicit package-task set.

## Source cause

The builder already computes:

```rust
let explicitly_requested_tasks: HashSet<_> = ...;
```

The separate path calls:

```rust
self.filter_engine_to_affected_tasks(
    engine,
    &pkg_dep_graph,
    &root_turbo_json,
    &scm,
    task_level_affected_package_scope.as_ref(),
)
```

Inside that function, affected entrypoints are intersected with package scope. `alpha#build` is outside beta scope and disappears. `select_engine_task_entrypoints` runs afterward against the already-pruned engine and cannot recreate it.

## Candidate boundary

Pass the explicit package-task set into `filter_engine_to_affected_tasks` as `always_include`.

Successful change-set path:

1. compute affected tasks and dependents;
2. intersect those affected entrypoints with package scope;
3. derive `selected_packages` from the scoped affected entrypoints;
4. extend entrypoints with `always_include`;
5. expand `with` siblings;
6. retain selected roots and required dependencies.

Conceptual ordering:

```rust
let selected_packages = affected_entrypoints
    .iter()
    .map(|task| PackageName::from(task.package()))
    .collect();

affected_entrypoints.extend(always_include.iter().cloned());
```

Deriving packages before explicit additions preserves beta-only package reporting while executing explicit `alpha#build`.

The invalid-range fail-open branch should extend its package-scoped task roots with the same explicit set before `expand_with_siblings` and dependency closure.

## Required candidate gates

- paired package-task tests both pass;
- package-scope, parallel, and exclude-only controls pass;
- same-name dependency closure passes;
- strict and legacy entrypoint controls pass;
- target `affected_test` suite passes;
- formatting and clippy pass;
- only `crates/turborepo-lib/src/run/builder.rs` changes in the production candidate.

## Current disposition

`EXECUTED DEFECT / FUTURE-FLAG-DEPENDENT EXPLICIT TASK PRECEDENCE`

An execution-only owned-fork candidate is justified. No public upstream interaction was performed.
