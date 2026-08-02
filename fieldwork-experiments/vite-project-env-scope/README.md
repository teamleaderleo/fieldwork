# Vite project environment process scope

Issue: `teamleaderleo/fieldwork#466`

State: `source-confirmed; model-executed; current-head baseline committed; repair boundary mapped; execution classification pending`

Upstream contact authorized: `false`

## In simple words

The Cloudflare Vite plugin reads a project's Cloudflare environment values and copies them into the whole Node.js process. A later project can then inherit the earlier project's credentials and settings. Because Vite gives existing process values priority, the earlier value can override an explicitly different value in the later project's `.env` file.

The broad process mutation also supplies credentials to a later asynchronous remote-binding operation. That makes a simple deletion or temporary save/restore incomplete: config selection can be explicit, but remote-binding authentication must receive project authority through an operation-owned input.

## Exact source revisions

Workers SDK original source pin:

- repository revision: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`
- `packages/vite-plugin-cloudflare/src/plugin-config.ts` blob: `26051e682807f4e2ba0d0153db1a7a9299569b47`
- `packages/workers-auth/src/credentials.ts` blob: `70dc58b4c7512fb5b239cbc1496fdfb5e1712144`

Workers SDK public-head refresh:

- repository revision: `20470fa8b09761c50b5c2c1d6a5f2652b61bd271`
- the five-commit drift from the original pin does not touch Vite plugin config loading, Workers auth credential resolution, remote-binding auth construction, or the relevant test directory;
- the source finding remains current at the refreshed head.

Current additional source identities:

- `packages/vite-plugin-cloudflare/src/workers-configs.ts` blob: `77e2c4dc45781c245229b738c9aa68f25cb2ab4d`
- `packages/workers-utils/src/config/index.ts` blob: `21f8278d4348701acc11bd6b9d0246d11e29b298`
- `packages/workers-utils/src/config/config-helpers.ts` blob: `e93f34f43f9fe0e5b58a035117d6dc7886c6ea14`
- `packages/workers-utils/src/config/validation.ts` blob: `f112f31cd6818265a1c81ca01c2856b99b555fde`
- `packages/vite-plugin-cloudflare/src/miniflare-options.ts` blob: `46ceb863a6fd482886fec1df0df0f927c152d537`
- `packages/remote-bindings/src/maybe-start-or-update-session.ts` blob: `a06232f49267e118b9e82f95f6e48f7fb8592cdd`
- `packages/remote-bindings/src/auth.ts` blob: `8e0cb85538901f55a7980869fadbd7c5edda9d41`

Vite load precedence:

- Vite `v6.1.0`, `packages/vite/src/node/env.ts` blob: `897524612f3c7d00d8b9d60b90db4fbc23229504`
- Vite `v7.1.12`, blob: `31ffc60be05b4bd5f556a91b0320443b9a3d3650`
- Vite `v8.1.5`, blob: `49c99b3f734dff73a8c59e567e056eb8eff4e682`

## Current source path

`resolvePluginConfig()` calls:

```ts
const prefixedEnv = vite.loadEnv(viteEnv.mode, root, [
  "CLOUDFLARE_",
  "WRANGLER_HYPERDRIVE_LOCAL_CONNECTION_STRING_",
]);

Object.assign(process.env, prefixedEnv);
```

There is no matching restoration in the function's success, failure, preview, or close paths.

Vite 6, 7, and 8 load matching env-file values first, then overwrite the returned record with matching values already present in `process.env`.

Workers SDK authentication reads global key/email and API token values from environment variables before stored OAuth state.

## Deeper source trace

### Config selection does not require broad process mutation

The plugin already reads these project values directly from `prefixedEnv`:

- `CLOUDFLARE_ENV`;
- `CLOUDFLARE_VITE_WRANGLER_CONFIG_PATH`;
- `CLOUDFLARE_VITE_FORCE_LOCAL`.

`readWorkerConfigFromFile()` calls `wrangler.unstable_readConfig({ config, env })` with the resolved `cloudflareEnv` value. Wrangler's raw-config path discovery is filesystem-only. During normalization, the active environment is selected with:

```ts
const envName = args.env ?? getCloudflareEnv();
```

Because the Vite path already passes `args.env`, project environment selection does not require writing `CLOUDFLARE_ENV` into `process.env`. API token, global key/email, account ID, config path, force-local mode, and Hyperdrive connection strings are not required to parse the Wrangler file through this path.

### Later remote binding currently depends on global credentials

During dev option construction, the plugin calls `maybeStartOrUpdateRemoteProxySession(...)` with `auth` set to `undefined`. The remote-bindings package then builds its own auth owner and reads process-global authority, including:

- `CLOUDFLARE_CF_AUTH` selection;
- API token or global key/email through Workers auth;
- profile state resolved from the project directory.

This async operation can run after `resolvePluginConfig()` returns and can overlap another project. Therefore:

- deleting `Object.assign()` without another auth path can break project `.env` credentials for remote bindings;
- installing values in `process.env` only around config resolution does not cover the later consumer;
- keeping them installed until server close preserves the cross-project leak;
- save-and-restore in `finally` is not concurrency-safe.

## Demonstrated model

Run:

```sh
node fieldwork-experiments/vite-project-env-scope/vite-project-env-scope.mjs
```

Executed output at model commit `18ddee7d7c5f64ff142482f138b36cf56a6fcdc6`:

```text
PASS: project A token overrides project B env file after process pollution
PASS: project B with no token inherits project A token
PASS: inherited global key/email outranks project B token
PASS: connection and mode values persist into a later project
PASS: explicit operation environments isolate owners and preserve host state
PASS: explicit config environment selects each project without process mutation
PASS: remote-binding auth hooks retain project credentials across overlap
PASS: concurrent load/assign phases leave asynchronous owner A observing owner B global state
```

The model uses sentinel values only. It performs no authentication, network request, deployment, or secret access.

## Current-head target-native baseline carrier

Owned fork PR: `teamleaderleo/workers-sdk#9`

