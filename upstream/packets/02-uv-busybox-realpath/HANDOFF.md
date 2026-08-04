# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-05`

State: `PUBLIC PR OPEN — CANONICAL CI GREEN — AWAITING HUMAN REVIEW`

## Live public surface

- Public issue: `astral-sh/uv#16209`
- Public pull request: `astral-sh/uv#20943`
- Title: `fix: make relocatable launchers compatible with BusyBox realpath`
- Public base at latest check: `08c032ee486dc064ab7892dfe23c02bd0ce203ff`
- Public head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Canonical CI: run `30942625490` — success
- Mergeability: mergeable at latest check
- Human review submissions: none
- Inline review threads: none
- Current conversation content: automated test inventory only; one test added, none removed

The public pull request is the exact four-file candidate validated by this packet.

## Canonical internal locations

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Completed investigation: `teamleaderleo/linux-fieldwork#307`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Fork branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Historical internal reconciliation PR: `teamleaderleo/uv#29`

## Source identity

- Head commit: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Source tree: `9c6099ab9e6489377775d710b48855aae02079c3`
- Diff: four files, 89 insertions, 15 deletions

Changed-file blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

## Selected behavior

- Remove only unsupported `realpath --` delimiters.
- Retain every `dirname --` delimiter.
- Preserve `realpath` canonicalization for external symlinks.
- Generate corrected POSIX and Fish activation text.
- Recognize historical and corrected `python` / `python3` launchers during entrypoint copying.
- Preserve generated script bodies and executable modes.

## Evidence

Pre-submission evidence covered Linux, Alpine/BusyBox, macOS, Bash, Fish, symlinks, spaces, relative/PATH invocation, leading-hyphen path forms, focused Rust tests, compilation, formatting, and full workspace clippy.

Canonical UV CI run `30942625490` subsequently passed all planned jobs, including:

- Rust, Python, and Prettier formatting;
- Linux and all three Windows cargo-test shards;
- Linux, Windows, macOS, FreeBSD, Android, musl, ARM, and AArch64 builds;
- docs, generated files, lockfile checks, lint, release planning, publish dry-run, and benchmarks.

## Next action

Wait for a concrete upstream event.

Act only when one of these occurs:

1. a maintainer leaves a review or question;
2. CI is rerun and changes state;
3. the base moves into conflict;
4. the PR is merged or closed.

Do not post a status-ping comment or duplicate explanation. If a reviewer requests a change, inspect the exact requested invariant and update this packet together with the public head identity.

Unit 02 is feedback-only maintenance. Continue other uv investigation separately.