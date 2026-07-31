# Supabase auth callback-error ownership continuation audit — 2026-07-30

State: `active-validation`

Campaign: #78

Central candidate: #148 generation 2 at the start of this audit

Parent scout: #21

Fieldwork PR: #91

Owned experiment: `teamleaderleo/supabase-js#1`

Supabase source pin: `63318987365bbcea2c31a00b62cbb95b21083ad5`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

The preferred `TOKEN_REFRESHED` correction remains narrow, but the source review found a stronger reason for it.

A refresh listener can throw an error object that Supabase recognizes as an `AuthError`. Current `_callRefreshToken` then treats the application callback failure as though token rotation failed. When the old access token is expired, that catch path can remove the newly stored rotated session and cache the listener error under the old refresh token.

The candidate must therefore separate successful refresh commit from application callback failure before the generic refresh-error catch classifies the exception.

The review also found two different callback-error bugs outside candidate #148:

1. a throwing `SIGNED_OUT` listener during failed-refresh cleanup can leave concurrent refresh joiners pending forever;
2. a throwing `INITIAL_SESSION` callback is called again with `null`, so one application exception can look like a second session state transition.

Those findings have different owners and should remain separate candidates after target execution confirms the focused tests.

## Source freshness

The public Supabase JS head remains [`63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5).

No later merged source revision changes the callback, refresh settlement, or disposal behavior described here.

## Finding A — `TOKEN_REFRESHED` callback `AuthError` can be misclassified as refresh failure

Evidence class before the new run: `source-read` plus `target-test-prepared`.

### Current path

At the source pin, `_callRefreshToken`:

1. fetches and validates the rotated session;
2. passes the storage and removal guards;
3. saves the rotated session;
4. awaits `_notifyAllSubscribers('TOKEN_REFRESHED', session)`;
5. constructs and resolves the successful shared result afterward.

`_notifyAllSubscribers` runs every callback, records callback exceptions, logs them, and throws the first collected error.

The outer `_callRefreshToken` catch then asks whether the thrown value is an `AuthError`. `AuthError` is publicly exported and uses an internal marker checked by `isAuthError`.

When a listener throws an `AuthError`, current code enters the ordinary token-refresh failure branch. For a non-retryable error it reads the stored session and checks whether its access token is still valid. If the token is expired, it calls `_removeSession`, then caches the error as the latest refresh failure and resolves the shared Deferred with an error result.

Because the rotated session was already saved before notification, this can delete valid newly rotated credentials due solely to an application callback exception.

### `throwOnError` interaction

`throwOnError` is a public `GoTrueClientOptions` flag. It changes whether an auth result containing an error is returned or thrown.

It does not prevent callback errors from entering `_callRefreshToken`:

- with `throwOnError: false`, an `AuthError` callback exception may be returned as the refresh error after cleanup;
- with `throwOnError: true`, the same error may be thrown by the public method;
- the destructive storage and cooldown classification occurs before the public return policy is applied.

The preferred candidate should return committed refresh success under both modes while retaining callback diagnostics.

### Candidate impact

This strengthens candidate #148 without expanding its owner.

The notification-scoped committed result plus event-specific callback-error isolation prevents the callback exception from crossing into the generic refresh catch. It should preserve:

- the rotated session in storage;
- a null refresh-failure cooldown entry;
- successful public refresh under both `throwOnError` modes;
- awaited callback completion;
- callback error logging;
- caller-visible notification transport failures.

The owned lab now includes this matrix at head `e7fdfbbe4818d764f1ec85186388b901477e9b6b`; execution is pending at the time this note was created.

## Finding B — failed-refresh `SIGNED_OUT` callback can orphan the shared Deferred

Evidence class before the new run: `source-read` plus `target-test-prepared`.

### Current path

For a non-retryable refresh failure after the access token has expired, `_callRefreshToken` awaits `_removeSession()` before it resolves `refreshingDeferred` with the refresh error.

`_removeSession()`:

1. increments the removal epoch;
2. clears cached refresh failure state;
3. removes session and verifier storage;
4. awaits `_notifyAllSubscribers('SIGNED_OUT', null)`.

If a `SIGNED_OUT` subscriber throws, `_removeSession()` rejects. That exception exits the `_callRefreshToken` catch before these later lines run:

- refresh-failure cache assignment;
- `refreshingDeferred.resolve(result)`.

The `finally` block clears `this.refreshingDeferred`, but it does not settle the Deferred object already returned to concurrent joiners.

Result:

- the initiating call rejects with the subscriber exception;
- storage is removed;
- a concurrent caller that joined the shared Deferred can remain pending indefinitely.

### Ownership

Do not fold this into #148. It belongs to refresh-failure teardown and total single-flight settlement, not successful `TOKEN_REFRESHED` result ownership.

A later candidate should decide how cleanup/subscriber failures are aggregated while guaranteeing that every created refresh Deferred settles exactly once.

The owned lab records the current pending-joiner result as a bounded negative characterization. It does not propose a repair yet.

## Finding C — `INITIAL_SESSION` callback failure produces a second null delivery

Evidence class before the new run: `source-read` plus `target-test-prepared`.

### Current path

`onAuthStateChange` registers a callback, then starts an unawaited async task that calls `_emitInitialSession` after initialization.

`_emitInitialSession` wraps both session retrieval and the application callback in one `try` block. Its catch block calls the same callback again with `INITIAL_SESSION, null`, then logs the original error.

If the first callback receives a real session and throws:

1. the application sees `INITIAL_SESSION` with the stored session;
2. the catch treats the callback exception as a session-loading failure;
3. the application sees a second `INITIAL_SESSION` with `null`;
4. the original callback error is logged.

If the callback also throws for the null delivery, that second exception can escape the unawaited task.

### Ownership

Keep this outside #148. It is initial-session callback error classification and delivery multiplicity.

A focused characterization now records the two deliveries. A future repair should separate session-loading errors from callback errors and must preserve the one-initial-delivery contract deliberately.

## Disposal classification correction

The earlier campaign ranking included an in-flight-disposal generation fence as a possible candidate.

Current source and `migrations/lockless-coordination.md` explicitly document the opposite contract:

- `dispose()` tears down timers, visibility handling, BroadcastChannel, and subscribers;
- it does not abort in-flight fetches;
- an in-flight refresh may still write a rotated session after disposal;
- a later client using the same storage key may consume that session.

Assessment:

**Reject an in-flight generation fence as a defect correction under the current contract.**

It may be considered later as a lifecycle-isolation feature or a v3 behavior decision, but it should not remain ranked beside confirmed correctness defects.

## Promise-constructor gate correction

`Deferred` has a mutable static `promiseConstructor` test seam, but `GoTrueClientOptions` exposes no custom Promise option and code search finds no target tests or documented consumer contract for replacing it.

Assessment:

- retain one internal thenable/single-flight control where useful;
- do not describe arbitrary custom Promise compatibility as a public production gate;
- focus the public compatibility matrix on `throwOnError`, custom storage, custom fetch, legacy custom lock, browser BroadcastChannel, SSR adapters, and Realtime token ownership.

## Callback error ownership map

The source currently uses different callback-error rules by path:

| Path | Current callback-error result |
| --- | --- |
| successful direct `TOKEN_REFRESHED` | crosses into `_callRefreshToken`; may reject or be misclassified as refresh failure |
| queued initialization notification | can reject `initialize()` after its internal dependency settled |
| incoming BroadcastChannel event | `_notifyAllSubscribers` logs/throws; channel handler catches and debug-logs |
| failed-refresh `SIGNED_OUT` cleanup | can replace refresh failure and orphan joined Deferred callers |
| initial `INITIAL_SESSION` delivery | callback is called again with `null`; second throw can escape unawaited task |
| ordinary direct non-refresh events | callback error crosses into the initiating public operation |

This map argues against a global fire-and-forget rewrite. Each event path has different transaction and delivery ownership.

## Updated candidate ordering

1. **#148 — successful `TOKEN_REFRESHED` notification settlement.** Keep the notification-scoped committed result and event-specific callback-error isolation. Add the `AuthError`/`throwOnError` controls.
2. **Failed-refresh teardown total settlement.** Characterize and then guarantee every shared Deferred settles even when storage cleanup or `SIGNED_OUT` subscribers fail.
3. **Initial-session callback error ownership.** Prevent callback failure from becoming a second null initial-session delivery.
4. **Refresh response diagnostics.** Keep successful-response service headers as a separate observability design.
5. **In-flight disposal isolation.** Demote from defect candidate to explicit feature or major-version contract decision.

## Recent Fieldwork review lessons applied

The broader Fieldwork review sweep reinforces these reporting rules:

- one candidate must own one decision-sized behavior boundary;
- an execution carrier is not a production branch;
- evidence must be claim-scoped rather than represented by one strongest label;
- exact candidate issue generation and code heads are both review inputs;
- temporary self-publishing workflows must be removed after receipts transfer;
- live issue, durable report, PR description, and review queue must move together when the decision changes.

Candidate #148 should advance to a new generation only after the focused exact-head run completes and the durable evidence head is synchronized.

## Pending exact-head execution

Owned experiment head: `e7fdfbbe4818d764f1ec85186388b901477e9b6b`

Queued workflows at note creation:

- Fieldwork auth refresh settlement;
- SDK Compliance;
- ordinary pull-request CI;
- expected draft merge blocker.

The focused settlement workflow now includes:

- `TOKEN_REFRESHED` callback `AuthError` controls under `throwOnError: false` and `true`;
- failed-refresh `SIGNED_OUT` callback orphan characterization;
- `INITIAL_SESSION` callback double-delivery characterization;
- the previous two-variant settlement and transport matrix.

No executed result is claimed until the workflow completes on the exact head.

## Next bounded actions

1. inspect the focused workflow result and logs at `e7fdfbbe4818d764f1ec85186388b901477e9b6b`;
2. repair the test harness if the assertion does not reach the intended source path;
3. update #148 only with the successful-refresh `AuthError` evidence;
4. create separate central candidates for Findings B and C only after target execution confirms them;
5. update campaign #78, PR #91, the owned experiment PR, and the review queue together;
6. keep the production branch absent until independent review accepts #148;
7. keep every public Supabase interaction unauthorized.

## Boundary

No public Supabase issue, pull request, comment, review, reaction, branch, or message was created or changed during this continuation audit.