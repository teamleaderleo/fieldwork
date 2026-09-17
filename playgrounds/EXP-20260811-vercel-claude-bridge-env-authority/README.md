# Vercel AI SDK Claude bridge environment authority

## State

`COMPLETE — source-read + model-executed + target-test-prepared`

Owner: `chatgpt:gpt-5.6-sol`  
Created: `2026-08-11`  
Claim scope: interface  
Target: `target:vercel-ai`  
Target hub: #2  
Programme: #13  
Owned execution carrier: `teamleaderleo/ai#56`  
Public upstream contact authorized: `no`

## In simple words

The Claude Code harness runs a WebSocket bridge inside the sandbox. The host authenticates to that bridge with `BRIDGE_CHANNEL_TOKEN`; the bridge also receives `BRIDGE_WS_PORT`.

At Vercel AI SDK revision `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`, those bridge transport values live in the bridge process environment. The Claude-specific bridge invokes the Anthropic Agent SDK from that same process. When caller environment overrides are configured, it explicitly passes `{ ...process.env, ...start.env }` as the Agent SDK subprocess environment. When no override is configured, an existing target test asserts that the Agent SDK inherits the bridge environment.

Anthropic documents Bash as a shell capability with access to environment variables. The shared Vercel AI SDK bridge treats the bridge token as the socket authentication credential: an authorized new socket replaces the current active socket and can send the same control messages the host uses, including tool approval/results, abort, stop, destroy, and replay requests.

The narrow concern is therefore an authority boundary: bridge-control credentials cross into the model runtime environment. Once that runtime has an executable path capable of reading environment variables and opening a local socket, possession of those credentials can confer bridge-control authority that was intended for the host.

Current answer: source and the retained model support this authority chain. The owned target-native test is prepared to prove the first target boundary — reserved bridge transport credentials should stay out of the Agent SDK environment — before any broader integration claim.

## Bounded question

Does the Claude Code harness place bridge-control credentials in the environment inherited by the Claude Agent SDK runtime, and does possession of those credentials authorize a second bridge socket to replace the host connection and submit control frames?

At the pinned revision:

- **source-read:** yes, the bridge token/port enter the bridge process environment and the reviewed Claude bridge preserves inherited process environment for the Agent SDK runtime;
- **source-read:** yes, the shared bridge uses the token as socket authority and an authorized new connection replaces the active host socket;
- **model-executed:** the retained discriminator preserves those rules, rejects a wrong-token negative control, then demonstrates replacement, replay, and approval settlement with the correct token;
- **target/integration execution:** pending for the model-controlled executable path.

## Exact subject