- branch: `fieldwork/466-vite-env-current-baseline`;
- exact base: `20470fa8b09761c50b5c2c1d6a5f2652b61bd271`;
- exact head: `8a90f59cbe4760065b222de8d43835a6f1343bc8`;
- changed path: `packages/vite-plugin-cloudflare/src/__tests__/project-env-authority.spec.ts`;
- current state: current-head characterization committed; repository workflows require classification.

The baseline resolves two temporary Vite projects in one process and records both forms of crossover:

1. project A's sentinel token overrides project B's distinct `.env` token through existing-process precedence;
2. project B with no token inherits project A's token.

The test restores the exact original host token state and removes all temporary roots.

Older-base PR `teamleaderleo/workers-sdk#14` and duplicate-base PR `#15` are closed as superseded. Neither is an admissible current-head receipt.

## Strongest supported conclusion

The current source creates a deterministic cross-project authority leak in a shared Node.js process:

1. resolving project A adds matching project values to `process.env`;
2. resolving project B gives those existing process values priority over B's env files;
3. later Workers SDK consumers can read A's credential or configuration authority while operating for B.

The source and model establish the control-flow and precedence defect. The current-head target baseline directly records A-to-B inheritance through real `resolvePluginConfig()`. The evidence does not establish incidence in common CLI use or prove that every copied variable reaches a network request.

## Selected repair boundary

### 1. Retain one immutable project environment

Keep the record returned by Vite's `loadEnv()` as project-owned operation input. Existing host variables retain Vite's documented precedence inside that record, but the record is not copied back into the host process.

### 2. Pass config-only values explicitly

Continue passing `CLOUDFLARE_ENV` to Wrangler's `env` argument. Resolve config path, force-local mode, and other plugin options directly from the operation record, as current code already does.

### 3. Give remote bindings an explicit auth hook

Construct an `AsyncHook<CfAccount>` that closes over the project operation environment and profile directory, then pass it to `maybeStartOrUpdateRemoteProxySession()` instead of `undefined`.

The hook must preserve the existing credential precedence and auth-family selection without mutating `process.env`. Its returned account/token pair belongs to that project operation even if another Vite server starts or finishes concurrently.

### 4. Pass other project values to their owners

Hyperdrive local connection strings, API base/environment, compliance mode, local/remote switches, and any future project-prefixed value should be passed to the exact consumer that owns it. Do not recreate one broad process-global compatibility bag.

### 5. Keep remote-session identity stable

`maybeStartOrUpdateRemoteProxySession()` compares the supplied auth hook with the previous session's hook and restarts when it changes. A newly allocated function on every config refresh can therefore cause unnecessary session replacement even when project authority is unchanged.

The target prototype needs one stable auth generation or memoized hook per project environment generation. A real credential or secret-derived hash must not be persisted merely to create that identity. Session restart on a genuine authority change remains desirable and is also part of issue #186's session-ownership boundary.

## Rejected repair shapes

- Delete only `Object.assign()`: can remove the credentials currently used by remote bindings.
- Save and restore the entire environment around `resolvePluginConfig()`: later async consumers outlive the scope.
- Hold project values globally until Vite close: preserves sequential and concurrent cross-project leakage.
- Serialize every Vite project in one process: hides the race while retaining stale global authority and breaks legitimate embedding.
- Persist raw or hashed project credentials to identify the operation: unnecessary secret-derived state.

## Required target-native tests

1. Classify exact workflows and run the focused package command for `teamleaderleo/workers-sdk#9`.
2. Assert B resolves B's value through a consumer-visible operation while the host process returns to its exact pre-test state.
3. Repeat with global key/email precedence and `CLOUDFLARE_CF_AUTH` selection.
4. Cover config failure after env loading.
5. Cover overlapping A/B resolution and out-of-order close.
6. Cover remote binding startup where A and B use different sentinel auth hooks and complete in reverse order.
7. Cover same-project refresh without unnecessary session restart and changed-authority refresh with required session replacement.
8. Cover Hyperdrive connection-string and local-mode variables through explicit consumers.
9. Run against Vite 6, 7, and 8.
10. Assert no sentinel credential appears in logs, errors, snapshots, or retained artifacts.

## Sensitive-handling boundary

The Linux Fieldwork `SECURITY_RECONVENE.md` rule was consulted because this finding concerns credentials. The work remains in the ordinary workflow: source is public, all tokens are obvious sentinels, directories are temporary, repository writes are owned, and no real secret, live target, authentication attempt, external request, deployment, destructive action, or persistence is involved.

Switch to a public-safe `RECONVENE` checkpoint and stop deepening the path if that boundary changes.

## Related boundaries

- `#187`: generated container-registry request authority
- `#186`: remote proxy-session identity and restart ownership
- `#190`: host fetch dispatcher authority
- `#183`: build/preview marker scope
- `#179`: logical Vite server ownership

This candidate owns project-loaded environment authority and the transfer of that authority into explicit operation inputs. It should remain separately testable even if those consumers later share one operation context.
