# Unit 02 — uv BusyBox `realpath` compatibility

## Current disposition

`TECHNICALLY GREEN — CLEAN SOURCE PUBLICATION PENDING`

The active four-file candidate is validated. The canonical clean branch is not yet authoritative: `teamleaderleo/uv:upstream/02-busybox-realpath` still points at superseded head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`, which removes both `realpath --` and `dirname --`, recognizes only the older two-form migration set, and omits the target-native venv expectation changes.

Do not review or submit that stale branch.

## Selected correction

The candidate removes only the unsupported `realpath --` delimiter and deliberately retains every `dirname --` delimiter. It changes four files:

| File | Responsibility |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate BusyBox-safe relocatable wheel launchers and update the exact unit assertion |
| `crates/uv-virtualenv/src/virtualenv.rs` | Generate BusyBox-safe POSIX and fish relocatable activation paths |
| `crates/uv/src/commands/project/run.rs` | Recognize corrected and historical `python`/`python3` launchers and test all four forms |
| `crates/uv/tests/python/venv.rs` | Update existing target-native POSIX and fish generated-text expectations |

No workflow, harness, publisher, packet, or receipt file belongs in the clean source commit.

## Exact validated identity

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Public target: `astral-sh/uv#16209`
- Public base/current main used by the candidate: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Execution carrier PR: `teamleaderleo/uv#7`
- Validated carrier commit: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Current execution carrier head: `1382154a7f0e68d530ca88b9ddfa81087b4829c7`
- Linux workflow run: `30753911776`
- Linux job: `91512671857` — success
- Linux artifact: `8835628919`
- Artifact ZIP SHA-256: `1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- Publication rerun: `30755813495`, job `91518761618` — queued when this record was written
- Public upstream contact authorized: `no`

Candidate blob identities recorded by the successful job:

| File | Blob |
| --- | --- |
| `wheel.rs` | `49c04343714990cfbc8bf891162b4889678b08f5` |
| `virtualenv.rs` | `b251b09b63771e6833b872ef05003e5290501bd3` |
| `run.rs` | `91bfe0517944f19aa3ac79f6788619131cd07949` |
| `venv.rs` | `f68dc858066242be1888b922262d53e22975856a` |

## Exact complete diff

The retained candidate patch is 175 lines and changes exactly four paths:

```text
2   2  crates/uv-install-wheel/src/wheel.rs
4   4  crates/uv-virtualenv/src/virtualenv.rs
81  7  crates/uv/src/commands/project/run.rs
2   2  crates/uv/tests/python/venv.rs
```

The source/test contract is exact:

- five generated-source `realpath --` occurrences removed;
- two existing venv expected-text occurrences updated;
- two historical delimiter-bearing shebang constants retained only for migration recognition;
- all `dirname --` occurrences retained: wheel 2, virtualenv 4, run 4, venv test 4.

## Executed gates

The successful Linux job passed:

- `cargo fmt --all --check`;
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
- `cargo test -p uv-install-wheel test_shebang`;
- `cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs`;
- `cargo test -p uv --test python --features test-python venv::verify_pyvenv_cfg_relocatable -- --exact`;
- `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`;
- GNU and Alpine 3.22 BusyBox launcher matrices;
- GNU and Alpine 3.22 BusyBox sourced-Bash activation matrices;
- direct generated-shebang `$0` probing.

BusyBox baseline behavior succeeded while emitting `realpath: --: No such file or directory` in every tested case. The candidate succeeded with empty stderr. GNU baseline and candidate behavior remained clean.

A separate Fish execution supplement is retained in `teamleaderleo/uv#18`; its Linux and macOS jobs were queued when this record was written. The target-native fish generated-text assertion already passed in the exact uv integration test above.

## Review conclusions

- `realpath` itself must remain. Historical upstream PR #8079 introduced canonical launcher resolution so an externally symlinked entrypoint selects the interpreter beside the real launcher rather than beside the symlink.
- Removing only `realpath --` is the smallest common GNU/BusyBox/macOS form. Generation-time shell-flavor detection would encode the build host into a relocatable artifact and is rejected.
- Direct kernel shebang execution supplies the script pathname as shell `$0`, even when the caller requests `argv[0]` values such as `-tool` or `--help`. The supported `./-tool` form also passed. No speculative normalization branch is selected.
- Migration recognition is bounded to the exact forms uv is shown to generate: current and historical, `python` and `python3`. Broader versioned or alternate-interpreter spellings are not added without an observed producer.
- No active equivalent upstream pull request was found in the current overlap search.

## First incomplete step

Publish the already validated four-file tree as one source-only commit directly on `79bbface771210df216b738e9bdc7df95e5a9e6b`, move `upstream/02-busybox-realpath` to that commit, and record its commit/tree identities. Then refresh this packet from `TECHNICALLY GREEN` to the final human-review state.

If the queued publisher remains unavailable, preserve this packet and artifact rather than weakening the one-commit source fence.

No public issue comment, pull request, review, reaction, email, or other upstream contact occurred.