Public repository: https://github.com/vercel/ai  
Pinned public revision: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`  
Retrieval date: `2026-08-11`

Primary target paths:

- `packages/harness-claude-code/src/claude-code-harness.ts`;
- `packages/harness-claude-code/src/bridge/index.ts`;
- `packages/harness-claude-code/src/bridge/index.test.ts`;
- `packages/harness-claude-code/src/bridge/package.json`;
- `packages/harness/src/bridge/index.ts`.

External contract sources:

- Anthropic Claude Platform Bash tool: https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool
- Claude Agent SDK TypeScript v0.3.149 release note: https://github.com/anthropics/claude-agent-sdk-typescript/releases/tag/v0.3.149

The target bridge pins `@anthropic-ai/claude-agent-sdk@0.3.213`, which is later than the release where Anthropic clarified the `Options.env` subprocess-environment contract.

## Source map

### 1. Host → sandbox bridge environment

The Claude Code harness creates a bridge token, then spawns the sandbox bridge with environment containing:

```text
BRIDGE_CHANNEL_TOKEN = <bridge token>
BRIDGE_WS_PORT        = <bridge port>
```

The same token is placed in the host WebSocket URL as `agent_bridge_token`.

### 2. Bridge → Claude Agent SDK environment

The Claude-specific bridge imports `process.env` as `procEnv` and calls the Anthropic Agent SDK `query()`.

When caller `start.env` exists, the bridge passes:

```text
env: { ...procEnv, ...start.env }
```

An existing Vercel AI SDK test asserts that caller values override inherited values while inherited bridge-process environment remains present.

When caller `start.env` is absent, the bridge omits the Agent SDK `env` option. The same target test names this behavior as letting the Agent SDK inherit the environment.

Anthropic's Agent SDK release notes clarify that a supplied `Options.env` replaces the subprocess environment, which explains why Vercel performs an explicit `process.env` merge when it wants inheritance plus caller overrides.

### 3. Runtime tool access

Anthropic documents its Bash tool as providing shell-command execution with access to environment variables and the working directory.

The Vercel Claude adapter exposes native Bash as a built-in harness tool. Permission handling varies by configured mode:

- `allow-all` maps to bypassed built-in approval;
- `allow-edits` still requires approval for Bash;
- `allow-reads` requires approval for Bash and edit operations.

This means the end-to-end authority consequence depends on an executable path being available. Under restricted modes, one approved shell execution can be enough to cross that boundary; source evidence alone does not establish that a model actually performs the takeover sequence.

### 4. Bridge token → control authority

The shared bridge runtime reads the expected token from `BRIDGE_CHANNEL_TOKEN` and binds its WebSocket server on `0.0.0.0`.

For each connection:

```text
wrong token       → close unauthorized
correct token     → activeSocket = new socket
```

The source explicitly describes the second behavior as single-flight replacement for host reconnect.

The active socket may send control frames including:

```text
tool-result
tool-approval-response
user-message
abort
resume
stop
destroy
```

`resume` replays bridge events after a supplied sequence cursor. Pending tool approvals are keyed by `approvalId`; a matching `tool-approval-response` resolves the pending approval decision.

The same credential therefore authenticates both legitimate host reconnect and any other process capable of reaching the bridge and presenting the token.

## Competing explanations

### H1 — bridge env is intentionally inherited and harmless because the model runtime cannot use it

The inheritance is intentional as a general environment behavior. The harmlessness premise remains unproven. Anthropic documents Bash access to environment variables, and the shared bridge token grants socket-control authority. A target-native or controlled integration discriminator is required for the exact executable path.

### H2 — bridge token is only a connection locator, not an authority credential

**Weakened by source.** A wrong token is rejected; a correct token makes the connection active. The active socket can answer pending approvals/results and terminate or abort the bridge.

### H3 — replacing the active socket cannot influence a pending approval

**Weakened by source and model.** Approval requests are replayable events and approval responses resolve pending approval IDs when received from the active authorized socket.

### H4 — removing all inherited environment from Claude is the right fix

**Rejected as too broad.** Provider authentication, client attribution, caller configuration, and other runtime values legitimately depend on environment propagation. The smallest boundary is reserved bridge-control credential isolation.

## Executable discriminator

Run:

```sh
python3 playgrounds/EXP-20260811-vercel-claude-bridge-env-authority/run.py
```

Retained environment:

- Python `3.13.5`;
- Linux `6.18.35` x86_64;
- zero dependencies;
- synthetic credentials only;
- network disabled.

Observed:

```json
{
  "authorized_second_socket_replaces_host": true,
  "authorized_socket_can_resolve_pending_approval": true,
  "child_env_contains_port": true,
  "child_env_contains_token": true,
  "replay_exposes_pending_approval_id": true,
  "unauthorized_socket_rejected": true
}
```

The negative control is important: a wrong-token connection fails and leaves the host active. The authority transition occurs only once the modeled process presents the inherited correct token.

This runner is `model-executed`. It does not open a real WebSocket or ask Claude to perform the sequence.

## Target-native discriminator

Owned fork PR: `teamleaderleo/ai#56`  
Head: `fieldwork/claude-bridge-env-authority-tests`  
Exact base: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`

The one-file target test configures ordinary caller env plus synthetic bridge token/port in the bridge process environment, imports the real Claude bridge module with the Agent SDK mocked at the call boundary, and asserts:

```text
APPLICATION_ENV          remains present
BRIDGE_CHANNEL_TOKEN     absent
BRIDGE_WS_PORT            absent
```

Current source is expected to fail because the Agent SDK env is built from `{ ...procEnv, ...start.env }`.

This test proves only the adapter environment boundary. A complete authority demonstration would require a controlled integration where a permitted sandbox execution reads the values, opens an authorized local bridge socket, and tests control ownership without touching production systems or public upstream.

## Change thesis

Current behavior:

```text
host creates bridge credential
        ↓
