# Workers SDK local, test, and deployment lifecycle scout

Issue: #18  
Programme: #13  
Target hub: #3  
Retrieval date: 2026-07-29  
Target revision: `cloudflare/workers-sdk@69ef8228fd96b4df192195d93c33e56ae665500a`  
Claim scope: mechanism and interface findings demonstrated; operational consequences marked as inferred until fault-injection trials run  
Upstream contact authorized: `false`

## Result in plain language

Cloudflare Workers SDK has several deliberate adapters around the same Worker configuration: Wrangler, the Vite plugin, the Vitest Workers pool, Miniflare, and deploy helpers. Most paths reuse Wrangler normalization and Miniflare option generation. The adapters still make independent choices about file discovery, runtime flags, worker identity, cleanup failures, and post-upload work.

The strongest demonstrated campaign is configuration discovery parity. Wrangler and the Vite plugin can select different configuration files from the same checkout. A second high-value campaign covers a deploy that changes the active Worker before a later container or trigger operation fails. Two additional candidates cover hidden teardown failures and the compatibility features injected by the Vitest pool.

No upstream contact occurred.

## Evidence labels

- **Documented** — stated in source comments, repository guidance, or official command behaviour at the pinned revision.
- **Observed** — reproduced by the retained probe in this scout.
- **Inferred** — consequence derived from source ordering or adapter behaviour; requires a focused trial before an operational claim.
- **Unknown** — downstream usage or consequence still needs repository-specific confirmation.

## Source and test map

| Area | Owning path | Lifecycle responsibility | Error and cleanup boundary |
| --- | --- | --- | --- |
| Shared config discovery | `packages/workers-utils/src/config/config-helpers.ts` | Resolves explicit config, script-relative discovery, upward search, and deploy-config redirection | Raises `UserError` for malformed or ambiguous redirected config |
| Wrangler config loading | `packages/wrangler/src/config/index.ts` | Reads raw config, normalizes environments and computed values, validates diagnostics | Validation diagnostics become `UserError`; Pages parse failures become `FatalError` |
| Vite config adapter | `packages/vite-plugin-cloudflare/src/workers-configs.ts` | Reads Wrangler config, removes or replaces Vite-owned fields, resolves entry and auxiliary workers | Uses generic `Error` for Vite-specific required-field and path checks |
| Binding conversion | `packages/wrangler/src/dev.ts` and `packages/wrangler/src/api/integrations/platform/index.ts` | Converts config bindings, applies preview IDs and local variables, starts remote binding proxy, emits Miniflare options | Hyperdrive local requirements fail early; `getPlatformProxy()` exposes explicit disposal |
| Local runtime | `packages/miniflare/src/index.ts` | Validates plugin options, serializes workerd config, launches runtime and local services | Zod failures become `MiniflareCoreError`; callers own disposal |
| Vite local execution | `packages/vite-plugin-cloudflare/src/miniflare-options.ts` and `src/plugins/dev.ts` | Adds router, asset, proxy, and runner workers; remote bindings; persistence; runtime restart handling | Patches Vite server close; container and Miniflare cleanup failures are hidden in debug output |
| Workers Vitest pool | `packages/vitest-pool-workers/src/pool/config.ts`, `src/pool/index.ts`, and `src/pool/cloudflare-pool-worker.ts` | Parses pool options, imports Wrangler config, creates Miniflare, injects Vitest runtime capabilities, transports test messages | Config failures become `TypeError`; runtime and remote-proxy disposal failures are hidden in `NODE_DEBUG` |
| Deploy orchestration | `packages/deploy-helpers/src/deploy/deploy.ts` | Validates, uploads assets, provisions bindings, uploads/deploys Worker, patches settings, deploys containers, then deploys triggers | Selected API failures receive focused messages; later container or trigger errors propagate after Worker mutation |
| Version upload | `packages/deploy-helpers/src/deploy/versions-upload.ts` | Uploads a version without changing traffic; defers declarative export reconciliation until deployment | Upload errors propagate after focused translation; tag patch failures become warnings |
| Rollback | `packages/wrangler/src/versions/rollback/index.ts` | Finds a previous 100% version and creates a new deployment routing 100% traffic to it | Rollback leaves local state and bound resources unchanged; changed secrets require confirmation |

### Test locations

- Wrangler unit tests: `packages/wrangler/src/__tests__/`; command helper runs Wrangler in-process with mocked Cloudflare APIs.
- Wrangler end-to-end tests: `packages/wrangler/e2e/`; account credentials are required.
- Miniflare tests: `packages/miniflare/test/`; fixtures dispose Miniflare and include retry handling for filesystem locks.
- Vite plugin unit and end-to-end tests: `packages/vite-plugin-cloudflare/__tests__/` and `packages/vite-plugin-cloudflare/e2e/`.
- Workers runtime tests: `packages/vitest-pool-workers/` plus `fixtures/vitest-pool-workers-examples/`; test code runs inside workerd while orchestration remains in Node.

