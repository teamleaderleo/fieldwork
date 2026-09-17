## In simple words

Current Vercel AI main added per-harness `mcpServers`. Most of the obvious private-name collision risks are already handled well: Claude Code, OpenCode, and ACP reserve their internal HarnessAgent MCP server names, Codex uses a separate relay for host tools, and DeepAgents prefixes external MCP tool names.

The OpenCode adapter has a more consequential boundary. The adapter presents `mcpServers` as caller configuration, but the OpenCode runtime also loads `opencode.json`, `opencode.jsonc`, and `.opencode` from the checked-out repository unless `OPENCODE_DISABLE_PROJECT_CONFIG=1` is set. Vercel's OpenCode bridge does not set that flag. A repository-local OpenCode config can therefore add an enabled local MCP server that OpenCode starts during runtime initialization. That local MCP subprocess inherits the OpenCode server environment. The same environment carries model/provider credentials forwarded by the harness, and `OPENCODE_CONFIG_CONTENT` can itself contain the provider API key serialized into Vercel's runtime config.

This means repository content can cause an extra local process to start and receive harness provider credentials before a model chooses a tool or a harness permission request is involved. Network exfiltration depends on sandbox network policy, but credential exposure to the repo-configured subprocess follows directly from the pinned source paths below.

Recommendation: promote the OpenCode project-config/MCP credential boundary into a campaign. Separately scout project-local OpenCode plugins, which are discovered and executed in the same server process and appear to cross the same trust boundary through a second mechanism.

## Scout identity

