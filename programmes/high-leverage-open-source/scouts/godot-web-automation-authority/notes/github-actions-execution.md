# Godot GitHub Actions execution path

Retrieved/executed: 2026-08-09.

## Result

The connected GitHub tool surface does not expose a workflow-dispatch creation endpoint. It can inspect workflow runs/jobs/logs and re-run existing failed jobs, but it cannot directly invoke GitHub's `workflow_dispatch` REST endpoint.

That is not an execution blocker for this owned fork.

Godot's inherited root workflow, `.github/workflows/runner.yml`, listens to `push`, `pull_request`, `merge_group`, and `workflow_dispatch`. Its Linux reusable workflow compiles test-enabled editor builds and runs the Godot unit-test binary.

A fork-only narrow workflow was added on branch `fieldwork/godot/animation-trs-probe` at:

```text
.github/workflows/fieldwork-animation-trs.yml
```

It listens to pushes on that branch and also declares `workflow_dispatch`. It:

1. checks out recursive submodules;
2. installs the Linux dependency used by Godot's current CI;
3. uses Godot's own `.github/actions/godot-deps` helper;
4. builds an editor with `dev_mode=yes`, which Godot's `SConstruct` defines as including `tests=yes`;
5. runs only the prepared AnimationPlayer TRS test using doctest's `--test-case` filter.

The workflow commit is:

```text
teamleaderleo/godot@588e4e4054ffe65d5f0f48aa296b9d17c89be129
```

## Observed execution

Pushing that commit successfully woke GitHub Actions on the owned fork.

Inherited Godot run:

```text
run id: 31289894452
workflow: 🔗 GHA
head: 588e4e4054ffe65d5f0f48aa296b9d17c89be129
```

At the first inspected checkpoint:

- static checks completed successfully;
- Android, Web, macOS, Windows, and Linux jobs were scheduled/in progress;
- Linux editor jobs include the normal Unit tests step.

This establishes that the fork can execute GitHub-hosted Godot builds and tests without any upstream interaction.

## Operational wrinkle

A normal source push to this branch also wakes Godot's inherited root CI, whose second stage fans out across all major platform builds after static checks. That is much broader than Fieldwork usually needs for a single probe.

For future narrow research execution, prefer one of these:

1. Set the owned fork repository Actions variable `DISABLE_GODOT_CI=true`, then use the dedicated Fieldwork workflows for individual probes. Godot's root runner checks that variable for ordinary runs; manual root dispatch/re-runs can still override it through the workflow's own condition.
2. If the connected GitHub tool later exposes workflow dispatch, keep the narrow workflow on the default branch and dispatch it directly by ref.
3. Otherwise retain a push-triggered narrow workflow and use deliberately scoped probe branches, while avoiding unnecessary source pushes that wake the inherited matrix.

The current connector does not expose repository-variable mutation, so setting `DISABLE_GODOT_CI` is the one useful owner-side action if we want narrow Actions execution without the inherited matrix.

## Evidence boundary

Established:

- Actions are enabled and executable on `teamleaderleo/godot`;
- an owned push successfully triggered the inherited Godot CI;
- static checks passed on the probe head;
- platform build/test jobs were scheduled;
- a dedicated narrow Animation TRS workflow is present on the probe branch.

Pending at this note revision:

- completion/result of the AnimationPlayer TRS target-native test;
- whether the dedicated push workflow appears through the connector's limited run-listing endpoint (the endpoint currently filters to pull-request-triggered runs).

No public upstream interaction occurred. Automated upstream contact remains prohibited.
