# Tests and receipts — Unit 02

## Exact source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Changed files: exactly four
- Diff: 89 insertions, 15 deletions

## Validation receipt

- Carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Workflow: `30753911776`
- Linux/source job: `91512671857` — success
- Artifact: `8835628919`
- Digest: `sha256:2e2bc57478d197298e0fe36815d77459d2b5c3e9b4409a646be971c3886f9d28`

## Publication receipt

- Workflow: `30756408587`
- Job: `91519210841` — success
- Artifact: `8836056361`
- Digest: `sha256:e0684ec5da7025a7b7cf4a8f7b932e06c3385d07e2146a5e8d5a8c344a2ed634`
- Published commit/tree: `047b724212905c034c15d4f4f6f9ef330bbd2daf` / `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`

## Source gates

All passed:

```text
cargo fmt --all --check
cargo check -p uv-install-wheel -p uv-virtualenv -p uv
cargo test -p uv-install-wheel test_shebang
cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs
cargo test -p uv --test python --features test-python \
  venv::verify_pyvenv_cfg_relocatable -- --exact
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
```

## Exact generation fence

```text
source realpath delimiters removed: 5
native expectation delimiters changed: 2
legacy realpath delimiters retained in run.rs: 2
dirname delimiters retained: wheel 2, virtualenv 4, run 4, venv test 4
```

Source blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

## Runtime matrices

Each launcher matrix covered current and candidate forms across absolute, relative, PATH, spaces, `./-tool`, and external symlink invocation.

Each sourced-Bash activation matrix covered absolute, relative, PATH-like lookup, spaces, `./-activate`, and external symlink sourcing.

- GNU launcher and Bash activation: pass.
- Alpine 3.22 BusyBox current: succeeds with the expected false diagnostic.
- Alpine 3.22 BusyBox candidate: succeeds with clean stderr.
- Linux direct-shebang probe: shell `$0` is the script path for forced `-tool`, `--help`, and ordinary argv0 values.

## Limits

The exact final carrier did not obtain a terminal macOS job before publication; the queued job was canceled when the carrier advanced. Earlier macOS 15 evidence passed the broader candidate, but is not claimed as an exact final-source execution.

The executable Fish supplement in `teamleaderleo/uv#18` was still queued. The exact target-native Fish generated-text assertion passed.

No public upstream contact occurred.