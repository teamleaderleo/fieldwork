# Developer tools scout round 004 — continuation 009

Date: 2026-08-06  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `CI repaired; candidate runners reworked; source receipts pending`  
Upstream contact authorized: `false`

## In simple words

The two product findings remain ordinary correctness defects rather than security disclosures.

The Helix finding is a local panic after the editor has already entered terminal state. The Turborepo finding is a task-selection mismatch that can omit an explicitly requested task under one future-flag composition.

This continuation cleans up CI problems in the owned tests, replaces a stale Turborepo candidate PR after a rebase, adds fail-open coverage, and separates an unrelated local Context7 receipt bundle from this round.

## Local workspace review

The local workspace contained no Helix or Turborepo checkout. It contained one prior evidence archive:

- archive: `context7-omit-client-ip-on-encryption-failure.zip`
- archive SHA-256: `c2de1d9c85b96c11b6620f49c8004f6329def70e47c011720e27ff5a1eb3d300`
- declared target head: `594a73133e14631af8c915a1b4f2c8039c964fe1`
- declared Fieldwork head: `3360d80d8aa90e3eaafea3367ff9dcfd4dfe0345`
- declared patch SHA-256: `bcdbef2c71e89d456267d3bc82a3eed2f62f03133b2dab326196d29fb24309d5`

The patch hash matches the included checksum. Its receipt records three focused Vitest cases plus complete MCP tests, formatting, lint, typecheck, build, and diff-hygiene gates as passing. Its boundary fields report no credentials, hosted API, MCP session, Redis, or upstream contact.

This is internally consistent prior Context7 evidence. It is unrelated to the current Helix and Turborepo branches and is not used as evidence for either finding.

## Turborepo CI cleanup

Canonical owned review:

- pull request: https://github.com/teamleaderleo/turborepo/pull/3
- branch: `verify/13656-round-004-controls`
- current review line: merged upstream repair plus owned compatibility and precedence tests

A normal lint run exposed a test-quality issue independent of the product candidate: three owned test files were not `rustfmt` clean.

The following files were formatted without changing their behavior:

- `affected_task_filter_dependency_closure_test.rs`;
- `affected_task_filter_legacy_entrypoint_test.rs`;
- `affected_task_filter_package_task_test.rs`.

This cleanup is necessary for two reasons:

1. the review branch itself should pass repository formatting policy;
2. a candidate workflow that runs `cargo fmt` and then demands a one-production-file diff would otherwise fail because formatting also touched the test files.

The canonical review head advanced through the formatting commits and remains production-source-free.

## Turborepo fail-open control

The package-task candidate modifies both the successful SCM path and the invalid-range fail-open path. The original paired test covered only successful changed-file resolution.

A third test now exercises the fail-open case by setting an intentionally missing `TURBO_SCM_BASE` while running:

```text
turbo run test alpha#build --affected --filter=beta --dry=json
```

Required contract:

```text
packages: [beta]
tasks: [alpha#build, beta#test]
```

The test is named:

```text
task_input_affected_fail_open_preserves_package_qualified_task
```

This asks the candidate to preserve the explicit package task when changed-file resolution fails, while keeping reported packages tied to the requested package scope.

The new control is prepared. A passing target receipt is not yet claimed.

## Turborepo clean candidate transition

The first clean candidate PR briefly had a head equal to its base during a force rebase, so GitHub closed it automatically as an empty pull request.

Replacement candidate:

- pull request: https://github.com/teamleaderleo/turborepo/pull/6
- branch: `fix/13656-package-task-clean`
- base branch: `verify/13656-round-004-controls`
- intended production diff: `crates/turborepo-lib/src/run/builder.rs`

The branch was rebased onto the formatted review line before its temporary workflow was restored. Temporary workflow and synchronization files remain until the candidate gates pass and create an ordinary source commit.

A one-shot workflow was also installed on the owned fork default branch. It checks out the exact candidate branch, applies the reviewed one-file change, runs the paired matrix, compatibility controls, upstream affected suite, and clippy, then commits only the production file if every gate passes.

No source commit or passing candidate receipt is claimed at this checkpoint.

## Helix current state

Upstream sequence repair:

- pull request: https://redirect.github.com/helix-editor/helix/pull/16136
- state: open and mergeable at recheck
- review submissions: none
- inline review threads: none

Executed owned characterization remains:

- pull request: https://github.com/teamleaderleo/helix/pull/3
- exact failing source head: `4b750d6db183c199f648ff1079b7cf1eac59e57c`
- Build run: `30981560017`
- workspace tests: passed
- integration result: `183 passed; 3 failed`

The failures remain confined to configured keymap macros, recorded-register macro replay, and counted dot-repeat continuing after the final view closes.

Clean owned candidate:

- pull request: https://github.com/teamleaderleo/helix/pull/7
- branch: `fix/final-view-replay-loops-clean`
- intended production diff:
  - `helix-term/src/commands.rs`;
  - `helix-term/src/ui/editor.rs`.

The normal Build matrix continues to reproduce the baseline failures while the branch contains no production change. A one-shot owned-fork workflow now checks out the exact clean branch, applies the three reviewed terminal checks, runs the focused command-sequence tests and workspace tests, then commits only the two production files if all gates pass.

No source commit or passing candidate receipt is claimed at this checkpoint.

## Review classification

### Helix

- category: local lifecycle correctness;
- current effect: panic after terminal editor state;
- current evidence of remote reachability, memory corruption, credential access, or code execution: none;
- severity posture: bounded application crash until broader evidence appears.

### Turborepo

- category: task-selection correctness;
- current effect: an explicitly requested package task can be omitted in one future-flag path;
- likely operational consequence: incomplete local or CI work under that configuration;
- current security evidence: none.

## Current boundary

- confirmed Helix replay failures: executed evidence;
- confirmed Turborepo package-task mismatch: executed evidence;
- Turborepo formatting cleanup: committed in the owned fork;
- Turborepo fail-open control: prepared, execution pending;
- clean production candidates: no passing receipt yet;
- local Context7 archive: reviewed separately and excluded from this round's conclusions;
- public upstream comments, reviews, reactions, issues, and pull requests created by this work: none.
