# Source and ownership map

Inspection pin: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`

Public comparison pin: [Codex `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)

## Current lifecycle

| Boundary | Source | Current ownership |
| --- | --- | --- |
| model call item accepted | [`stream_events_utils.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/stream_events_utils.rs#L289-L347) | records the call response item immediately, then queues execution |
| tool admission and handler terminal state | [`tools/parallel.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/tools/parallel.rs#L76-L204) | tracks execution admission and terminal outcome in runtime memory; cancellation can return an aborted result |
| runtime metadata | [`tools/registry.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/tools/registry.rs#L50-L151) | exposes tool name, specification, exposure, parallelism, hooks, telemetry, and cancellation behavior; no operation-effect field |
| result conversion | [`tools/registry.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/tools/registry.rs#L166-L190) | `AnyToolResult` carries call ID, payload, output, and post-tool hook payload; no durable terminal receipt |
| provider completion and tool drain | [`session/turn.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/session/turn.rs#L2506-L2541) | provider response can complete before all in-flight tool futures drain |
| prompt normalization | [`context_manager/normalize.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/context_manager/normalize.rs#L22-L221) | inserts synthetic `aborted` outputs for missing calls, preserves duplicates and order, and removes orphan outputs |
| local compaction | [`compact.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/core/src/compact.rs#L264-L401) | compacts the normalized prompt projection and installs user messages plus summary without a raw identity gate |
| remote v1 | [`compact_remote_request.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_request.rs#L25-L99), [`compact_remote.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote.rs#L170-L381) | normalizes history, calls the remote endpoint, then drops call and result variants from installed history |
| remote v2 | [`compact_remote_v2_attempt.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_v2_attempt.rs#L32-L137), [`compact_remote_v2.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_v2.rs#L203-L439) | validates provider completion and one compaction item, then installs retained messages and compaction output |
| durable replacement | [`session/mod.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L3208-L3254) | persists replacement history; no parallel operation receipt is recorded |
| resume and fork | [`session/rollout_reconstruction.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/rollout_reconstruction.rs#L114-L443) | newest replacement becomes the base and later orphan outputs are removed during prompt projection |
| typed failure option | [`protocol/src/error.rs`](https://redirect.github.com/teamleaderleo/codex/blob/2b7b93081361b77f8ddaceaf362a09765b4153bf/codex-rs/protocol/src/error.rs#L71-L179) | `CodexErrorDetails::InvalidRequest` can carry a recoverable validation message |

## First missing owner

The first missing owner is **operation effect and terminal receipt at dispatch**.

Raw history can establish that a call or output exists, but it cannot establish:

- whether the action was read-only or potentially mutating;
- whether the handler reached a terminal outcome before cancellation or task loss;
- whether a result item was constructed and persisted exactly once;
- whether the client received the result;
- whether a retry is authorized.

The compaction layer should consume this state, not infer it from tool names or payloads.

## Candidate staged seams

### Stage 1 — effect and receipt model

Candidate owner: `codex-tools` or a small protocol/common type used by tool runtimes and rollout persistence.

Candidate fields:

- logical operation identity;
- call identity digest or internal call ID reference;
- operation effect: `ReadOnly` or `PotentialMutation`;
- terminal state: pending, completed, failed, aborted, or unknown;
- result persistence state;
- idempotency/reconciliation state;
- receipt version.

Unknown runtimes should default to `PotentialMutation` until explicitly classified.

### Stage 2 — dispatch lifecycle integration

Candidate seams:

- create pending receipt when the call item is persisted;
- mark handler terminal state in `ToolCallRuntime`;
- mark result construction and persistence during in-flight drain;
- emit the privacy-safe L06 receipt view without retaining arguments or output bodies.

### Stage 3 — pre-compaction validator

Validate raw history plus receipts before prompt normalization for local, remote v1, and remote v2:

- exactly one call identity;
- exactly one result identity;
- call precedes result;
- terminal state and persisted result agree;
- potentially mutating unknown or incomplete states reject compaction;
- reconciled states carry a bounded checkpoint receipt.

### Stage 4 — replacement and reconstruction

Persist the minimal receipt set needed to prevent replay after resume, fork, retry, or a late suffix result. Preserve old checkpoint compatibility through an explicit version and conservative unknown state.

## Rejected shortcut

A hard-coded tool-name allowlist or denylist is rejected as the campaign contract. Native, dynamic, extension, MCP, app, shell, code-mode, and subagent paths evolve independently and can alias the same operation through different names.
