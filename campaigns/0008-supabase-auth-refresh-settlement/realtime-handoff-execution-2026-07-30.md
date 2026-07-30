# SupabaseClient Realtime refresh handoff execution — 2026-07-30

## Status

Evidence class: `target-executed` for the selected wrapper timing invariant.

Production implementation: absent.

Upstream contact authorized: `false`.

Upstream contact performed: `false`.

## Exact inputs

- Supabase source pin: `63318987365bbcea2c31a00b62cbb95b21083ad5`.
- Owned experiment branch: `fieldwork/auth-refresh-settlement-lab`.
- Executed owned head: `9b00bfe5888083df98a268885bbfae9fa7449ffa`.
- Focused workflow: `30512200146`.
- Variants:
  - `early-shared-settlement`;
  - `token-aware-committed-result`.

## Source seam

`SupabaseClient._listenForAuthEvents()` registers an Auth callback that forwards the event session's access token into `_handleTokenChanged()`.

For `TOKEN_REFRESHED`, `SIGNED_IN`, and `INITIAL_SESSION`, `_handleTokenChanged()` updates `changedAccessToken` and invokes `realtime.setAuth(token)`.

The wrapper does not await the promise returned by `RealtimeClient.setAuth()`. The public refresh therefore owns token handoff, not completion of Realtime channel authentication.

## Executed control

The owned wrapper test:

1. constructs a real `SupabaseClient` with memory-backed persisted Auth storage;
2. initializes the concrete Auth client;
3. writes an expired session using access token `access-r1` and refresh token `refresh-r1`;
4. stubs the Auth transport to return a rotated session using `access-r2` and `refresh-r2`;
5. replaces `realtime.setAuth()` with a controlled promise that records the token and remains pending;
6. calls `refreshSession()`;
7. verifies the refresh resolves with the rotated session;
8. verifies `realtime.setAuth('access-r2')` was invoked exactly once before the refresh returned;
9. verifies Realtime auth completion was still pending at that point;
10. releases the Realtime promise and verifies it completes afterward.

## Result

Both settlement variants passed:

```text
Auth-js:
  4 suites passed
  15 tests passed

SupabaseClient wrapper:
  1 suite passed
  1 test passed
```

The result establishes this bounded invariant:

> A committed Auth refresh hands the rotated access token to the SupabaseClient Realtime wrapper before `refreshSession()` returns, while the refresh does not wait for Realtime authentication completion.

This clears the basic wrapper timing gate for candidate #148.

## Harness history

Three predecessor heads supplied no wrapper behavior evidence:

1. `5ebcf21aa3ba4f178f1d359e2bb83c7a162110d6` stopped because the public `SupabaseAuthClient` type hides the concrete `initialize()` method.
2. `e0882719b1388509f7c0e1eaa7cc6b5595560659` stopped because the same public type hides the concrete `refreshSession()` method in this direct-source test arrangement.
3. `1c042330d8efd2f14c0307aac946d7f906585f5d` reached SupabaseClient compilation but stopped because workspace package outputs such as `@supabase/auth-js` had not been built.

The executed head uses one explicit concrete Auth handle and builds `@supabase/supabase-js` with its workspace dependencies before running the wrapper test.

## Limits

This test does not prove:

- successful completion of `RealtimeClient._performAuth()`;
- channel access-token push success;
- socket reconnect or channel resubscribe behavior;
- handling of a rejected `realtime.setAuth()` promise;
- callback-managed custom-token mode;
- browser BroadcastChannel delivery;
- React Native persisted-session behavior;
- a hosted Realtime service interaction.

Those remain separate compatibility or integration gates. In particular, the wrapper currently discards the promise returned by `realtime.setAuth(token)`; rejection ownership should be reviewed separately rather than folded into refresh settlement without a target-executed consequence.

## Candidate boundary

- #148 owns successful committed refresh settlement and `TOKEN_REFRESHED` callback-error isolation.
- #188 owns failed-refresh cleanup settlement for every shared joiner.
- #189 owns one-time `INITIAL_SESSION` delivery after application callback failure.
- Realtime completion and Realtime promise-rejection ownership remain wrapper concerns rather than auth-js settlement semantics.
