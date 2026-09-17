# Source, history, and adjacent-component audit

## Scope and pins

Audit date: `2026-07-30`

- Supabase JS: [`63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5)
- Supabase SSR: [`69a6209482ddde7b1bd769f7c8ca9a604cb65960`](https://redirect.github.com/supabase/ssr/commit/69a6209482ddde7b1bd769f7c8ca9a604cb65960)
- Supabase Auth: [`163ab6faf15b3a4e578ce2f7f2e3f2725768dd05`](https://redirect.github.com/supabase/auth/commit/163ab6faf15b3a4e578ce2f7f2e3f2725768dd05)
- Owned experiment: [`teamleaderleo/supabase-js#1`](https://github.com/teamleaderleo/supabase-js/pull/1)
- Campaign: `#78`
- Parent scout: `#21`
- Upstream contact authorized: `false`

The three public repository heads above still matched the scout pins when this audit began.

## Claim-to-source table

| Claim | Primary source | Evidence class | Audit result |
| --- | --- | --- | --- |
| Auth-js saves the rotated session before notifying listeners and resolves `refreshingDeferred` afterward | [Pinned `GoTrueClient.ts`](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/src/GoTrueClient.ts) | Current source | Confirmed |
| Nested refresh from `TOKEN_REFRESHED` is a documented residual cycle | [Pinned `GoTrueClient.ts`](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/src/GoTrueClient.ts), [migration note](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/migrations/lockless-coordination.md) | Current source and maintained migration note | Confirmed |
| Listeners are invoked together, awaited, logged on failure, then the first listener error is thrown | [Pinned `GoTrueClient.ts`](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/src/GoTrueClient.ts) | Current source | Confirmed |
| SSR uses an async auth listener to persist cookie changes | [Pinned `createServerClient.ts`](https://redirect.github.com/supabase/ssr/blob/69a6209482ddde7b1bd769f7c8ca9a604cb65960/src/createServerClient.ts) | Current source | Confirmed |
| Timer deferral can let a server response finish before cookie persistence | [Issue #2037](https://redirect.github.com/supabase/supabase-js/issues/2037), [PR #2039](https://redirect.github.com/supabase/supabase-js/pull/2039) | Reproduced regression and merged revert | Confirmed |
| A global fire-and-forget listener change was rejected because it recreates the SSR cookie failure | [PR #2016 discussion](https://redirect.github.com/supabase/supabase-js/pull/2016) | Maintainer review and closed proposal | Confirmed |
| The accepted lockless design deliberately retained awaited listeners and documented one remaining refresh cycle | [PR #2392](https://redirect.github.com/supabase/supabase-js/pull/2392) | Merged design and migration note | Confirmed |
| Initialization uses dependency-first settlement while the initiating call still awaits listeners | [PR #2498](https://redirect.github.com/supabase/supabase-js/pull/2498) | Merged implementation and tests | Confirmed |
| Warning on every async listener creates false positives, including SSR | [PR #2477 discussion](https://redirect.github.com/supabase/supabase-js/pull/2477) | Maintainer closure explanation | Confirmed |
| The Auth service handles common lost-response and concurrent-refresh reuse cases | [Pinned token service](https://redirect.github.com/supabase/auth/blob/163ab6faf15b3a4e578ce2f7f2e3f2725768dd05/internal/tokens/service.go) | Current service source | Confirmed |
| Auth-js successful requests return parsed JSON rather than response headers | [Pinned auth fetch helper](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/src/lib/fetch.ts) | Current source | Confirmed; adjacent diagnostics candidate |

## History, with intention separated from later interpretation

### 1. Long-running reports

The archived auth-js issue [#762](https://redirect.github.com/supabase/auth-js/issues/762) collected reports of auth operations hanging when called from auth listeners.

Supabase JS issue [#1566](https://redirect.github.com/supabase/supabase-js/issues/1566) described a mobile OAuth flow where the stored session and later authenticated calls disagreed. The reporter observed fewer hangs after moving asynchronous listener work elsewhere. This is trigger evidence, rather than proof that timer deferral is a safe library rule.

### 2. One notification was deferred

[PR #2014](https://redirect.github.com/supabase/supabase-js/pull/2014) moved one OAuth notification into `setTimeout(..., 0)` to escape a lock cycle.

### 3. SSR exposed the missing completion contract

[Issue #2037](https://redirect.github.com/supabase/supabase-js/issues/2037) reported that OAuth callbacks could return before SSR cookie writes completed. [PR #2039](https://redirect.github.com/supabase/supabase-js/pull/2039) reverted the timer change.

Recovered intention: a listener can perform work required for the auth operation's externally visible completion.

### 4. Global fire-and-forget was considered and rejected

[PR #2016](https://redirect.github.com/supabase/supabase-js/pull/2016) proposed detached listeners across every auth event. A maintainer review explicitly required a solution that prevents cycles, keeps critical async cookie work awaited, and works in both serverless and long-running server runtimes.

Recovered intention: remove the circular dependency without detaching all observers.

### 5. Lockless coordination removed the broad mutex problem

[PR #2392](https://redirect.github.com/supabase/supabase-js/pull/2392) removed the default shared lock, retained per-client refresh single-flight, added commit guards, added `dispose()`, and kept listeners awaited. Its final documentation names nested refresh during `TOKEN_REFRESHED` as the residual cycle.

Recovered intention: the client owns local single-flight and commit safety; the Auth service owns cross-client token convergence; listeners remain part of operation timing.

### 6. Initialization established a close precedent

[PR #2498](https://redirect.github.com/supabase/supabase-js/pull/2498) fixed another promise cycle by letting `initializePromise` settle before queued listeners ran. `initialize()` still waited for those listeners before returning.

Recovered intention: an internal dependency and the public operation can have different settlement points.

### 7. Broad warnings were narrowed to the real operation

[PR #2477](https://redirect.github.com/supabase/supabase-js/pull/2477) proposed warning for every async callback. It was closed because async callbacks are supported and SSR itself uses one. The closure suggested handling the exact refresh reentry point instead.

Recovered intention: identify the hazardous operation, rather than the `async` keyword.

## Adjacent Supabase component checks

### Public Supabase client wrapper

[`SupabaseClient.ts`](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/supabase-js/src/SupabaseClient.ts) creates auth, PostgREST, Storage, Functions, and Realtime clients.

Its own auth listener is synchronous. It forwards `SIGNED_IN`, `INITIAL_SESSION`, and `TOKEN_REFRESHED` access tokens to `realtime.setAuth()` without awaiting application work.

Conclusion: the wrapper listener does not create the reproduced cycle.

The same file obtains tokens for PostgREST, Storage, and Functions through `auth.getSession()`. An auth cycle can therefore stall calls that appear to belong to other Supabase products. This is propagation of the auth problem, rather than independent failures in those clients.

### Realtime

The wrapper's Realtime token update is synchronous. The campaign found no evidence that Realtime owns the settlement disagreement.

A production patch still needs a regression assertion that Realtime receives the rotated access token before the initiating refresh returns.

### SSR

[`createServerClient.ts`](https://redirect.github.com/supabase/ssr/blob/69a6209482ddde7b1bd769f7c8ca9a604cb65960/src/createServerClient.ts) configures controlled initialization and registers an async listener that applies queued cookie changes for `TOKEN_REFRESHED` and several other events.

Conclusion: awaited listener completion is an active cross-repository contract, even though `onAuthStateChange` is described as less useful on servers in general documentation.

### Cross-tab delivery

The auth client creates a `BroadcastChannel` when supported. Incoming events call `_notifyAllSubscribers(..., false)` and catch notification errors in the channel handler.

Conclusion: callback-error propagation already differs by origin. Manual and initialization notifications can reject their initiating operation, while incoming cross-tab callback errors are caught by the channel handler. Event-specific callback isolation would reduce this inconsistency.

### Auth service

The Auth service locks the refresh token row and session during refresh. It permits common lost-response and close-concurrency reuse cases, returning the active token rather than always rotating again. Outside the permitted window, reuse can terminate the token family or session.

Conclusion: the client should consume the committed event session rather than issue another refresh merely to learn the token it just received.

### Transport diagnostics

The Auth service sets diagnostic headers describing refresh counter and reuse causes. Auth-js successful requests parse JSON and discard response headers.

Conclusion: this remains a separate observability candidate. It does not own the listener cycle and should stay outside the first settlement patch.

## Review of other current work

### Open PR #2568: offline refresh recovery

[PR #2568](https://redirect.github.com/supabase/supabase-js/pull/2568) changes retry behavior, online-event handling, initialization/disposal interleavings, and auto-refresh resumption. It does not change the listener settlement order.

Overlap risk:

- both changes touch `GoTrueClient` lifecycle code;
- production tests must include dispose-during-initialization and reconnect-triggered refresh;
- the settlement patch must preserve the first transport attempt and failure cooldown behavior.

### Open PR #2573: bounded auto-refresh failures

[PR #2573](https://redirect.github.com/supabase/supabase-js/pull/2573) proposes an opt-in failure budget and a new `TOKEN_REFRESH_FAILED` event. Its draft implementation catches that event's listener errors to avoid reentering the ticker's catch path.

Relevance:

- it is current evidence that event-specific listener-error handling is being considered elsewhere;
- it remains unmerged and cannot define the current contract;
- if it lands, the settlement patch must distinguish `TOKEN_REFRESHED` committed-success errors from `TOKEN_REFRESH_FAILED` failure-notification errors.

## Self-audit findings and corrections

### 1. Experiment workflow used the wrong Node version

The repository's `.nvmrc` specifies Node 22 and the pinned package manager is pnpm 11. The first focused workflow requested Node 20, so dependency installation failed before any experiment test ran.

Correction: the workflow now reads `.nvmrc` through `actions/setup-node`.

Evidence status: the dependency-free model ran locally and is preserved; the real auth-js matrix must be judged only from the corrected workflow run.

### 2. Early shared settlement can split one refresh into two answers

Variant A resolves the shared Deferred before calling `_notifyAllSubscribers`.

If `BroadcastChannel.postMessage` then throws:

- a joined caller can already receive the successful committed result;
- the initiating caller receives the transport exception.

This is a stronger compatibility cost than early timing alone. The matrix now records joined-caller behavior during a post-commit transport failure.

Current assessment: this weighs heavily against Variant A.

### 3. Notification-scoped state is token-and-time scoped, not caller scoped

Variant B exposes the event result to any caller using the event's rotated token while the notification is active. Browser JavaScript cannot prove that such a caller descended from the listener.

This still narrows exposure substantially compared with resolving every existing joiner, though it must be documented as a temporary token window rather than true callback ancestry.

### 4. Explicit stale-token reentry remains unresolved in Variant B

A listener that explicitly calls `refreshSession({ refresh_token: oldToken })` does not match the event's rotated token and can still form the manual-refresh cycle.

Current assessment: handle common no-argument usage first, then choose deliberately between a typed stale-token error and a larger callback-context API.

## Updated recommendation

Rank the current choices:

1. **Notification-scoped committed result plus `TOKEN_REFRESHED` callback-error isolation.** Smallest timing change; covers normal manual, initialization, and cross-tab usage.
2. **Notification-scoped result plus a typed stale-token rule.** More complete, but requires a new public error contract and careful treatment of unrelated concurrent callers.
3. **Early shared settlement.** Complete for explicit old-token manual reentry, but changes all joiner timing and can split transport-failure outcomes.
4. **Global detached listeners, timers, or broad async warnings.** Rejected by prior regressions and maintainer reasoning.

## Remaining checks before a production branch

- corrected real-code matrix passes for the notification-scoped variant;
- baseline current source reproduces the cycle and committed-session callback failure;
- early variant transport-failure split is observed and recorded;
- Realtime sees the rotated access token before initiating refresh completion;
- SSR-like cookie work finishes before the initiating call returns;
- initialization, cross-tab, offline-reconnect, and disposal paths retain their existing behavior;
- tests contain no token fragments in logs;
- rebase against any merged form of PR #2568 or PR #2573;
- upstream packet remains held for explicit authorization.
