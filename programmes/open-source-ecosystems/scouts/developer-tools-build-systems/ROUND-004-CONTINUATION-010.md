# Developer tools scout round 004 — continuation 010

Date: 2026-08-06  
Programme: #207  
Scout lane: #210  
Owner: `chatgpt:gpt-5.6-thinking`  
State: `Helix defect strengthened; Turborepo defect claim withdrawn pending output capture`  
Upstream contact authorized: `false`

## In simple words

Helix still has three reproducible local crash paths after the final editor view closes. Additional controls now prove that normal continuation also clears macro replay state and command counts.

The Turborepo package-task finding has been reclassified. Once its supposed control was run independently, the control failed too. That means the expected contract or fixture is wrong or incomplete; no production defect or fix is currently justified.

## Helix strengthened controls

Canonical owned review:

- pull request: https://github.com/teamleaderleo/helix/pull/3
- review branch: `review/16136-round-004-controls`
- cleanup-control head after correction: `6e34c90b877167679d4f7d753ea6816059869699`

The matrix now includes passing controls for:

- configured macro continuation while another view remains;
- configured macro replay-stack cleanup after a refused close;
- recorded macro continuation and replay-stack cleanup;
- counted dot-repeat continuation and `editor.count` cleanup.

An initial refused-close cleanup test also required an error status that this configured macro path does not retain. That unrelated assertion was removed. The cleanup property itself passed.

The three terminal cases remain the only intended product failures:

1. configured keymap macro dispatch after final-view close;
2. recorded-register macro dispatch after final-view close;
3. counted dot-repeat after final-view close.

MSRV, formatting, clippy, docs, grammar, and workspace tests remain green on the review line. The clean source candidate remains draft until it is rebased onto the corrected cleanup-control head and produces a passing source receipt.

## Turborepo correction

Canonical owned review:

- pull request: https://github.com/teamleaderleo/turborepo/pull/3
- review branch: `verify/13656-round-004-controls`
- diagnostic head: `c992d798b89bece93e87940f919abfe3cb944f93`

The original package-task characterization expected:

```text
packages: [beta]
tasks: [alpha#build, beta#test]
```

for:

```text
turbo run test alpha#build --affected --filter=beta --dry=json
```

The matrix was split into independent jobs for:

- combined `filterUsingTasks`;
- normal `affectedUsingTaskInputs`;
- invalid-range fail-open `affectedUsingTaskInputs`.

All three expectations failed, including the supposed combined-path control. Therefore the earlier future-flag-dependent defect claim is withdrawn.

The characterization now prints a compact line:

```text
ROUND004_RESULT packages=<json> tasks=<ids>
```

and the workflow captures only the final diagnostic section. Current work is reconstructing the actual contract from those three outputs.

## Turborepo candidate disposition

The clean candidate workflow and fork-default one-shot were disabled. Candidate pull request `teamleaderleo/turborepo#8` was closed without merge. No production source commit was created.

No new Turborepo production candidate should be opened until:

1. actual outputs are recorded for all three paths;
2. the combined path's behavior is understood from source and existing tests;
3. a real differential or independently invalid behavior is demonstrated.

## Current classification

### Helix

- confirmed local lifecycle correctness defects;
- application panic after terminal editor state;
- no current evidence of remote reachability, memory corruption, credential access, or code execution.

### Turborepo

- characterization under correction;
- no confirmed product defect at this checkpoint;
- no security relevance identified.

## Current boundary

- Helix three replay failures: executed and confirmed;
- Helix cleanup controls: prepared and largely executed; corrected exact-head run in progress;
- Turborepo compatibility controls: passing;
- Turborepo package-task expectation: rejected by all three paths;
- Turborepo production candidate: withdrawn;
- public upstream comments, reviews, reactions, issues, and pull requests created by this work: none.
