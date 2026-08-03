# Pull-request draft — Unit 02

Status: `READY FOR HUMAN REVIEW; CURRENT-MAIN CI QUEUED`  
Public interaction authorized: `no`

## Proposed title

`fix: make relocatable launchers compatible with BusyBox realpath`

## Draft body

### Summary

BusyBox `realpath` treats `--` as a pathname. As a result, uv-generated relocatable launchers and activation scripts can complete successfully on Alpine while emitting:

```text
realpath: --: No such file or directory
```

This change removes `--` only from generated `realpath` calls. It preserves `dirname --`, quoting, and `realpath` canonicalization, so externally symlinked relocatable entrypoints continue to resolve the environment that owns the launcher.

The generated text is also consumed later by `uv run` when an entrypoint is copied into an overlay environment. That recognizer now accepts corrected and historical relocatable shebangs for both `python` and `python3`, so launchers created before this change remain copyable after an upgrade.

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