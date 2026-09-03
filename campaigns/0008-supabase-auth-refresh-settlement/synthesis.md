# Supabase auth refresh settlement synthesis

State: `ready-for-coordinator-review`

Campaign: #78

Parent scout: #21

Fieldwork PR: #91

Owned experiment: `teamleaderleo/supabase-js#1`

Public source pin: [`supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5)

Owned experiment head: `f589f01234bf057c6d872ac44a1255fe31b433cf`

Retrieval and validation date: `2026-07-30`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

Supabase Auth receives and stores a new session before it tells application listeners that the token was refreshed.

The client then waits for those listeners before it finishes the shared refresh promise. A listener that asks for another refresh can therefore wait for the refresh that is waiting for that listener. A listener exception can also make a successfully stored refresh look like a failed operation.

The correction must break that circular dependency while retaining awaited listener completion for server-side cookie writes.

## Final decision

Prefer a **notification-scoped committed result with `TOKEN_REFRESHED` callback-error isolation**.

While a `TOKEN_REFRESHED` notification is active, calls using the event's rotated refresh token may consume the committed event result. The initiating auth operation still awaits all listeners. Ordinary old-token callers retain their existing shared-promise timing.

This is preferred over resolving the shared refresh Deferred before notification because early shared settlement can give two callers different answers after one committed refresh: a joined caller can receive success before a later notification-transport failure reaches the initiating caller.

## What is established

### Current client behavior

At the pinned revision, auth-js:

1. deduplicates same-instance refreshes through `refreshingDeferred`;
2. requests a rotated session from the Auth service;
3. applies storage and removal-epoch commit guards;
4. saves the rotated session;
5. awaits `TOKEN_REFRESHED` subscribers;
6. resolves the shared refresh result afterward.

The current source and migration note explicitly identify nested `refreshSession()` from a `TOKEN_REFRESHED` listener as the remaining refresh reentry hazard.

### Callback errors

`_notifyAllSubscribers` invokes every listener, awaits all returned promises, logs every listener exception, and throws the first exception. During a committed refresh, that exception crosses back into `_callRefreshToken` after the new session is already stored.

The preferred rule is event-specific:

- preserve all-listener delivery;
- preserve awaited completion;
- log listener exceptions;
- keep the committed refresh result successful;
- retain propagation for notification transport failures;
- retain existing error behavior for unrelated auth events.

### SSR completion contract

`@supabase/ssr` registers an async auth listener that applies queued cookie changes. The initiating auth operation must continue waiting for this work.

Prior timer deferral and global fire-and-forget proposals were rejected because serverless responses could finish before cookie persistence. The library therefore needs a local dependency correction rather than detached listeners.

### Auth-service boundary

The Auth service already handles common lost-response and close-concurrency token reuse cases. The client should consume the committed event session rather than request another rotation merely to learn the token carried by the event.

## Experiment result

The owned fork compared two source patches against the same real auth-js fixture.

| Candidate | Focused suites | Focused tests | Clean exit | Full repository CI |
| --- | ---: | ---: | --- | --- |
| Early shared settlement | 3 | 11 | yes | pass |
| Notification-scoped committed result | 3 | 11 | yes | pass |

Both candidates passed the common cases:

- normal nested `refreshSession()` receives the rotated session;
- one token-service stub request;
- stored and returned credentials agree;
- listener exceptions are logged without overturning committed refresh success;
- every listener still runs;
- no unhandled rejection is observed;
- the initiating call waits for SSR-like async cookie work;
- queued initialization and cross-tab notifications reuse the event session;
- unrelated auth-event listener failures retain current behavior;
- notification transport failures remain visible.

The distinguishing cases were:

| Property | Early shared settlement | Notification-scoped result |
| --- | --- | --- |
| Old-token joined caller during notification | settles before listeners finish | waits with initiating call |
| Explicit stale-token nested call | succeeds through resolved Deferred | remains unresolved in bounded probe |
| Transport failure after commit | joined caller succeeds; initiator rejects | joined caller and initiator reject together |

The final row is decisive against broad early settlement.

## Remaining edge

A listener can explicitly call:

```ts
refreshSession({ refresh_token: oldToken })
```

The notification-scoped result is keyed to the rotated event token, so this stale-token call can still join the unresolved manual refresh and reproduce the cycle.

This edge should receive a deliberate follow-up contract:

1. a typed stale-token reentry error near `_callRefreshToken`; or
2. a larger public callback/operation context that can identify listener ancestry.

A client-wide boolean does not identify ancestry. It also affects unrelated code that happens to call refresh while notification is active.

## Candidate ranking

1. **Notification-scoped committed result plus `TOKEN_REFRESHED` callback-error isolation.** Smallest timing change; covers normal manual, initialization, and cross-tab usage.
2. **Notification-scoped result plus a typed stale-token rule.** More complete but adds a public error contract and requires concurrent-caller analysis.
3. **Early shared settlement.** Handles explicit stale-token manual reentry but changes every joined caller's timing and can split caller-visible outcomes.
4. **Global detached listeners, timers, microtask deferral, or broad async warnings.** Rejected by prior regressions, supported SSR usage, and maintainer reasoning.

## Platform and application responsibility

| Owner | Responsibility |
| --- | --- |
| Auth service | token rotation, transaction locking, reuse convergence, token-family enforcement |
| auth-js | persisted session, same-instance single-flight, commit guards, notification delivery, settlement result |
| Supabase client wrapper | forwards auth tokens to Realtime and provides token-aware fetch to PostgREST, Storage, and Functions |
| SSR adapter | writes response cookies from awaited auth events |
| Application | listener work and listener exceptions |

The application triggers the cycle by refreshing from a refresh listener. The client owns the indefinite wait and the disagreement between committed storage and the public result.

## Adjacent Supabase findings

### Realtime persisted-session issue

Open Supabase JS issue [#1730](https://redirect.github.com/supabase/supabase-js/issues/1730) reports React Native Realtime subscriptions using the anonymous token after a session is restored from storage. The report targets Supabase JS `2.39.8` and remains active through 2026.

Current source now forwards `INITIAL_SESSION` to `realtime.setAuth()`, and current unit tests assert this behavior. The issue therefore needs a current React Native/AsyncStorage characterization before promotion. Treat it as a stale-or-runtime-specific Realtime candidate rather than evidence for the refresh-settlement patch.

### Auto-refresh outage behavior

Open issue [#1680](https://redirect.github.com/supabase/supabase-js/issues/1680) concerns repeated refresh attempts while the server is unavailable. Current open PRs [#2568](https://redirect.github.com/supabase/supabase-js/pull/2568) and [#2573](https://redirect.github.com/supabase/supabase-js/pull/2573) explore offline recovery and bounded automatic failures. They touch nearby lifecycle code but do not change notification settlement order.

A production settlement branch must rebase over any landed form of these changes and retain cooldown, reconnect, ticker, and disposal behavior.

### Session-user warning

Open issue [#1709](https://redirect.github.com/supabase/supabase-js/issues/1709) tracks false or repeated server warnings around stored `session.user`. PR [#1817](https://redirect.github.com/supabase/supabase-js/pull/1817) merged a proxy change, yet the issue was later reopened. This is a separate trust-warning and serialization boundary.

### Refresh diagnostics

The Auth service emits refresh-token counter and reuse-cause headers, while successful auth-js requests return parsed JSON and discard response headers. This is a separate observability candidate. It should not expand the first settlement patch.

## Review of other Fieldwork work

Two current Fieldwork reviews produced reusable lessons:

- PR #105's review queue correctly separates exact evidence classes and already places this campaign on its watchlist. Its Workers SDK queue entry needs refresh against the newer batch synthesis before that queue merges.
- PR #112's Workers SDK synthesis carefully marks package execution as a gate. One sentence describing an unexecuted package matrix as demonstrating behavior should be narrowed to source-confirmed distinctions plus a prepared matrix.

These reviews reinforce the campaign's evidence wording: focused target tests and repository CI are executed evidence; live service, React Native, browser BroadcastChannel, and real SSR framework behavior remain separate gates.

## Production-branch gate

Before selecting a production patch:

1. create one clean branch containing the notification-scoped candidate rather than the two-variant lab;
2. move focused cases into normal auth-js test locations;
3. add a SupabaseClient regression proving Realtime receives the rotated access token before the initiating refresh returns;
4. run a bounded real SSR cookie trial;
5. run a browser or React Native cross-tab/persisted-session trial where applicable;
6. rebase against current auth lifecycle changes;
7. review `throwOnError`, custom `PromiseConstructor`, disposal, reconnect, and auto-refresh interactions;
8. retain an upstream packet without filing it until explicit authorization.

## Evidence packet

- [Technical report](report.md)
- [Plain-language explanation](plain-language.md)
- [Source, history, and adjacent-component audit](source-audit.md)
- [Validation record](validation.md)
- [Owned-fork draft experiment](https://github.com/teamleaderleo/supabase-js/pull/1)
- [Parent scout report](../../programmes/sdk-integration-lifecycle/scouts/supabase-client-runtime-contracts/report.md)

## Coordinator handoff

Recommended disposition: **accept the campaign mechanism and preferred contract; authorize a fork-only production branch; retain upstream contact as unauthorized.**

The campaign issue should remain in its coordinator-owned state until the coordinator decides whether to open the production branch gate or close the campaign as a completed design result.