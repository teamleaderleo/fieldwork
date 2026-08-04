# Review — Unit 02

## Disposition

`READY FOR HUMAN REVIEW — CURRENT-MAIN CI QUEUED`

## Subject

- Base: `92b7185783b56e8ad1dbe0bb7600432708f2c9fb`
- Current head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Tree: `9c6099ab9e6489377775d710b48855aae02079c3`
- Branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Relationship: one commit ahead, zero behind
- Internal current-context PR: `teamleaderleo/uv#29`
- Current-context CI: `30844806321` — queued at last check
- Public authority: none

The canonical uv repository advanced by 12 commits after the previously validated source. None changed the four touched files. The current head applies the same validated four source blobs to the newer canonical tree.

## Changed files

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

## Human review notes — 2026-08-04

The first independent human read found the core correction clear and appropriately narrow:

- remove `--` only from `realpath`;
- retain supported `dirname --` calls;
- retain exact legacy recognition;
- use named constants for the four known migration forms rather than broad parsing.

Public-writing preference:

- make the summary less formal and less report-like;
- split the explanation into shorter paragraphs;
- explain why BusyBox users matter;
- state the Windows boundary directly.

The pull-request draft has been revised accordingly. This is an ongoing review, not an approval or authorization to contact upstream.

## Why BusyBox matters

BusyBox supplies compact implementations of common Unix commands and is widely used in minimal Linux systems. Alpine Linux uses BusyBox utilities by default, and Alpine is common in small container images and CI environments.

The public issue reproduces the problem on Alpine 3.22 with BusyBox 1.37: the installed command succeeds but emits a false-looking `realpath: --:` error. A Python tool manager that advertises portable environments should not produce spurious diagnostics on a supported and common minimal-Linux userland when one tested portable form works across GNU, BusyBox, and macOS.

This does not mean every BusyBox environment is identical or that Alpine is the only affected system. Alpine is the concrete reported and executed carrier.

## Platform and Windows boundary

### Native command launchers

`wheel.rs` emits this shell wrapper only when the target operating-system name is `posix`. The source itself notes that Windows uses binary trampoline launchers, which already support relative executable paths.

### `uv run` migration

The four shell-string constants, the shell-entrypoint copying function, and its regression test are guarded by `#[cfg(unix)]`. Windows has a separate `#[cfg(windows)]` implementation that reads and rewrites binary trampolines. No Windows trampoline code changed.

### Virtual-environment activation

The patch updates the POSIX `activate` and Fish `activate.fish` templates. `activate.bat` is unchanged, and the source notes that `activate.ps1` is already relocatable by default.

A Unix-like shell running on Windows could still consume a Bash or Fish activation file. Therefore the precise claim is **native Windows launcher, batch, and PowerShell behavior are unchanged**, not that no Windows machine could ever read the modified shell text.

### Why there is no Windows runtime matrix

The defect is a command-line contract difference between GNU/macOS-style and BusyBox `realpath` inside POSIX/Fish shell fragments. No Win32 launcher or native Windows activation implementation changed.

The affected behavior was therefore executed in the environments that own that contract:

- GNU/Linux;
- Alpine 3.22 / BusyBox 1.37;
- macOS;
- Bash-compatible activation;
- Fish activation.

The workspace compile and lint gates still cover the changed Rust source structurally. A Windows generated-text assertion could be added if maintainers request it, but it would not exercise the BusyBox failure and is not currently required to distinguish this patch's behavior.

## Complete-diff review result

No remaining product-code defect was found in the exact four-file diff.

Review focus:

1. Only `realpath --` is removed; every supported `dirname --` remains.
2. `realpath` itself remains, preserving externally symlinked relocatable entrypoints.
3. The project-run recognizer accepts four explicit migration forms: corrected/historical × `python`/`python3`.
4. The absolute-shebang fallback remains unchanged.
5. The private regression test verifies copied content and executable mode.
6. Existing relocatable-venv generated-text expectations move with the generator.

## Design challenge reviewed

A public issue comment suggested detecting BusyBox and conditionally post-processing generated text. The selected unconditional form is stronger for relocatable artifacts: generation host and execution host can differ, while `realpath "$operand"` passed on GNU, BusyBox, and macOS. Host-flavour branching would add state without protecting a demonstrated supported case.

## Completed gates

- exact four-file source and publication fences;
- format and affected-crate compilation;
- wheel, project-run, and relocatable-venv tests;
- full locked workspace clippy with warnings denied;
- GNU and BusyBox launcher and Bash activation probes;
- GNU, BusyBox, and macOS Fish activation probes;
- exact-source macOS main carrier;
- clean one-commit publication.

Main run `30753911776`:

- Linux/source `91621197004`: success
- macOS `91621196098`: success
- publication `91621231746`: success

Fish run `30755096609`:

- Linux GNU/BusyBox `91515786243`: success
- macOS `91515786224`: success

## Known limits

- The full repository test suite was not run.
- Exact current-main CI remains queued.
- Public overlap requires one final refresh.
- The four explicit matcher strings are intentionally narrow. Broader parsing would need a concrete producer or migration case.

## Human decision

Approve this for upstream preparation when the reviewer agrees that:

- the four-string migration recognizer is preferable to a broader parser or refactor;
- exact current-main CI is adequately classified;
- exact current-main overlap remains clear;
- the public contribution policy and authorship requirements are satisfied;
- the final public action is explicitly authorized.

No public action has been taken.