## Lifecycle map

### 1. Configuration loading

**Documented.** Wrangler’s shared discovery searches upward from the script directory or current directory. It checks `wrangler.json`, then `wrangler.jsonc`, then `wrangler.toml`.

**Documented.** The Vite plugin scans only its resolved Vite root when `configPath` is absent. It checks `wrangler.jsonc`, then `wrangler.json`, then `wrangler.toml`.

**Documented.** Explicit `configPath` bypasses both discovery differences. Both paths eventually use Wrangler normalization for an on-disk file. Vite then removes fields owned by Vite, including Wrangler `alias`, `define`, `minify`, `build`, `rules`, `site`, and `tsconfig` behaviour.

**Consequence, inferred.** A checkout containing both JSON variants can use different Worker names, entries, bindings, compatibility dates, environments, or assets between Wrangler and Vite commands. A nested application can inherit a parent config under Wrangler while Vite reports no config or uses plugin defaults.

### 2. Binding conversion

**Documented.** Local Wrangler binding conversion uses preview IDs and merges values in this order:

```text
default bindings
→ normalized config bindings
→ .dev.vars / .env values for variable-like bindings
→ caller-supplied input bindings
```

**Documented.** Hyperdrive requires a local connection string during local execution. `getPlatformProxy()` can start remote binding sessions by default, persists local data under `.wrangler/state/v3` by default, and returns a disposal function.

**Documented.** Vite and the Vitest pool call Wrangler’s Miniflare option generator, then add adapter-specific workers and overrides. The Vitest pool disables containers and filters tail consumers that do not exist in the test worker set.

### 3. Local execution

**Documented.** Miniflare validates shared and per-worker plugin options, creates workerd configuration, launches local storage and binding services, and exposes disposal to the caller.

**Documented.** Vite adds internal router, asset, proxy, and module-runner workers. It injects an ephemeral runner Durable Object, an unsafe evaluation binding, a module fallback service, and Vite middleware service bindings. A workerd crash triggers a Vite server restart so module runners are recreated.

**Documented.** Vite state defaults to `<vite root>/.wrangler/state/v3`; temporary runtime files default to `<vite root>/.wrangler/tmp`.

### 4. Testing

**Documented.** The Workers Vitest pool runs orchestration in Node and test execution inside workerd. It renames the runner Worker and rewrites self-service references.

**Documented.** The pool adds or forces compatibility capabilities needed by Vitest, including:

- `no_handle_cross_request_promise_resolution`;
- `nodejs_compat_v2` and several Node feature flags;
- `unsafe_module`;
- an unsafe evaluation binding and module fallback service;
- injected `node:console` and `node:vm` modules;
- an ephemeral test-runner Durable Object.

**Consequence, inferred.** Tests can execute with capabilities or request-lifetime behaviour that the deployed Worker does not receive from its declared compatibility configuration. This is an adapter contract to test explicitly, especially for code paths that depend on Node modules, cross-request promises, worker names, or self-bindings.

### 5. Deployment

**Documented.** Deployment proceeds through these major stages:

```text
local validation
→ API-backed pre-upload checks
→ overwrite confirmation
→ asset and Workers Sites synchronization
→ binding provisioning when enabled
→ Worker version upload or script PUT
→ active deployment creation on the versions path
→ non-versioned settings patch
→ container deployment
→ routes, cron triggers, and other trigger deployment
```

Docker availability is checked before Worker upload when a configured container needs a local Dockerfile build. This prevents one clear partial-deploy path.

**Inferred.** Container deployment and trigger deployment occur after the Worker upload, and the versions path activates the version before those later operations. A later failure can therefore return a failed command after the active Worker has changed. The deploy function has no compensating deployment or automatic trigger restoration in this boundary.

### 6. Rollback

**Documented.** Wrangler rollback selects an explicit version or the newest previous deployment containing a version at 100% traffic, then creates a new deployment sending 100% traffic to it.

**Documented.** Rollback leaves local development state and bound resources such as Durable Objects, D1, R2, and KV unchanged. Secret changes can block rollback until the user confirms an override.

**Boundary decision.** Resource rollback semantics belong to the hosted platform contract. Keep them in the lifecycle map and outside a Workers SDK defect campaign unless the CLI misstates or mishandles that contract.

### 7. Cleanup and error propagation

