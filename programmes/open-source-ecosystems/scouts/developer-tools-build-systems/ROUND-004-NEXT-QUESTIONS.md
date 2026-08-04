# Developer tools scout round 004 — next source questions

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `fresh bounded questions; no defect claim`  
Upstream contact authorized: `false`

## Turborepo — package-qualified task authority

Current source exposes a contract difference worth testing after the merged affected-filter repair.

The combined task-filter path collects explicitly package-qualified task requests and adds them through the `always_include` constraint after selector, affected, exclude, and entrypoint filtering.

The separate `affectedUsingTaskInputs` path computes affected entrypoints, intersects them with package scope, and then restores execution dependencies. It does not visibly apply the same `always_include` step during that intersection.

## Bounded question

When a user names a package-qualified task and also supplies package scope, which input has final authority?

Example:

```text
turbo run alpha#test --affected --filter=beta --dry=json
```

Competing contracts:

1. the explicit `alpha#test` request is unconditional and survives `--filter=beta`, matching the combined path's `always_include` behavior;
2. package scope remains authoritative and removes `alpha#test`;
3. explicit package tasks bypass ordinary filters but remain subject to task-input affectedness.

## Required controls

- combined `filterUsingTasks` path versus separate `affectedUsingTaskInputs` path;
- include selector and exclude-only selector;
- explicitly requested task affected versus unaffected;
- strict entrypoint selection on and off;
- package reporting aligned with whichever execution contract is established.

## Stop condition

Retire the question if current documentation or existing target-native tests explicitly define package filters as authoritative over package-qualified task requests in both paths.

Do not call this a regression until the expected contract is established and an exact-head test distinguishes the implementations.

## Helix — review lane boundary

The active upstream repair for final-view command sequences matches the owned source model. The next useful Helix work is compatibility execution of the review overlay, not inventing another production patch.

Potential later exploration should start from a different lifecycle boundary rather than extending the resolved final-view question.

No public upstream interaction occurred.
