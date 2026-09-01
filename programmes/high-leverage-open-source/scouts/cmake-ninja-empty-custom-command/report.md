# CMake Ninja evaluated-empty custom-command candidate

Date: 2026-09-01  
Programme: high-leverage-open-source  
Worker: ChatGPT  
Claim scope: interface  
Upstream contact authorized: `false`

## In simple words

CMake can retain a custom-command placeholder even when generator-expression evaluation removes every executable command. Ninja then sees a working-directory-only command instead of the generator's existing phony fallback. On Windows the resulting bare `cd /D ...` command is reported to fail process creation; on POSIX the stray `cd` can succeed and hide the underlying defect.

An owned-fork candidate makes the custom-command generator report zero executable commands only when every evaluated command line is empty. A portable RunCMake regression checks the generated Ninja rule directly, so the proof does not depend on whether a host shell happens to accept `cd`.

## Question

Can the evaluated-empty custom-command failure be expressed as a generator invariant and tested portably at generated-Ninja-file level?

## Assignment boundary

Expected deliverable: exact source/test map, portable regression, narrow owned-fork candidate, fork CI, and recommendation.  
Owned output path: `programmes/high-leverage-open-source/scouts/cmake-ninja-empty-custom-command/report.md`  
Dependencies: public CMake source; owned CMake fork; GitHub-hosted Linux Actions.  
Target revision: `Kitware/CMake` `b56fabdb461bf51e63061fb04b013bb72641ca4b`.  
Stop condition: portable regression and source fix are isolated, complete diff is reviewed, fork verifier executes the Ninja RunCMake suite, and upstream remains read-only.

## Exact source state

Repository: https://github.com/Kitware/CMake  
Issue identifier from the investigation: CMake issue `24802` on Kitware GitLab.  
Owned candidate PR: https://github.com/teamleaderleo/cmake/pull/1  
Candidate head: `8af431505e70a5dad91f276bc3cc4569237ead32`

The public GitLab issue body is bot-protected from the current retrieval environment, so this report limits issue-derived claims to the reproduction and failure description already retained in the investigation. Source and candidate claims below are pinned independently.

## Code and test map

Production owner: `Source/cmCustomCommandGenerator.cxx`

- custom-command evaluation preserves empty placeholder command lines for internal invariants;
- `HasOnlyEmptyCommandLines()` already detects the fully empty evaluated set;
- `GetNumberOfCommands()` previously returned the raw vector size even when every line was empty.

Ninja consumer: `Source/cmLocalNinjaGenerator.cxx`

- it adds the working-directory command when `GetNumberOfCommands() > 0`;
- empty evaluated commands contribute no executable lines;
- when the resulting command list is empty, the generator already has a `phony` fallback.

Regression owner: existing `Tests/RunCMake/Ninja/CommandConcat` case.

- fixture adds one command erased by generator-expression evaluation;
- check file reads `build.ninja` and requires the output to use the existing `phony` rule.

## Candidate commits

- `d216f4799c9e1efa772f5377a11c601bbc84cbca` — add the evaluated-empty fixture.
- `f2dab8031af1e31e0bc06d0e8494abd1a9a92862` — add the portable generated-rule assertion.
- `8af431505e70a5dad91f276bc3cc4569237ead32` — make `GetNumberOfCommands()` return zero when `HasOnlyEmptyCommandLines()` is true.

The production change is one expression. Mixed empty/nonempty command sets keep their original vector count and indexes.

## Portable discriminator

A local control using CMake 3.31.6 and Ninja 1.12.1 generated a `CUSTOM_COMMAND` whose command body consisted only of `cd <build-dir>`. Linux accepts that shell command, so build success alone is a false negative for the underlying defect.

The retained regression instead checks the generated rule kind. The desired output is the generator's existing `phony` rule, making the test portable across host shells.

## Proofability / consequence

**Proofability: 5/5.** The source already contains the exact predicate needed to state the invariant, the bad generated file is inspectable, and one existing RunCMake case can distinguish the states without platform-specific execution.

**Consequence: 3/5 at interface scope.** The documented failure prevents a Ninja custom-command build on the affected Windows path. This report makes no estimate of affected-project prevalence.

**Cross score: strong.** The consequence is narrower than the cmux paste loss, while the proof and implementation are exceptionally compact.

## Fork execution

Fork verifier workflow: https://github.com/teamleaderleo/cmake/actions/runs/33526460394

The verifier lives on the owned fork's default branch and explicitly checks out the candidate. It bootstraps and builds CMake on Ubuntu and runs the Ninja RunCMake suite, leaving the upstream-facing candidate diff free of the GitHub Actions carrier.

Status at initial record creation: running. Update this section with the final job result before treating execution as complete.

## Evidence labels

- Generator source behavior and helper semantics: **Observed** on pinned public source.
- Pre-fix Linux generated `CUSTOM_COMMAND` containing only `cd`: **Observed** in local control execution.
- Windows process-creation consequence: **Documented** in the retained investigation; public issue retrieval is currently blocked by GitLab's bot protection.
- Portable phony-rule regression and source candidate: **Observed** in the owned fork.
- Full candidate RunCMake execution: **Unknown** until the owned-fork verifier completes.
- Ecosystem prevalence: **Unknown** and outside this scout's supported scope.

## Recommendation

Retain as a contribution candidate. If the fork verifier passes, prepare a human-facing upstream packet for the canonical Kitware GitLab workflow; do not mutate upstream without a fresh bounded greenlight.