- Fieldwork lane: #827
- Programme: #13 (`sdk-integration-lifecycle`)
- Target hub: #2 (`vercel-ai`)
- Worker: `chatgpt:gpt-5.6-sol`
- Claim scope: mechanism and interface
- Pinned Vercel AI revision: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`
- Per-harness MCP feature revision: `a03ff6c8682501c151306b93f36ec4b654ae779a`
- Pinned OpenCode runtime used by the Vercel bridge: `v1.18.3`
- Upstream contact authorized: false

## Exact question

At the pinned Vercel AI revision, does per-harness `mcpServers` preserve one unambiguous owner for server identity and tool classification across Claude Code, Codex, OpenCode, ACP/Grok Build, DeepAgents, and Pi, including collision and translation cases?

The scout broadened one step after source tracing showed that OpenCode's effective MCP set can include repository-local configuration in addition to `createOpenCode({ mcpServers })`. That discovery stays inside the lane's MCP server ownership question.

## Source map

### Vercel AI OpenCode adapter

Relevant pinned files:

- `vercel/ai@74556f7946cdf50aa41c01c5d5b3bd2b733acc86:packages/harness-opencode/src/opencode-harness.ts`
- `vercel/ai@74556f7946cdf50aa41c01c5d5b3bd2b733acc86:packages/harness-opencode/src/opencode-auth.ts`
- `vercel/ai@74556f7946cdf50aa41c01c5d5b3bd2b733acc86:packages/harness-opencode/src/bridge/index.ts`
- `vercel/ai@74556f7946cdf50aa41c01c5d5b3bd2b733acc86:packages/harness-opencode/src/bridge/package.json`
- `vercel/ai@74556f7946cdf50aa41c01c5d5b3bd2b733acc86:content/providers/02-ai-sdk-harnesses/04-opencode.mdx`

Observed flow:

1. `resolveOpenCodeEnv` selects and forwards provider credentials such as `AI_GATEWAY_API_KEY`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, or `OPENAI_API_KEY` into the sandbox bridge environment.
2. The bridge calls `createOpencodeServer` with `buildOpenCodeConfig(...)` and the session `workdir`.
3. `buildOpenCodeConfig` serializes provider configuration and, when present, caller MCP settings. For gateway/OpenAI/Anthropic-compatible routes the provider config includes credential values in provider options.
4. The Vercel bridge isolates HOME/XDG locations, but it does not set `OPENCODE_DISABLE_PROJECT_CONFIG`.
5. The bridge constructs the OpenCode client with `directory: workdir` and calls `client.mcp.status()` during `ensureRuntime`, forcing MCP state discovery before the first prompt is run.

The public adapter docs describe `mcpServers` as an adapter setting and say authentication is forwarded into the sandbox bridge. They do not describe repository-local OpenCode config as another source of MCP servers.

### Pinned OpenCode `v1.18.3`

Relevant files:

- `anomalyco/opencode@v1.18.3:packages/sdk/js/src/v2/server.ts`
- `anomalyco/opencode@v1.18.3:packages/core/src/flag/flag.ts`
- `anomalyco/opencode@v1.18.3:packages/opencode/src/config/config.ts`
- `anomalyco/opencode@v1.18.3:packages/opencode/src/config/paths.ts`
- `anomalyco/opencode@v1.18.3:packages/opencode/src/mcp/index.ts`
- `anomalyco/opencode@v1.18.3:packages/opencode/src/mcp/catalog.ts`

Observed flow:

1. `createOpencodeServer` spawns `opencode serve` with `{ ...process.env, OPENCODE_CONFIG_CONTENT: JSON.stringify(options.config ?? {}) }`.
2. Project config scanning is enabled unless `OPENCODE_DISABLE_PROJECT_CONFIG` is truthy.
3. `ConfigPaths.files('opencode', directory, worktree)` walks upward for `opencode.jsonc` and `opencode.json`.
4. `.opencode` directories are also discovered while project config is enabled.
5. Project config is merged before `OPENCODE_CONFIG_CONTENT`; nested objects are deep-merged, so unique repo-local MCP entries remain alongside SDK-supplied entries.
6. MCP state initialization walks configured MCP entries and creates enabled clients.
7. `connectLocal` creates `StdioClientTransport` with an environment beginning with `...process.env`, then applies MCP-entry-specific environment overrides.
8. Therefore a repo-configured local MCP subprocess receives the OpenCode server environment, including direct provider credential variables and `OPENCODE_CONFIG_CONTENT`.
9. OpenCode's MCP tool naming is `sanitize(clientName) + '_' + sanitize(toolName)`. Vercel's dynamic classifier computes matching sanitized server prefixes for connected external servers.

## Finding F1 — repo-local OpenCode MCP startup receives harness provider credentials

### Invariant

A caller choosing the OpenCode harness should be able to identify which adapter/runtime configuration can start credential-bearing MCP subprocesses. Repository content may influence the coding task, but an extra MCP process created from repository-local config belongs to a different trust decision than the caller's `createOpenCode({ mcpServers })` setting or a model-requested shell/tool action.

### Trigger sequence

A representative sequence is:

1. Harness setup places or clones a repository into the session work directory.
2. That repository contains `opencode.json[c]` with an enabled local MCP server under `mcp`.
3. The OpenCode harness resolves a real provider credential and forwards it into the bridge.
4. The bridge starts OpenCode using `createOpencodeServer` without `OPENCODE_DISABLE_PROJECT_CONFIG=1`.
5. OpenCode discovers the repository config, then merges the SDK-supplied `OPENCODE_CONFIG_CONTENT`.
6. The repository MCP entry survives as a distinct key.
7. OpenCode initializes MCP clients and spawns the repository-declared local command.
8. The local command inherits the OpenCode server environment.
9. That environment contains the direct provider credential and can also contain the same credential serialized inside `OPENCODE_CONFIG_CONTENT`.

No model tool call, HarnessAgent host-tool call, or built-in tool permission decision is needed for steps 5–9.

### Consequence

The repository-configured MCP subprocess can read harness provider credentials. It can write those values to the sandbox workspace, return them through its MCP protocol, or use any network access available to that process. Direct outbound exfiltration is conditional on sandbox network policy; local credential disclosure to the subprocess is source-evidenced independently of that policy.

This also means the effective MCP server set is wider than the adapter setting suggests: caller-owned `mcpServers` and repo-owned OpenCode config are merged into one runtime set.

### Likely owner

The immediate Vercel boundary is `packages/harness-opencode/src/bridge/index.ts`, where the harness decides which OpenCode-native project configuration is allowed into a sandbox session carrying provider credentials.

The underlying runtime behavior is normal OpenCode behavior. The harness adapter is the component combining that behavior with sandbox-forwarded credentials and an API that presents MCP servers as adapter configuration.

### Evidence class

- **Source-confirmed:** Vercel credential forwarding, OpenCode server launch, absence of the project-config disable flag, project config discovery/merge order, automatic MCP connection, local MCP process environment inheritance.
- **Model-executed probe:** `probe-opencode-project-mcp-env.mjs` models only the two relevant object/environment operations and confirms all four expected predicates.
- **Target-executed probe:** unavailable in this worker environment because direct package/repository network access from the execution container is unavailable. GitHub source retrieval remained available through the connected repository tool.

### Probe

Run:

```text
node programmes/sdk-integration-lifecycle/scouts/vercel-ai-harness-mcp-server-boundaries-20260811/probe-opencode-project-mcp-env.mjs
```

Observed output:

```json
{
  "repoMcpSurvivesConfigMerge": true,
  "callerMcpAlsoPresent": true,
  "repoMcpReceivesDirectProviderCredential": true,
  "repoMcpReceivesSerializedProviderCredential": true
}
```

The probe deliberately uses dummy credentials and a dependency-free merge helper. It does not claim runtime reproduction; the source chain above carries the main evidence.

### Reversing evidence

Downgrade or close this branch if one of these becomes true:

- the harness intentionally treats repository-local OpenCode config as trusted runtime code and documents that it may automatically execute with provider credentials before a prompt;
- the actual sandbox provider strips provider credentials and `OPENCODE_CONFIG_CONTENT` from child MCP processes despite OpenCode's explicit `...process.env` handoff;
- a hidden launch path sets `OPENCODE_DISABLE_PROJECT_CONFIG` before OpenCode loads config;
- a target-executed reproduction on the pinned versions proves repository MCP entries are excluded from the bridge-created OpenCode instance.

Current source review found no Vercel reference to `OPENCODE_DISABLE_PROJECT_CONFIG`, `opencode.json`, or another project-MCP suppression path.

## Candidate remediations for a campaign

These are campaign questions, not a patch recommendation yet.

1. **Disable project config for harness-managed OpenCode sessions.** Pinned OpenCode already supports `OPENCODE_DISABLE_PROJECT_CONFIG=1`. This gives the cleanest ownership boundary, but it may suppress native project commands/plugins/settings users expect.
2. **Make project-config inheritance explicit.** Add an adapter setting whose safe/default mode suppresses project config and whose opt-in mode documents the credential/execution consequences.
3. **Separate credentials from OpenCode child-process environment.** This is harder because `createOpencodeServer` puts SDK config into `OPENCODE_CONFIG_CONTENT`, and Vercel's provider config may serialize the key there. Even removing the direct `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` variable would leave a credential-bearing config string available to children.
4. **Upstream child-env filtering.** OpenCode could offer an MCP child environment policy, but that would require upstream behavior and still leaves project-local plugins running in the OpenCode server process.

The first campaign experiment should establish target-executed behavior with a fake credential and a repo-local MCP command that writes only boolean presence markers, never the credential itself.

## Negative results and dead ends

### Claude Code private MCP collision — defended

`createClaudeCode` rejects caller MCP server name `harness-tools`. The bridge shallow-copies caller servers and then owns `harness-tools` for HarnessAgent tools. The reserved-name guard gives the internal server one clear owner.

Disposition: stop this branch.

### OpenCode private MCP collision — defended

`createOpenCode` rejects caller MCP server name `harness-tools`. The bridge then owns that name for its local HarnessAgent tool relay.

Disposition: stop the literal reserved-name collision branch. F1 is distinct because repo-local OpenCode configuration bypasses the adapter's caller-settings guard by entering through OpenCode's own config loader.

### ACP private MCP collision — defended

`createACP` rejects caller MCP server name `ai-sdk-harness-tools`; the ACP bridge appends its host-tool relay under that reserved name after converting external servers.

Disposition: stop this branch.

### Codex host-tool collision — separate mechanism

Codex forwards caller `mcpServers` to native Codex config, while HarnessAgent tools use a CLI relay because the pinned Codex path has an MCP tool limitation. No adapter-owned MCP server name is merged into caller settings.

Disposition: no collision finding from this scout.

### DeepAgents external/host tool collision — deterministic host precedence

DeepAgents prefixes MCP tools with server identity through `MultiServerMCPClient`, then filters external tools whose final name collides with a host tool name. Host tools win. This can silently hide an unusually named external tool, but the collision requires caller-controlled surfaces and has low consequence compared with F1.

Disposition: retain as a low-priority interface curiosity; no campaign.

### OpenCode dynamic classification — naming logic matches pinned runtime

Vercel snapshots connected external MCP server prefixes during runtime initialization and marks matching tool calls/results dynamic. Pinned OpenCode names MCP tools with the same sanitizer and server-name prefix convention. Tool-list changes from an already connected server preserve the same server prefix.

A failed/disconnected server that later reconnects through an out-of-band control could make the prefix snapshot stale, but this scout found no harness-reachable reconnection path that makes the case consequential.

Disposition: stop unless a future adapter exposes MCP connect/add during a live session.

### Pi forwarding — no server-identity defect found

Pi validates each MCP entry as an object, hands settings to `pi-mcp-adapter`, enables direct tools with `mcp` prefixing, and keeps the adapter extension in the same resource-loader lifecycle as caller extensions.

Disposition: no branch from current evidence.

## Ranked branch candidates

### 1. Promote — OpenCode repo-local MCP auto-start with provider credentials

- Consequence: high. Repository content can create a credential-bearing process during runtime initialization.
- Confidence: high from pinned source; target-executed confirmation still desirable.
- Likely owner: Vercel OpenCode bridge/project-config policy.
- Next evidence: target-executed fake-secret reproduction across at least one auth mode; verify whether sandbox network policy changes only exfiltration or also process env inheritance.
- Campaign question: how should `@ai-sdk/harness-opencode` bound OpenCode project config so repository-local runtime extensions cannot silently inherit harness credentials?

### 2. Dispatch separate scout — repository-local OpenCode plugins

Pinned OpenCode scans `.opencode/{plugin,plugins}/*.{ts,js}`, records them as local plugins, loads external plugin modules, and executes server plugin functions in the OpenCode process. The same process holds provider env/config.

This is adjacent to F1 but has a different execution mechanism and remediation tradeoff. A separate scout should map when plugin initialization occurs relative to session creation and permission controls, then test a fake-secret presence marker.

### 3. Stop — dynamic-prefix and host-name collision branches

Current naming/runtime contracts explain the suspicious cases well enough. Reopen only if live MCP add/reconnect becomes harness-reachable or naming changes upstream.

## Recent/context checks

- The MCP setting entered Vercel AI in `a03ff6c8682501c151306b93f36ec4b654ae779a` and is present at pinned head `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`.
- Fieldwork had extensive active Vercel harness work, but duplicate searches found no existing lane for this OpenCode project-config/MCP credential boundary and no existing Fieldwork references to `OPENCODE_DISABLE_PROJECT_CONFIG` or `opencode.json`.
- Vercel code search found no use of `OPENCODE_DISABLE_PROJECT_CONFIG` or `opencode.json` at the pinned head.
- A targeted open-issue search in `vercel/ai` found no matching OpenCode project-config/MCP credential issue.

## Recommendation

Promote F1 into a bounded campaign under `sdk-integration-lifecycle` / `vercel-ai` and keep upstream read-only until a coordinator authorizes contact.

Campaign first move: obtain target-executed proof using fake credentials and boolean markers, then compare two runs on the pinned versions:

- baseline OpenCode harness with repo-local MCP config;
- same run with `OPENCODE_DISABLE_PROJECT_CONFIG=1` injected into the bridge environment.

Measure only whether the repo MCP starts and whether credential-bearing variables/config are present. That experiment will distinguish the adapter policy decision cleanly from sandbox network policy.

Dispatch a separate scout for project-local OpenCode plugins after the campaign claim is recorded, because the plugin path appears to cross the same trust boundary without going through MCP at all.
