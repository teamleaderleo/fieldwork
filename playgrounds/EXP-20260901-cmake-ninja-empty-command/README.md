# CMake Ninja empty-command discriminator

Experiment: `EXP-20260901-cmake-ninja-empty-command`

## Question

Does an empty generator-expression custom command still produce a failing Ninja command on current Windows CMake while the equivalent Linux Ninja build succeeds?

## Why this candidate

CMake issue 24802 reports a Windows Ninja failure when a custom command becomes empty after generator-expression evaluation. The failure surface is attractive for a bounded contribution because it is build-file correctness, has a tiny synthetic fixture, and the issue is tagged for external contribution. Before source work, this experiment checks whether the reported behavior still exists on a current hosted Windows environment.

## Linux control

A local Linux/x86-64 control with CMake 3.31.6 and Ninja 1.11.1 configured and built the `OUTPUT` variant successfully. Its generated command was only a working-directory change:

```text
COMMAND = cd <build-directory>
```

That result supports a platform-specific discriminator: a working-directory-only line is harmless through the POSIX shell, while the reported Windows path may attempt to launch `cd` directly.

## Windows treatment

The branch-local workflow tests two fixtures on `windows-latest`:

1. `add_custom_command(OUTPUT ...)` with its only `COMMAND` erased by a false generator expression;
2. `add_custom_target(...)` with the same empty command.

For each fixture it records the installed CMake/Ninja versions, the generated Ninja `COMMAND =` line, and the build exit code.

## Decision

- **Promote to source/test mapping** if the Windows build reproduces the process-creation failure while configuration succeeds.
- **Stop as a negative result** if both variants build successfully on the current runner.
- Keep upstream read-only during this experiment. No external contact is authorized.
