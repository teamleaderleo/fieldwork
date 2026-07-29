# Host and MCP Lifecycle Reconciliation Validation

## In simple words

Campaign #84 now has three compiled results.

1. An owned Codex source change makes explicit host MCP config reload create a fresh ready client while ordinary reconciliation retains ready-client reuse.
2. A focused official-Rust-SDK fixture proves that the SDK cache can reject a late stale relist write while application code still receives and publishes that stale result.
3. A focused public-Codex fixture proves that inference can receive cached schema A while call dispatch later invokes same-name live tool B with a changed schema. B rejects the A-shaped arguments, and Codex returns B's error without first producing a typed A/B revision-mismatch decision.

Broader Codex package runs exposed unrelated baseline failures. Those are retained separately and do not count against the focused candidates.

## Owned Codex host-refresh receipt

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

### Passing validation

```bash
cargo fmt --all
cargo fmt --all -- --check
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
just test -p codex-mcp reconciliation_reuses_connection_without_relisting_regular_tools
```

Results:

- Rust formatting passed;
- explicit host reload created a fresh client;
- ordinary ready-client reconciliation continued reusing the existing connection without relisting.

### Baseline limits

Full `codex-core` later encountered unrelated sandbox-dependent failures in apply-patch, approval, exec-policy, unified-exec, and workspace-root cases.

Classification: `baseline_environment_blocker`.

The app-server MCP filter stopped at an existing test initializer missing `ItemCompletedEvent.started_at_ms`.

Classification: `baseline_compile_blocker`.

Harness history:

- repository-wide formatting initially stopped because unrelated `uv` and `dotslash` tools were absent;
- a focused test attempt stopped because `cargo-nextest` was absent;
- the successful attempt installed the expected runner and used Rust-only formatting.

Classification for missing runner tools: `harness_unavailable`.

## Official Rust SDK relist receipt

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

A safe generic coordinator needs one of:

- public relist ticket plus accepted-current result;
- internal coalescing with newest-result publication;
- a stream or watch channel containing only accepted catalogue snapshots.

## Public Codex cached-schema receipt

- Public repository under test: `openai/codex`
- Exact pin: `a5082373f18119dc5d3eb993267c97f37880935d`
- Fieldwork branch: `campaign/84-host-mcp-lifecycle-reconciliation`
- Workflow run: `30488803287`
- Workflow job: `90701186402`
- Evidence artifact: `8739076993`
- Artifact digest: `sha256:f759a6b2e0a75bd8b2e2cfb8ef23c42a9d5e4e259473ae121a3b7614089e3148`
- Retained path: `campaigns/0004-host-mcp-lifecycle-reconciliation/artifacts/codex-cached-schema-drift/`

### Harness

The workflow:

1. checked out public Codex with credentials disabled;
2. installed `just` and `cargo-nextest` before test execution;
3. applied the two-file patch only in the ephemeral checkout;
4. passed `cargo fmt --all -- --check` and `git diff --check`;
5. explicitly built `codex-rmcp-client --bin test_stdio_server`;
6. ran one focused `codex-core` integration test;
7. uploaded the exact patch and test log.

The completed temporary workflow was removed after evidence retention.

### Controlled transition

```text
catalogue A exposes echo(message: string)
→ A is cached and advertised before replacement startup completes
→ the model emits {"message":"hello"}
→ catalogue B exposes echo(count: integer)
→ current call dispatch resolves through B
```

### Assertions proved

- the inference request contained A's required `message` field;
- A's advertised schema contained no `count` field;
- after startup, the same tool call reached B;
- B rejected the A-shaped arguments with `echo schema v2 requires integer count`;
- Codex returned that B-side error in the model-visible function-call output;
- Codex did not surface a typed A/B catalogue-revision mismatch before invoking B;
- the unrelated tool continued while MCP startup was pending;
- a tool absent from B remained unavailable, preserving the existing removed-tool negative control.

### Retained output

```text
running 1 test
test suite::mcp_tool_cache::regular_mcp_definition_cache_preserves_live_session_state ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 1062 filtered out; finished in 0.51s
```

The test passed because it asserts the current mixed-revision behavior. This is a successful reproduction, not a passing repair.

### Classification

`advertisement_execution_revision_mismatch`

The observed B-side argument rejection is fail-closed for this test server. It is not a general guarantee. A B implementation may accept the old field, ignore it, reinterpret it, or perform changed behavior.

### Required correction

For a cached tool with no captured prepared call:

- retain A's authority fingerprint;
- wait for B only as the bounded cached-startup exception;
- compare A and B before file rewrite, approval, or execution;
- execute B only when equality is verified;
- otherwise return a typed revision-mismatch result and require a new sampling step.

## Adjacent ownership evidence

### Campaign #83

Campaign #83 accepted one bounded session-scoped receipt owner in owned Codex. It now separates:

- operation effect;
- terminal execution outcome;
- authoritative result persistence;
- client delivery;
- display.

#84 should consume that owner for call lifecycle evidence. It should not create a second terminal or persistence receipt system inside MCP publication code.

### Scout #130/#131

The adjacent `rmcp 3.0.0` timeout probe produced:

```text
external_timeout:
  cancellation_observed=false
  side_effect_completed=true

native_request_timeout:
  cancellation_observed=true
  side_effect_completed=false
```

The external timeout matches Codex's current ownership pattern: a local outer timeout can end the wait without sending MCP cancellation. A timed-out server call can therefore remain active during host refresh, reconnect, catalogue publication, or shutdown.

This scout owns timeout and cancellation mechanism analysis. Campaign #84 owns how a still-live timed-out call is represented relative to captured authority and a newer published binding.

## Next validation gates

### Generation-bound host reconnect

Prove an older publication cannot consume a reconnect request assigned to a newer config generation.

### Captured approval

Sample under prompt-required A, apply permissive B before dispatch, and prove the call still prompts or fails. Reverse the policies and prove current B may tighten the call.

### Cached A/live B authority matrix

The changed-input-schema case is now compiled. Remaining cases include:

- verified equal fingerprint and recorded late rebind;
- changed approval or permission policy;
- changed annotations, visibility, file metadata, hook metadata, provenance, or behavior;
- output-schema policy;
- typed mismatch before execution.

### Notification publication

Use the compiled SDK ordering case inside Codex. Prove only an accepted-current relist result increments the thread catalogue revision and changes future request bindings.

### Timed-out live call

Start an MCP operation, let the local outer timeout fire without server cancellation, publish a newer runtime, then prove:

- the original operation retains its original identity and authority;
- no late result is attributed to the newer binding;
- terminal and persistence receipts remain distinct;
- retry or fallback remains blocked while the original mutation state is ambiguous.

### Failed and partial refresh

Test old-state retention, unavailable publication, per-server partial success, cancellation, timeout, and later recovery.

### Host reconstruction

Test `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` across resume and fork.

## Current decision

Retain owned Codex PR #5 as a valid first implementation slice. Keep it draft.

Treat the SDK relist ordering and public-Codex schema split as confirmed evidence for the next publication and request-authority slices.

Do not accept Campaign #84 as complete until generation ownership, request authority, notification publication, timed-out live-call treatment, failed-refresh policy, and host reconstruction pass compiled tests.
