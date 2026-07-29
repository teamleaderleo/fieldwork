# Supabase auth refresh and session recovery scout

- Fieldwork issue: `#21`
- Programme: `sdk-integration-lifecycle` (`#13`)
- Target hub: `supabase` (`#12`)
- Worker: `teamleaderleo`
- State: `ready-for-synthesis`
- Retrieval date: `2026-07-29`
- Selected bounded surface: `auth refresh and session recovery`
- Claim scope requested: `interface`
- Claim scope supported: `interface`, backed by a bounded `mechanism` probe
- Integration context: Stensibly trial defined below; trial has not begun
- Upstream contact: unauthorized; no contact occurred

## Asked

Scout Supabase client and runtime contracts, choose one bounded surface, separate platform behaviour from application behaviour, and return ranked branch candidates. The lane also requires pinned revisions, code-and-test mapping, a runnable synthetic scenario, a Fin Agent or Stensibly integration trial, quiet research, and a durable handoff.

## Examined

### Pinned revisions

| Role | Repository | Revision | Why it was pinned |
| --- | --- | --- | --- |
| JavaScript client monorepo | `supabase/supabase-js` | [`63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5) | Public client entrypoint, auth-js implementation, tests, contribution rules |
| Auth service | `supabase/auth` | [`163ab6faf15b3a4e578ce2f7f2e3f2725768dd05`](https://redirect.github.com/supabase/auth/commit/163ab6faf15b3a4e578ce2f7f2e3f2725768dd05) | Refresh endpoint, token rotation, transactional reuse rules |
| CLI | `supabase/cli` | [`dcf444369db97c4d38caa7274b5394f283a48e87`](https://redirect.github.com/supabase/cli/commit/dcf444369db97c4d38caa7274b5394f283a48e87) | Local Auth configuration and default refresh-token reuse interval |
| Platform monorepo | `supabase/supabase` | [`0d2d47c26f4c14c99785b46c7c8a90df95573153`](https://redirect.github.com/supabase/supabase/commit/0d2d47c26f4c14c99785b46c7c8a90df95573153) | Revision completeness for the target; no owning code for this bounded mechanism was needed |

The auth-js package manifest reports an automated workspace version, so this scout treats the commit as the release identity.

### Repository protocols and package policy

Fieldwork protocols were read before claiming the lane. The claim comment records the worker, owned paths, revisions, scope, stop condition, dependencies, and the ban on upstream contact. The additional probe paths were claimed in a follow-up comment before repository writes.

The Supabase JavaScript contribution guide requires Node.js 20 or newer, pnpm, Docker for auth-js integration tests, TypeScript changes under `packages/core/`, conventional commits with an `auth` scope, affected tests, formatting, and builds. `packages/core/auth-js/AGENTS.md` says version-pinned source and TSDoc are canonical for this package. This scout produced Fieldwork evidence only and made no upstream branch, issue, comment, or pull request.

### Evidence labels

- `source`: version-pinned implementation or configuration
- `test`: version-pinned test coverage
- `mechanism-probe`: local synthetic execution preserving selected control-flow properties
- `inference`: consequence derived from source plus probe
- `negative-result`: suspected gap that current code and tests already cover
- `policy`: repository or lane protocol

## Ownership map

| Layer | Entrypoint or owner | State | Side effects | Recovery and tests |
| --- | --- | --- | --- | --- |
| Public SDK | `packages/core/supabase-js/src/SupabaseClient.ts` | Project-scoped auth URL, storage key, client settings | Creates `SupabaseAuthClient`; listens for auth events; updates Realtime auth | Unit coverage exists for wrapper construction and auth option flow |
| Auth client | `packages/core/auth-js/src/GoTrueClient.ts` | Persisted session, refresh single-flight, failure cooldown, timer, visibility listener, subscribers, broadcast channel, removal epoch | Reads and writes session storage; calls Auth service; emits events; broadcasts cross-tab state | Large Jest suite covers refresh, recovery, races, cooldown, initialization, and basic disposal |
| Client transport | `packages/core/auth-js/src/lib/fetch.ts` | Request options and parsed JSON | `POST /token?grant_type=refresh_token`; converts response/error JSON to auth types | Transport tests are indirect through auth-js suites |
| Auth HTTP endpoint | `supabase/auth/internal/api/token.go` and `token_refresh.go` | Request grant type and validated refresh token | Dispatches the refresh grant to token service; sends JSON | Auth service token tests cover grant behaviour |
| Auth token service | `supabase/auth/internal/tokens/service.go` | Session row, token family or token counter, last refresh time, configured reuse interval | Serializes refresh, rotates token, converges accepted reuse, can revoke token family/session | Service tests cover token rotation and reuse cases |
| Local runtime configuration | `supabase/cli/apps/cli-go/pkg/config/auth.go` and config template | Rotation flag and reuse interval | Maps local config into Auth service settings | CLI config tests and generated schema cover the fields |

## Client behaviour

### Public construction and cross-product coupling

`SupabaseClient` derives `/auth/v1` from the project URL, namespaces storage with the project reference, applies auth defaults, creates `SupabaseAuthClient`, and registers a synchronous auth listener. `TOKEN_REFRESHED`, `SIGNED_IN`, and `INITIAL_SESSION` update the Realtime access token. `SIGNED_OUT` clears it.

This wrapper listener performs synchronous state propagation and does not trigger the two candidate failures below. The owning boundary is auth-js.

### Initialization, persistence, and multi-tab state

`GoTrueClient` owns:

- `autoRefreshTicker` and an immediate refresh timeout;
- `visibilityChangedCallback`;
- `refreshingDeferred`, the per-instance refresh single-flight;
- `lastRefreshFailure`, keyed by refresh token and bounded by a cooldown;
- `_sessionRemovalEpoch`, which detects sign-out during an asynchronous save;
- `initializePromise` and queued initialization notifications;
- optional custom locking, with a lockless default path;
- browser `BroadcastChannel` notification for shared storage keys.

Persisted browser sessions use local storage when available. Non-browser clients use configured storage or an in-memory adapter. Multiple clients in one browser realm under the same storage key produce a warning.

### Recovery and proactive refresh

`_recoverAndRefresh` loads the session, migrates optional user storage, validates the required fields, and refreshes a session inside the expiry margin. It delegates failure removal or preservation to `_callRefreshToken`. A valid session outside the margin emits `SIGNED_IN`.

The auto-refresh ticker checks expiry in ticks. Browser execution follows visibility; non-browser execution runs continuously until the application calls `stopAutoRefresh` or `dispose`.

### Refresh request and retry

`_refreshAccessToken` calls `POST /token?grant_type=refresh_token` with the refresh token in the body. Retryable transport failures use 200, 400, 800 millisecond exponential waits while the next attempt still fits inside the auto-refresh tick duration.

`_callRefreshToken` then applies four client guards:

1. concurrent callers join `refreshingDeferred`;
2. serial same-token failures join a cooldown result;
3. a before/after storage snapshot discards rotated credentials when another actor cleared or replaced the slot;
4. `_sessionRemovalEpoch` catches sign-out during the asynchronous save and removes any write that landed after removal began.

A non-retryable refresh failure preserves storage while the access token remains valid. Once the access token has expired, the client removes the session and emits `SIGNED_OUT`. Retryable failures preserve storage.

### Notification settlement boundary

On success, `_callRefreshToken` performs this order:

1. save the rotated session;
2. await `_notifyAllSubscribers('TOKEN_REFRESHED', session)`;
3. build and resolve the refresh result;
4. clear the in-flight marker in `finally`.

`_notifyAllSubscribers` invokes all listeners concurrently, awaits all of them, collects errors, logs each error, and throws the first.

That ordering creates two separate behaviours at the same owner boundary:

- A `TOKEN_REFRESHED` listener that awaits `refreshSession()` joins the still-pending outer `refreshingDeferred`. The outer call waits for the listener, producing a promise cycle.
- A listener exception occurs after the rotated session is saved. The exception crosses back into `_callRefreshToken`, rejects the internal `Deferred`, and makes the public refresh call throw despite a successful service refresh and persisted credentials.

The source explicitly documents and deprecates the async-listener overload for the nested-refresh cycle. The general TSDoc also says async callbacks can call other auth methods and that callbacks are awaited, which leaves the exact safe method set easy to misread.

### Disposal

`dispose()` stops timers, removes the visibility listener, closes the broadcast channel, and clears subscribers. It does not abort an in-flight fetch. The TSDoc states that a disposed instance can write rotated credentials after disposal and suggests awaiting pending auth work or changing the storage key. Current disposal tests cover idempotency, subscriber clearing, and timer shutdown; they do not exercise a refresh that completes after disposal.

## Auth service behaviour

The HTTP token endpoint selects `RefreshTokenGrant` when `grant_type=refresh_token`. The refresh handler validates token form and delegates to `tokens.Service.RefreshTokenGrant`.

The service performs a short retry loop around row contention, then serializes access in a database transaction. Its rotation agreement deliberately supports client and multi-tab failure modes:

- For legacy refresh tokens, the revoked parent of the active token can return the active child token when the client likely failed to save the prior response.
- Reuse inside the configured interval can converge callers on the active token.
- For counter-based refresh tokens, a caller one token behind is treated as a likely failed-save case.
- Calls close in time can be treated as concurrent refreshes.
- Accepted reuse returns the current token without incrementing the counter.
- Reuse beyond accepted conditions can return `refresh_token_already_used` and, when rotation is enabled, terminate the token family or session.

The local CLI template enables rotation and sets `refresh_token_reuse_interval = 10`. Hosted project values were outside this source-only scout, so the report makes no hosted-default claim.

The service adds diagnostic response headers including token counter, reuse status, and reuse cause. The auth-js `_handleRequest` path returns parsed JSON for successful calls and drops response headers. Operational value from exposing those headers remains an inference and ranks below the reproduced notification findings.

## Client and service agreement

The client retry strategy and service reuse rules agree on a crucial recovery case: a service may commit a token rotation while the response is lost, after which the client retries with the prior token. The service can identify the parent or one-behind token and return the current active token. This converts a suspected retry/rotation incompatibility into a negative result.

The client adds per-instance single-flight and cooldown controls, while the service adds cross-instance transactional serialization and bounded convergence. Browser tabs can still issue separate requests because `refreshingDeferred` is instance-local; the service contract explicitly handles close concurrent refreshes.

## Platform behaviour and application behaviour

| Classification | Behaviour |
| --- | --- |
| Platform: client | Persists the rotated session before observer completion; awaits observers before settling refresh; shares the in-flight promise with nested callers; rejects the internal deferred on a non-auth observer error |
| Platform: service | Serializes token rotation; accepts bounded failed-save and concurrent reuse; returns an active token or a specific refresh error |
| Platform: local runtime | Exposes rotation and reuse interval through CLI config; local template uses a 10-second interval |
| Application trigger | Registers an async `onAuthStateChange` listener that calls `refreshSession` during `TOKEN_REFRESHED` |
| Application trigger | Throws or rejects inside an auth-state listener |
| Application responsibility | Starts and stops auto-refresh around mobile or desktop foreground state; disposes replacement clients during HMR or component cleanup |
| Application policy, excluded | Row-level access rules, role design, authorization decisions, and product-specific sign-out policy |

The first two application triggers are application code, yet the durable consequences come from the client settlement contract. A listener bug can stall or overturn the result of a successfully committed platform operation.

## Tests and recent changes

### Existing coverage

The pinned auth-js suite includes:

- concurrent refresh deduplication;
- initialization callbacks that call `getSession` during `SIGNED_IN` or `TOKEN_REFRESHED`;
- storage preservation for proactive failures;
- session removal for expired credentials;
- retryable failure preservation;
- explicit `refreshSession` error semantics;
- same-token failure cooldown;
- storage and removal race guards;
- acceptance of externally supplied tokens against empty or different stored sessions;
- disposal idempotency, subscriber clearing, and timer shutdown.

### Blind spots found

Search and source review found no test for:

- `refreshSession()` awaited inside a `TOKEN_REFRESHED` listener;
- a `TOKEN_REFRESHED` listener throwing after the rotated session is saved;
- the internal rejected `Deferred` becoming unhandled when no concurrent joiner observes it;
- an in-flight refresh completing after `dispose()`.

### Recent change context

A recent auth change, [`ad23adffb73377295516ab01dce5fb7cbd2edaf9`](https://redirect.github.com/supabase/supabase-js/commit/ad23adffb73377295516ab01dce5fb7cbd2edaf9), added valid-session preservation and failure cooldown. The pinned tests strongly cover that work.

An earlier change, [`3360596ccb4381a0f546a3641eb9ffeddbc3710e`](https://redirect.github.com/supabase/supabase-js/commit/3360596ccb4381a0f546a3641eb9ffeddbc3710e), discusses recursive auth calls and deadlock risk around older locking behaviour. The current lockless implementation removed many lock-induced cycles, while the notification/single-flight cycle remains as a distinct mechanism.

## Runnable synthetic mechanism probe

Artifacts:

- `programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/artifacts/auth-refresh-subscriber-ordering.mjs`
- `programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/artifacts/auth-refresh-subscriber-ordering.result.json`

Run:

```bash
node programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/artifacts/auth-refresh-subscriber-ordering.mjs
```

The probe preserves:

- the pinned `Deferred` semantics;
- one in-flight refresh promise;
- successful service response;
- save-before-notify ordering;
- awaited asynchronous subscribers;
- single-flight settlement after subscriber completion.

It omits HTTP, JWT contents, concrete storage adapters, BroadcastChannel, and auth-service database state. Its claim scope is `mechanism`.

Observed outcomes:

| Scenario | Outcome | Service calls | Stored token | Additional observation |
| --- | --- | ---: | --- | --- |
| Nested refresh inside `TOKEN_REFRESHED` | Timeout at 100 ms | 1 | `R2` | Inner refresh joined the unresolved outer promise |
| Listener throws after save | Public call rejected with listener error | 1 | `R2` | Internal deferred rejection reached `unhandledRejection` |
| Read-only listener control | Resolved | 1 | `R2` | Normal notification order completed |

The timeout is a liveness result, not a service failure. The throwing-listener case is a state/result divergence: credentials have advanced while the caller receives an application exception.

## Strongest supported finding

A successful Auth service refresh remains coupled to application subscriber completion inside auth-js. The client saves rotated credentials, then waits for every auth-state subscriber before settling the shared refresh promise. Reentrant refresh creates a deterministic promise cycle. Subscriber failure turns a committed refresh into a caller-visible rejection and can create an unhandled internal rejection. The owner is isolated to `GoTrueClient._callRefreshToken`, `_notifyAllSubscribers`, and their public listener contract.

## Ranked branch candidates

### 1. Isolate subscriber failure from a committed refresh

- Candidate slug: `auth-refresh-subscriber-failure-isolation`
- Rank basis: reproduced, undocumented consequence; high user impact; exact client owner; compact regression surface
- Claim scope: `interface`
- Evidence: `source`, `test`, `mechanism-probe`, `inference`
- Current consequence: service refresh succeeds and `R2` is persisted, while `refreshSession()` throws the application listener error; the internal single-flight rejection can also become unhandled
- Owning boundary: `GoTrueClient._callRefreshToken` and `_notifyAllSubscribers`
- Next bounded question: How should observer exceptions be reported while preserving a successful refresh result and event ordering?
- Acceptance target:
  - rotated session persists once;
  - explicit refresh settles as success when service and storage succeeded;
  - all subscribers receive the event;
  - subscriber exceptions have a deliberate reporting path;
  - no unhandled internal rejection;
  - current auth-error handling and `throwOnError` behaviour remain intact.

### 2. Break reentrant refresh cycles from `TOKEN_REFRESHED`

- Candidate slug: `auth-refresh-reentrant-subscriber-deadlock`
- Rank basis: deterministic liveness failure and missing test; source already acknowledges the hazard, which lowers novelty
- Claim scope: `interface`
- Evidence: `source`, `test`, `mechanism-probe`
- Current consequence: outer refresh waits for the listener; inner refresh joins the outer unresolved promise; both wait indefinitely after credentials are saved
- Owning boundary: refresh single-flight settlement plus auth-state notification
- Next bounded question: Should nested refresh receive the freshly committed result, a typed reentry error, or a queued second refresh after notification completes?
- Acceptance target:
  - nested listener call settles within a bounded time;
  - one service request for the original refresh;
  - no duplicate token rotation;
  - explicit event ordering;
  - regression tests cover manual refresh and initialization-triggered refresh.

Candidates 1 and 2 share an owner and could become one campaign, `auth-refresh-notification-settlement`, with two independent acceptance cases.

### 3. Fence in-flight refresh commits across `dispose()`

- Candidate slug: `auth-dispose-inflight-generation-fence`
- Rank basis: source-documented lifecycle caveat and test gap; application workaround exists; field prevalence unmeasured
- Claim scope: `mechanism` first, then `interface` if replacement-client consequences reproduce
- Evidence: `source`, `test`, `inference`
- Current consequence: a disposed client can write rotated credentials into a shared storage key after a replacement client starts
- Owning boundary: `dispose`, `_callRefreshToken`, and session commit guard generation
- Next bounded question: Can disposal advance a client generation that discards later commits without invalidating the shared session or breaking SSR hydration?
- Acceptance target:
  - delayed old-client refresh cannot overwrite replacement state;
  - ordinary refresh and sign-out race guards still pass;
  - repeated disposal stays idempotent;
  - storage-key sharing semantics remain explicit.

### 4. Preserve refresh-reuse diagnostics at the client boundary

- Candidate slug: `auth-refresh-reuse-diagnostics`
- Rank basis: clear service metadata loss; operational consequence remains inferred; lower priority than reproduced correctness and liveness failures
- Claim scope: `interface` only after a consumer trial demonstrates use
- Evidence: `source`, `inference`
- Current consequence: service-side reuse cause and counter headers disappear when auth-js converts a successful response to JSON data
- Owning boundary: auth-js transport response envelope and refresh debug/event surface
- Next bounded question: Which minimal diagnostic signal helps distinguish concurrent refresh convergence, failed-save recovery, and suspicious reuse without exposing refresh-token material?
- Acceptance target:
  - no credential fragments exposed;
  - stable optional diagnostics for successful refreshes;
  - no breaking change to `AuthResponse`;
  - demonstrated use in a local multi-client scenario.

## Failed hypotheses and negative results

1. **Retry after a lost rotation response breaks the session.** Negative result. The service explicitly converges parent or one-behind tokens in failed-save and concurrent cases.
2. **Serial application reads can create unbounded refresh storms.** Negative result at the pinned client revision. Concurrent calls share one promise and serial same-token failures use a cooldown; tests cover repeated calls.
3. **A sign-out during refresh can resurrect the session.** Negative result for the tested timing windows. Storage snapshots plus `_sessionRemovalEpoch` discard or undo rotated writes; tests cover cleared and replaced storage.
4. **A proactive refresh failure always logs the user out.** Negative result. The client preserves a still-valid access token and returns the preserved session on read paths; tests cover proactive and reactive cases.
5. **The Supabase wrapper’s Realtime token listener triggers refresh reentry.** Negative result. The wrapper listener synchronously forwards the token to Realtime and performs no nested auth call.
6. **The bounded issue belongs to application authorization policy.** Negative result. The owner is client lifecycle and event settlement; row policies and role decisions are outside the claim.

## Alternative architectures

These are design directions for a future branch, not patch commitments:

1. Settle the internal refresh result after storage commit, then dispatch observer work through a separate notification promise or queue.
2. Keep awaited ordering but detect refresh reentry from the active `TOKEN_REFRESHED` notification and return the committed session or a typed error.
3. Split state propagation into internal listeners, which must complete before settlement, and application observers, whose failures are isolated.
4. Add an explicit subscriber-error hook or debug event while preserving successful auth operation results.
5. Advance a client generation on disposal and verify the generation immediately before and after session writes.

## Stensibly integration trial

### Trial name

`Stensibly auth-event settlement trial`

### State

Defined; execution has not begun. No `testbed:*` label should be added yet.

### Setup

Use a local Stensibly workspace and a synthetic Supabase Auth fetch adapter. Create one short-lived session and one work item whose assigned agent subscribes to auth changes. Run two cases:

1. During `TOKEN_REFRESHED`, the agent awaits `refreshSession()` before recording the work-item transition.
2. During `TOKEN_REFRESHED`, the agent records the transition and throws once.

No live Supabase project, production data, or upstream service is required.

### Preserved integration properties

- real Stensibly task or handoff transition;
- real application subscriber callback;
- pinned auth-js package or a Fieldwork test branch;
- synthetic token endpoint with deterministic rotation;
- observation of task completion, refresh settlement, stored token, service call count, and unhandled rejection events.

### Success criteria for a candidate branch

- Stensibly work-item processing remains responsive;
- exactly one initial token rotation occurs;
- the stored token and refresh result agree;
- listener errors appear through the chosen error channel;
- no unhandled rejection;
- no duplicate task transition;
- the control case stays unchanged.

### Claim scope

`integration`. The trial can begin after a coordinator selects candidate 1, candidate 2, or their combined campaign.

## Wider context

- Where the mechanism sits: auth-js session refresh, below the `supabase-js` wrapper and above the Auth HTTP service.
- Actual documented or observed use: browser, SSR, React Native, Electron, and server runtimes can persist sessions and receive `TOKEN_REFRESHED` events. The public docs encourage auth-state listeners and explain foreground management for non-browser runtimes.
- Inferred consequence: application observers can stall or overturn the apparent result of a committed credential rotation, leaving storage ahead of caller state.
- Illustrative examples: token refresh inside a listener; UI or telemetry listener throwing; HMR replacing a client during refresh.
- Operational visibility: listener exceptions are logged; the public refresh call may reject; the internal deferred can become unhandled; service reuse headers are dropped on success.
- What the model preserves: single-flight, save-before-notify, awaited subscribers, delayed settlement, native Deferred rejection.
- What the model omits: real package compilation, browser scheduling, service database transactions, BroadcastChannel, and hosted configuration.

## Remaining uncertainty

- The runner could not clone GitHub over the local network, so the full pnpm/Jest/Docker suite was unavailable. Version-pinned source and tests were retrieved through the GitHub connector.
- The probe models the exact selected ordering and Deferred semantics, while omitting unrelated package code. A candidate branch should add direct Jest regression tests in auth-js.
- Hosted Auth rotation and reuse values remain unknown here.
- Field prevalence of nested refresh listeners, throwing listeners, and dispose-during-refresh remains unmeasured.
- Subscriber error behaviour under every custom `PromiseConstructor` assigned to `Deferred.promiseConstructor` remains untested.

## Dependencies and blockers

- Programme `#13` and target hub `#12` remain the governing parents.
- Candidate implementation requires a coordinator-created campaign or probe issue.
- Upstream work requires separate explicit authorization.
- The Stensibly integration trial awaits candidate selection.

## Decision needed

Choose one of these paths:

1. open one combined campaign for candidates 1 and 2 at the notification settlement boundary;
2. open candidate 1 first and keep candidate 2 as a follow-up acceptance case;
3. request a direct auth-js Jest probe before campaign creation.

The evidence supports path 1 or 2. Candidate 1 carries the strongest new finding.

## Suggested next action

Create a bounded auth-js campaign around subscriber failure isolation, with the nested-refresh cycle as a mandatory adjacent regression case. Keep disposal and reuse diagnostics as separate later probes.

## Durable artifacts

- `programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/report.md`
- `programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/artifacts/auth-refresh-subscriber-ordering.mjs`
- `programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/artifacts/auth-refresh-subscriber-ordering.result.json`

## Upstream contact

External contact remains unauthorized. No Supabase issue, pull request, discussion, comment, review, or message was created or updated.

## Fieldwork handoff

- Batch: none
- Campaign: none
- Assignment or lane: Fieldwork issue `#21`
- Worker: `teamleaderleo`
- State: `ready-for-synthesis`
- Fieldwork issue: `#21`
- Fieldwork pull request or durable paths: paths listed above
- Target revision: four pinned revisions listed above
- Claim scope requested: `interface`
- Claim scope supported: `interface`, with `mechanism` probe evidence
- Integration context: Stensibly trial defined in this report

### Completion comment

```text
FIELDWORK HANDOFF
State: ready-for-synthesis
Batch: none
Campaign: none
Assignment: lane #21
Claim scope supported: interface, backed by mechanism probe
Integration context: Stensibly auth-event settlement trial defined in report; not begun
Durable artifacts: programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/report.md and adjacent artifacts
Finding: auth-js saves rotated credentials and then awaits application subscribers before settling the shared refresh promise. Nested refresh in TOKEN_REFRESHED creates a promise cycle; subscriber failure makes a committed refresh reject and can create an unhandled internal Deferred rejection. The Auth service rotation/reuse contract otherwise agrees with client retry and concurrency handling.
Evidence labels used: source, test, mechanism-probe, inference, negative-result, policy
Uncertainty: full upstream Jest/Docker suite unavailable in this runner; hosted reuse configuration and field prevalence remain unknown
Decision needed: choose a combined notification-settlement campaign or start with subscriber-failure isolation and carry nested refresh as an adjacent regression case
Upstream contact authorized: no
```
