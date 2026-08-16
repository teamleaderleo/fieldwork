# Vercel AI SDK OpenCode project-plugin credential boundary

Date: 2026-08-11

Fieldwork lead: #831  
Programme: #13  
Target hub: #2  
Worker: `chatgpt:gpt-5.6-sol`  
Claim scope: mechanism and interface  
Upstream contact authorized: `false`

## In simple words

The current Vercel AI SDK OpenCode harness starts an OpenCode server with provider credentials in its process environment. It also passes provider configuration to `createOpencodeServer()`, whose SDK implementation serializes that configuration into `OPENCODE_CONFIG_CONTENT` for the OpenCode child process.

Before Vercel creates an OpenCode session or sends the first prompt, the bridge calls `client.mcp.status()` for the session work directory. OpenCode's instance middleware loads that directory first. Instance loading runs the bootstrap path, and bootstrap calls `plugin.init()` immediately after config loading. Project `.opencode/plugin(s)/*.{ts,js}` files are discovered by config loading and their exported plugin functions execute in the OpenCode server process.

That gives checked-out repository code a pre-prompt execution path with access to the harness provider credentials carried in `process.env` and to provider credentials embedded in `OPENCODE_CONFIG_CONTENT`.

`OPENCODE_DISABLE_PROJECT_CONFIG=1` removes project `.opencode` directory discovery at the OpenCode config-path layer. It is the cleanest existing discriminator for this path.

The source chain is direct enough to classify the mechanism as `source-confirmed`. A target-native OpenCode `v1.18.3` execution remains pending because this execution environment has Node but lacks the packaged OpenCode runtime and package installation access. A ready-to-run target probe is included under `probe/`.

## Exact source

Vercel AI SDK repository: `vercel/ai`  
Reviewed current `main`: `74556f7946cdf50aa41c01c5d5b3bd2b733acc86`  
OpenCode bridge runtime pinned by Vercel: `@opencode-ai/sdk@1.18.3` and `opencode-ai@1.18.3`  
OpenCode source tag reviewed: `anomalyco/opencode@v1.18.3`

Primary Vercel surfaces:

- `packages/harness-opencode/src/opencode-auth.ts`
- `packages/harness-opencode/src/opencode-harness.ts`
- `packages/harness-opencode/src/bridge/index.ts`
- `packages/harness-opencode/src/bridge/package.json`
- `packages/harness-pi/src/pi-session.ts` as an adjacent harness precedent

Primary OpenCode surfaces:

- `packages/sdk/js/src/v2/server.ts`
- `packages/opencode/src/config/paths.ts`
- `packages/opencode/src/config/config.ts`
- `packages/opencode/src/config/plugin.ts`
- `packages/opencode/src/plugin/index.ts`
- `packages/opencode/src/project/bootstrap.ts`
- `packages/opencode/src/project/instance-store.ts`
- `packages/opencode/src/server/routes/instance/httpapi/middleware/instance-context.ts`
- `packages/opencode/src/server/routes/instance/httpapi/handlers/mcp.ts`
- `packages/web/src/content/docs/plugins.mdx`

## Source-confirmed call path

### 1. Vercel puts provider authentication in the bridge environment

`resolveOpenCodeEnv()` returns the selected provider's credentials as environment variables. Depending on settings, that can include `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, or `AI_GATEWAY_API_KEY` plus related provider configuration.

`createOpenCode().doStart()` builds the bridge `env` from `resolveOpenCodeEnv()` and spawns `bridge.mjs` with that environment.

Evidence class: `source-read`.

### 2. OpenCode receives both environment and config carriers

The bridge builds provider config from those same environment variables and passes it as `config` to `createOpencodeServer()`.

OpenCode SDK `v1.18.3` launches the `opencode` child with:

- `...process.env`; and
- `OPENCODE_CONFIG_CONTENT: JSON.stringify(options.config ?? {})`.

So the server process inherits the provider environment and also receives a serialized config that can contain the provider API key under `provider.<id>.options.apiKey`.

Evidence class: `source-read`.

### 3. Project plugins are automatically discovered

OpenCode `ConfigPaths.directories()` includes project `.opencode` directories discovered upward from the requested directory while `OPENCODE_DISABLE_PROJECT_CONFIG` is false.

For every config directory, config loading calls `ConfigPlugin.load(dir)`. That function scans `{plugin,plugins}/*.{ts,js}` and returns local file URLs.

OpenCode's own plugin documentation describes project plugin files as automatically loaded at startup.

Evidence class: `source-read`.

### 4. The first Vercel directory-scoped request triggers plugin initialization

Vercel's `ensureRuntime()` creates the OpenCode server and client, then immediately calls `runtime.client.mcp.status()`. Only after `ensureRuntime()` returns does `runTurn()` call `ensureSession()` and then `runPrompt()`.

OpenCode's instance HTTP middleware resolves the request directory and calls `InstanceStore.load({ directory })` before the MCP handler executes.

`InstanceStore.load()` boots a fresh instance. The bootstrap path runs `config.get()` and then `plugin.init()` before the remaining per-instance services initialize.

`plugin.init()` materializes plugin state. The plugin service loads external plugin modules and calls their exported plugin functions inside the OpenCode server process.

Therefore Vercel's `mcp.status()` request can execute repository-local OpenCode plugin code before session creation and before the first prompt.

Evidence class: `source-read`; mechanism classification: `source-confirmed`.

### 5. The existing OpenCode control removes the project discovery path

