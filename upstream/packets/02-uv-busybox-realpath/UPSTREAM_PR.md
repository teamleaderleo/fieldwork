# Upstream pull-request inputs — Unit 02

Status: `READY FOR HUMAN LAST-MILE REVIEW AND REWRITE`  
Proposed source: `teamleaderleo/uv:upstream/02-busybox-realpath` at `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`  
Base: `astral-sh/uv:main` at `79bbface771210df216b738e9bdc7df95e5a9e6b`  
Public interaction authorized: `no`

## Suggested title

`fix: make relocatable launchers compatible with BusyBox realpath`

## Suggested human-authored body input

### Summary

BusyBox `realpath` treats `--` as a pathname, so uv's relocatable launchers and activation scripts can succeed while emitting a misleading `realpath: --: No such file or directory` line on Alpine.

This change removes `--` only from generated `realpath` calls. It keeps `dirname --`, quoting, and `realpath` canonicalization intact, so externally symlinked relocatable entrypoints continue to resolve their original environment.

Project-run now recognizes corrected and historical relocatable shebangs for both `python` and `python3`, allowing launchers generated before this change to keep working when copied into an overlay environment.

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

The BusyBox baseline reproduced the diagnostic. The candidate retained successful interpreter/environment resolution with clean stderr. GNU and macOS remained clean.

## Exact source

- Head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Diff: four files, 89 insertions, 15 deletions

Changed files:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

## Why this is worth upstream attention

- The public issue remains open and has a recent report against the official Alpine image.
- The failure pollutes stderr on a successful command, which confuses logs and strict automation.
- The fix changes one unsupported delimiter rather than redesigning launchers.
- All known generated owners and the matching consumer move together.
- Historical launchers remain recognized after upgrades.
- Exact Linux, BusyBox, macOS, Bash, and Fish evidence exists.

## Reviewer questions

1. Are four explicit migration strings preferred over a broader helper or parser?
2. Is the private `copy_entrypoint` regression test the preferred placement?
3. Has current main introduced an equivalent fix or changed the generated fragments?

## Human last-mile checklist

- Refresh current upstream head and overlap immediately before submission.
- Read every changed line in the exact four-file diff.
- Confirm contribution and AI-assistance policy compliance.
- Rewrite the public body in the human author's own voice.
- Explicitly authorize the public pull request action.

No public upstream interaction occurred.