# Workers SDK Browser Rendering timeout experiments

Status: active investigation

Coordination: issue #907

Target: `cloudflare/workers-sdk`, Miniflare Browser Rendering

Pinned source revision: `49f73de207124171b3f8e9ffb182facb48727388`

No upstream writes are part of this experiment. Third-party GitHub references use redirect.GitHub.

## Trigger

The Browser Rendering test `it creates a browser session` failed on Windows four times in the `packages-and-tools` job for [workers-sdk PR #15143](https://redirect.github.com/cloudflare/workers-sdk/pull/15143) with the generic message `Test timed out in 20000ms`. The same revision later passed the same Windows job on the owned fork.

The investigation separates two ownership gaps:

- Candidate A: the test owns a bounded acquisition deadline and a larger outer watchdog so the inner cause can surface.
- Candidate B: BrowserSession owns a bounded persistent DevTools connection attempt and acquisition handles registration failure explicitly.

These remain separate candidates.

## Historical negative control

[workers-sdk PR #14708](https://redirect.github.com/cloudflare/workers-sdk/pull/14708) tried broader timeout/retry changes: browser test timeout 20s -> 120s, a longer Windows readiness window, and broader transient retry matching. It closed unmerged after the author reported that it did not help much. This is evidence against another blanket timeout increase.

## Candidate A

Clean owned-fork branch: `fieldwork/browser-session-timeout-current`

Commit: `d93625eed59148442a96ca0925d1e62269753ac7`

Shape:

- suite-level 20s timeout unchanged;
- only `it creates a browser session` gets a 60s acquisition deadline and 75s outer timeout;
- acquisition uses `AbortSignal.timeout()` around `mf.dispatchFetch()`;
- named error: `Browser session acquisition timed out after 60000ms`;
- target retry condition uses named Chrome readiness/acquisition failures rather than generic `Test timed out`.

Exact-diff Windows validation: run `31891360605`, job `95027999575`. The normal path passed, and a deterministic 65s browser-launch stall produced the named 60s acquisition timeout before the 75s outer watchdog.

Earlier warm focused samples were about 1.6-1.9s of test-body acquisition and 7.67-7.92s command wall time. Browser installation/setup is a separate slower phase.

## Candidate B discovery history

### v1

A first product-side prototype added per-attempt timeouts to `fetchWithConnectRetry()`. Normal Browser Rendering tests passed. Under a deterministic stalled connection, acquisition still appeared successful because `BrowserRenderingRouter.#acquireSession()` ignored the `/session-info` response status.

Finding: bounding the inner connect alone is insufficient if the acquisition owner discards registration failure.

### v2

Owned-fork branch: `fieldwork/browser-connect-timeout-proof-v2`

Normal typecheck/build/full Browser Rendering spec passed. Under deterministic connect stall, the target test failed after retry-scale elapsed time, but Vitest showed only `expected false to be true`.

Finding: the test worker reads the binding response body and creates a new default-200 response, then the test only checks whether the text contains `sessionId`. That assertion masks useful registration/connect attribution.

### v3 source review before proof

The v2 candidate was too broad. `fetchWithConnectRetry()` is also used by DevTools JSON proxy operations, including side-effecting `PUT /json/new`. Making timeout retries the helper default could replay a timed-out side-effecting operation.

The candidate was narrowed so `perAttemptTimeoutMs` is opt-in and only BrowserSession's persistent Chrome DevTools health WebSocket opts into the deadline.

A second lifecycle invariant emerged: `/browser/launch` registers a Chrome process before BrowserSession registration. If registration fails, acquisition must release that ownership through the module-level browser close path.

The surviving-state oracle is `/browser/status`: 410 means the session is no longer registered. This proves registry ownership release. It does **not** prove OS-process termination, because the existing `/browser/close` path removes the registry entry before process close and suppresses process-close errors.

### v3 core proof

Owned-fork branch: `fieldwork/browser-connect-timeout-proof-v3`

Invalid harness attempt: run `31893035391`, job `95032053906`. The injection script had an escaping error and failed before candidate source was exercised.

Successful repaired run: `31893274327`, job `95032621710`, Windows Server 2025 / Vitest 4.1.0.

Observed:

- candidate typecheck/build passed;
- full Browser Rendering spec passed: 20 passed, 1 skipped;
- deterministic stalled persistent DevTools connect made exactly 5 attempts;
- final named error was `Chrome DevTools connection attempt timed out after 2000ms (attempt 5/5)`;
- acquisition-level `Failed to establish Chrome DevTools connection for browser session ...` attribution survived;
- focused stalled test body completed in 11.436s, before the 20s Vitest watchdog;
- `/browser/status` returned 410 after failed registration;
- injected non-retryable connect failure made exactly 1 attempt and also released registry ownership;
- a BrowserSession-local cancellation injection won over the per-attempt timeout on the first attempt and released registry ownership.

This proves the timeout/retry/attribution mechanics and the existing registry-release contract. It does not prove end-to-end user-worker signal propagation.

## Caller-cancellation boundary

workerd's request-signal passthrough tests explicitly enable `enable_request_signal`, `request_signal_passthrough`, and `enable_abortsignal_rpc`. The Miniflare Browser Rendering internal service uses compatibility date `2025-05-01` with `nodejs_compat` and does not explicitly enable those request-signal flags. `enable_request_signal` has no default activation date in the inspected workerd compatibility source.

Three attempted end-to-end caller-abort probes were invalid harnesses rather than product evidence:

- run `31893720300`, job `95033700813`: faulted build ran without the dependency-build prerequisite;
- run `31893851018`, job `95034015132`: typecheck was placed after synthetic fault injection;
- run `31893967509`, job `95034289131`: healthy candidate typecheck/build and a 7.5s warm browser acquisition passed, but the generated inline test-worker template had an escaping error before the cancellation assertion ran.

Because current Browser Rendering does not opt into the relevant request-signal compatibility features, route-level caller-signal propagation is excluded from the clean Candidate B. It is a separate compatibility/runtime question unless later evidence makes it necessary.

## Clean Candidate B

Owned-fork branch: `fieldwork/browser-connect-timeout-current`

Commit: `9d9f32771622eb72a61173321efde4d1f28ba88a`

Parent: exact pinned source revision `49f73de207124171b3f8e9ffb182facb48727388`.

Current diff: one production file, `packages/miniflare/src/workers/browser-rendering/binding.worker.ts`; 85 additions, 14 deletions.

Shape:

- adds a 2s per-attempt timeout option to `fetchWithConnectRetry()`;
- preserves any signal already supplied to the helper, but adds no route-level signal plumbing;
- timeout is opt-in only for BrowserSession's persistent DevTools health WebSocket;
- timed-out connection attempts remain retryable; unrelated non-retryable failures are not broadened;
- failed persistent connection clears BrowserSession state and rethrows;
- acquisition checks `/session-info` status/body instead of discarding it;
- failed registration calls the existing module-level `/browser/close` path to release the launched browser's registry ownership;
- the registration failure remains the primary error if the cleanup fetch itself throws.

Exact-clean Windows validation is running as `31894196383` from `fieldwork/browser-connect-timeout-final-validation`.

## Budget and interpretation

Five 2s connect attempts plus current backoff are roughly 10.4s before cleanup. `closeBrowserProcess()` itself allows up to 5s graceful close and then up to 5s after force-kill. A pathological failed-registration path can therefore approach or exceed the existing 20s test watchdog.

This is why Candidate B does not replace Candidate A. A owns test timeout attribution/budget. B bounds and attributes the product-side persistent DevTools connection and handles failed registration coherently.

## Current recommendation

Keep A and B as separate review units. A is the smaller first proposal and directly fixes test timeout ownership. B is a product hardening follow-up backed by deterministic connection-stall and negative-control evidence, provided the exact clean commit passes its final Windows validation.

Do not bundle caller-signal compatibility changes into B. Do not claim registry status 410 proves Chrome process termination.