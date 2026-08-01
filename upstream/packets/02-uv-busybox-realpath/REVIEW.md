# Review — Unit 02: uv BusyBox `realpath` compatibility

## Current disposition

`READY FOR LAST-MILE LOOK`

The source and focused technical validation are complete. This file is the human inspection checklist, not a request for more exploratory work.

## Review subject

- Target repository: `astral-sh/uv`
- Public source base/current main: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Canonical source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Exact source head: `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`
- Exact source tree: `fdcbe687e0afaaf499e5098b3308525e03000526`
- Complete compare: [`79bbface...c42973e`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c42973ef0490c75df1c7e7f4e9a54d46c6bca059)
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Public upstream authority: none

## Reading order

1. [`README.md`](./README.md)
2. exact source compare above
3. [`TESTS.md`](./TESTS.md)
4. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
5. [`APPROACHES.md`](./APPROACHES.md)
6. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact source links

| Area | Exact link | Review focus |
| --- | --- | --- |
| Wheel generator/assertion | [`wheel.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv-install-wheel/src/wheel.rs) | Delimiter removal and exact generated text |
| Virtualenv activation | [`virtualenv.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv-virtualenv/src/virtualenv.rs) | POSIX/fish forms and rustfmt-required braced arm |
| Project-run recognizer/test | [`run.rs@c42973e`](https://github.com/teamleaderleo/uv/blob/c42973ef0490c75df1c7e7f4e9a54d46c6bca059/crates/uv/src/commands/project/run.rs) | Dual historical/current recognition and direct unit test |

## Decisions already made

### Remove utility delimiters from generated launchers

Approved technical direction. BusyBox baseline emits the diagnostic; corrected GNU, BusyBox, and macOS cases pass.

### Preserve historical shebang recognition

Selected direction. Existing environments may contain delimiter-bearing launchers generated before this change. `copy_entrypoint` now accepts historical and corrected forms. A direct test covers both exact strings, interpreter replacement, body retention, and mode retention.

Human question: does upstream want this migration compatibility in the same patch? The packet recommends yes.

### Option-like `$0`

Closed for the actual launcher entry path. Linux and macOS direct shebang probes requested argv0 `-tool` and `--help`; shell `$0` became the script path. Synthetic shell injection remains outside the supported direct entry behavior.

### macOS

Closed for the tested contract. Corrected launcher passed all six invocation forms on macOS 15.

## Source cleanliness

- [x] Exact source head recorded.
- [x] One commit directly on current public main.
- [x] One commit ahead, zero behind.
- [x] Exactly three source files changed.
- [x] No execution workflow or harness in source diff.
- [x] No packet or receipt file in source diff.
- [x] No unrelated generated churn.
- [x] Exact source links resolve to `c42973e`.
- [ ] Human has read every changed line.

## Test checklist

- [x] `git diff --check`
- [x] `cargo fmt --all --check`
- [x] `cargo check -p uv-install-wheel -p uv-virtualenv -p uv`
- [x] `cargo test -p uv-install-wheel test_shebang`
- [x] `cargo test -p uv copy_entrypoint_accepts_current_and_legacy_relocatable_shebangs`
- [x] GNU matrix 12/12
- [x] Alpine 3.22 BusyBox matrix 12/12
- [x] macOS 15 matrix 12/12
- [x] Linux direct-shebang `$0` probe
- [x] macOS direct-shebang `$0` probe
- [x] exact three-file publication fence
- [ ] Human decides whether full clippy or complete suite is desirable before submission

## Final receipt

- Execution carrier: `6fbdf4d7fb0ff577f5be24972b1a5bba73111793`
- Closed PR: [`teamleaderleo/uv#7`](https://github.com/teamleaderleo/uv/pull/7)
- Workflow: [`30690034279`](https://github.com/teamleaderleo/uv/actions/runs/30690034279)
- Linux/source job: `91342987834`
- macOS job: `91342987814`
- publication job: `91343684491`
- Linux artifact: `8815417615`
- macOS artifact: `8815330073`
- publication artifact: `8815424130`

## Human judgment prompts

1. **Migration policy:** Keep both exact relocatable shebang forms in `copy_entrypoint`?
2. **Test placement:** Is the private-function unit test in `run.rs` appropriate, or would upstream prefer a project-run integration test?
3. **Scope:** Is three files the right contribution boundary, or should constant sharing wait for a follow-up?
4. **Submission gates:** Request full clippy or complete suite, or accept the focused gates?
5. **Public wording:** Rewrite the issue/PR text in the human author's own voice.

## Suggested disposition

Approve:

`Unit 02 source c42973e is approved for human upstream preparation.`

Request a change:

`Unit 02 concern: <specific line, compatibility decision, test request, or wording issue>.`

## Public-action gate

Source readiness and public authorization are separate. Even after source approval:

- a human must independently understand the code;
- a human must author the public communication in their own words;
- explicit permission must exist before any public upstream action.
