# Tests and execution receipts

## Current status

`PASS / ISSUE-FIRST EVIDENCE COMPLETE`

## Exact source

- base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- source: `b2a704c708748462d7893fe82cf8971f00ca751e`
- source PR: `teamleaderleo/codex#144`
- one commit, exact four-file fence

## Authoritative paired execution

Carrier: `teamleaderleo/codex#137`  
Corrected run: `30699322569`

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

The earlier run `30698706605` used the wrong broad integration gate and produced the same 159 failures on baseline and source. It is retained only as runner/gate-selection evidence and is superseded by the corrected paired run.

## Behaviors proved

The focused controls cover:

- completed output emitted before the streaming subscriber attaches;
- partial subscriber transcript replacement with producer-owned output;
- local stdout retained despite a lagged live receiver;
- invalid UTF-8 retained despite broadcast lag;
- exec-server producer retention;
- bounded head/tail output behavior;
- live delta cap and UTF-8 boundary behavior;
- normal output-close/drain ordering;
- current synchronous completion fallback behavior.

The exact run’s source-defined count is `12/12`; older packet references to nine controls are superseded.

## Current public drift check

At public head `7325f348a2ff9e1a7dd931ed9ad65f365d064146`, all four base files retain the same blobs as `ee0247f...`. No intervening public commit changed the source fence.

This is a drift comparison, not a new execution receipt. An eventual authorized source must still be rebuilt as a direct child of the then-current public head and rerun.

## Final authorized gate

```bash
cd codex-rs
cargo fmt --all -- --check
# Resolve each focused selector from --list and require one exact match.
cargo test -p codex-core --lib --locked
# Compile the relevant integration targets using current repository commands.
git diff --check
```

The final carrier must verify exact parent and the exact four-file source fence and retain full logs.

## Evidence classification

- Run `30699322569`: authoritative source-vs-baseline execution.
- Run `30587866332`: valid historical full pass on an older exact source.
- Run `30651607704`: focused pass followed by an unclassified broader failure; superseded.
- Setup, shallow-history, missing-tool, and source-guard failures: retained only as carrier diagnostics.

No public upstream interaction occurred.