# Compiled rmcp relist-ordering validation

Date: 2026-07-30  
Official SDK pin: `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07`  
Fixture: `fieldwork-rmcp-relist-ordering`

## Command

```bash
cargo test \
  --manifest-path campaigns/0002-tool-surface-continuity/lanes/L01-lifecycle-provenance/artifacts/rmcp-relist-ordering/Cargo.toml \
  -- --nocapture
```

The workflow used only Cargo and the Rust toolchain. It did not invoke repository-wide formatters, `uv`, or `dotslash`.

## Retained result

```text
running 1 test
sdk_cache=catalogue_c naive_application=catalogue_b ticketed_application=catalogue_c requests=3
test stale_relist_result_can_roll_back_application_but_not_sdk_cache ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

The retained `latest.log` is the exact test stdout. `Cargo.lock` preserves the dependency resolution used by the run.

## Workflow evidence

- warning-free verification run: `30485576165`, job `90690277996` — success;
- evidence-retention run: `30486255948`, job `90692564165` — test and finalization succeeded;
- retained evidence commit: `b7fed328b848e5d895ae67f1038c40abad26ffe1`;
- `Cargo.lock` blob: `33f2b165a7b83ed4687385038f67946f94f8a17d`;
- `latest.log` blob: `699a0aca3071278850782f9922b7fb912b74e630`;
- temporary workflow: removed by the retained evidence commit.

## What the compiled test proves

The real SDK receive loop accepted two `notifications/tools/list_changed` events. Each callback issued a real overlapping `tools/list` request through `context.peer`.

The controlled order was:

```text
R1 captures older cache generation and waits
→ second notification invalidates again
→ R2 returns catalogue C and publishes first
→ R1 returns catalogue B late
```

Observed outcomes:

- the SDK response cache retained catalogue C;
- the late R1 result was still returned successfully to its callback;
- a naive application publisher replaced C with stale B;
- a publisher guarded by the callback notification generation retained C;
- a final `list_tools` read returned C from the SDK cache without a fourth server request.

This confirms that the SDK's private cache generation protects the SDK cache but does not provide application publication ordering.

## Candidate API implication

A generic opt-in relist helper needs to expose an accepted-current result, a public freshness ticket, or a watch stream containing only accepted catalogue snapshots. Merely calling `list_tools` in every change callback is insufficient under concurrent notifications.

## Boundaries

- In-process duplex transport only.
- Two ordinary tool-list-change callbacks; subscription-channel lag and reconnect remain untested.
- The naive and ticketed publishers are fixture-owned application state.
- This fixture tests the Rust SDK boundary, not Codex catalogue publication.

The official Rust SDK and public Codex repositories remained read-only. No upstream contact occurred.