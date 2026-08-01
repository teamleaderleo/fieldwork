# Tests and receipts — Unit 02: BusyBox-safe relocatable launchers

## Current judgment

`HOLD — source and focused tests complete; human review remains`

The clean source candidate passed the current-head formatting, affected-crate compile, native shebang test, GNU behavior matrix, Alpine BusyBox behavior matrix, exact changed-path fence, exact replacement-count fence, and source-only publication gate. Remaining limits are human review, macOS/BSD execution or acceptance, bare option-like `$0`, and public authorization.

## Identity

- Original executed base: `1da26a68629be6ae5fd7f924a7d49ff54763a7df`
- Current public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source head: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`
- Clean source tree: `63c644c8bba5a5cb3376401f64bd1ce561aa674e`
- Final execution base: `d2ebfd92457b0047a4b02e3ccb8431769e12b145`
- Final execution carrier head: `9c1465a8beff5e44053756523a053dbc64abc047`
- Final execution PR: [`teamleaderleo/uv#6`](https://github.com/teamleaderleo/uv/pull/6), closed without merge
- Test dates: 2026-07-31 and 2026-08-01
- Environments: GitHub-hosted Ubuntu 24.04; `alpine:3.22` with BusyBox 1.37.0

## Final current-head receipt

- Workflow: [`30676914631`](https://github.com/teamleaderleo/uv/actions/runs/30676914631)
- Job: `91305994591`
- Conclusion: success
- Artifact: `8810846105`
- Artifact digest: `sha256:88af531d65679b1a756541d598c8c8fc85d250dd03ee32b58ede2d8a883ad45c`
- Published source commit: [`c43b126`](https://github.com/teamleaderleo/uv/commit/c43b1262be71d9fc0b60ca613700ef7ae60bf69d)
- Complete compare: [`79bbface...c43b126`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c43b1262be71d9fc0b60ca613700ef7ae60bf69d)

### Passed steps

1. Exact two-file execution-carrier fence against base `d2ebfd9`.
2. Python patch-generator syntax check.
3. POSIX shell matrix syntax check.
4. Exact current-source candidate generation.
5. Exact replacement counts: five `realpath --`, seven `dirname --`.
6. `git diff --check`.
7. Exact three-source-file fence.
8. `rustup component add rustfmt`.
9. `cargo fmt --all --check`.
10. `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`.
11. `cargo test -p uv-install-wheel test_shebang` — one selected test passed.
12. GNU current/candidate matrix — 12 passed cases.
13. Alpine 3.22 BusyBox current/candidate matrix — 12 passed cases.
14. Result-marker verification.
15. Alternate-index source-tree construction from parent `79bbface`.
16. Exact three-file publication fence.
17. Force-push of one source-only commit to `upstream/02-busybox-realpath`.
18. Artifact retention.

### Exact source diff fence

| File | Additions | Deletions | Blob |
| --- | ---: | ---: | --- |
| `crates/uv-install-wheel/src/wheel.rs` | 2 | 2 | `1d77576b32df7f8711b29012cf380b178d87e362` |
| `crates/uv-virtualenv/src/virtualenv.rs` | 4 | 4 | `fc79fde1dd3630a3fd529ee83a3e4bf154becaa1` |
| `crates/uv/src/commands/project/run.rs` | 1 | 1 | `fa3419e21dd494a4473874f8e284d83d061c331d` |

Total: three files, seven additions, seven deletions, one commit ahead, zero behind. The virtualenv 4/4 hunk includes rustfmt's required braced match arm.

## Behavior matrix

Each platform executes current and candidate launchers for:

- absolute path;
- relative path;
- PATH lookup;
- a filename containing spaces;
- `./-tool`;
- external symlink.

Assertions:

- status 0;
- the resolved executable is the sibling fake `python`;
- argument `probe` arrives;
- GNU stderr is empty for current and candidate;
- BusyBox current stderr contains `realpath: --`;
- BusyBox candidate stderr is empty.

Final result: GNU 12/12 and Alpine BusyBox 12/12.

## Prior retained receipts

### Original behavior discriminator

- Carrier head: `f8adfc6a573e3b8c44713e132ba9b7a2a3dbd502`
- Workflow/job: `30625826268` / `91140735058`
- Result: 24/24 passed.
- Established: current BusyBox diagnostic, quiet candidate, preserved GNU behavior, sibling interpreter, argument delivery, spaces, `./-tool`, relative/PATH invocation, external symlink.

### Original synchronized source candidate

- Carrier head: `0aad1cc1fc9aa03fc5705da44112671101e20624`
- Workflow/job: `30650924197` / `91223680476`
- Result: passed exact three-file generation, `git diff --check`, affected-crate compile, and both matrices.
- Artifact: `8801371654`
- Digest: `sha256:ff4221a734d356250aa38ed97d0b194635f6ef3847a24d0a652ec4b3912bbb97`

### First current-head artifact

- Carrier head: `1e1a66d96b4ef827ef470848cd19c504a6bdd739`
- Workflow/job: `30674680508` / `91299352922`
- Passed candidate generation, path fence, replacement fence, and `git diff --check`.
- Setup failure: Rust 1.97.1 lacked the `rustfmt` component.
- Artifact: `8810498589`
- Digest: `sha256:78fb757cc283506262b7d39e4cdafa5760b0656ba9560aa42886a11a68fa8272`

### Formatting discriminator

- Carrier head: `76cdc876678e6bb517f543f1021aaeb87e6d0f4a`
- Workflow/job: `30676820652` / `91305721883`
- Generation and rustfmt installation passed.
- `cargo fmt --all --check` exposed a source formatting requirement in the virtualenv match arm.
- Repair: emit rustfmt's braced `Cow::Borrowed` arm in the exact generator.
- Product consequence: final source hunk is +4/-4 in virtualenv while preserving the same 2/4 delimiter replacement count.

## Local current-head artifact control

The exact first current-head artifact was rerun locally:

- GNU matrix: passed 12/12.
- First BusyBox command used GNU `realpath` through host PATH; output was empty and classified as a harness-path mismatch.
- Corrected control prepended BusyBox applet symlinks for `realpath` and `dirname`; passed 12/12.
- Corrected BusyBox output SHA-256: `110d8138cfa35e747bd169c86da2fd138cce2161d28d03f5256a32c855c7f9a`.
- Matrix script SHA-256: `a1e79b9d831a1f9f8f907d2dcb23aaea08edb629d1a17ca732eb2ed15b082a39`.

The final GitHub-hosted Alpine matrix is the authoritative current-head BusyBox receipt.

## Setup and losing-path record

| Attempt | Observation | Classification | Disposition |
| --- | --- | --- | --- |
| broad CI `30625826344` | generated documentation/OpenAPI gate failed outside unit files | unrelated repository gate | no whole-repository green claim |
| PR #5 against stale fork `main` | carrier comparison included 244 unrelated public-history files | carrier setup | replaced by exact fences and isolated base |
| first PR #5 trigger | custom workflow appeared only after close/reopen | trigger behavior | recorded; later path replaced |
| workflow `30674680508` | missing `rustfmt` component | runner setup | installed component in isolated run |
| workflow `30676820652` | rustfmt required a braced virtualenv arm | source formatting | generator corrected; final run passed |
| temporary commit `3ddcd43820b41d6752efa1ebd3f200848aee73bc` | wheel reconstruction carried one unrelated formatting hunk | exactness failure | rejected before clean-branch use |
| Fieldwork PR #453 | duplicate carrier remained queued | redundant path | closed without merge |
| uv PR #5 | ordinary CI competed with the focused job | carrier noise | closed; replaced by isolated base/PR #6 |

## Ordinary gate status

| Gate | Result |
| --- | --- |
| `cargo fmt --all --check` | passed at final carrier head |
| `cargo check -p uv-install-wheel -p uv-virtualenv -p uv` | passed at final carrier head |
| `cargo test -p uv-install-wheel test_shebang` | passed, 1 selected test |
| GNU matrix | passed, 12/12 |
| Alpine BusyBox matrix | passed, 12/12 |
| full project clippy | not run |
| complete project suite | not run on source-only branch |
| macOS/BSD utilities | not run |

## Cleanup receipt

- Clean source commit constructed from public base through an alternate Git index.
- Only the three declared source paths entered the source tree.
- Temporary workflows, execution scripts, packet files, and receipts are absent from source head `c43b126`.
- Execution PR #6 is closed without merge.
- Execution PR #5 and Fieldwork PR #453 are closed without merge.
- Prior PRs #2 and #3 remain durable evidence carriers.

## Remaining evidence gaps

- native macOS utility execution;
- FreeBSD or another BSD-family execution;
- a supported invocation yielding a bare option-like `$0`;
- explicit compatibility decision for recognizing persisted old launcher text;
- complete project suite on the clean source branch;
- independent human code review.

## Reversing conditions

Reopen the source conclusion if:

- macOS/BSD rejects the delimiter-free fragment;
- a supported bare option-like `$0` is demonstrated and fails;
- current upstream replaces the three owners or lands an equivalent correction;
- maintainers require project-run to recognize both old and new shebang forms;
- human review finds an ownership or compatibility error.
