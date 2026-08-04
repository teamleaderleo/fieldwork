# Pull-request draft — Unit 02

Status: `READY FOR HUMAN REVIEW; CURRENT-MAIN CI QUEUED`  
Public interaction authorized: `no`

## Proposed title

`fix: make relocatable launchers compatible with BusyBox realpath`

## Draft body

### Summary

On Alpine, BusyBox `realpath` treats `--` as a pathname instead of an option delimiter. That means uv-generated relocatable launchers can still run successfully while printing:

```text
realpath: --: No such file or directory
```

This removes `--` from the generated `realpath` calls only. It leaves `dirname --`, quoting, and symlink resolution unchanged.

`uv run` can later copy one of these generated launchers into another environment. The recognizer now accepts both the corrected and historical forms, for `python` and `python3`, so launchers written by older uv versions keep working after an upgrade.

The changed launcher and recognizer paths are Unix shell paths. Native Windows entrypoints continue to use uv's binary trampoline implementation, and the Windows batch and PowerShell activation paths are unchanged.

Closes #16209.

### Test plan

- `cargo fmt --all --check`
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`
- `cargo test -p uv-install-wheel test_shebang`
- `cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs`
- `cargo test -p uv --test python --features test-python venv::verify_pyvenv_cfg_relocatable -- --exact`
- `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`
- generated-launcher matrices on GNU and Alpine 3.22 / BusyBox 1.37
- Bash activation probes on GNU, Alpine/BusyBox, and macOS
- Fish activation probes on GNU, Alpine/BusyBox, and macOS

The BusyBox baseline reproduced the diagnostic. The candidate preserved successful interpreter and environment resolution with empty stderr. GNU and macOS remained clean.

## Current exact source

- Canonical base: `92b7185783b56e8ad1dbe0bb7600432708f2c9fb`
- Clean head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Tree: `9c6099ab9e6489377775d710b48855aae02079c3`
- Branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Relationship: one commit ahead, zero behind
- Diff: four files, 89 insertions, 15 deletions
- Internal current-context PR: `teamleaderleo/uv#29`
- Current-context CI: `30844806321` — queued at last check

The four source blobs are unchanged from the previously executed cross-platform candidate. The canonical repository advanced by 12 commits, but none touched these four paths; the clean branch was rebuilt with the validated blobs on top of the new canonical tree.

Changed files:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

## Reviewer questions

1. Are four explicit migration strings preferable to a broader generated-shebang parser?
2. Is the private `copy_entrypoint` regression test the preferred placement?
3. Does the project prefer an issue comment before the pull request, despite the existing complete report?

## Human gates

- Wait for or classify the exact current-context CI run.
- Refresh upstream issue and pull-request overlap immediately before submission.
- Read the exact four-file diff.
- Verify Astral's current contribution and AI-assistance policies.
- Rewrite or approve the public wording in the human author's own voice.
- Explicitly authorize the upstream pull-request action.

No public upstream interaction occurred.
