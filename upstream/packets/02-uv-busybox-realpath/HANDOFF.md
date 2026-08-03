# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-04`

State: `READY FOR HUMAN REVIEW — CURRENT-MAIN CI QUEUED`

External contact: `unauthorized; none occurred`

## Canonical locations

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Completed investigation: `teamleaderleo/linux-fieldwork#307`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Fork: `teamleaderleo/uv`
- Clean branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Current internal reconciliation PR: `teamleaderleo/uv#29`
- Existing public issue: `astral-sh/uv#16209`

## Exact current source

- Canonical base: `92b7185783b56e8ad1dbe0bb7600432708f2c9fb`
- Clean head: `53a4bd1f7d715f57aed33bd1453954a14bb327e6`
- Source tree: `9c6099ab9e6489377775d710b48855aae02079c3`
- Relationship: one commit ahead, zero behind
- Diff: four files, 89 insertions, 15 deletions
- Current-context CI: `30844806321` — queued at last check

The canonical repository advanced 12 commits from the prior validation base. None touched the candidate's four files. The current tree combines the latest canonical base with the same four previously validated blobs.

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

## Completed evidence for the unchanged source blobs

Main exact-source carrier:

- run `30753911776`
- Linux/source job `91621197004`: success
- macOS job `91621196098`: success
- publication job `91621231746`: success

Fish supplement:

- run `30755096609`
- GNU and Alpine/BusyBox Fish job `91515786243`: success
- macOS Fish job `91515786224`: success

Passed gates include formatting, affected-crate compilation, focused native tests, full locked workspace clippy, GNU/BusyBox/macOS launcher and activation matrices, Bash and Fish, symlinks, spaces, relative/PATH invocation, leading-hyphen path forms, and exact source publication.

## First incomplete step

Read run `30844806321` by first non-green owner. Queue state is not success evidence.

If green:

1. update the packet to `READY FOR PUBLIC-ACTION DECISION`;
2. refresh canonical issue and PR overlap;
3. review the exact four-file compare;
4. verify Astral contribution and AI-assistance policy;
5. present `UPSTREAM_ISSUE.md` and `UPSTREAM_PR.md` for human approval;
6. require explicit authorization before any public action.

If red:

1. classify formatting, compilation, test, repository-CI, or infrastructure ownership;
2. repair only the owning layer;
3. retain the prior cross-platform evidence but do not use it to conceal a current-context failure.

## Review guides

- `CODE_WALKTHROUGH.md` explains uv, Rust, the shell fragment, every changed file, and the rejected alternatives.
- `UPSTREAM_ISSUE.md` contains an optional comment draft for the existing issue.
- `UPSTREAM_PR.md` contains the complete PR draft.
- `PRESENTATION.md` contains the decision case.

No public issue comment, pull request, review, reaction, email, or other upstream action occurred.