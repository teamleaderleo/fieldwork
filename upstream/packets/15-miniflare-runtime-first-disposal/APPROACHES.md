# Approaches — Miniflare runtime-first disposal

## Decision

Select the narrow early-start approach:

1. remove the exit hook;
2. invoke `Runtime.dispose()` immediately and retain its promise;
3. attach a rejection observer to that promise;
4. await browser cleanup;
5. await proxy-client cleanup;
6. await the retained runtime-exit promise;
7. continue the existing later cleanup sequence.

This changes when runtime ownership discharge begins while preserving the surrounding completion order.

## Approach A — Early-start runtime disposal

### Sketch

```ts
let runtimeDisposePromise: Promise<void>;
try {
	runtimeDisposePromise = Promise.resolve(this.#runtime?.dispose());
} catch (error) {
	runtimeDisposePromise = Promise.reject(error);
}
void runtimeDisposePromise.catch(() => {});

await this.#closeBrowserProcesses();
await this.#proxyClient?.dispose();
await runtimeDisposePromise;
```

### Advantages

- repairs the precise skipped/pending ownership path;
- uses current `Runtime.dispose()` semantics, where the kill request happens synchronously;
- keeps the external API unchanged;
- keeps the candidate to one production source location;
- permits direct target-native controls through prototype injection and child-process observation;
- leaves broad cleanup policy for separate review.

### Costs and limits

- simultaneous runtime and earlier-hook failures still lack complete aggregation;
- the attached rejection observer prevents transient unhandled rejection reporting and may leave the runtime failure secondary when another hook fails first;
- browser-before-runtime completion ordering becomes runtime-start-before-browser, which deserves maintainer confirmation.

### Status

Selected for unit 15.

## Approach B — Await runtime disposal before every other hook

### Sketch

```ts
await this.#runtime?.dispose();
await this.#closeBrowserProcesses();
await this.#proxyClient?.dispose();
```

### Advantages

- very easy to read;
- guarantees runtime exit before later cleanup begins.

### Costs

- changes the established completion ordering more aggressively;
- a slow child exit delays browser and proxy cleanup even though the termination request itself was already sufficient for ownership discharge;
- a runtime rejection prevents browser and proxy cleanup;
- preserves the same sequential interruption problem at a new first step.

### Status

Rejected for this unit.

## Approach C — Phase-wide `Promise.allSettled()` with error aggregation

### Sketch

```ts
const results = await Promise.allSettled([
	this.#runtime?.dispose(),
	this.#closeBrowserProcesses(),
	this.#proxyClient?.dispose(),
]);
throwCombinedCleanupError(results);
```

### Advantages

- attempts all phase members;
- can retain every failure;
- removes ordering dependencies within a declared phase.

### Costs

- requires an explicit phase model and error-precedence contract;
- can alter browser/proxy/runtime interactions simultaneously;
- expands source and test scope;
- overlaps the separate teardown-error-visibility work;
- raises compatibility questions beyond the unit assignment.

### Status

Valuable follow-on. Excluded from unit 15.

## Approach D — Bound each pre-runtime hook with a deadline

### Sketch

```ts
await withDeadline(this.#closeBrowserProcesses(), browserDeadline);
await withDeadline(this.#proxyClient?.dispose(), proxyDeadline);
await this.#runtime?.dispose();
```

### Advantages

- converts indefinite pending hooks into bounded failures;
- can improve total teardown latency.

### Costs

- a quick rejection still skips runtime disposal;
- deadlines require policy choices, cancellation semantics, diagnostics, and platform tuning;
- timed-out operations may continue in the background;
- broader than the ownership invariant.

### Status

Rejected as the primary repair. Suitable for separate phase-specific hardening.

## Approach E — Catch and continue around each hook

### Sketch

```ts
let firstError;
try {
	await this.#closeBrowserProcesses();
} catch (error) {
	firstError ??= error;
}
try {
	await this.#proxyClient?.dispose();
} catch (error) {
	firstError ??= error;
}
await this.#runtime?.dispose();
if (firstError) throw firstError;
```

### Advantages

- guarantees later statements execute after rejected hooks;
- preserves one earlier error.

### Costs

- pending hooks still block runtime termination;
- error aggregation remains incomplete;
- introduces repeated error bookkeeping across the entire method if applied consistently.

### Status

Insufficient because the pending-hook case is part of the unit.

## Approach F — Add a pool-level fallback kill

### Sketch

Catch `Miniflare.dispose()` at the vitest-pool layer and terminate workerd through a separate handle.

### Advantages

- could protect one caller.

### Costs

- the pool does not own the private runtime child handle;
- duplicates ownership knowledge outside Miniflare;
- leaves other Miniflare callers exposed;
- weakens the single-owner cleanup contract.

### Status

Rejected.

## Approach G — Treat public hang reports as sufficient proof and patch directly

### Advantages

- quick narrative route.

### Costs

- current public reports lack a clonable reproduction for this exact mechanism;
- multiple runtime-side and proxy-side hang causes exist;
- overstates causal confidence;
- conflicts with the repository request for issue engagement on non-trivial work.

### Status

Rejected. The issue draft separates the source-proven invariant from the open symptom attribution.

## Prior-art interpretation

| Record | Use in this unit |
| --- | --- |
| `workers-sdk#12025` / `#11675` | Confirms `Runtime.dispose()` owns immediate child termination and stream closure. |
| `workers-sdk#13078` / `#10511` | Demonstrates selective isolation of secondary teardown cleanup. |
| `workers-sdk#14727` | Demonstrates bounded browser shutdown and narrows one pending-hook risk. |
| `workers-sdk#14903` | Strong symptom match; causal link remains unverified. |
| `workers-sdk#14180`, `#12764`, `#11122` | Alternative or adjacent teardown mechanisms. |
| `miniflare#392` | Historical migration context only. |
| Fieldwork A001 at `fa39841...` | Executable control-flow evidence and selected patch direction. |
| Legacy test fourth case | Separate error-aggregation unit; excluded. |

## Reversal conditions

Reconsider the selected approach when any of these emerge:

- browser cleanup requires a live workerd process;
- current `Runtime.dispose()` stops initiating the kill synchronously;
- target-native controls show the early-start invocation fails to request termination;
- maintainers prefer a phase-wide cleanup contract and accept the broader change;
- simultaneous-failure semantics require full aggregation in the same patch.
