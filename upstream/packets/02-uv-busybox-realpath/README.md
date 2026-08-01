# Unit 02 — uv BusyBox `realpath` compatibility

## Current disposition

`READY FOR LAST-MILE LOOK`

The technical work is complete. The clean source branch is one source-only commit directly on current public uv main, changes exactly the three launcher owners, preserves recognition of launchers generated before this fix, and passed focused Linux, Alpine BusyBox, and macOS validation. The remaining work is the requested human last-mile inspection, human-owned public wording, and explicit authorization before upstream contact.

## Final decision

Relocatable launchers should omit `--` from `realpath` and `dirname` calls. BusyBox interprets `--` as a pathname and emits a misleading diagnostic. The corrected fragment stays quiet on BusyBox and preserves the tested GNU and macOS behavior.

`copy_entrypoint` should recognize both forms:

- the corrected delimiter-free relocatable shebang;
- the historical delimiter-bearing shebang already present in environments created by earlier uv releases.

This avoids turning a portability fix into an upgrade-time entrypoint migration regression.

## Exact identity

- Routing issue: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Target repository: `astral-sh/uv`
- Fork repository: `teamleaderleo/uv`
- Clean source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Public source base and current public main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Clean source tree: `fdcbe687e0afaaf499e5098b3308525e03000526`
- Relationship: one commit ahead, zero behind
- Existing public issue: [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209)
- Public upstream contact authorized: `no`

## Exact source diff

Complete compare: [`79bbface...c42973e`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c42973ef0490c75df1c7e7f4e9a54d46c6bca059)

| File | Exact source | Diff stats | Role |
| --- | --- | ---: | --- |
| `crates/uv-install-wheel/src/wheel.rs` | [`wheel.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv-install-wheel/src/wheel.rs) | +2 / -2 | Generate corrected relocatable wheel shebang and update its exact assertion |
| `crates/uv-virtualenv/src/virtualenv.rs` | [`virtualenv.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv-virtualenv/src/virtualenv.rs) | +4 / -4 | Generate corrected POSIX and fish relocatable activation paths |
| `crates/uv/src/commands/project/run.rs` | [`run.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv/src/commands/project/run.rs) | +59 / -7 | Recognize corrected and historical shebangs and test both forms |

Total: three files, 65 additions, 13 deletions. The larger `run.rs` hunk is the compatibility constant pair plus one direct regression test. No workflow, carrier, packet, publisher, or harness file appears in the clean source commit.

Exact source blobs:

- wheel: `1d77576b32df7f8711b29012cf380b178d87e362`
- virtualenv: `fc79fde1dd3630a3fd529ee83a3e4bf154becaa1`
- project-run: `7a6d980ed06a46a40cbd41e3f35fe73eac8ecd05`

## Final last-mile execution receipt

- Execution-only base: `d2ebfd92457b0047a4b02e3ccb8431769e12b145`
- Execution carrier head: `6fbdf4d7fb0ff577f5be24972b1a5bba73111793`
- Closed execution PR: [`teamleaderleo/uv#7`](https://github.com/teamleaderleo/uv/pull/7)
- Workflow: [`30690034279`](https://github.com/teamleaderleo/uv/actions/runs/30690034279)
- Linux/source job: `91342987834` — success
- macOS job: `91342987814` — success
- publication job: `91343684491` — success

Artifacts:

- Linux/source: `8815417615`, digest `sha256:6a2f205d91e2a70021cc16c8d6b4a30ee2f983a90344a88f5e9d9206d1d9dd8d`
- macOS: `8815330073`, digest `sha256:9f9a50fe67a2df015a17f79303f340512a35da28a0841e9ba6e9377ff0dc8b8c`
- publication: `8815424130`, digest `sha256:f33ce4b084c7a37dcb7cc6bacc4b2f00f8e82200294afda491d77cac2327f3d8`

Passed gates:

- exact carrier ancestry and five-file execution-only fence;
- Python and POSIX shell harness syntax checks;
- exact three-source-file candidate and publication fences;
- replacement count: five generated `realpath --` and seven generated `dirname --` calls removed;
- one historical `realpath --` and `dirname --` form deliberately retained in the legacy recognizer;
- `git diff --check`;
- `cargo fmt --all --check`;
- `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`;
- `cargo test -p uv-install-wheel test_shebang`;
- `cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs`;
- GNU matrix: 12/12;
- Alpine 3.22 BusyBox matrix: 12/12;
- macOS 15 matrix: 12/12;
- direct shebang `$0` probes on Linux and macOS;
- alternate-index source-only commit construction and publication.

## Decisions closed during the deeper pass

### Historical generated shebangs

Decision: accept both historical and corrected forms in `copy_entrypoint`.

Evidence: the new target-native test feeds both exact strings through `copy_entrypoint`, verifies the rewritten interpreter, script body, and executable mode, and passes at the final carrier head.

### Option-like `$0`

A synthetic shell command with bare `$0=-tool` makes delimiter-free GNU `realpath` parse an option. Direct shebang execution behaves differently: Linux and macOS both replace forced process argv0 values `-tool`, `--help`, and `plain-name` with the actual script path in shell `$0`. The supported launcher entry path therefore supplies a pathname, including the tested `./-tool` invocation.

Decision: no shell normalization branch is needed.

### macOS

The corrected launcher passed absolute, relative, PATH, spaces, `./-tool`, and external-symlink cases on macOS 15. An initial harness comparison saw `/var` versus canonical `/private/var`; canonicalizing the expected interpreter path fixed the assertion. Product behavior was successful in that first run and the corrected harness passed completely.

Decision: the macOS gap is closed for the tested launcher contract.

## Retained negative and setup records

- Fork `main` is stale at `1da26a`; carrier-wide diffs against it are excluded from source evidence.
- Workflow `30674680508` retained exact source files after discovering a missing `rustfmt` runner component.
- Workflow `30676820652` exposed rustfmt's required braced virtualenv arm.
- Temporary wheel reconstruction `3ddcd43820b41d6752efa1ebd3f200848aee73bc` carried unrelated formatting drift and was rejected before clean-branch use.
- The first last-mile generator draft had a Python quoting error and was corrected before source execution.
- An inherited superseded publisher fired on PR #7; its exact fence failed, then it was disabled before the final run.
- The first macOS assertion compared lexical and canonical temp paths; the harness was corrected.
- The first final Linux attempt formatted before installing rustfmt; runner order was corrected.
- Execution PRs #5, #6, and #7 and Fieldwork PR #453 were closed without merge after durable receipts were retained.

## Last-mile human look

Review source head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059` and focus on:

1. whether retaining both shebang forms in `copy_entrypoint` is the desired migration policy;
2. whether the direct unit test belongs in `run.rs` or should move to an integration test;
3. whether the focused compile/test/platform coverage is sufficient for submission;
4. wording and scope of the human-authored upstream PR.

Technical blockers: none identified.

Public-action gates:

- a human independently reads and understands the exact diff;
- a human authors the public title/body in their own words under Astral's contribution policy;
- explicit authorization is recorded before any public comment or pull request.

## Continuation order

1. Read this README, [`TESTS.md`](./TESTS.md), and [`REVIEW.md`](./REVIEW.md).
2. Review the exact compare `79bbface...c42973e`.
3. Record one human disposition on #435: approved for upstream preparation, or a specific requested change.
4. After approval, update `REVIEW.md` and human-rewrite [`UPSTREAM_PR.md`](./UPSTREAM_PR.md).
5. Contact public upstream only after explicit authorization.

No public upstream issue comment, reaction, assignment, branch, or pull request was created.
