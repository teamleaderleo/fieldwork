# Vite container registry authentication-scope follow-up

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #187

Related candidates: #165, #179

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `f9f6e84fb64d72f5954325855c3846f7a069821b`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

Container registry credential generation uses one generated `OpenAPI` configuration singleton. The Cloudflare Vite plugin mutates that singleton with an account URL and bearer token before asynchronous image preparation.

Concurrent Vite servers can overwrite each other's account/token. A later external-only server can inherit an earlier server's credentials even though it never configures the client.

## Source findings

`configureOpenAPIForContainerPull(accountId, apiToken)` writes the generated client's account-specific base URL and Authorization header.

`ImageRegistriesService.generateImageRegistryCredentials()` passes that singleton into the generated request helper.

`prepareContainerImagesForDev()` later processes images asynchronously. Every pulled image, including external registries, first calls `dockerLoginImageRegistry()`, which requests configured credentials from Cloudflare.

Vite configures the singleton only when at least one image is Cloudflare-managed.

Consequences:

- server A account/token can remain active for later external-only server B;
- concurrent A can make its request after B overwrites the singleton, using B's endpoint/token;
- restoring in `finally` cannot isolate concurrent operations;
- without prior contamination, external-only lookup starts from empty generated-client defaults and falls into the existing warning/public-pull path.

## Executed model

Executed:

```sh
node /tmp/vite-container-registry-auth-scope.mjs
```

The executed content is identical to the committed Workers SDK artifact.

Output:

```text
PASS: external-only later work inherits prior account and token
PASS: concurrent configuration sends operation A through operation B identity
PASS: per-operation clients isolate account, token, and endpoint
PASS: absent per-operation credentials cannot fall back to stale global auth
```

Evidence class: `source-read` plus `model-executed`.

No real account, API token, registry request, Docker login, image pull, Vite package test, or network call executed.

## Draft repair

`container-registry-client-scope.patch` sketches an immutable per-operation credential client passed explicitly through image preparation and pull.

Desired behavior:

- Cloudflare-managed images require an operation client;
- external-only work without a client performs no Cloudflare API request and follows warning/fallback behavior;
- concurrent operations keep distinct account endpoints, tokens, custom API bases, and loggers;
- failed preparation leaves no shared credential state;
- token values never enter diagnostics or retained artifacts;
- existing static-client CLI callers migrate under explicit compatibility tests.

A try/finally restore of the singleton is rejected because it is not concurrency-safe.

## Required tests

1. Concurrent servers with different mocked account/token pairs use their own endpoint/header.
2. External-only B after account-A A does not send A's token/account URL.
3. Failed preparation leaves no credential state visible later.
4. External-only work without client makes no Cloudflare API request.
5. Managed image without account/token fails before preparation.
6. Mixed managed/external images intentionally share one operation client.
7. Logger and custom API base remain operation-scoped.
8. Tokens never appear in logs, errors, snapshots, or artifacts.
9. Dev and preview do not share merely because they run in one process.
10. Existing Wrangler/container CLI behavior is retained or explicitly migrated.

## Coordination placement

- #187 is canonical for container registry credential authority.
- #165 owns container cleanup.
- #179 owns logical runtime/tunnel state.
- #88 remains the parent hub.
- #112 retains synthesis and notes.
- #87 and PR #105 own generated coordination.

## Boundary

This candidate governs account and bearer-token authority and remains separate from lifecycle cleanup, though one logical Vite operation may hold the immutable client.

No upstream interaction occurred.
