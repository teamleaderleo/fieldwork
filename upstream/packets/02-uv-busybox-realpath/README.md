# Unit 02 — uv BusyBox `realpath` compatibility

## Disposition

`PUBLIC ISSUE COMMENT POSTED — USER-OWNED PR PENDING; CURRENT-MAIN CI QUEUED`

A clean source-only candidate removes only the unsupported `--` operand from generated `realpath` calls. It preserves every `dirname --`, retains symlink canonicalization, and keeps `uv run` compatible with persisted relocatable launchers generated before the change in both `python` and `python3` forms.

## Canonical internal ownership

- `teamleaderleo/linux-fieldwork#307` is the completed investigation and reproduction record.
- `teamleaderleo/fieldwork#435`, unit 02, owns this finished source packet and the internal handoff.
- No second uv implementation lane is active for this defect.
- The public issue comment and any formal upstream PR are user-owned public actions, not Fieldwork automation actions.

## Current exact identity

- Canonical base: `92b7185783b56e8ad1dbe0bb7600432708f2c9fb`
- Clean source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Clean source head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Source tree: `9c6099ab9e6489377775d710b48855aae02079c3`
- Relationship: one commit ahead, zero behind
- Diff: four files, 89 insertions, 15 deletions
- Internal current-context PR: `teamleaderleo/uv#29`
- Current-context CI: `30844806321` — queued at last check
- Existing public issue: `astral-sh/uv#16209`
- Public issue comment: comment `5180749150`, posted by `teamleaderleo`
- Formal upstream PR: not recorded at last check; user stated intent to open it independently

The canonical repository advanced by 12 commits from the prior reviewed base. None changed the four touched files. The clean source was rebuilt with the same previously validated four blobs on top of the current canonical tree.

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

## Previously completed evidence

The unchanged four source blobs passed:

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

The BusyBox baseline emitted the false diagnostic. The candidate preserved the selected interpreter or environment with empty stderr. GNU and macOS remained clean.

## Public-action record

The user posted a public comment to `astral-sh/uv#16209` stating that a tested patch is ready, explaining the realpath-only correction, and announcing intent to open a PR. That comment is now part of the canonical record.

Do not post another issue comment, create a duplicate issue, or create the public PR from Fieldwork. The next public action belongs to the user unless they explicitly delegate a specific action.

## Packet guide

- `PRESENTATION.md` — executive decision brief.
- `CODE_WALKTHROUGH.md` — baby-to-technical explanation of uv, Rust, shell generation, and every changed file.
- `DEEP_DIVE.md` — technical invariants and historical constraints.
- `APPROACHES.md` — selected, rejected, and deferred designs.
- `TESTS.md` — exact execution receipts.
- `UPSTREAM_ISSUE.md` — posted issue comment and issue strategy.
- `UPSTREAM_PR.md` — complete pull-request draft.
- `REVIEW.md` — human diff-review guide.
- `HANDOFF.md` — current stopping point.

## Remaining gates

- Classify the exact current-context CI run.
- Refresh canonical overlap immediately before or after the user opens the public PR.
- Verify the public PR, if opened, points to the clean four-file candidate.
- Respond only to concrete CI or reviewer feedback.

Unit 02 is frozen except for terminal CI recording and concrete upstream feedback. New uv investigation should proceed in a separate Fieldwork lane.