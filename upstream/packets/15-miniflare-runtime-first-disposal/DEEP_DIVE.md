# Deep dive — Miniflare runtime-first disposal

Date: `2026-08-01`

## Question

Can an awaited teardown hook prevent Miniflare from requesting termination of the workerd child it owns?

## Answer

Yes. Current control flow reaches `Runtime.dispose()` only after awaiting browser cleanup and proxy-client disposal. A rejection exits the `finally` block. An unresolved promise suspends it. Both paths leave the runtime termination step unstarted.

This establishes a sufficient lifecycle defect. It does not establish the frequency of the triggering conditions or tie the mechanism to a specific public hang report.

## Exact current source

Base: [`cloudflare/workers-sdk@95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`](https://github.com/cloudflare/workers-sdk/commit/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d)

Primary source:

- [`packages/miniflare/src/index.ts`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/packages/miniflare/src/index.ts)
- [`packages/miniflare/src/runtime/index.ts`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/packages/miniflare/src/runtime/index.ts)
- [`packages/miniflare/AGENTS.md`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/packages/miniflare/AGENTS.md)
- [`packages/miniflare/package.json`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/packages/miniflare/package.json)
- [`CONTRIBUTING.md`](https://github.com/cloudflare/workers-sdk/blob/95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d/CONTRIBUTING.md)

## Disposal sequence

`Miniflare.dispose()` currently:

1. aborts its disposal controller;
2. poisons existing proxy references synchronously;
3. waits for initialization and runtime-mutex drainage;
4. enters the cleanup `finally` block;
5. awaits browser-process cleanup;
6. removes the exit hook;
7. awaits proxy-client disposal;
8. awaits runtime disposal;
9. closes runtime and dev-registry dispatchers;
10. stops the loopback server;
11. closes WebSocket resources;
12. schedules best-effort temporary-directory cleanup and removes email-session state;
13. disposes inspector, dev-registry, and Hyperdrive controllers;
14. removes the instance from the registry.

The `finally` block guarantees entry into cleanup after readiness failure. It does not guarantee execution of statements after an awaited rejection or unresolved promise.

## Runtime ownership boundary

At the current revision, `Runtime.dispose()` performs its ownership actions before returning:

1. reads and clears the current child-process reference;
2. destroys stdin, stdout, stderr, and the control pipe;
3. sends `SIGKILL` to the workerd process;
4. returns the recorded process-exit promise.

That distinction permits a narrow repair: call `Runtime.dispose()` before awaiting independent hooks, retain its returned promise, then preserve the existing await order for completion and error propagation.

## Failure sequences

### Rejected pre-runtime hook

```text
Miniflare.dispose()
  -> await ProxyClient.dispose()
      -> rejects
  -> exits finally block
  -> Runtime.dispose() never called
  -> no SIGKILL request from this owner
```

### Pending pre-runtime hook

```text
Miniflare.dispose()
  -> await ProxyClient.dispose()
      -> remains pending
  -> Runtime.dispose() never begins
  -> workerd remains owned by a suspended disposal
```

### Later rejection control

```text
Miniflare.dispose()
  -> Runtime.dispose()
      -> sends SIGKILL
  -> await DevRegistry.dispose()
      -> rejects
  -> runtime ownership was already discharged
```

## Selected candidate behavior

The candidate starts `Runtime.dispose()` immediately after the exit hook is removed, stores its promise, attaches a rejection observer, then awaits browser and proxy cleanup before awaiting the runtime-exit promise.

The intended properties are:

- the workerd kill request begins before browser or proxy cleanup is awaited;
- the existing browser/proxy completion order is preserved;
- a proxy-cleanup rejection remains the observed rejection in the single-failure case;
- a runtime rejection does not become an unhandled rejection while an earlier hook is pending or rejects;
- later cleanup still begins only after the runtime-exit promise resolves under the ordinary successful path.

## Evidence classification

### Established from current source

- Browser cleanup and proxy-client disposal are awaited before runtime disposal.
- A rejection from an earlier await skips the runtime-disposal statement.
- A pending earlier await delays the runtime-disposal statement indefinitely.
- `Runtime.dispose()` sends the kill request synchronously before returning its promise.
- The pool-level catch around Miniflare disposal does not contain a fallback child kill.

### Established by prior executable models

The A001 work recorded passing controls for sequential cleanup, isolated cleanup, bounded pending cleanup, and post-runtime failures. Those models prove JavaScript control-flow properties and the selected repair direction.

### Prepared in target-native tests

The three unit tests create a real Miniflare runtime, inject failures through exported component prototypes, and observe the actual `ChildProcess.kill()` call for a workerd child.

### Unknown

- Whether `cloudflare/workers-sdk#14903` exercises this path.
- How frequently `ProxyClient.dispose()` rejects or remains pending in ordinary use.
- Whether starting runtime termination before browser cleanup disrupts an undocumented dependency.
- Whether the candidate satisfies current lint, formatting, type, and package tests.
- Error precedence when runtime disposal and an earlier hook both reject. That belongs to the separate aggregation unit.

## Public prior art

### Strongest symptom match

- [`cloudflare/workers-sdk#14903`](https://github.com/cloudflare/workers-sdk/issues/14903) reports passing parallel test files followed by a process hang with a live workerd child. Single-file runs exit and serial file execution works. The report has no clonable reproduction and no teardown error, so causal attribution remains open.

### Runtime termination behavior

- [`cloudflare/workers-sdk#12025`](https://github.com/cloudflare/workers-sdk/pull/12025), fixing [`#11675`](https://github.com/cloudflare/workers-sdk/issues/11675), made `Runtime.dispose()` destroy child streams and send `SIGKILL` before returning the exit promise. That implementation enables this unit's early-start approach.

### Earlier and adjacent cleanup fixes

- [`cloudflare/workers-sdk#13078`](https://github.com/cloudflare/workers-sdk/pull/13078), fixing [`#10511`](https://github.com/cloudflare/workers-sdk/issues/10511), made temporary-directory cleanup best-effort after runtime disposal. It demonstrates selective isolation of secondary cleanup failures.
- [`cloudflare/workers-sdk#14727`](https://github.com/cloudflare/workers-sdk/pull/14727) bounded Browser Rendering shutdown with graceful CDP close and process-tree termination. It reduces one pre-runtime pending risk while preserving the broader sequencing gap.
- [`cloudflare/workers-sdk#14180`](https://github.com/cloudflare/workers-sdk/issues/14180) describes a Durable Object teardown hang involving `blockConcurrencyWhile()`, console output, and rejection. It is a credible alternative runtime-side cause.
- [`cloudflare/workers-sdk#12764`](https://github.com/cloudflare/workers-sdk/issues/12764) covers visible `outputGateBroken` teardown noise. It supports nearby cleanup edge cases, not skipped host child termination.
- [`cloudflare/workers-sdk#11122`](https://github.com/cloudflare/workers-sdk/issues/11122) covers a direct Durable Object proxy call that never settles and prevents JavaScript timeout progress. It is a separate proxy/runtime behavior.

### Historical repository migration

- [`cloudflare/miniflare#392`](https://github.com/cloudflare/miniflare/pull/392) migrated Miniflare toward the open-source runtime and removed obsolete packages. Earlier records cited it as lifecycle history. Its reviewed diff does not directly establish the fine-grained runtime-first ownership rule in this unit, so this packet treats it only as migration context.

## Compatibility and review concerns

### Browser cleanup ordering

Browser Rendering now uses its own CDP connection and process-tree termination helper. Starting workerd termination first appears independent from closing external browser processes. A maintainer should confirm there is no expected workerd-mediated browser cleanup dependency.

### Error precedence

The candidate preserves the earlier browser/proxy rejection when that is the only failure. A simultaneous runtime failure may be observed only by the attached rejection handler when an earlier await exits first. Comprehensive retention and aggregation belong to another unit. This packet records that limitation openly.

### Repeated disposal

`Runtime.dispose()` clears the child reference before returning, making repeated calls idempotent at that owner boundary. The focused tests include cleanup fallback only to terminate a child on the unfixed baseline.

### Initialization failure

`#runtime` is constructed in the Miniflare constructor, while its child may remain absent after failed initialization. Early invocation therefore returns safely when no process exists. Preservation of the original initialization error across later cleanup failures remains outside this unit.

## Contribution-policy consequence

The Workers SDK contribution guide asks contributors to engage through an issue or discussion before a non-trivial change. The public issue draft in this packet is therefore the proposed next upstream-facing artifact. Public contact remains prohibited until explicit authorization is recorded.
