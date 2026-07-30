# Wrangler import-time proxy dispatcher ownership

State: `candidate-created`

Batch: `B20260730-001`

Canonical candidate: #190

Related authority candidates: #186, #187

Parent review hub: #88

Synthesis PR: #112

Workers SDK branch: `fieldwork/teardown-lifecycle-hardening`

Reviewed Workers SDK head: `8f8123f9e0c0d1e0f26ff1e843dc214f10e7af3a`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Finding

The Cloudflare Vite plugin imports the public `wrangler` package as a library. That package root resolves to the Wrangler CLI bundle.

When proxy environment variables are present, module evaluation installs an `EnvHttpProxyAgent` through Undici's process-global dispatcher and emits a Wrangler startup warning.

Importing the Vite plugin can therefore replace host-process fetch routing before any Vite server or Cloudflare operation begins.

## Source findings

- `wrangler` root export points to `wrangler-dist/cli.js`.
- Vite plugin modules import `* as wrangler from "wrangler"`.
- Wrangler's root source reads proxy/no-proxy environment during module evaluation.
- When proxy is present, it calls `setGlobalDispatcher(new EnvHttpProxyAgent(...))` at top level.
- The existing proxy-output test dynamically imports Wrangler with `HTTPS_PROXY` set and observes the warning before invoking `main()`.

Consequences:

- host custom dispatcher is replaced;
- unrelated host fetches use Wrangler's proxy agent;
- import has no restoration owner;
- embedded operations cannot choose independent routes;
- module caching freezes the first import-time proxy decision;
- import can emit CLI output before command configuration;
- custom TLS/direct-routing assumptions can be changed silently.

## Executed model

Executed:

```sh
node /tmp/vite-wrangler-import-proxy-dispatcher.mjs
```

Output:

```text
PASS: importing Wrangler can replace the host global dispatcher
PASS: a side-effect-free library import preserves host routing
PASS: CLI-owned dispatcher setup can restore the prior host dispatcher
PASS: operation dispatchers isolate concurrent host and Vite routes
```

Evidence class: `source-read` plus `model-executed`.

No real proxy, HTTP request, TLS configuration, Vite package test, or network call executed.

## Draft repair

`wrangler-cli-proxy-dispatcher-scope.patch` moves dispatcher installation into the Wrangler CLI command lifetime:

- capture prior host dispatcher;
- install CLI-owned EnvHttpProxyAgent;
- restore prior dispatcher after success/failure;
- close CLI-owned agent;
- keep library import side-effect-free.

Embedded Wrangler APIs still need explicit operation dispatchers/fetch contexts so proxy-env support is retained without global mutation. A Vite server-scoped restore is rejected as concurrency-unsafe.

## Required tests

1. Importing Wrangler with proxy env preserves a preinstalled host dispatcher.
2. Importing the Vite plugin preserves host routing and emits no proxy warning.
3. Wrangler CLI uses proxy routing for the command lifetime.
4. CLI success/failure restore the exact prior dispatcher and preserve errors.
5. Long-running dev retains proxy until final close.
6. Concurrent embedded operations use distinct explicit dispatchers without affecting host fetch.
7. Vite remote binding, tunnel, config/API, and registry credential paths retain explicit proxy support.
8. No-proxy defaults and proxy-output JSON behavior remain compatible.
9. Module caching and changed proxy environment are characterized.

## Coordination placement

- #190 is canonical for host fetch-routing ownership.
- #186 owns authenticated remote sessions.
- #187 owns account/token registry authority.
- #88 remains the batch hub.
- #112 retains synthesis and notes.
- #87 and PR #105 own generated coordination.

## Boundary

This candidate concerns import-time host-process network mutation. It remains separate from server lifecycle and account/session authority even when those requests later consume explicit operation dispatchers.

No upstream interaction occurred.
