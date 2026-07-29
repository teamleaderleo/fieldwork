# Host and MCP Lifecycle Reconciliation Validation

## In simple words

Campaign #84 now has two compiled results.

1. An owned Codex source change makes explicit host MCP config reload create a fresh ready client while ordinary reconciliation retains ready-client reuse.
2. A focused official-Rust-SDK fixture proves that the SDK cache can reject a late stale relist write while application code still receives and publishes that stale result.

Broader Codex package runs also exposed unrelated baseline failures. Those are retained separately and do not count against the focused candidate.

## Owned Codex source receipt

- Repository: `teamleaderleo/codex`
- Branch: `fieldwork/31-mcp-config-reload-reconnect`
- Draft PR: `teamleaderleo/codex#5`
- Base: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Source commit: `dbbd2bb0a9981cea8d8dfe231015349af84662a3`
- Commit message: `fix(mcp): reconnect on host config reload`
- Changed source files: 2

### Source change

`codex-rs/core/src/codex_thread.rs`

- documents host MCP config reload as an explicit freshness boundary;
- calls `reconnect_on_next_refresh()` before applying the supplied MCP config.

`codex-rs/core/tests/suite/mcp_tool_exposure.rs`

- adds `host_mcp_config_refresh_reconnects_ready_clients`;
- uses the existing Apps MCP startup counter;
- requires one additional initialize attempt after `CodexThread::refresh_mcp_config`.

## Passing owned Codex validation

### Rust formatting

```bash
cargo fmt --all
cargo fmt --all -- --check
```

Result: passed.

### Host reload reconnect

```bash
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
```

Result: passed.

This proves the candidate creates a fresh client after the public host MCP config reload entrypoint.

### Ordinary reconciliation reuse

```bash
just test -p codex-mcp reconciliation_reuses_connection_without_relisting_regular_tools
```

Result: passed.

This proves the candidate leaves the ordinary ready-client reuse contract intact.

## Owned Codex baseline limits

### Full `codex-core`

```bash
just test -p codex-core
```

The campaign regression passed. Unrelated sandbox-dependent cases later failed with sandbox helper or command sandbox aborts. Representative groups included apply-patch, approval matrix, persisted exec policy, unified exec, and workspace-root tests.

Classification: `baseline_environment_blocker`.

### App-server MCP filter

```bash
just test -p codex-app-server mcp_refresh
```

Compilation stopped in an existing test initializer because `ItemCompletedEvent` lacked the required `started_at_ms` field.

Classification: `baseline_compile_blocker`.

The candidate changes no app-server event type or initializer.

### Harness history

- Repository-wide formatting stopped because unrelated `uv` and `dotslash` tools were absent.
- A later focused test attempt stopped because `cargo-nextest` was absent.
- The successful attempt installed the expected test runner and used Rust-only formatting.

Classification for missing runner tools: `harness_unavailable`.

## Official Rust SDK compiled receipt

- Repository under test: `modelcontextprotocol/rust-sdk`
- Pin: `cb50ae7890d8a5daacae1a4ad95f395f06733c07`
- Fixture location on L01 amendment PR #74:
  `campaigns/0002-tool-surface-continuity/lanes/L01-lifecycle-provenance/artifacts/rmcp-relist-ordering/`
- Retained fixture commit: `b7fed328b848e5d895ae67f1038c40abad26ffe1`
- Warning-free verification run: `30485576165`
- Verification job: `90690277996`
- Final evidence run: `30486255948`
- Final evidence job: `90692564165`
- `Cargo.lock` blob: `33f2b165a7b83ed4687385038f67946f94f8a17d`
- `latest.log` blob: `699a0aca3071278850782f9922b7fb912b74e630`

### Command

```bash
cargo test \
  --manifest-path campaigns/0002-tool-surface-continuity/lanes/L01-lifecycle-provenance/artifacts/rmcp-relist-ordering/Cargo.toml \
  -- --nocapture
```

The run used Cargo and the Rust toolchain only.

### Controlled sequence

```text
initial catalogue A is cached
→ notification N1 invalidates and starts R1; R1 waits
→ notification N2 invalidates and starts R2
→ R2 returns catalogue C and publishes first
→ R1 returns catalogue B late
```

### Retained output

```text
running 1 test
sdk_cache=catalogue_c naive_application=catalogue_b ticketed_application=catalogue_c requests=3
test stale_relist_result_can_roll_back_application_but_not_sdk_cache ... ok

test result: ok. 1 passed; 0 failed
```

### Assertions proved

- both callbacks issued real overlapping `tools/list` requests without blocking response delivery;
- the second relist completed first;
- the SDK cache retained C;
- the older callback still received successful B;
- a naive application publisher rolled back from C to B;
- an application notification-generation ticket retained C;
- a final `list_tools` returned C from cache without a fourth server request.

### Claim supported

The SDK's private response-cache generation protects the SDK cache. It does not tell application code whether a returned relist result remains current enough to publish.

### Candidate API implication

A safe generic coordinator needs one of:

- public relist ticket plus accepted-current result;
- internal coalescing with newest-result publication;
- a stream or watch channel containing only accepted catalogue snapshots.

## Source-confirmed Codex authority boundary

Current public Codex can freeze catalogue A for model sampling and later resolve approval and execution through current binding B.

The existing integration test proves:

- inference sees process A's cached description;
- the same tool name executes on process B;
- removal in B fails closed.

Missing compiled cases:

- same name, changed input schema;
- same name, changed approval or permission policy;
- same name, changed annotations, visibility, file metadata, hook metadata, or behavior;
- permissive B arriving while an A response is in flight;
- verified-equal A/B authority fingerprint.

## Next validation gates

### Generation-bound host reconnect

Prove an older publication cannot consume a reconnect request assigned to a newer config generation.

### Captured approval

Sample under prompt-required A, apply permissive B before dispatch, and prove the call still prompts or fails. Reverse the policies and prove current B may tighten the call.

### Cached A/live B

Require one of:

- verified equal fingerprint and recorded late rebind;
- typed fail-closed mismatch;
- an explicit approved policy that records both revisions.

### Notification publication

Use the compiled SDK ordering case inside Codex. Prove only an accepted-current relist result increments the thread catalogue revision and changes future request bindings.

### Failed and partial refresh

Test old-state retention, unavailable publication, per-server partial success, cancellation, timeout, and later recovery.

### Host reconstruction

Test `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` across resume and fork.

## Current decision

Retain owned Codex PR #5 as a valid first implementation slice. Keep it draft.

Treat the compiled SDK result as confirmed dependency evidence for the next notification-relist slice. Do not equate SDK cache correctness with Codex application publication correctness.

Do not accept Campaign #84 as complete until the generation, request-authority, notification, failed-refresh, and host-reconstruction gates pass.