# Unit 02 — uv BusyBox `realpath` compatibility

## Current disposition

`HOLD`

The defect, source ownership, selected correction, prior-art lineage, and prior focused execution are established. A clean target branch exists at current public uv base and contains the verified virtualenv portion of the source correction. Exact current-head materialization and testing are running through two private execution carriers. Public upstream contact remains unauthorized, and Astral's contribution policy requires independent human ownership of any eventual submission.

## In simple words

uv's relocatable launchers call `realpath -- "$0"`. BusyBox treats `--` as a pathname and prints `realpath: --: No such file or directory`, even though the launcher then succeeds. The candidate removes the unsupported delimiter from the synchronized wheel, virtualenv, and project-run launcher strings while preserving symlink resolution and sibling-interpreter selection.

## Identity

- Work class: upstream bug-fix preparation
- Routing issue: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Target repository: `astral-sh/uv`
- Fork repository: `teamleaderleo/uv`
- Clean source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Public source base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current clean source head at this packet revision: `5fa75d388d230fa378b9d2a42b4497927ca313c3`
- Current clean source status: one verified source owner materialized; final one-commit three-file head pending
- Existing public issue: [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209)
- Public upstream contact authorized: `no`

## Intended source diff

Exact final file fence:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`

Exact replacement fence: five `realpath --` and seven `dirname --` occurrences become delimiter-free calls. The final source branch must be one source-only commit directly on `79bbface771210df216b738e9bdc7df95e5a9e6b` with no temporary workflow, evidence, or Fieldwork files.

Current verified source edit:

- [`virtualenv.rs` at `5fa75d3`](https://github.com/teamleaderleo/uv/blob/5fa75d388d230fa378b9d2a42b4497927ca313c3/crates/uv-virtualenv/src/virtualenv.rs) — exact compare against public base is one file with two additions and two deletions.

## Packet contents

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — ownership, failure model, invariant, compatibility, risks, and claim limits
- [`APPROACHES.md`](./APPROACHES.md) — selected correction, viable alternatives, executed losing approaches, and prior art
- [`TESTS.md`](./TESTS.md) — exact commands, revisions, workflow/job/artifact receipts, setup failures, and current gaps
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — existing-issue disposition and human-authored comment inputs
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — internal PR draft and submission checklist
- [`REVIEW.md`](./REVIEW.md) — human review guide and disposition gate

## Evidence summary

### Established

- Public issue #16209 reproduces the BusyBox diagnostic and remains open.
- Prior workflow `30625826268`, job `91140735058`, passed 24/24 controlled GNU/BusyBox launcher cases.
- Prior workflow `30650924197`, job `91223680476`, passed the synchronized three-owner source generation, exact changed-path fence, `git diff --check`, affected-crate compilation, and the same GNU/BusyBox matrix.
- Prior candidate carrier head: `0aad1cc1fc9aa03fc5705da44112671101e20624`.
- Prior artifact: `8801371654`, digest `sha256:ff4221a734d356250aa38ed97d0b194635f6ef3847a24d0a652ec4b3912bbb97`.
- Public current source `79bbface` still contains all three delimiter forms.
- Upstream issue #8058 and merged PR #8079 define the symlink-first canonicalization that this correction preserves.

### Current execution carriers

- uv carrier PR [`teamleaderleo/uv#5`](https://github.com/teamleaderleo/uv/pull/5), head `1e1a66d96b4ef827ef470848cd19c504a6bdd739`
  - focused workflow `30674680508`, job `91299352922`
  - status at this packet revision: queued
- isolated Fieldwork carrier PR [`teamleaderleo/fieldwork#453`](https://github.com/teamleaderleo/fieldwork/pull/453), head `9e4903c94c16de60b5eeaec4c80bbb874309c22d`
  - focused workflow `30675833021`, job `91302764901`
  - status at this packet revision: queued

Both carriers are private execution machinery. Neither is a proposed source branch.

## Tests executed

| Revision | Command or workflow | Result |
| --- | --- | --- |
| `f8adfc6a573e3b8c44713e132ba9b7a2a3dbd502` | focused GNU/Alpine BusyBox current-vs-candidate launcher matrix | passed, 24/24 |
| `0aad1cc1fc9aa03fc5705da44112671101e20624` | exact 3-file generation fence, `git diff --check`, `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`, GNU/Alpine matrix | passed |
| `5fa75d388d230fa378b9d2a42b4497927ca313c3` | Git compare against `79bbface` for virtualenv owner | passed: one file, 2 additions, 2 deletions |
| `3ddcd43820b41d6752efa1ebd3f200848aee73bc` | rejected temporary wheel blob compare | failed exactness: intended two hunks plus one unrelated formatting drift; blob rejected before clean branch use |
| `1e1a66d96b4ef827ef470848cd19c504a6bdd739` | current-head uv carrier workflow `30674680508` | queued at this packet revision |
| `9e4903c94c16de60b5eeaec4c80bbb874309c22d` | isolated current-head Fieldwork materializer workflow `30675833021` | queued at this packet revision |

## Remaining blockers

1. Complete the exact three-file source tree and collapse the clean branch to one commit directly on `79bbface`.
2. Obtain a successful current-head focused receipt for formatting, affected-crate compilation, native shebang test, GNU matrix, and Alpine BusyBox matrix.
3. Review the exact final source head and update all packet links and receipts.
4. Resolve or explicitly accept the macOS/BSD utility gap and the unmeasured bare option-like `$0` case.
5. Obtain independent human code review and human-authored public wording under Astral's AI policy.
6. Obtain explicit authorization before any public upstream comment, issue action, or pull request.

## Negative and setup records

- The fork default branch is stale at `1da26a`, so temporary carrier PRs against it include unrelated public history. Focused jobs fence against public source `79bbface`; carrier-wide diffs cannot stand in for the clean source diff.
- The first uv custom trigger remained absent until PR close/reopen.
- Both current focused jobs entered the runner queue and had not started at this packet revision.
- Temporary wheel object `3ddcd43820b41d6752efa1ebd3f200848aee73bc` exposed one accidental unrelated formatting change. The object was rejected and never moved onto the clean branch.

## Continuation order

1. Read this README, `TESTS.md`, and the latest unit 02 handoff on #435.
2. Poll workflows `30674680508` and `30675833021`.
3. Prefer the successful isolated artifact containing all three complete source files.
4. Build one Git tree on base `79bbface`, create one source-only commit, and force-update `upstream/02-busybox-realpath`.
5. Verify the complete compare is exactly three files and five additions/five deletions.
6. Update `TESTS.md`, `REVIEW.md`, this README, and #435 with exact final heads and links.
7. Keep public upstream untouched until human review and explicit authorization.
