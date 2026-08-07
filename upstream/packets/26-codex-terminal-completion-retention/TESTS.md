# Tests and execution receipts

## Current status

`ISSUE-FIRST EVIDENCE COMPLETE / CURRENT PROOF NEEDS FRESH PAIRED RECEIPT BEFORE PUBLIC PR`

Upstream issue: `openai/codex#37207`  
Owned proof: `teamleaderleo/codex#144`

## Current proof source

- base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- current source: `d4ff73f50e30e96b6db4a08205c9d3600e15488e`
- source PR: `teamleaderleo/codex#144`
- four Rust files

The current source uses one shared `OutputState` mutex for the polling and completion `HeadTailBuffer` views.

## Earlier authoritative paired execution

Carrier: `teamleaderleo/codex#137`  
Corrected run: `30699322569`  
Source under test: `b2a704c708748462d7893fe82cf8971f00ca751e`

Baseline job `91367377859`:

- exact checkout and fence guard: passed;
- `codex-core` library: `2,129 passed; 0 failed`;
- integration targets: compiled.

Source job `91367377889`:

- exact checkout, direct parent, and four-file fence: passed;
- formatting: passed;
- exact terminal-retention controls: `12/12` passed;
- `codex-core` library: `2,133 passed; 0 failed`;
- integration targets: compiled.

Artifacts:

- baseline artifact `8818360397`, digest `sha256:e7c45061d1db81f8ec05fd25043a4b2d01b3804a5b713656cb691b6e800bbb0b`;
- source artifact `8818363591`, digest `sha256:558e5b55af81200f53e3edca65cc80bf49fdf695d6273d7e50e750a15c689de8`.

This run validates the behavior and the earlier two-mutex implementation. It is not an exact-head receipt for the current single-mutex source.

## Current-head CI

Current source head `d4ff73f50e30e96b6db4a08205c9d3600e15488e`:

- `v8-canary` run `31072774070`: passed;
- `blocking-ci` run `31072774224`: failed;
- formatting: passed;
- Rust benchmark smoke: passed;
- cargo-shear: passed;
- blob-size policy: passed;
- cargo-deny: passed;
- codespell: passed.

The first deterministic blocking failure occurs in repository manifest validation before product tests:

```text
codex-rs/code-mode/Cargo.toml:
  - remove the stale [features] exception from MANIFEST_FEATURE_EXCEPTIONS
```

That file and checker are outside the four-file terminal-retention source fence. The later SDK/Bazel/platform failures and cancellations are retained as broad owned-fork CI signals, not classified as terminal-retention failures without a paired current-baseline run.

## Behaviors covered by the proof tests

- completed output emitted before the streaming subscriber attaches;
- partial subscriber transcript replacement with retained completion output;
- local stdout retained despite a lagged live receiver;
- invalid UTF-8 retained despite broadcast lag;
- exec-server producer retention;
- bounded head/tail output behavior;
- live delta cap and UTF-8 boundary behavior;
- normal output-close/drain ordering;
- synchronous completion fallback behavior.

## Historical `Lagged` coverage upstream

Merged `openai/codex#4992` added explicit `Lagged(_) => continue` handling and an integration test proving unified exec continues streaming later output after the receiver falls behind.

That historical test validates the resilience behavior we want to preserve. The current issue asks that the skipped live messages stop controlling the completed transcript.

## Latest public drift check

Latest public head checked: `b3278e96cb6df4b77b8dd93cf6c65d74990a033d`.

Upstream now differs in `async_watcher.rs` and `process.rs`, primarily through merged `openai/codex#37083` output-state consolidation. The two proof test files remain byte-identical to the implementation base.

The bug remains present on that public head: the completion watcher and local collector still continue after `Lagged` and cannot recover the missed chunks.

## Required gate before a public PR

A later authorized PR should first be restacked semantically onto current public main, then run a paired baseline/source gate on that exact parent.

The focused set should include the existing retention controls plus:

- sustained simultaneous stdout/stderr with concurrent polling;
- output around the cancellation/trailing-output grace boundary.

Then run current repository formatting, the complete relevant core library gate, integration-target compilation, and exact source-fence checks.

## Evidence classification

- Run `30699322569`: authoritative paired execution for the earlier two-mutex source.
- Runs `31072774070` / `31072774224`: current single-mutex CI signals; not a paired behavior receipt.
- Run `30587866332`: valid historical full pass on an older exact source.
- Run `30651607704`: focused pass followed by an unclassified broader failure; superseded.
- Setup, shallow-history, missing-tool, and source-guard failures: carrier diagnostics only.

The upstream issue is already filed. No follow-up public interaction is authorized without another owner decision.