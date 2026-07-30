# Supabase refresh settlement generation 4 execution — 2026-07-30

## Status

Evidence class: `target-executed` for the selected auth-js and SupabaseClient wrapper controls.

Preferred candidate: **notification-scoped committed result plus visible post-commit notification failure**.

Production implementation: absent.

Upstream contact authorized: `false`.

Upstream contact performed: `false`.

## Exact inputs

- public Supabase JS source pin: [`supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5);
- public SSR integration source pin: [`supabase/ssr@69a6209482ddde7b1bd769f7c8ca9a604cb65960`](https://redirect.github.com/supabase/ssr/commit/69a6209482ddde7b1bd769f7c8ca9a604cb65960);
- owned lab branch: `teamleaderleo/supabase-js:fieldwork/auth-refresh-settlement-lab`;
- executed owned head: `693d544c3f02c1772696bdc7329e03036a959802`;
- focused workflow: `30514559018`;
- generation-4 job: `notification-failure-separation`, job `90781406006`.

## Compared lanes

The exact workflow executed four independent lanes from one owned head:

1. unpatched SSR cookie-write baseline;
2. rejected generation-3 early shared settlement;
3. rejected generation-3 token-aware committed result with broad callback isolation;
4. generation-4 notification-failure separation.

All four jobs completed successfully. The first three preserve the already executed comparison showing why generation 3 was rejected. The fourth executes the replacement contract.

## Generation-4 implementation form

The owned patch adds two internal concepts:

- `committedRefreshResult` — local to one `_callRefreshToken()` operation after token exchange, commit guards, and session storage have succeeded;
- `notifyingRefreshResult` — a notification-scoped result exposed only to a refresh call using the event's rotated refresh token while `TOKEN_REFRESHED` callbacks are running.

The ordinary shared `refreshingDeferred` remains unsettled until notification completion.

When notification succeeds:

- initiator and ordinary old-token joiners resolve with the committed session;
- nested rotated-token refresh returns the committed session without another token request.

When notification fails after commit:

- the internal shared dependency rejects;
- ordinary callers receive the notification failure under existing public `throwOnError` handling;
- the initiating direct path throws the same failure;
- rotated internal storage remains committed;
- `lastRefreshFailure` remains clear;
- callback-thrown `AuthError` bypasses refresh-token cleanup and cannot remove R2;
- a handled observer is attached to the internal shared promise so zero-joiner failure does not create an unhandled rejection.

## Executed generation-4 result

Auth-js generation-4 suites:

```text
2 suites passed
8 tests passed
```

SupabaseClient wrapper:

```text
1 suite passed
1 test passed
```

### Controls passed

1. **Nested rotated-token refresh plus later callback failure**
   - one token request;
   - nested no-argument `refreshSession()` receives R2;
   - throwing and healthy callbacks are both attempted;
   - initiator and old-token joiner receive the same callback failure;
   - R2 remains stored;
   - cooldown remains clear;
   - no unhandled rejection is observed.

2. **Callback-thrown public `AuthError` under both `throwOnError` policies**
   - `throwOnError: false` returns the error through the public result;
   - `throwOnError: true` rejects;
   - one token request and one callback attempt;
   - R2 remains stored;
   - cooldown remains clear.

3. **SSR-style cookie `setAll` failure**
   - the public refresh exposes the persistence failure;
   - only one token request and one cookie-write attempt occur;
   - internal storage contains R2;
   - the modeled response cookie remains R1;
   - cooldown remains clear.

4. **Notification transport failure**
   - initiator and ordinary joiner both reject after commit;
   - R2 remains stored;
   - cooldown remains clear.

5. **Successful async notification timing**
   - initiator and old-token joiner remain pending while the callback is blocked;
   - both resolve with R2 after callback completion;
   - one token request.

6. **Non-refresh callback failure**
   - direct `SIGNED_IN` notification failure remains a rejection.

7. **Initial-session callback characterization**
   - the separate #189 negative characterization remains stable and is not silently folded into generation 4.

8. **SupabaseClient Realtime handoff**
   - `realtime.setAuth()` receives the rotated access token before refresh returns;
   - Realtime authentication completion remains non-blocking.

## Harness history

The generation-4 result followed three non-product failures:

1. malformed first patch hunk metadata;
2. malformed later hunk metadata;
3. listener tests registered against already expired storage, allowing asynchronous `INITIAL_SESSION` recovery to race the controlled refresh and leak callback failures into later tests.

The executed head initializes empty storage, waits for every subscription's initial delivery, then plants R1 and starts exactly one controlled refresh. Rejection expectations are attached before releasing the token request so test-owned promises cannot reject before handlers exist.

None of the three predecessor runs supplied candidate behavior evidence.

## Decision

Generation 4 replaces generation 3 as the preferred bounded contract.

The candidate should not classify every `TOKEN_REFRESHED` subscriber error as ignorable application behavior. Public subscribers may own critical external persistence. Instead, it should separate:

- successful Auth service exchange and internal storage commit;
- nested rotated-token reentry needed to avoid callback deadlock;
- ordinary public settlement after all notification owners finish;
- visible post-commit notification failure without destructive refresh cleanup.

## Remaining gates

The focused result does not yet prove:

- overlapping or concurrently interleaved `TOKEN_REFRESHED` notifications;
- notification-scoped result correctness under out-of-order completion;
- local callback delivery after BroadcastChannel transport failure;
- callback-managed Realtime custom-token mode;
- channel token-push completion, reconnect, or resubscribe;
- a real SSR framework response-cookie write;
- intentionally non-writing server adapter behavior;
- browser BroadcastChannel execution;
- React Native persisted-session execution;
- hosted Auth or Realtime service behavior;
- disposal during notification;
- exact full repository compatibility at the generation-4 head.

A single client-wide notification-result slot is a source-reviewed concurrency risk until overlapping notification controls pass or the implementation uses serialized or generation-owned state.

## Boundaries

- #148 owns the generation-4 successful-refresh and post-commit notification contract.
- #188 remains separate for total single-flight settlement when failed-refresh cleanup callbacks throw.
- #189 remains separate for one-time initial-session delivery.
- explicit stale pre-refresh-token reentry remains a separate typed-error or callback-context decision.
- no production branch has been created.

No public Supabase or `@supabase/ssr` issue, pull request, review, comment, reaction, branch, or message was created or changed.
