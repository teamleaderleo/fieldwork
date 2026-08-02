# Upstream pull-request inputs — Unit 02

Status: `READY FOR HUMAN LAST-MILE REVIEW AND REWRITE`  
Proposed source: `teamleaderleo/uv:upstream/02-busybox-realpath` at `047b724212905c034c15d4f4f6f9ef330bbd2daf`  
Base: `astral-sh/uv:main` at `79bbface771210df216b738e9bdc7df95e5a9e6b`  
Public interaction authorized: `no`

## Suggested title input

`fix: make relocatable launchers compatible with BusyBox realpath`

## Verified summary inputs

- Remove unsupported `--` only from generated `realpath` calls.
- Preserve supported `dirname --` delimiters and existing symlink-first resolution.
- Update wheel and relocatable-venv generated-text expectations.
- Recognize corrected and historical relocatable shebangs for both `python` and `python3`.
- Test copied content and executable mode.
- Keep the source to one four-file commit directly on the reviewed base.

## Exact source

- Head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Diff: four files, 89 insertions, 15 deletions

Changed files:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

## Verified tests

- formatting and affected-crate compilation;
- wheel generated-shebang test;
- four-form `copy_entrypoint` migration test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy;
- GNU and Alpine 3.22 BusyBox launcher matrices;
- GNU and Alpine sourced-Bash activation matrices;
- Linux direct-shebang `$0` probe.

The exact final macOS job did not reach execution before the carrier advanced. Do not claim exact final-source macOS coverage. Earlier macOS 15 evidence may be mentioned only as supporting context.

## Human last-mile checklist

- Read every changed line.
- Decide whether four explicit migration strings are preferable to another exact representation.
- Decide whether the private-function regression test is the right placement.
- Write any public title/body independently.
- Explicitly authorize public upstream interaction.

No public upstream interaction occurred.