bridge process receives token + port
        ↓
Claude Agent SDK runtime inherits bridge process env
        ↓
model runtime can have shell access to environment
        ↓
credential can authenticate a replacement bridge socket
        ↓
active socket owns bridge controls
```

Concrete consequence: the same sandbox runtime that may execute model-selected commands can receive the credential that authenticates host control of that runtime's bridge. That collapses the separation between model execution authority and host bridge-control authority once an executable path is available.

Candidate repair boundary:

```text
bridge process env
        ↓
copy inherited/provider/caller env for Agent SDK
        ↓
remove reserved bridge transport keys
        ↓
launch Claude runtime
```

At minimum review:

- `BRIDGE_CHANNEL_TOKEN`;
- `BRIDGE_WS_PORT`;
- other bridge-only control variables such as replay/debug transport settings before deciding their exposure contract.

The repair should preserve provider credentials and ordinary caller env. A focused helper for child-runtime environment sanitization may make the invariant testable across bridge-backed adapters if sibling source shows the same boundary.

## Candidate tests

1. caller env reaches the Claude Agent SDK runtime;
2. `BRIDGE_CHANNEL_TOKEN` does not;
3. `BRIDGE_WS_PORT` does not;
4. caller attempts to set reserved transport keys have an explicit outcome rather than silently exposing the live credential;
5. provider/auth environment remains available;
6. no-custom-env path is checked against the Agent SDK inheritance contract;
7. wrong-token bridge connection remains rejected;
8. authorized host reconnect continues to replace the stale host socket;
9. restricted approval behavior remains unchanged;
10. one controlled integration test determines whether an approved Bash process currently observes bridge transport keys before widening the security claim.

## Negative results and limits

- No claim is made that a model has exploited this path in a real application.
- No claim is made that all permission modes immediately expose an executable shell; restricted modes gate Bash.
- The shared bridge's authorized socket replacement is intentional for reconnect. The issue is credential placement across an authority boundary, not the existence of reconnect.
- Provider credentials and caller env have legitimate reasons to reach the runtime, so removing all environment inheritance is outside the selected boundary.
- No public upstream interaction occurred.
- No provider credentials, production data, or paid calls were used.

## Evidence classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| bridge process receives token and port | `source-read` | pinned Claude adapter |
| Agent SDK runtime inherits bridge process env | `source-read` | Claude bridge + target test + Agent SDK contract |
| Bash can access environment variables | `Documented` | Anthropic tool contract; exact harness execution pending |
| correct bridge token authenticates and replaces active socket | `source-read` | shared bridge runtime |
| active socket can replay and answer pending approval | `source-read` | shared bridge runtime |
| source-derived authority chain behaves as described | `model-executed` | no real socket or Claude runtime |
| target should scrub token/port at Agent SDK boundary | `target-test-prepared` | owned PR #56; execution pending |
| model-controlled shell can take over a real harness bridge | `Unknown` | controlled integration required |

## Recommendation

Retain this finding and promote a bounded campaign. The next question should remain narrow:

> Can the Claude Code harness keep bridge-control credentials out of the Agent SDK runtime environment while preserving provider authentication, ordinary caller env, host reconnect, and existing permission behavior?

After that passes target-native execution, run one controlled integration discriminator for the complete authority path. Check sibling bridge-backed adapters separately rather than assuming Claude's environment propagation pattern is universal.

## Boundaries

- Third-party `vercel/ai` remained read-only.
- All writes were confined to Fieldwork and the owned `teamleaderleo/ai` fork.
- Automated upstream contact remains prohibited.
- This record distinguishes source/model evidence from target and integration execution.
