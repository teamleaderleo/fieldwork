# Unit 02 — uv BusyBox `realpath` compatibility

## Disposition

`READY FOR HUMAN REVIEW — CURRENT-MAIN CI QUEUED`

A clean source-only candidate removes only the unsupported `--` operand from generated `realpath` calls. It preserves every `dirname --`, retains symlink canonicalization, and keeps `uv run` compatible with persisted relocatable launchers generated before the change in both `python` and `python3` forms.

## Canonical internal ownership

- `teamleaderleo/linux-fieldwork#307` is the completed investigation and reproduction record.
- `teamleaderleo/fieldwork#435`, unit 02, owns this finished source packet and the human publication decision.
- No second UV implementation lane is active for this defect.

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
- Public upstream interaction authorized: `no`

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

## Packet guide

- `PRESENTATION.md` — executive decision brief.
- `CODE_WALKTHROUGH.md` — baby-to-technical explanation of uv, Rust, shell generation, and every changed file.
- `DEEP_DIVE.md` — technical invariants and historical constraints.
- `APPROACHES.md` — selected, rejected, and deferred designs.
- `TESTS.md` — exact execution receipts.
- `UPSTREAM_ISSUE.md` — existing-issue strategy and optional comment draft.
- `UPSTREAM_PR.md` — complete pull-request draft.
- `REVIEW.md` — human diff-review guide.
- `HANDOFF.md` — current stopping point.

## Remaining gates

- Classify the exact current-context CI run.
- Refresh canonical overlap immediately before any public action.
- Verify Astral's current contribution and AI-assistance policies.
- Have a human own the final wording and explicitly authorize upstream contact.

No public upstream interaction occurred.