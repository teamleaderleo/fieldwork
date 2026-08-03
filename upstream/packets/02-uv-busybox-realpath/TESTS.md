# Tests and receipts — Unit 02

## Exact source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Relationship: one commit ahead, zero behind
- Changed files: exactly four
- Diff: 89 insertions, 15 deletions

## Main exact-source receipt

Run `30753911776`, latest completed attempt:

- Linux/source job `91621197004` — success
- macOS job `91621196098` — success
- publication job `91621231746` — success

Artifacts:

- Linux `8835628919`, digest `sha256:1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- macOS `8847852798`, digest `sha256:5053067966a50e9bcf842a9433f9509b89d49e0d202e492884e5ced8f203646b`
- publication `8847875671`, digest `sha256:0c7f3655f2ec681db1d3d2caf4ab1c6a7de29b3657898cb13d96a75b9d849b9d`

The publication job regenerated the candidate, checked the four expected blob hashes, built a tree from the exact base, created one source-only commit, verified the changed paths, and updated only the controlled clean branch.

An earlier independent publication also succeeded:

- run/job `30756408587` / `91519210841`
- artifact `8836056361`
- digest `sha256:e0684ec5da7025a7b7cf4a8f7b932e06c3385d07e2146a5e8d5a8c344a2ed634`

## Fish supplement

Run `30755096609`:

- GNU and Alpine/BusyBox Fish job `91515786243` — success
- macOS Fish job `91515786224` — success

Artifacts:

- Linux Fish `8836836696`, digest `sha256:cf515d657784f09ba555517769842f364738a7961ee91151552c3b5aebccc9b0`
- macOS Fish `8836553214`, digest `sha256:23a08fed67b9edc573122025f6057560b68872e9cb580dd9ea316468ab755615`

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

Launcher matrices covered current and candidate forms across absolute, relative, PATH, spaces, `./-tool`, and external-symlink invocation.

Bash activation probes covered absolute, relative, PATH-like lookup, spaces, `./-activate`, and external-symlink sourcing.

Fish activation probes covered absolute, relative, spaces, `./-activate.fish`, and symlink sourcing.

Results:

- GNU launchers and Bash activation: pass, clean stderr.
- Alpine 3.22 / BusyBox 1.37 baseline: succeeds while reproducing the false diagnostic.
- Alpine candidate: succeeds with clean stderr.
- macOS Bash and Fish candidate: pass, clean stderr.
- Linux direct-shebang probe: `$0` is the script path for forced `-tool`, `--help`, and ordinary argv0 values.

Each matrix asserted the resolved sibling interpreter or environment, status, arguments where applicable, and stderr policy.

## Limits

- The complete repository test suite was not run.
- Public overlap and current-main applicability must be refreshed before submission.
- No public upstream contact occurred.