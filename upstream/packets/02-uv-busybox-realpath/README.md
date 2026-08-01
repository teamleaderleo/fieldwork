# Unit 02 — uv BusyBox `realpath` compatibility

## Current disposition

`HOLD — clean source ready; independent human review and public authorization remain`

The defect, source ownership, prior-art lineage, selected correction, current-head tests, exact source branch, and internal upstream drafts are complete. The clean branch is one source-only commit directly on current public uv base and changes exactly the three synchronized launcher owners. Public upstream contact remains unauthorized. Astral's contribution policy requires a human to understand and independently review the change, then author any public communication in their own words.

## In simple words

uv's relocatable launchers call `realpath -- "$0"`. BusyBox treats `--` as a pathname and prints `realpath: --: No such file or directory`, even though the launcher then succeeds. The candidate removes the unsupported delimiters from the synchronized wheel, virtualenv, and project-run launcher strings while preserving symlink-first resolution and sibling-interpreter selection.

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
- Clean source head: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`
- Clean source relationship: one commit ahead, zero behind
- Existing public issue: [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209)
- Public upstream contact authorized: `no`

## Exact source diff

Complete compare: [`79bbface...c43b126`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c43b1262be71d9fc0b60ca613700ef7ae60bf69d)

| File | Exact reviewed link | Diff stats |
| --- | --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | [`wheel.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv-install-wheel/src/wheel.rs) | +2 / -2 |
| `crates/uv-virtualenv/src/virtualenv.rs` | [`virtualenv.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv-virtualenv/src/virtualenv.rs) | +4 / -4 |
| `crates/uv/src/commands/project/run.rs` | [`run.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv/src/commands/project/run.rs) | +1 / -1 |

Total: three files, seven additions, seven deletions. The source replacement fence remains five `realpath --` and seven `dirname --` occurrences. The extra virtualenv line movement is the rustfmt-required braced match arm. No temporary workflow, evidence, packet, publisher, or harness file appears in the source commit.

Exact source blobs:

- wheel: `1d77576b32df7f8711b29012cf380b178d87e362`
- virtualenv: `fc79fde1dd3630a3fd529ee83a3e4bf154becaa1`
- project-run: `fa3419e21dd494a4473874f8e284d83d061c331d`

## Packet contents

- [`DEEP_DIVE.md`](./DEEP_DIVE.md) — ownership, failure model, invariant, compatibility, risks, and claim limits
- [`APPROACHES.md`](./APPROACHES.md) — selected correction, viable alternatives, executed losing approaches, and prior art
- [`TESTS.md`](./TESTS.md) — exact commands, revisions, workflow/job/artifact receipts, setup failures, and platform gaps
- [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md) — existing-issue disposition and human-authored comment inputs
- [`UPSTREAM_PR.md`](./UPSTREAM_PR.md) — internal PR draft and submission checklist
- [`REVIEW.md`](./REVIEW.md) — human review guide and final remaining gate

## Final current-head execution receipt

- Execution-only base: `d2ebfd92457b0047a4b02e3ccb8431769e12b145`
- Execution-only carrier head: `9c1465a8beff5e44053756523a053dbc64abc047`
- Closed execution PR: [`teamleaderleo/uv#6`](https://github.com/teamleaderleo/uv/pull/6)
- Workflow: [`30676914631`](https://github.com/teamleaderleo/uv/actions/runs/30676914631)
- Job: `91305994591`
- Artifact: `8810846105`
- Artifact digest: `sha256:88af531d65679b1a756541d598c8c8fc85d250dd03ee32b58ede2d8a883ad45c`
- Source tree: `63c644c8bba5a5cb3376401f64bd1ce561aa674e`
- Published source commit: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`

Passed gates:

- exact two-file execution-carrier fence;
- Python and shell harness syntax checks;
- exact three-source-file candidate fence;
- exact `realpath:5,dirname:7` replacement count;
- `git diff --check`;
- `cargo fmt --all --check`;
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
- `cargo test -p uv-install-wheel test_shebang` — 1 passed;
- GNU matrix — 12 passed cases;
- Alpine 3.22 BusyBox matrix — 12 passed cases;
- result-marker checks;
- alternate-index source tree construction;
- exact three-file publication fence;
- force-push of the one-commit clean source branch.

## Prior retained evidence

- Workflow `30625826268`, job `91140735058`: 24/24 controlled GNU/BusyBox current-vs-candidate cases.
- Workflow `30650924197`, job `91223680476`: synchronized three-owner generation, exact path fence, `git diff --check`, affected-crate compilation, and GNU/BusyBox matrix.
- Prior candidate carrier head: `0aad1cc1fc9aa03fc5705da44112671101e20624`.
- Prior artifact: `8801371654`, digest `sha256:ff4221a734d356250aa38ed97d0b194635f6ef3847a24d0a652ec4b3912bbb97`.
- Public issue #8058 and merged PR #8079 define the symlink-first canonicalization preserved by the source branch.

## Negative and setup records

- The fork default branch is stale at `1da26a`; carrier-wide PR diffs against it included unrelated public history and were rejected as source evidence.
- Workflow `30674680508` generated the exact current candidate but stopped because Rust 1.97.1 lacked the `rustfmt` component. Artifact `8810498589` retained those exact files.
- Isolated workflow `30676820652` installed rustfmt and exposed a real formatting requirement in the virtualenv match arm. The generator was corrected to emit rustfmt's braced form.
- A local BusyBox rerun initially used GNU `realpath` through host PATH. The corrected PATH-appet control passed all 12 BusyBox cases; output SHA-256 `110d8138cfa35e747bd169c86da2fd138cce2161d28d03f5256a32c855c7f9a`.
- Temporary wheel object `3ddcd43820b41d6752efa1ebd3f200848aee73bc` contained one unrelated formatting drift and was rejected before clean-branch use.
- Fieldwork PR #453 and uv PR #5 were closed without merge after their useful receipts were retained.

## Remaining blockers

1. Independent human review of source head `c43b1262be71d9fc0b60ca613700ef7ae60bf69d` and this packet.
2. Human acceptance or closure of the macOS/BSD utility gap and the unmeasured bare option-like `$0` case.
3. Human-authored public issue/PR wording under Astral's AI policy.
4. Explicit authorization before any public upstream comment, issue action, or pull request.

## Continuation order

1. Read this README, `TESTS.md`, `REVIEW.md`, and the latest unit 02 handoff on #435.
2. Review the exact compare `79bbface...c43b126` and confirm the three-file fence.
3. Decide whether macOS/BSD execution or dual old/new shebang recognition is required.
4. Record human disposition on #435 and update `REVIEW.md`.
5. Only after explicit authorization, let a human rewrite and submit the public PR against `astral-sh/uv:main`.

No public upstream issue comment, reaction, assignment, branch, or pull request was created.