`ConfigPaths.directories()` omits project `.opencode` discovery when `Flag.OPENCODE_DISABLE_PROJECT_CONFIG` is true. The flag maps to `OPENCODE_DISABLE_PROJECT_CONFIG`.

This control applies earlier than plugin loading and also blocks other project-local OpenCode config discovered through that path.

Evidence class: `source-read`.

## Model-executed control

Path: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-opencode-project-plugin-20260811/probe/model-probe.mjs`

Command executed in the Fieldwork research environment:

```text
node /tmp/fieldwork-opencode-model-probe.mjs
```

Retained receipt: `probe/model-receipt.json`.

Observed result:

```json
{
  "baseline": {
    "pluginLoaded": true,
    "openaiApiKeyPresent": true,
    "configContainsSentinel": true
  },
  "disabled": {
    "pluginLoaded": false,
    "openaiApiKeyPresent": false,
    "configContainsSentinel": false
  }
}
```

This probe models only the same-process environment-visibility property with fake sentinels and the project-config gate. It does not count as OpenCode target execution.

## Target-native discriminator prepared

Path: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-opencode-project-plugin-20260811/probe/target-opencode-1.18.3.mjs`

Run it from a Vercel AI checkout at the pinned revision after installing the bridge dependencies:

```text
cd packages/harness-opencode/src/bridge
pnpm install --frozen-lockfile --store-dir .pnpm-store
node /path/to/fieldwork/programmes/sdk-integration-lifecycle/scouts/vercel-ai-opencode-project-plugin-20260811/probe/target-opencode-1.18.3.mjs
```

The probe creates a temporary repository with `.opencode/plugins/fieldwork-presence.js`, starts the actual OpenCode server through the pinned SDK, calls only `client.mcp.status()`, and records booleans for:

- plugin execution;
- fake `OPENAI_API_KEY` visibility;
- fake `OPENCODE_CONFIG_CONTENT` sentinel visibility.

It then repeats with `OPENCODE_DISABLE_PROJECT_CONFIG=1`.

No model request or real provider credential is needed.

## Why this is a useful contribution lane

The behavior crosses a trust boundary before the user or model asks OpenCode to execute repository code. A harness consumer can clone or mount a repository and reach the first runtime-status call with provider credentials already present. Repository-local OpenCode plugins can execute during that initialization path.

The Vercel AI SDK already uses a stricter policy in the Pi harness. Current `harness-pi` disables filesystem extension discovery with `noExtensions: true`; its source comment says the purpose is to avoid loading personal or project Pi extensions inside the server process. Caller-supplied inline extension factories remain available as an explicit capability.

That adjacent precedent makes an OpenCode opt-in policy especially coherent.

## Ranked contribution candidates

### 1. Default-disable OpenCode project config in harness sessions

Candidate: set `OPENCODE_DISABLE_PROJECT_CONFIG=1` in the OpenCode bridge environment by default.

Why first:

- one existing OpenCode control blocks the project plugin path at discovery time;
- the control also blocks repo-local config mechanisms that can spawn local MCP servers, aligning with adjacent campaign #830;
- the policy matches the Pi harness's explicit extension-discovery stance.

Main compatibility question: whether `@ai-sdk/harness-opencode` currently promises automatic use of repository-local `opencode.json` / `.opencode` settings. That contract needs review before patching.

### 2. Add an explicit opt-in for repository-local OpenCode config

Candidate public setting: a narrowly named boolean such as `projectConfig` / `allowProjectConfig`, defaulting to disabled for harness sessions and enabling the existing OpenCode behavior when a caller deliberately trusts the repository.

This is stronger if users rely on repo-local OpenCode customization and the project needs a migration path.

### 3. Add a regression fixture around startup execution

A harness-level test should create a repository-local plugin that writes only booleans, then prove:

- default harness startup reaches `mcp.status()` without executing the plugin;
- explicit opt-in executes it;
- provider authentication still reaches the model runtime when project config is disabled.

This test catches future changes in OpenCode startup ordering or config discovery.

## Recommendation

Run the included target-native discriminator first. If baseline executes the plugin and the disable control suppresses it, promote this lead to a campaign focused on a default project-config boundary with an explicit opt-in if compatibility requires one.

Treat #830 and this lead as sibling mechanisms sharing one likely policy control:

- #830: repo config starts a local MCP subprocess;
- #831: repo plugin code executes directly in the OpenCode server process.

A single `OPENCODE_DISABLE_PROJECT_CONFIG=1` default may close both paths. Keep separate regression tests because the execution mechanisms differ.

## Negative results and limits

- Target-native OpenCode `v1.18.3` execution has not run in this environment.
- The model probe does not prove OpenCode discovery or bootstrap timing; the source trace establishes those properties.
- No real provider key was used or written.
- No claim is made about global OpenCode config outside the project-discovery path.
- No claim is made about every OpenCode extension mechanism.
- No upstream issue, pull request, comment, reaction, or message was created.
- No third-party repository was mutated.

## Next bounded work

1. Execute `probe/target-opencode-1.18.3.mjs` against the pinned bridge runtime.
2. Record baseline and disabled-control receipts.
3. Review `@ai-sdk/harness-opencode` docs/tests for any promised repo-local config behavior.
4. If execution confirms the source trace, promote a campaign with two patch variants: unconditional disable versus explicit opt-in.
5. Add a harness regression that checks the plugin path independently from the MCP subprocess path in #830.
