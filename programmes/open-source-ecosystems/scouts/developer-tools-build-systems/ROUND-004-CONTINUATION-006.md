# Developer tools scout round 004 — continuation 006

Date: 2026-08-05  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `executed compatibility evidence plus adjacent replay and precedence characterizations`  
Upstream contact authorized: `false`

## In simple words

The first verification layer is complete for Helix. The upstream command-sequence repair plus five owned controls passed the fork's full Build workflow across the repository's test and lint matrix.

The deeper pass found three other Helix input-replay loops with the same terminal-state risk. Those new tests are running on a later exact head.

Turborepo now has a fork-local workflow for the retained compatibility controls. A new paired test compares package-qualified task precedence between the combined task-filter path and the separate task-input-affected path.

No production candidate is selected until the new exact-head runs complete.

## Helix executed evidence

Owned review PR:

- repository: https://github.com/teamleaderleo/helix
- pull request: https://github.com/teamleaderleo/helix/pull/3
- upstream repair base: `85e9b90b66e614e10ace01f50e03d5abc0908b1d`
- previously executed owned head: `4fba0b672d792e3468194a7a6c23564f6b931637`
- workflow run: `30946764729`
- workflow: `Build`
- conclusion: `success`

The successful workflow included:

- `cargo check` at the declared MSRV;
- `cargo test` and `cargo integration-test` on macOS;
- `cargo test` and `cargo integration-test` on Ubuntu x86-64 and ARM;
- `cargo test` and `cargo integration-test` on Windows x86-64 and ARM;
- formatting, clippy, documentation, grammar, query, indent, highlight, and theme validation.

This executes the five controls that were present at that head:

1. single-command final close remains safe;
2. normal-mode command sequences stop after final close;
3. ordinary non-closing sequences still complete;
4. closing one of multiple views continues against the remaining view;
5. refused final close continues and preserves the error state.

Disposition for those controls: `PASS`.

## Helix deeper replay pass

The upstream patch stops only `KeymapResult::MatchedSequence`. Source review found three other synthetic-input loops:

1. configured keymap macros in `MappableCommand::Macro`;
2. recorded-register macro replay in `replay_macro`;
3. counted dot-repeat in `EditorView::command_mode`.

Each loop can dispatch another synthetic key or iteration after a prior key closes the final view.

Current owned head:

- branch: `review/16136-round-004-controls`
- head: `4b750d6db183c199f648ff1079b7cf1eac59e57c`
- current Build run: `30981560017`
- state at record time: queued

New characterizations:

- configured macro closes final view, then contains movement;
- configured macro continues when another view remains;
- recorded `Q … Q`, `q` macro closes final view before a later recorded key;
- counted `.` replay closes final view on its first iteration and must not begin the second.

Evidence label: `prepared and workflow-queued`.

## Turborepo execution setup

Owned verification PR:

- repository: https://github.com/teamleaderleo/turborepo
- pull request: https://github.com/teamleaderleo/turborepo/pull/3
- merged-fix base: `0b1f46670fc4ea8687416549fb583585846c80a5`
- branch: `verify/13656-round-004-controls`
- current head: `e8bdd25fdf7db5de27b33524d215f6fad5fbd429`
- production source changes: none

A branch-scoped workflow was added at:

- `.github/workflows/round-004-affected-filter-controls.yml`

It runs the four standalone integration-test binaries using the repository's own Node, Rust, Zig, and capnproto setup actions.

Current focused workflow:

- run: `30981301116`
- state at record time: queued

The fork also launched the repository's ordinary Test, Lint, JavaScript test, title, release-gate, and cache-cleanup workflows for the exact head.

## Turborepo package-qualified task contract

A merged maintainer change, `vercel/turborepo#13398`, explicitly preserved package-qualified task semantics. Its tests establish that an explicitly requested package task remains selected alongside unqualified work scoped by an unrelated package filter.

The combined `filterUsingTasks` path implements this through `TaskFilterConstraints.always_include`, extending explicit package tasks after selector, affected, and exclusion constraints.

The merged `affectedUsingTaskInputs` composition path scopes affected entrypoints to package scope before restoring execution dependencies and does not visibly apply the same explicit-task inclusion rule.

Paired characterization command:

```text
turbo run test alpha#build --affected --filter=beta --dry=json
```

Fixture:

- only beta changes;
- `beta#test` is the affected unqualified task;
- `alpha#build` is explicitly requested;
- the reported package scope remains beta.

Expected task set under the established package-task contract:

- `alpha#build`;
- `beta#test`.

The test runs once with `filterUsingTasks = true` and once through the separate `affectedUsingTaskInputs` path. A mismatch would establish future-flag-dependent precedence behavior.

Evidence label: `prepared and workflow-queued`.

## Current disposition

- Helix sequence repair controls: `EXECUTED / PASS`.
- Helix macro and repeat replay questions: `EXECUTION PENDING`.
- Turborepo compatibility and package-task precedence questions: `EXECUTION PENDING`.
- Public upstream interaction: `false`.

The next durable record must quote exact failing test names and outputs or record exact-head success. No production edit should precede that evidence.
