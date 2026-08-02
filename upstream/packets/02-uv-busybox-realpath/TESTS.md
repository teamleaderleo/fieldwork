# Tests and receipts — Unit 02: BusyBox-safe relocatable launchers

## Current judgment

`TECHNICALLY GREEN — SOURCE PUBLICATION PENDING`

The exact four-file candidate passed the complete declared Linux gate. The old clean branch is superseded and must not be used as the review subject.

## Exact execution receipt

- Source base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Validated execution carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Workflow run: `30753911776`
- Job: `91512671857` (`source-linux`) — success
- Runner: Ubuntu 24.04.4
- Rust: 1.97.1
- Artifact: `8835628919`
- Downloaded artifact ZIP SHA-256: `1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- Publication rerun: `30755813495`, job `91518761618` — queued at record time

## Exact candidate fence

```text
2   2  crates/uv-install-wheel/src/wheel.rs
4   4  crates/uv-virtualenv/src/virtualenv.rs
81  7  crates/uv/src/commands/project/run.rs
2   2  crates/uv/tests/python/venv.rs
```

Candidate blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

The retained patch is 175 lines. It removes five source `realpath --` delimiters, changes two target-native expectations, retains two legacy `realpath --` forms solely in migration constants, and retains every `dirname --` delimiter.

## Rust gates

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

Focused results:

- wheel generated-shebang assertion: 1 passed;
- four-form `copy_entrypoint` migration test: 1 passed;
- existing relocatable-venv integration test: 1 passed;
- full declared workspace clippy: passed.

The migration test exercises corrected/historical × `python`/`python3`, rewrites to the new interpreter, preserves body bytes, and preserves executable mode `0751`.

## GNU and BusyBox launcher matrix

Each current and candidate launcher ran through:

- absolute path;
- relative path;
- PATH lookup;
- spaces;
- leading-hyphen path via `./-tool`;
- external symlink.

Results:

- GNU current: all cases status 0, correct sibling interpreter, clean stderr;
- GNU candidate: all cases status 0, correct sibling interpreter, clean stderr;
- Alpine 3.22 BusyBox current: all cases status 0 and the expected false `realpath: --:` diagnostic;
- Alpine 3.22 BusyBox candidate: all cases status 0 and clean stderr.

## Bash activation matrix

The same GNU and BusyBox comparison executed sourced activation through:

- absolute path;
- relative path;
- PATH-like lookup;
- spaces;
- `./-activate`;
- external symlink.

The candidate selected the canonical environment path and produced empty stderr in every case. BusyBox current behavior produced the same false diagnostic.

## Direct shebang `$0` discriminator

Direct generated launchers were invoked while the caller requested `argv[0]` values `-tool`, `--help`, and `plain-name`. In every case the shell observed the actual script pathname as `$0`, status was 0, and stderr was empty.

A separate synthetic shell control confirmed that delimiter-free GNU `realpath` rejects a manually injected bare `$0=-tool`. That synthetic condition is not delivered by the operating-system shebang entry path. No normalization branch is supported by the observed contract.

## Fish coverage

The exact uv integration test validates the generated fish activation text and passed. Separate executable Fish matrices exist in `teamleaderleo/uv#18` for GNU, BusyBox, and macOS; their jobs were queued when this record was written. Their result is supplemental unless it reverses the target-native test or exposes a runtime defect.

## Cleanup and rerun

The execution fixtures use private temporary roots and cleanup traps. The successful job completed without retained process or temporary-state failures. Artifact download and independent patch inspection confirmed the reported four-file fence and SHA-256.

## Evidence limits

Not yet claimed:

- a clean source commit/tree for the four-file candidate;
- macOS execution for this exact four-file carrier;
- FreeBSD or another BSD-family environment;
- the complete uv test suite.

The first item is the only mechanical promotion blocker. The Linux technical gate is complete. No public upstream contact occurred.