**Documented.** Wrangler config diagnostics become `UserError`; API errors remain separately reportable. Vite config checks commonly throw generic `Error`; Vitest pool option failures become `TypeError`; Miniflare validation becomes `MiniflareCoreError`.

**Documented.** Cleanup policies vary:

- `getPlatformProxy().dispose()` awaits the remote proxy session, then Miniflare, and propagates failure to its caller.
- Vite catches Miniflare disposal failures during server close and writes them only to debug output.
- The Vitest pool catches Miniflare and remote proxy disposal failures and writes them only to `NODE_DEBUG`.
- Wrangler deploy translates selected binding, secret, export-reconciliation, size, and startup failures, then rethrows remaining failures.

**Consequence, inferred.** Hidden cleanup failures can leave file locks, child processes, remote sessions, registry entries, or state directories that affect the next run while the original command still appears to have completed cleanly.

## Controlled comparison

Retained probe: `config-discovery-probe.mjs`

Run from the Fieldwork repository root:

```sh
node programmes/sdk-integration-lifecycle/scouts/workers-local-remote-lifecycle/config-discovery-probe.mjs
```

### Observations

| Scenario | Wrangler model | Vite model | Result |
| --- | --- | --- | --- |
| Same root contains `wrangler.json` and `wrangler.jsonc` | `wrangler.json` | `wrangler.jsonc` | Divergence observed |
| Vite root is nested below a parent `wrangler.jsonc` | Parent config | No config | Divergence observed |
| Same root contains only `wrangler.toml` | `wrangler.toml` | `wrangler.toml` | Control agrees |

The probe models only the source-pinned discovery functions. It avoids package installation and hosted credentials. A campaign trial should add real package calls at the same revision to confirm the adapter output end to end.

## Ranked campaign candidates

### 1. Align or diagnose Wrangler and Vite config discovery

**Rank:** 1  
**Evidence:** Observed mechanism; documented source paths  
**Owning packages:** `@cloudflare/workers-utils`, `@cloudflare/vite-plugin`  
**Campaign value:** High confidence, small reproduction, broad downstream effect

**Question.** Can Wrangler and Vite select different effective Worker configurations from the same checkout without a decisive diagnostic?

**Reproduction strategy.** Build two fixtures:

1. one root containing `wrangler.json` and `wrangler.jsonc` with distinct names, main files, and plain-text bindings;
2. a nested Vite application with a parent Wrangler config and no config in the Vite root.

Run the Vite config resolver and Wrangler `unstable_readConfig()` or a dry-run build. Record selected path, Worker name, main, bindings, and compatibility date. Add an explicit `configPath` control.

**Likely campaign outcomes.** A shared discovery helper, matching precedence, or an explicit multi-config diagnostic would each eliminate silent divergence. Maintainer intent is required before selecting a remedy.

**Candidate Stensibly trial.** On an isolated branch or disposable fixture, place a Worker Vite root under a parent directory and give parent and root configs distinct sentinel bindings. Compare the binding observed through Vite local execution with Wrangler dry-run deployment metadata. Confirm Stensibly’s actual repository layout before making any integration claim. The trial has not begun, so no `testbed:*` label was added.

### 2. Expose partial deployment when post-upload work fails

**Rank:** 2  
**Evidence:** Documented operation order; operational consequence inferred  
**Owning packages:** `@cloudflare/deploy-helpers`, Wrangler trigger and container integration  
**Campaign value:** High consequence; bounded mocked-API reproduction available

**Question.** When version activation succeeds and a later container or trigger operation fails, does Wrangler clearly report the resulting partial state and recovery action?

**Reproduction strategy.** Use the existing deploy unit-test harness and mocked APIs:

1. return success for version upload and 100% deployment;
2. inject failure in container deployment or `triggersDeploy()`;
3. assert the command exits with failure;
4. capture whether output states that the Worker version changed;
5. verify the mocked active deployment remains changed and no compensating call occurs.

Keep container and trigger cases separate because their recovery actions differ.

### 3. Surface local-runtime teardown failures consistently

**Rank:** 3  
**Evidence:** Documented suppression in Vite and Vitest; downstream residue inferred  
**Owning packages:** `@cloudflare/vite-plugin`, `@cloudflare/vitest-pool-workers`, Miniflare caller contract  
**Campaign value:** Moderate consequence; deterministic fault injection

**Question.** Should disposal failures remain debug-only when they can affect the next local or test run?

**Reproduction strategy.** Inject rejecting `disposeMiniflare()` and remote-session disposal functions into Vite server close and Vitest pool stop tests. Assert visible diagnostics, exit/result preservation, and cleanup ordering. A useful result preserves the primary test failure while attaching teardown diagnostics.

