# Supabase refresh settlement generation 5 overlap ownership — 2026-07-30

## Status

Evidence class: `target-executed` for the token-owned active-notification map and all retained generation-4 controls.

Preferred candidate: **committed refresh plus visible notification failure, with active notification results owned by refresh token and reference count**.

Production implementation: absent.

Upstream contact authorized: `false`.

Upstream contact performed: `false`.

## Exact inputs

- public Supabase JS source pin: [`supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5);
- owned lab branch: `teamleaderleo/supabase-js:fieldwork/auth-refresh-settlement-lab`;
- executed owned head: `906a540ebb635a47a2ff603fb81e4827d7a371d8`;
- focused workflow: `30515136573`;
- generation-5 job: `notification-result-map`, job `90783180827`.

## Why generation 4 needed one more revision

Generation 4 used one client-wide `notifyingRefreshResult` slot with save-and-restore behavior around each `TOKEN_REFRESHED` notification.

The exact overlap characterization at predecessor head `0a2496f15da12a66c7e6f92d44d4c380d7a43399`, focused run `30514877495`, passed and confirmed the race:

1. R2 notification begins and stores R2 in the slot;
2. R3 notification begins and stores R3, remembering R2 as its previous value;
3. R2 finishes first and restores the null value it observed before R3 began;
4. R3 is still active, but nested R3 refresh can no longer see its committed result;
5. R3 finishes and restores stale R2;
6. every notification is complete, yet R2 remains exposed as an active committed result.

That run passed three Auth suites and nine tests plus the SupabaseClient wrapper control. The green result is a target-executed negative characterization, not acceptance of the single-slot implementation.

## Generation-5 implementation form

The replacement patch uses:

```text
Map<refresh_token, { result, count }>
```

For every `TOKEN_REFRESHED` notification:

- the event refresh token is inserted with count 1, or its active count is incremented;
- `_callRefreshToken(refreshToken)` may consume only the matching active result;
- completion decrements the matching token count;
- the entry is deleted only when its last owner finishes.

Distinct tokens cannot erase or resurrect each other. Same-token overlapping notifications remain active until every notification owner has completed.

The generation-4 post-commit settlement contract is otherwise unchanged:

- ordinary callers wait for notification completion;
- callback and transport failure remain visible;
- R2 remains stored;
- callback-thrown `AuthError` bypasses destructive refresh cleanup and cooldown;
- zero-joiner shared rejection is internally observed;
- successful notification remains awaited;
- nested rotated-token refresh avoids a second token request.

## Exact execution result

Generation-5 Auth-js suites:

```text
3 suites passed
10 tests passed
```

SupabaseClient wrapper:

```text
1 suite passed
1 test passed
```

The same focused workflow also passed:

- unpatched SSR cookie-write baseline;
- rejected generation-3 early settlement;
- rejected generation-3 broad token-aware settlement;
- generation-4 single-slot implementation plus its negative overlap characterization.

## New overlap controls

### Distinct-token out-of-order completion

The test starts R2 and R3 notifications, then completes R2 first while R3 remains blocked.

Observed generation-5 behavior:

- active map contains R2 and R3 while both run;
- completing R2 removes only R2;
- R3 remains available to a matching nested refresh without invoking the token endpoint;
- completing R3 empties the map;
- a later R2 refresh cannot consume stale committed state and reaches the real refresh path.

### Same-token overlap

The test starts two R2 notifications concurrently.

Observed generation-5 behavior:

- active R2 count becomes 2;
- first completion decrements the count to 1;
- second completion removes the entry;
- no active result remains afterward.

## Retained generation-4 controls

The map variant reran and passed the earlier notification-failure separation controls:

- nested R2 refresh plus later callback failure;
- callback-thrown public `AuthError` under both `throwOnError` policies;
- SSR-style cookie persistence failure;
- notification transport failure;
- successful callback timing for initiator and old-token joiner;
- non-refresh callback failure;
- initial-session negative characterization;
- SupabaseClient Realtime token handoff.

## Current disposition

Generation 5 supersedes the single-slot generation-4 implementation as the preferred owned design.

The accepted bounded model is:

1. token exchange and internal session commit are one fact;
2. active notification ownership is keyed by the event refresh token;
3. nested matching-token refresh may observe the committed result;
4. ordinary callers settle only after notification owners finish;
5. notification failure remains visible without deleting committed storage or starting refresh cooldown;
6. active committed results are removed by exact token ownership, not stack-style restoration.

## Remaining gates

- exact SDK Compliance at the generation-5 head;
- exact full repository CI at the generation-5 head;
- local subscriber delivery after BroadcastChannel transport failure;
- callback-managed Realtime custom-token mode;
- channel token-push completion, reconnect, and resubscribe;
- real writable and intentionally non-writing SSR adapters;
- browser BroadcastChannel execution;
- React Native persisted-session execution;
- hosted Auth and Realtime service execution;
- disposal while one or more notification-map entries are active;
- memory-retention controls if a callback never settles;
- clean direct source/test branch and complete-diff review.

## Boundaries

- #148 owns generation 5.
- #188 remains separate for failed-refresh cleanup settlement.
- #189 remains separate for initial-session delivery multiplicity.
- no production branch has been created.

No public Supabase or `@supabase/ssr` issue, pull request, review, comment, reaction, branch, or message was created or changed.
