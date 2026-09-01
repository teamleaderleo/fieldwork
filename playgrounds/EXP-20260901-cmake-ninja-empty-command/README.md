# CMake Ninja empty-command discriminator

Experiment: `EXP-20260901-cmake-ninja-empty-command`

## In simple words

CMake's Ninja generator can keep a working-directory command after every real custom command has disappeared through generator-expression evaluation. On POSIX that leaves a harmless shell `cd`. On Windows current master spells the same line `cd /D ...`, while the single-command Ninja path does not wrap it in `cmd.exe`; issue 24802 reports the resulting process-creation failure.

Current master already knows how to represent a custom command with no executable command lines: it emits a `phony` rule. The stray working-directory line prevents that existing fallback from being reached.

## Executed control

The retained Linux/x86-64 probe used:

```text
CMake 3.31.6
Ninja 1.12.1
python3 run.py
```

For this fixture:

```cmake
add_custom_command(
  OUTPUT empty
  COMMAND "$<$<BOOL:0>:${CMAKE_COMMAND}>"
  VERBATIM
)
add_custom_target(gen ALL DEPENDS empty)
```

CMake generated:

```text
build empty | ${cmake_ninja_workdir}empty: CUSTOM_COMMAND
  COMMAND = cd <temporary-build-directory>
```

The generator expression removed the executable command, yet the rule stayed a real custom command because the working-directory line survived. The POSIX build succeeds because `cd` is interpreted by the shell.

## Current master source mapping

Public mirror revision `457b8a2acb76d0331889955b1ab74b0d21357ddf` retains the same mechanism:

1. `AppendCustomCommandLines` checks the declared command count and appends a working-directory line before examining evaluated commands.
2. Under `_WIN32` that line begins `cd /D `.
3. Each evaluated command is then read; an empty command is skipped.
4. If all commands are skipped, the working-directory line is the only line left.
5. `BuildCommandLine` wraps multiple Windows lines in the command processor, but a single line is wrapped only when `RuleNeedsCMD` recognizes a shell operator. The bare `cd /D` line does not meet that condition.
6. `WriteCustomCommandBuildStatement` already emits a `phony` build when `cmdLines` is empty.

This makes the smallest repair local to `AppendCustomCommandLines`: when the function added only the working-directory line and no evaluated command survived, remove that line and let the existing phony path handle the no-command case.

## Prepared candidate

[`candidate.patch`](candidate.patch) contains:

- one small `cmLocalNinjaGenerator.cxx` change that records the incoming command-line count and drops the lone working-directory line when every command evaluates empty;
- a six-line Ninja fixture with one false generator-expression command;
- a five-line RunCMake check requiring the generated output to use the existing `phony` rule;
- one registration line in the Ninja RunCMake suite.

The patch format was checked against reconstructed exact current-source/test hunks. The candidate still needs execution in an actual current CMake checkout before it becomes submission-ready.

## Evidence boundary

The current Windows failure was not physically rerun in this experiment. A branch-local GitHub workflow was attempted as a disposable carrier, but GitHub does not execute a newly introduced workflow from a pull request head when that workflow is absent from the base branch; the carrier was removed.

The supported mechanism claim comes from the executed Linux generated-rule control plus current master source. The Windows process-creation consequence remains the behavior documented by CMake issue 24802 until reproduced again on a current Windows build.

## Next action

Apply `candidate.patch` to the user's current CMake fork, run the focused Ninja RunCMake test and the repository-required relevant checks, inspect the exact diff, then decide whether the candidate is ready for a human-authored GitLab merge request.

Upstream contact remains unauthorized in Fieldwork. CMake's current AI policy permits AI-assisted preparation while requiring a human author to understand and own the submission.