Existing upstream reports already cover individual watch-mode and filesystem symptoms. This campaign should test the shared adapter policy and avoid duplicating those reports.

### 4. Define the Vitest-to-deployed compatibility delta

**Rank:** 4  
**Evidence:** Documented test-runner mutations; deployed consequence inferred  
**Owning packages:** `@cloudflare/vitest-pool-workers`, Wrangler bundling and deploy configuration  
**Campaign value:** Moderate; needs a carefully selected capability matrix

**Question.** Which runtime capabilities can pass in the Workers Vitest pool solely because the pool injects flags, modules, or request-lifetime exceptions absent from deployment?

**Reproduction strategy.** Generate a small matrix around:

- `nodejs_compat_v2` and one injected Node feature;
- cross-request promise resolution;
- renamed Worker self-bindings;
- injected `node:console` or `node:vm` modules.

For each row, compare declared config, Vitest worker options, Wrangler deployment metadata, and a local Miniflare instance built directly from Wrangler options. Promote only rows where the difference survives bundling and has a clear user-facing consequence.

Node module and watch-mode parity issues already have upstream history. Use those as regression context and avoid a duplicate issue.

## Negative results and stop decisions

- **Observed:** TOML-only same-root discovery agrees across the two modeled paths.
- **Documented:** Explicit `configPath` removes the discovery ambiguity.
- **Documented:** `getPlatformProxy()` offers explicit disposal and a shared default local-state location.
- **Documented:** Docker is checked before Worker mutation for locally built container images, preventing that specific disjoint state.
- **Documented:** Version upload can stage a version without changing traffic; use it when a workflow needs a separate activation step.
- **Documented:** Non-versioned settings and tag patch failures are intentionally reduced to warnings in selected paths.
- **Stopped:** Bound-resource rollback semantics are explicit hosted-platform behaviour.
- **Stopped:** Warning wording alone does not meet this lane’s threshold.
- **Stopped:** Existing upstream reports around Vitest Node-module transforms and watch-mode storage cleanup should not receive duplicate contact.

## Validation limits

The full Workers SDK test suite was not run. The connected upstream repository was read-only, and this scout avoided cloning, dependency installation, Cloudflare credentials, and hosted side effects. Evidence consists of exact-revision source tracing plus the dependency-free retained probe. Campaigns 2–4 remain source-supported hypotheses until their fault-injection tests run.

## Recommendation

Promote candidate 1 into a focused experiment first. It has a directly observed mismatch, a compact real-package confirmation path, and a clear owning boundary. Run candidate 2 in parallel when a worker can use Wrangler’s mocked deploy harness. Keep candidates 3 and 4 queued until the first two establish whether the programme needs a broader adapter-parity campaign.

## Source record

All source links below are pinned to the claimed revision and were retrieved on 2026-07-29.

- Workers SDK revision: https://redirect.github.com/cloudflare/workers-sdk/commit/69ef8228fd96b4df192195d93c33e56ae665500a
- Shared config discovery: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/workers-utils/src/config/config-helpers.ts
- Shared raw config loading: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/workers-utils/src/config/index.ts
- Wrangler config normalization: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/wrangler/src/config/index.ts
- Wrangler local binding conversion: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/wrangler/src/dev.ts
- Wrangler Miniflare integration: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/wrangler/src/api/integrations/platform/index.ts
- Miniflare runtime: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/miniflare/src/index.ts
- Vite config adapter: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/vite-plugin-cloudflare/src/workers-configs.ts
- Vite Miniflare options: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/vite-plugin-cloudflare/src/miniflare-options.ts
- Vite development cleanup: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/vite-plugin-cloudflare/src/plugins/dev.ts
- Vitest pool config: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/vitest-pool-workers/src/pool/config.ts
- Vitest runtime adapter: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/vitest-pool-workers/src/pool/index.ts
- Vitest worker lifecycle: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/vitest-pool-workers/src/pool/cloudflare-pool-worker.ts
- Deploy orchestration: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/deploy-helpers/src/deploy/deploy.ts
- Version upload: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/deploy-helpers/src/deploy/versions-upload.ts
- Rollback: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/wrangler/src/versions/rollback/index.ts
- Error classes: https://redirect.github.com/cloudflare/workers-sdk/blob/69ef8228fd96b4df192195d93c33e56ae665500a/packages/workers-utils/src/errors.ts
- Existing Node-module parity report: https://redirect.github.com/cloudflare/workers-sdk/issues/9719
- Existing watch-mode storage report: https://redirect.github.com/cloudflare/workers-sdk/issues/9913
