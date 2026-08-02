# Unit 02 — uv BusyBox `realpath` compatibility

## Disposition

`READY FOR LAST-MILE LOOK`

The clean candidate removes only the unsupported `--` operand from generated `realpath` calls. It deliberately preserves every `dirname --`, which BusyBox supports. It also keeps project-run compatible with persisted relocatable launchers generated before the change, including both `python` and `python3` forms.

## Exact identity

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Clean source head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Clean source tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Relationship: one commit directly on the reviewed base
- Existing public issue: `astral-sh/uv#16209`
- Public upstream interaction authorized: `no`

## Source boundary

| File | Change |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate `realpath "$0"` while retaining `dirname --`; update the exact wheel assertion. |
| `crates/uv-virtualenv/src/virtualenv.rs` | Apply the same realpath-only correction to POSIX and Fish activation generation. |
| `crates/uv/src/commands/project/run.rs` | Recognize corrected and historical `python`/`python3` relocatable shebangs; test all four forms. |
| `crates/uv/tests/python/venv.rs` | Update uv's existing relocatable activation expectations. |

Diff: four files, 89 insertions, 15 deletions. No workflow, harness, packet, or receipt file is present in the clean source commit.

Source blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

## Why this boundary

BusyBox `dirname` explicitly removes an optional `--` before reading its operand. BusyBox `realpath` instead iterates every argument as a pathname, so it reports `--` as missing. Removing both delimiters would work, but would discard protection where BusyBox already supports it.

Existing relocatable environments can be rediscovered through `bin/python3`; their wheel launchers can therefore contain `/'python3'`. Exact recognition of corrected and historical `python` and `python3` forms prevents an upgrade-time copy regression.

## Final evidence

Validation:

- Carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Workflow: `30753911776`
- Linux/source job: `91512671857` — success
- Artifact: `8835628919`
- Artifact digest: `sha256:2e2bc57478d197298e0fe36815d77459d2b5c3e9b4409a646be971c3886f9d28`

Publication:

- Workflow: `30756408587`
- Job: `91519210841` — success
- Artifact: `8836056361`
- Artifact digest: `sha256:e0684ec5da7025a7b7cf4a8f7b932e06c3385d07e2146a5e8d5a8c344a2ed634`
- Published commit/tree: `047b724212905c034c15d4f4f6f9ef330bbd2daf` / `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`

Passed gates:

- exact four-file generation and publication fences;
- `git diff --check` and `cargo fmt --all --check`;
- affected-crate compilation;
- wheel shebang test;
- four-form project-run recognizer test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy;
- GNU and Alpine 3.22 BusyBox launcher matrices;
- GNU and Alpine sourced-Bash activation matrices;
- Linux direct-shebang `$0` probe.

## Evidence limits

The exact final four-file source was not rerun on macOS because the hosted macOS job remained queued and was canceled when the carrier advanced. An earlier broader delimiter-removal candidate passed macOS 15, and the final source restores the already-supported `dirname --` form, but that is supporting evidence rather than an exact final-carrier macOS result.

A separate executable Fish supplement exists in `teamleaderleo/uv#18`; its jobs were still queued when this packet was finalized. The target-native Fish generated-text assertion passed in uv's exact integration test.

## Human last mile

Review the exact four-file compare and decide whether the explicit four-string migration recognizer is the preferred upstream shape. Public wording and any public action remain human-owned.

No public upstream interaction occurred.