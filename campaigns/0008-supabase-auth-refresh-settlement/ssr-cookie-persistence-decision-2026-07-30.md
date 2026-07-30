# Supabase SSR cookie persistence decision — 2026-07-30

## Status

Generation 3's broad `TOKEN_REFRESHED` callback-error isolation is **superseded**.

Evidence class:

- `source-read` for the live `@supabase/ssr` cookie-writing subscriber;
- `target-executed` for unpatched auth-js and both generation-3 candidate variants;
- generation-4 implementation trial: prepared and executing in the owned fork.

Production implementation: absent.

Upstream contact authorized: `false`.

Upstream contact performed: `false`.

## Exact inputs

### Auth source and owned lab

- Supabase JS source pin: [`supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5).
- Executed owned comparison head: `teamleaderleo/supabase-js@265c1383d880e854b72e737fa7c7ae0570617963`.
- Three-way focused workflow: `30513520741`.

### SSR integration source

- `@supabase/ssr` source pin: [`supabase/ssr@69a6209482ddde7b1bd769f7c8ca9a604cb65960`](https://redirect.github.com/supabase/ssr/commit/69a6209482ddde7b1bd769f7c8ca9a604cb65960).

At that source, `createServerClient()` registers an async public `auth.onAuthStateChange()` subscriber. For `TOKEN_REFRESHED` and related session-changing events, it awaits `applyServerStorage()`. The storage helper awaits the framework-provided cookie `setAll()` operation.

A middleware cookie write failure is therefore a public auth subscriber failure, not optional observability work.

## Three-way executed comparison

### Unpatched source

The unpatched baseline passed one target-native test:

```text
1 suite passed
1 test passed
```

Controlled result:

1. refresh token exchange succeeds;
2. rotated session R2 is written to auth storage;
3. the SSR-style `TOKEN_REFRESHED` subscriber attempts to write the response cookie and throws;
4. the initiating public `refreshSession()` and a concurrent ordinary joiner both receive the failure;
5. only one token request and one cookie-write attempt occur;
6. internal auth storage contains R2;
7. the response cookie remains R1;
8. refresh-failure cooldown remains clear.

The existing source exposes persistence failure, although it does so through the same post-commit path that currently misclassifies a callback-thrown `AuthError`.

### Generation-3 early shared settlement

The early-settlement candidate passed:

```text
5 auth-js suites passed
18 auth-js tests passed
1 SupabaseClient wrapper suite passed
1 wrapper test passed
```

Its SSR consequence test confirms:

1. the first cookie write fails after R2 is committed;
2. the candidate logs and swallows that failure;
3. public `refreshSession()` continues and sends a second token request;
4. a second `TOKEN_REFRESHED` cookie-write attempt also fails and is swallowed;
5. the public caller receives success;
6. internal storage contains R2 while the response cookie remains R1;
7. cooldown remains clear.

A direct initiator plus ordinary joiner likewise both receive success after one swallowed cookie-write failure.

### Generation-3 token-aware committed result

The token-aware candidate passed the same test counts and the same SSR consequence controls.

It therefore shares the production blocker even though it preserves better old-token joiner timing than broad early settlement.

## Decision

Do **not** isolate every `TOKEN_REFRESHED` subscriber exception.

A refresh commit and its notification outcome are separate facts:

- the token exchange and internal storage commit may already be successful;
- an awaited subscriber may still own critical external persistence, such as SSR response cookies;
- ordinary callers need that persistence failure to remain visible;
- the rotated internal session must not be deleted merely because the subscriber error is an `AuthError` instance;
- refresh-failure cooldown must not start because the Auth service did not fail;
- every subscriber still needs an attempt before the failure is surfaced.

## Generation-4 candidate invariant

The next candidate should implement **committed refresh plus visible notification failure**:

1. save the rotated session before notification, preserving current commit ordering;
2. expose the committed result only to a nested refresh using the event's rotated refresh token while notification is in progress;
3. keep the initiating operation and ordinary old-token joiners pending until notification finishes;
4. attempt every subscriber;
5. on success, resolve every ordinary caller with the committed session;
6. on callback or notification-transport failure, reject or return an error to every ordinary public caller under the existing public `throwOnError` policy;
7. preserve rotated internal storage after post-commit notification failure;
8. leave `lastRefreshFailure` clear;
9. never route callback-thrown `AuthError` through refresh-token rejection cleanup;
10. avoid an unhandled rejection from the internal shared dependency when no joiner exists.

## Prepared owned variant

The owned lab now contains:

- patch: `.fieldwork/auth-refresh-settlement/patches/notification-failure-separation.patch`;
- tests: `.fieldwork/auth-refresh-settlement/notification-failure-separation.test.ts`;
- matrix variant: `notification-failure-separation`.

The trial uses a notification-scoped committed result for rotated-token reentry, retains the shared dependency for ordinary callers until notification completion, and adds a committed-result branch before the outer refresh-error classifier.

The first execution carrier stopped on malformed patch hunk metadata and supplied no source result. The metadata is repaired at owned head `b4bb48424b28776ca308cf87acaaf6da966483da`; exact execution is pending.

## Required generation-4 controls

1. nested default refresh from a `TOKEN_REFRESHED` callback returns R2 without another token request;
2. another callback throws after the nested refresh succeeds;
3. initiator and old-token joiner both receive the callback failure;
4. every callback is attempted;
5. no unhandled rejection occurs when the shared dependency has zero joiners;
6. callback-thrown `AuthError` remains visible under both `throwOnError` policies without session deletion or cooldown;
7. SSR-style `setAll` failure stops the public refresh after one token request;
8. notification transport failure rejects every ordinary caller after commit;
9. successful async cookie work remains awaited;
10. Realtime still receives the rotated token before refresh returns on the success path;
11. non-refresh callback failures retain their existing behavior.

## Boundaries

- #148 owns successful committed refresh settlement and post-commit notification ownership.
- #188 remains separate for total shared-promise settlement during failed-refresh cleanup.
- #189 remains separate for one-time `INITIAL_SESSION` delivery.
- SSR adapter behavior is an integration constraint on #148, not a new auth-js campaign.
- The public `refreshSession()` second request observed in generation 3 is recorded only as a consequence of swallowing the first persistence failure. It is not promoted as an independent defect without a clean successful-notification baseline.

No public Supabase or `@supabase/ssr` issue, pull request, review, comment, reaction, branch, or message was created or changed.
