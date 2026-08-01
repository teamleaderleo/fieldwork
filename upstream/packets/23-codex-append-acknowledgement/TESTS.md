# Tests and receipts

## Required current gate

Run against exact clean-source base `670f69416bf91c5dfd8b58669e78050b584ff053`:

```sh
cd codex-rs
cargo fmt --all -- --check
cargo test -p codex-core --lib --locked -- --list
cargo test -p codex-core --lib --locked '<full exact test name>' -- --exact --nocapture
cargo test -p codex-thread-store --locked
```

Declared exact controls:

1. `append_outcome_ephemeral_history_is_authoritative`
2. `append_outcome_reports_successful_live_append`
3. `append_outcome_reports_prewrite_failure`
4. `append_outcome_reports_commit_then_error_as_failure`

The carrier requires exactly one enumerated full-name match for each suffix and runs all four with `--exact`.

## Historical receipts

### Source #51

- source: `30a0a9b50da5fd2f7d58ee81315e0311e84e221e`
- parent: `b545c94041017d000e2c8b2f6272705d21b85dfb`
- run: `30550323542`
- result: four exact append controls passed
- result: `codex-thread-store` 158 passed, 0 failed
- formatting and three-file fence passed
- review: `4820933076`

Evidence class: exact prior public pin; retired source.

### Carrier #52 failed transformation

- carrier: `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`
- failed run: `30560746088`
- job: `90932794178`
- failure: expected source anchor absent during transformation
- formatting: never executed
- exact controls: 0
- thread-store package: never executed
- source publication: none

Evidence class: transformation failure receipt only.

### Carrier #52 later exact-pin execution

- carrier: `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`
- reviewed source: `30a0a9b50da5fd2f7d58ee81315e0311e84e221e`
- execution base: `97576b1794872e342450ebd577123e052ab57626`
- run: `30582576317`
- review: `4823321811`

Evidence class: exact-pin prior execution; retired by later current-pin sources.

### Source #84 through carrier #80

- source: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`
- parent: `a01a2d91461a57809e944de7758477b92617ab01`
- carrier: `401c2e5e6a37730aae3e8da95591cc6f56655cfc`
- run: `30583967538`
- job: `91010830120`
- source commit and exact three-file fence: passed
- carrier fence: passed
- `cargo fmt --all -- --check`: passed
- four unique exact controls: passed, `4/4`
- complete `codex-thread-store` package: passed
- clean source publication: passed
- independent review: `4823945751`

Evidence class: authoritative selected predecessor for Fieldwork #435 unit 23.

### Source #97 through carrier #98

- source: `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`
- parent: `4642370542739d5dd080b0c87a9de06a6435d3db`
- carrier: `8161e9ee3423d78768263e8838bd6e4800178902`
- run: `30598744048`
- exact parent and three-file source fence: passed
- formatting: passed
- four unique exact controls: passed, `4/4`
- complete `codex-thread-store` package: passed
- Fieldwork receipt: PR #326

Evidence class: latest fully validated predecessor before current public drift.

## Current execution

- carrier PR: `teamleaderleo/codex#132`
- carrier head: `4bd35b35dee5649c6ba5af4c3535af2081c58bfc`
- public source base: `670f69416bf91c5dfd8b58669e78050b584ff053`
- run: `30674601315`
- status at packet creation: queued
- clean target branch: `fix/session-durable-append-acknowledgement`

After the current source publishes, ordinary owned-fork source CI must run from a source-only PR against an owned base mirror of `670f6941...`. Carrier-only ordinary checks do not substitute for source checks.

## Claims withheld until current run completes

- current clean source head;
- current exact four-control result;
- current complete thread-store result;
- current ordinary source-PR gates;
- current complete-diff acceptance.
