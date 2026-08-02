# Vite project environment process scope

Issue: `teamleaderleo/fieldwork#466`

State: `source-confirmed; model-executed; target-test-committed; target-result-pending`

Upstream contact authorized: `false`

## In simple words

The Cloudflare Vite plugin reads a project's Cloudflare environment values and copies them into the whole Node.js process. A later project can then inherit the earlier project's credentials and settings. Because Vite gives existing process values priority, the earlier value can override an explicitly different value in the later project's `.env` file.

## Exact source revisions

Workers SDK original source pin:

- repository revision: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`
- `packages/vite-plugin-cloudflare/src/plugin-config.ts` blob: `26051e682807f4e2ba0d0153db1a7a9299569b47`
- `packages/workers-auth/src/credentials.ts` blob: `70dc58b4c7512fb5b239cbc1496fdfb5e1712144`

Workers SDK public-head refresh:

- repository revision: `20470fa8b09761c50b5c2c1d6a5f2652b61bd271`
- the five-commit drift from the original pin does not touch Vite plugin config loading, Workers auth credential resolution, or the relevant test directory;
- the source finding remains current at the refreshed head.

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

## Demonstrated model

Run:

```sh
node fieldwork-experiments/vite-project-env-scope/vite-project-env-scope.mjs
```

Executed output:

```text
PASS: project A token overrides project B env file after process pollution
PASS: project B with no token inherits project A token
PASS: inherited global key/email outranks project B token
PASS: connection and mode values persist into a later project
PASS: explicit operation environments isolate owners and preserve host state
PASS: concurrent load/assign phases leave asynchronous owner A observing owner B global state
```

The model uses sentinel values only. It performs no authentication, network request, deployment, or secret access.

## Target-native reproduction carrier

Owned fork PR: `teamleaderleo/workers-sdk#14`

- branch: `fieldwork/466-vite-env-authority-repro`;
- exact base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- exact reproducer head: `16b0d5d8e8462bf9fb9c026a306c5fadd9747a83`;
- changed path: `packages/vite-plugin-cloudflare/src/__tests__/project-env-authority.spec.ts`;
- current state: target-native plugin regression committed; exact CI conclusion pending.

The test creates two temporary project roots with distinct sentinel API tokens, resolves them through the real `resolvePluginConfig()`, and requires the host `process.env` to remain at its exact pre-test credential state. Current source is expected to fail after project A because it assigns the project value globally.

This first target test proves host-process mutation. It does not yet invoke an authentication or network consumer.

## Strongest supported conclusion

The current source creates a deterministic cross-project authority leak in a shared Node.js process:

1. resolving project A adds matching project values to `process.env`;
2. resolving project B gives those existing process values priority over B's env files;
3. later Workers SDK consumers can read A's credential or configuration authority while operating for B.

The source and model establish the control-flow and precedence defect. The committed target test directly checks the host-process mutation but awaits its exact CI result. The evidence does not establish incidence in common CLI use or prove that every copied variable reaches a network request.

## Required target-native tests

1. Conclude the exact focused result on `teamleaderleo/workers-sdk#14`.
2. Assert B resolves B's value through a consumer-visible operation while the host process returns to its exact pre-test state.
3. Repeat with B omitting the value.
4. Repeat with global key/email precedence.
5. Cover config failure after env loading.
6. Cover overlapping A/B resolution.
7. Cover Hyperdrive connection-string and local-mode variables.
8. Run against Vite 6, 7, and 8.
9. Assert no sentinel credential appears in logs, errors, snapshots, or retained artifacts.

## Candidate design

Prefer an explicit immutable operation environment passed into Wrangler config, authentication, remote binding, registry, and deployment helpers.

A temporary `process.env` installation with exact restoration is only a compatibility fallback. It cannot support overlapping operations safely and may fail when asynchronous consumers outlive the temporary scope.

## Sensitive-handling boundary

The Linux Fieldwork `SECURITY_RECONVENE.md` rule was consulted because this finding concerns credentials. The work remains in the ordinary workflow: source is public, all tokens are obvious sentinels, directories are temporary, repository writes are owned, and no real secret, live target, authentication attempt, external request, deployment, destructive action, or persistence is involved.

Switch to a public-safe `RECONVENE` checkpoint and stop deepening the path if that boundary changes.

## Related boundaries

- `#187`: generated container-registry request authority
- `#186`: remote proxy-session identity
- `#190`: host fetch dispatcher authority
- `#183`: build/preview marker scope
- `#179`: logical Vite server ownership

This candidate owns project-loaded environment authority. It should remain separately testable even if those consumers later share one operation context.
