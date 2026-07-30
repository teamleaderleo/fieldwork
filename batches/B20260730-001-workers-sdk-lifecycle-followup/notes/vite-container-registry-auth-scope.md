# Vite container registry authentication-scope follow-up

State: `investigating — client boundary revised; mocked request execution required`

Batch: `B20260730-001`

Canonical candidate: #187

Related candidates: #165, #179

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `e92165ac96cd0648a2c824920e7605128a82afb4`

Independent reviews: comments `5125221394`, `5125225141`

Revision receipt: comment `5125330316`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

Container registry credential generation uses one generated `OpenAPI` configuration singleton. The Cloudflare Vite plugin mutates that singleton with an account URL and bearer token before asynchronous image preparation.

Concurrent Vite servers can overwrite each other's account/token. A later external-only server can inherit an earlier server's credentials even though it never configures the client.

The per-operation authority invariant is accepted. Independent review rejected the first client sketch because it still spread mutable global OpenAPI state and retained a silent fallback to the global generated service.

## Source findings

`configureOpenAPIForContainerPull(accountId, apiToken)` writes the generated client's account-specific base URL and Authorization header.

`ImageRegistriesService.generateImageRegistryCredentials()` passes that singleton into the generated request helper.

`prepareContainerImagesForDev()` later processes images asynchronously. Every pulled image, including external registries, first calls `dockerLoginImageRegistry()`, which requests configured credentials from Cloudflare.

Vite configures the singleton only when at least one image is Cloudflare-managed.

Consequences:

- server A account/token can remain active for later external-only server B;
- concurrent A can make its request after B overwrites the singleton, using B's endpoint/token;
- restoring in `finally` cannot isolate concurrent operations;
- without prior contamination, external-only lookup starts from empty generated-client defaults and falls into warning/public-pull fallback.

## Review correction

The first draft used `...OpenAPI`, which could inherit:

- `TOKEN`;
- `USERNAME` and `PASSWORD`;
- global headers;
- global logger;
- credential mode;
- path encoder.

The generated request helper can apply inherited token or Basic authentication after custom headers, replacing the intended operation bearer token.

The first draft also kept `ImageRegistriesService` as a default parameter, allowing missed callers to silently re-enter the global service.

## Revised client boundary

The current artifact:

- builds a fresh `OpenAPIConfig` from explicit constants and operation inputs;
- explicitly sets base URL, version, credential mode, Authorization header, path encoder, and operation logger;
- explicitly clears token, username, and password fields;
- makes the operation client mandatory for Cloudflare credential lookup;
- keeps any temporary legacy global path separately named rather than a default;
- makes external-only no-client work perform zero Cloudflare API requests before warning/public-pull fallback;
- fails managed-image work without exact account/token before preparation.

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
PASS: a closed client inherits no global token, Basic auth, headers, encoder, or logger
PASS: later global mutation cannot affect an in-flight operation client
PASS: concurrent operation clients isolate endpoint, token, and logger
PASS: operation diagnostics redact Authorization
PASS: Cloudflare credential lookup cannot silently fall back to a global service
PASS: external-only no-client work performs no credential request
```

Evidence class: `source-read` plus `model-executed`.

No real account, API token, registry request, Docker login, image pull, Vite package test, or network call executed.

## Remaining execution controls

1. Contaminate every global auth/logger field and capture actual generated request config.
2. Run account A and B requests concurrently and capture exact endpoint/header/logger at dispatch.
3. Prove omission of an operation client cannot compile or silently select the global service.
4. Prove external-only work after contaminated state performs zero Cloudflare API calls.
5. Prove managed-image work without exact account/token fails before preparation.
6. Prove logger sanitization removes Authorization from errors and logs.
7. Prove custom API base and path encoding remain operation-scoped.
8. Assert secrets are absent from errors, logs, snapshots, and retained artifacts.
9. Retain or explicitly migrate existing Wrangler/container CLI behavior.

## Coordination placement

- #187 is canonical for container registry credential authority.
- #165 owns container cleanup.
- #179 owns logical runtime/tunnel state.
- #88 remains the parent hub.
- #112 retains synthesis and notes.
- #87 and PR #105 own generated coordination.

## Boundary

This candidate remains `state:investigating`. The authority invariant and revised client direction are strong, but generated-request package execution is still required before promotion.

No upstream interaction occurred.
