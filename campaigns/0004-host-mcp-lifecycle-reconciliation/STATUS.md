# Host Capability and MCP Catalogue Lifecycle Reconciliation

## In simple words

Campaign #84 is claimed and its first owned Codex source slice is active. Codex deliberately reuses unchanged ready MCP connections during ordinary runtime reconciliation. The host-facing MCP config reload enters through a different public method, yet that method currently allows the same reuse. A stable endpoint can therefore keep its startup-captured server identity and tool catalogue after an explicit host reload.

The first candidate makes host config reload request fresh MCP connections while preserving ordinary per-turn reuse. A compiled integration regression uses the existing Apps MCP startup counter to require a second initialize attempt after `CodexThread::refresh_mcp_config`.

- Campaign issue: #84
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- Priority: P0 after #83
- State: `investigating`
- Worker: GPT-5.6 Thinking
- Fieldwork branch: `campaign/84-host-mcp-lifecycle-reconciliation`
- Owned Codex branch: `fieldwork/31-mcp-config-reload-reconnect`
- Owned draft Codex PR: `teamleaderleo/codex#5`
- Public source campaign pin: [Codex revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Owned fork base: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Upstream contact: unauthorized

## Completed

- consumed accepted L01, L04, and L06 evidence from Campaign #31;
- separated ordinary low-latency reconciliation from explicit host refresh;
- confirmed that `Op::RefreshMcpServers` already requests reconnect;
- confirmed that `CodexThread::refresh_mcp_config` currently applies config without requesting reconnect;
- confirmed that `notifications/tools/list_changed` reaches a handler that records a log entry only;
- confirmed that the RMCP client already exposes a typed `list_tools` request;
- opened the owned fork branch and draft PR;
- added a source-native reconnect candidate and focused integration regression to a temporary validation workflow;
- preserved two failed validation receipts caused by missing runner tools before test execution.

## Active work

1. Run Rust formatting, the focused reconnect regression, `codex-core`, and `codex-app-server` tests.
2. Commit the source and regression only after the validation job passes.
3. Record whether host config reload gives the new runtime a fresh client while ordinary reconciliation retains its existing reuse test.
4. Design the next independent slice for tool-list-change notification relist and publication ordering.
5. Add server identity, catalogue digest, revision, generation, and typed refresh outcomes after the first source seam is accepted.

## Current implementation boundary

This slice changes one host-facing refresh boundary. It does not alter ordinary sampling-step reconciliation, request-scoped bindings, router registration, model advertisement, fallback policy, or automatic repair.

The larger campaign still owns:

- host `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` policy;
- remote identity and catalogue digest validation;
- notification-driven relist;
- concurrent and late relist ordering;
- per-server typed refresh outcomes and catalogue revision;
- stable-endpoint stub-to-real and host resume/fork regressions.

## Validation receipts

### Attempt 1

- source patch applied in the ephemeral runner;
- repository-wide `just fmt` stopped because unrelated Python/Bazel formatter dependencies `uv` and `dotslash` were absent;
- no Rust tests ran;
- no source commit was created.

### Attempt 2

- source patch and regression applied;
- `cargo fmt --all -- --check` passed;
- focused test command stopped because `cargo-nextest` was absent;
- no test binary ran;
- no source commit was created.

### Attempt 3

- adds the expected `cargo-nextest` runner;
- preserves the same source patch and regression;
- current result pending in owned fork CI.

## Stop rule

Do not accept the reconnect candidate until the focused integration regression and scoped package tests compile and pass. Do not treat this slice as the generic catalogue refresh contract. Notification-driven relist, identity validation, catalogue revision, host reconstruction policy, and failed-refresh behavior remain separate required evidence.
