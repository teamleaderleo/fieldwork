# MCP Host-Reload Reconnect Validation

## In simple words

The first owned Codex source slice compiled and passed its two decisive MCP contracts:

- a host MCP config reload creates a fresh ready client;
- ordinary runtime reconciliation still reuses an unchanged ready client without relisting regular tools.

The source candidate and integration regression are committed in the owned Codex fork. Broader package runs exposed two baseline runner or source failures outside the changed files. Those failures are retained here and keep the draft from becoming a general campaign repair.

## Source receipt

- Owned repository: `teamleaderleo/codex`
- Branch: `fieldwork/31-mcp-config-reload-reconnect`
- Draft PR: `teamleaderleo/codex#5`
- Base: `2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Source commit: `dbbd2bb0a9981cea8d8dfe231015349af84662a3`
- Commit message: `fix(mcp): reconnect on host config reload`
- Changed source files: 2
- Temporary validation workflow: deleted by the source commit

## Source change

`codex-rs/core/src/codex_thread.rs`

- documents host MCP config reload as an explicit freshness boundary;
- calls `reconnect_on_next_refresh()` before applying the caller-supplied MCP config.

`codex-rs/core/tests/suite/mcp_tool_exposure.rs`

- adds `host_mcp_config_refresh_reconnects_ready_clients`;
- uses the existing Apps MCP startup counter;
- records initial initialization attempts;
- calls `CodexThread::refresh_mcp_config`;
- requires exactly one additional initialization attempt.

## Passing validation

### Rust formatting

```bash
cargo fmt --all
cargo fmt --all -- --check
```

Result: passed.

### Host reload reconnect contract

```bash
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
```

Result: passed.

This proves the source candidate causes the stable Apps MCP endpoint to initialize a fresh client after the public host MCP config reload entrypoint.

### Ordinary reconciliation reuse contract

```bash
just test -p codex-mcp reconciliation_reuses_connection_without_relisting_regular_tools
```

Result: passed.

This proves the source candidate leaves the existing low-latency ordinary reconciliation contract intact.

## Broader validation limits

### Full codex-core run

```bash
just test -p codex-core
```

The run executed the campaign regression successfully, then failed across unrelated sandbox-dependent tests. Representative failures included:

- apply-patch hard-link and path-traversal cases;
- approval matrix and persisted exec-policy cases;
- unified-exec sandbox cases;
- workspace-root command and file-write cases.

The repeated failure mode was the filesystem sandbox helper or command sandbox aborting with `SIGABRT`. The candidate changes no sandbox, approval, apply-patch, unified-exec, or workspace-root code.

Conclusion: the full-package receipt is inconclusive for repository-wide health and provides no evidence against the MCP candidate.

### codex-app-server MCP filter

```bash
just test -p codex-app-server mcp_refresh
```

Compilation stopped in an unrelated app-server test initializer because `ItemCompletedEvent` lacked the newer required field `started_at_ms`. The candidate changes no app-server source or event initializer.

Conclusion: app-server package validation remains blocked at the owned fork base. The core public method and app-server caller path are source-mapped, while a clean app-server package run requires repairing or rebasing that baseline first.

## Publication race during validation

Two workflow triggers ran against the same branch. Both created the same validated source commit. One pushed first; the other received a non-fast-forward rejection. The remote branch now points at the successful source commit, and the draft PR contains only the two intended source files.

## Claim supported

At the owned fork pin, a bounded source change can give host-triggered MCP config reload fresh-client semantics while preserving ordinary reusable reconciliation. The focused compiled regressions support that interface claim.

## Claim withheld

This source slice does not establish a complete host/MCP lifecycle repair.

Remaining required evidence:

- generation-bound reconnect intent under an already-running publication;
- stable-endpoint stub-to-real catalogue and server-identity assertions in compiled Codex;
- failed reconnect behavior and old-state retention policy;
- tool-list-change notification relist and publication;
- late relist rejection;
- concurrent host reload, notification, auth, and config changes;
- host preserve, replace, clear, and reject semantics across resume and fork;
- per-server typed outcomes and catalogue revision;
- a clean app-server package run after baseline repair or rebase.

## Current decision

Retain owned Codex PR #5 as a valid first implementation slice for Campaign #84. Keep it draft. Build the next test around generation ownership before proposing merge into an owned default branch.
