# Unit 02 — uv BusyBox `realpath` compatibility

## Disposition

`PUBLIC PR OPEN — CANONICAL CI GREEN — AWAITING HUMAN REVIEW`

Public pull request: `astral-sh/uv#20943`  
Public head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`  
Canonical CI: run `30942625490` — success

A clean source-only candidate removes only the unsupported `--` operand from generated `realpath` calls. It preserves every `dirname --`, retains symlink canonicalization, and keeps `uv run` compatible with persisted relocatable launchers generated before the change in both `python` and `python3` forms.

## Canonical ownership

- `teamleaderleo/linux-fieldwork#307` is the completed investigation and reproduction record.
- `teamleaderleo/fieldwork#435`, unit 02, owns this internal packet and handoff.
- `astral-sh/uv#20943` is now the live public review surface, opened by `teamleaderleo`.
- No second implementation lane is active for this defect.

## Public PR state

- Title: `fix: make relocatable launchers compatible with BusyBox realpath`
- Public base at the latest check: `08c032ee486dc064ab7892dfe23c02bd0ce203ff`
- Head branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Head commit: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Diff: four files, 89 insertions, 15 deletions
- Mergeability: mergeable at the latest check
- Canonical CI: run `30942625490` completed successfully
- Human reviews: none at the latest check
- Inline review threads: none at the latest check
- Conversation: only the automated test-inventory comment, recording one added test and no removed tests

The public diff is the exact four-file candidate reviewed and validated in this packet. Canonical CI passed formatting, Linux and Windows test shards, builds across supported targets, generated-file checks, docs, lockfiles, lint, release planning, publish dry-run, and simulated benchmarks.

## Source boundary

| File | Change |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate `realpath "$0"` while retaining `dirname --`; update the exact launcher assertion. |
| `crates/uv-virtualenv/src/virtualenv.rs` | Apply the same realpath-only correction to POSIX and Fish activation generation. |
| `crates/uv/src/commands/project/run.rs` | Recognize corrected and historical `python`/`python3` relocatable shebangs; test all four forms. |
| `crates/uv/tests/python/venv.rs` | Update uv's existing relocatable activation expectations. |

## Why this boundary

BusyBox `dirname` accepts an optional `--`. BusyBox `realpath` treats every argument as a pathname and reports `--` as missing. The candidate removes the incompatible token and leaves the rest of the path-resolution algorithm intact.

A relocatable environment can be generated on one host and executed on another, so generation-host BusyBox detection is weaker than one portable fragment.

Historical launchers persist across uv upgrades. Exact recognition of corrected and legacy `python` and `python3` forms prevents a migration regression while keeping the accepted grammar narrow.

## Evidence

Before public submission, the unchanged source blobs passed:

- exact four-file generation and publication fences;
- formatting and affected-crate compilation;
- wheel generated-shebang test;
- four-form `uv run` migration test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy;
- GNU and Alpine 3.22 / BusyBox 1.37 launcher matrices;
- GNU, Alpine/BusyBox, and macOS Bash activation probes;
- GNU, Alpine/BusyBox, and macOS Fish activation matrices;
- Linux direct-shebang `$0` discriminator.

Canonical upstream CI has now also passed at the public head.

## Operating rule

Do not add another issue comment or unsolicited PR comment. The next useful event is concrete maintainer feedback, a requested change, a base conflict, or merge/closure. Respond only to the actual owner of that event.

## Packet guide

- `PRESENTATION.md` — executive decision brief.
- `CODE_WALKTHROUGH.md` — explanation of uv, Rust, shell generation, and every changed file.
- `DEEP_DIVE.md` — technical invariants and historical constraints.
- `APPROACHES.md` — selected, rejected, and deferred designs.
- `TESTS.md` — execution receipts.
- `UPSTREAM_ISSUE.md` — issue strategy and posted comment.
- `UPSTREAM_PR.md` — public PR source material.
- `REVIEW.md` — diff-review guide.
- `HANDOFF.md` — current stopping point.

Unit 02 is now feedback-only maintenance. New uv work belongs in a separate lane.