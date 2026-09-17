# Supabase auth refresh notification settlement campaign

- Campaign issue: `#78`
- Parent scout: `#21`
- Programme: `sdk-integration-lifecycle` (`#13`)
- Target hub: `supabase` (`#12`)
- Worker: `chatgpt:gpt-5.6-thinking`
- State: `in progress`
- Retrieval date: `2026-07-30`
- Public source pin: [`supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5)
- Owned fork probe: [`teamleaderleo/supabase-js#1`](https://github.com/teamleaderleo/supabase-js/pull/1)
- Upstream contact: unauthorized; none occurred

## Campaign question

After a refresh response passes the existing storage and removal guards and the rotated session is saved, which internal result should become observable before `TOKEN_REFRESHED` subscribers complete, and how should subscriber failures be reported without changing successful auth-operation results or breaking SSR/serverless callback completion?

## Current answer

The narrow owner is the auth-js settlement boundary, rather than token rotation, the Auth service, or the public Supabase wrapper.

The client currently commits the rotated session and then waits for application subscribers before resolving the per-instance refresh single-flight. Two consequences follow:

1. a subscriber that awaits `refreshSession()` can wait on the unresolved refresh that is waiting on the subscriber;
2. a subscriber exception can cross into the already-committed refresh, reject the public call, and reject the internal Deferred without a joiner.

A broad non-blocking subscriber change conflicts with a real SSR contract. `@supabase/ssr` registers an async auth callback and awaits cookie persistence. The initiating auth operation must retain that callback in its await chain so the server response does not finish first.

The owned fork therefore compares two narrower variants:

- **early shared settlement:** resolve the shared refresh result after storage commit but before awaited subscribers;
- **notification-scoped committed result:** preserve shared-promise timing and expose the event session only while `TOKEN_REFRESHED` subscribers run.

Both variants keep the initiating operation waiting for callback completion, isolate subscriber exceptions from a committed `TOKEN_REFRESHED` result, preserve other auth-event error behavior, and keep notification transport failures visible.

## Exact current owner

### Manual refresh path

At the pinned revision, `_callRefreshToken` performs:

1. same-instance single-flight join through `refreshingDeferred`;
2. same-token failure cooldown;
3. Auth service request and retry;
4. before/after storage guard;
5. session-removal epoch guard around `_saveSession`;
6. persisted rotated session;
7. awaited `_notifyAllSubscribers('TOKEN_REFRESHED', session)`;
8. success result construction and `refreshingDeferred.resolve(result)`;
9. single-flight cleanup in `finally`.

The liveness cycle sits between steps 7 and 8.

### Notification path

`_notifyAllSubscribers`:

- optionally posts the event through `BroadcastChannel`;
- invokes every subscriber concurrently;
- awaits every returned promise;
- collects every callback error;
- logs every callback error;
- throws the first callback error after all callbacks settle.

The all-subscriber and awaited-completion behavior is deliberate and useful. The coupling of callback failure to the committed auth operation is the questionable part.

### Initialization path

[Supabase JS PR #2498](https://redirect.github.com/supabase/supabase-js/pull/2498) introduced `_pendingInitNotifications`. Auth events produced during initialization are queued until `initializePromise` resolves, then flushed in order while `initialize()` still waits for callback completion.

This changes the refresh-reentry analysis:

- during a manual refresh, the original `refreshingDeferred` is active while subscribers run;
- during a queued initialization event, the original refresh is already complete when subscribers run;
- a fix tied only to the active refresh Deferred misses queued initialization and can allow a nested no-argument `refreshSession()` to request a second rotation;
- a result scoped to the actual `TOKEN_REFRESHED` notification covers manual, queued initialization, and cross-tab delivery.

## Platform and application boundary

| Classification | Behaviour |
| --- | --- |
| Platform: Auth service | Rotates and converges refresh tokens; this campaign does not change the service contract |
| Platform: auth-js storage | Persists the rotated session before notifying subscribers |
| Platform: auth-js single-flight | Shares one in-progress refresh result inside one client instance |
| Platform: auth-js notification | Awaits every callback and propagates the first callback exception |
| Platform: SSR adapter | Uses an async auth callback to flush cookie changes during the request |
| Application trigger | Calls `refreshSession()` from a `TOKEN_REFRESHED` callback |
| Application trigger | Throws or rejects from a `TOKEN_REFRESHED` callback |
| Application policy, excluded | Authorization roles, row policies, product sign-out policy, or session-duration choices |

The callback code belongs to the application. The hang and state/result disagreement come from the client contract that makes a committed platform operation depend on arbitrary observer completion.

## History and intention

### Long-running callback reentry reports

The archived auth-js issue [#762](https://redirect.github.com/supabase/auth-js/issues/762) collected reports of auth methods and authenticated requests hanging when called from `onAuthStateChange`. Application workarounds moved asynchronous work into a later task. Those workarounds reduced deadlocks while giving up completion guarantees.

Supabase JS issue [#1566](https://redirect.github.com/supabase/supabase-js/issues/1566) recorded Capacitor/iOS OAuth flows where the session was stored and `SIGNED_IN` fired, while later auth or PostgREST work hung. The reporter later found that making the callback synchronous and deferring side effects reduced the problem. That observation supports callback reentry as a trigger, while it does not establish timer deferral as a safe library contract.

### Timer deferral was tried and reverted

[PR #2014](https://redirect.github.com/supabase/supabase-js/pull/2014) changed one OAuth exchange notification to `setTimeout(..., 0)` to release an older lock before callback execution.

Supabase JS issue [#2037](https://redirect.github.com/supabase/supabase-js/issues/2037) then showed a server boundary failure: `exchangeCodeForSession()` returned and the route response completed before `@supabase/ssr` wrote cookies. OAuth succeeded at the provider while the application remained logged out.

[PR #2039](https://redirect.github.com/supabase/supabase-js/pull/2039) restored awaited notification and repaired the SSR OAuth regression.

**Intent recovered:** callback completion can be part of the auth operation's useful result, especially when callbacks persist server response state.

### Global fire-and-forget was rejected

[PR #2016](https://redirect.github.com/supabase/supabase-js/pull/2016) proposed making `_notifyAllSubscribers` globally non-blocking. Review identified the same SSR cookie problem: `@supabase/ssr` has an async callback whose work must finish before a serverless response returns.

**Intent recovered:** the library should avoid making all observers detached merely to escape one circular dependency.

### Lockless coordination narrowed the remaining problem

[PR #2392](https://redirect.github.com/supabase/supabase-js/pull/2392) removed the default Web Locks mutex, added refresh commit guards and `dispose()`, and deliberately retained awaited subscribers. Its documentation explicitly records one residual hazard: `refreshSession()` inside `TOKEN_REFRESHED` joins the unresolved refresh Deferred.

The lockless migration also warns that internal await changes alter microtask order and that downstream tests should avoid depending on incidental request order.

**Intent recovered:** in-instance refresh deduplication belongs to `refreshingDeferred`; cross-tab convergence belongs to the Auth service; callback waiting remains part of the public timing contract.

### Initialization used dependency-first settlement

Issue [#2491](https://redirect.github.com/supabase/supabase-js/issues/2491) reported sign-in and recovery operations hanging after the server had already returned success.

[PR #2498](https://redirect.github.com/supabase/supabase-js/pull/2498) fixed a separate promise cycle by queuing initialization events until `initializePromise` resolved, then flushing callbacks in order while `initialize()` continued to await them.

**Intent recovered:** an internal dependency may settle before callback execution while the initiating public operation still waits for callbacks. This is the closest accepted precedent for early shared refresh settlement.

### Broad async warnings were rejected

[PR #2477](https://redirect.github.com/supabase/supabase-js/pull/2477) proposed warning whenever an async callback was registered. It was closed because most async callbacks are now valid, and `@supabase/ssr` itself registers one on every server client. The maintainer response said residual handling should live at the actual `_callRefreshToken` reentry point to avoid false positives.

**Intent recovered:** target the exact hazardous operation rather than treating `async` syntax as misuse.

## Variant A: early shared settlement

### Change

After successful storage commit:

1. construct the successful refresh result;
2. clear the same-token failure cache;
3. resolve `refreshingDeferred`;
4. await `TOKEN_REFRESHED` subscribers;
5. return from the initiating refresh after subscribers finish.

During actual `TOKEN_REFRESHED` dispatch, also expose the event session to calls carrying its rotated token. This covers queued initialization and cross-tab events where no original Deferred remains.

### Expected strengths

- default nested refresh receives the committed session;
- explicit nested refresh carrying the old token receives the already-resolved manual-refresh Deferred;
- one service request occurs in the manual reproducer;
- queued initialization and cross-tab no-argument callbacks avoid a second rotation;
- the initiating refresh still waits for SSR cookie work;
- callback exceptions cannot reject an unresolved internal Deferred.

### Compatibility cost

Every concurrent caller already joined to the refresh Deferred may settle before subscriber completion, including a caller outside the callback that carries the old token.

That timing was previously coupled to subscriber completion. The returned credentials are already committed, but downstream code may have treated refresh completion as evidence that all auth observers also finished.

## Variant B: notification-scoped committed result

### Change

Keep `refreshingDeferred` settlement after subscriber completion. While `TOKEN_REFRESHED` subscribers are actually running, expose `{ data: eventSession, error: null }` to calls carrying the event's rotated token.

### Expected strengths

- default nested `refreshSession()` reads the rotated token from storage and receives the event session;
- manual, queued initialization, and cross-tab no-argument callbacks avoid another service request;
- ordinary old-token joiners preserve their current wait timing;
- the initiating refresh still waits for SSR cookie work;
- the change exists only during the notification window.

### Completeness cost

An explicit nested call carrying the old refresh token does not match the event token. During manual refresh it still joins the unresolved Deferred and reproduces the cycle. During queued or cross-tab notification it can start a new refresh.

This is a real gap, though explicitly passing the stale token from inside the event is narrower than the common no-argument call.

## Candidate C: typed fail-fast reentry

A maintainer comment on PR #2477 suggested failing at the `_callRefreshToken` reentry point.

The difficulty is caller identity. Browser JavaScript does not provide a portable asynchronous call-context primitive that distinguishes:

- a call awaited by the active subscriber;
- an unrelated caller that happens to invoke refresh while the subscriber is running.

A client-wide `isNotifying` flag would classify both. Node's `AsyncLocalStorage` is unsuitable for the browser package. A public callback context or operation token would be more precise but expands the API.

A typed error can still be considered for an old-token call during active notification, but it may reject unrelated concurrent callers and would require a new public error contract. It remains a design candidate rather than an experiment patch.

## Error ownership

The experiment treats callback exceptions and notification transport failures differently.

### Callback exceptions during `TOKEN_REFRESHED`

- invoke every subscriber;
- await every subscriber;
- log every exception;
- keep the committed refresh result successful;
- avoid rejecting the internal Deferred;
- avoid an unhandled rejection.

### Other auth-event callback exceptions

Keep current propagation. This campaign has no evidence supporting a global error-semantics change for sign-in, sign-out, user update, recovery, or MFA events.

### Notification transport failure

Keep propagation. A `BroadcastChannel.postMessage` failure is produced by the auth client notification mechanism rather than application callback code. The focused tests ensure it is not hidden by subscriber-error isolation.

## Patterns to keep

- **Commit before observation:** callbacks receive a session already stored locally.
- **Initiator waits for required side effects:** SSR cookie persistence remains inside the auth call's await chain.
- **All observers receive the event:** one callback failure does not skip later callbacks.
- **Single service rotation:** nested session retrieval should consume the committed event result.
- **Service/client responsibility split:** server convergence handles cross-tab token races; client code handles local settlement and observer delivery.
- **Bounded event context:** any temporary committed result is visible only during the corresponding notification.
- **Explicit timing tests:** concurrent caller timing is an acceptance property rather than an accidental microtask outcome.

## Anti-patterns to avoid

1. **Global fire-and-forget callbacks.** Breaks SSR completion and changes every auth event.
2. **`setTimeout(0)` as synchronization.** Moves work beyond server request lifetime and creates scheduler-dependent behavior.
3. **`queueMicrotask` as a substitute.** It changes ordering without expressing ownership and still does not guarantee a server framework waits for the task.
4. **Warn on every async callback.** Produces false positives for supported usage and for `@supabase/ssr` itself.
5. **Swallow every notification error.** Hides client transport failures and changes unrelated auth operations.
6. **Rotate again to read the event session.** Adds token churn and can recurse indefinitely.
7. **Client-wide reentry flags presented as caller identity.** Conflate callback ancestry with coincidence.
8. **Node-only async context in browser code.** Breaks runtime portability.
9. **Credentials in debug tags.** Refresh-token fragments must remain absent from logs.
10. **Microtask-order assumptions.** Internal await changes can reorder parallel downstream work.
11. **Patch every auth event.** The reproduced state/result divergence belongs to a committed refresh.
12. **Treat application authorization as part of this campaign.** Roles and row policies do not own the settlement cycle.

## Owned-fork experiment

Draft PR: [`teamleaderleo/supabase-js#1`](https://github.com/teamleaderleo/supabase-js/pull/1)

The branch contains:

- two patch files applied independently to the pinned source;
- focused real-code Jest tests;
- a shell runner that restores the checkout after each variant;
- a GitHub Actions matrix;
- a dependency-free executable model and recorded result;
- this campaign's history and guardrails mirrored in the fork README.

### Real-code test matrix

The tests cover:

1. default nested manual refresh returns the rotated session;
2. exactly one token-service stub call;
3. callback exception logging, all-subscriber delivery, successful outer result, and no unhandled rejection;
4. initiating refresh remains pending until SSR-like async work finishes;
5. old-token joiner timing distinguishes variants;
6. explicit old-token nested behavior distinguishes variants;
7. queued initialization callback receives the event session without a second rotation;
8. cross-tab callback receives the event session without a second rotation;
9. non-refresh callback errors retain current rejection behavior;
10. BroadcastChannel transport failure remains visible;
11. stored and returned credentials agree.

### Executable model result

Both variants produce:

- default nested result `R2`;
- queued default nested result `R2`;
- one service call;
- stored and returned token agreement;
- logged callback failure with all callbacks visited;
- initiating refresh pending until the SSR-like callback gate is released.

The distinguishing outcomes are:

| Property | Early shared settlement | Notification-scoped result |
| --- | --- | --- |
| Old-token joiner before callback completion | settles | waits |
| Explicit old-token nested call during manual refresh | succeeds | bounded probe times out |

The model preserves the selected promise relationships and omits package initialization, storage adapters, BroadcastChannel implementation, TypeScript compilation, and the full Jest environment. It supports the comparison but does not establish package-level compatibility.

## Current validation state

- Owned-fork draft PR is open and mergeable.
- The focused two-variant workflow and the fork's ordinary pull-request checks have been queued.
- Full upstream pnpm/Jest/Docker execution remains unavailable in the local runner because the runner cannot resolve GitHub for cloning.
- No production branch has been selected.

## Preliminary recommendation

The design trade is now explicit:

- Variant A is more complete for explicit old-token manual reentry and has a strong precedent in PR #2498, but it releases all refresh joiners before callback completion.
- Variant B preserves ordinary joiner timing and covers the common no-argument API across manual, initialization, and cross-tab events, but it leaves explicit stale-token reentry unresolved.

Do not select a production patch until the real-code matrix passes. If both pass, prefer Variant B when compatibility conservatism outranks the explicit stale-token edge. Prefer Variant A when the contract is defined as “storage commit settles the shared refresh result,” and document that subscriber completion remains guaranteed only to the initiating call.

A typed fail-fast result remains available if maintainers prefer explicit rejection over either timing change, but precise caller ancestry would require a larger public design.

## Remaining questions

- Does any supported downstream client rely on a concurrent joined refresh waiting for all auth subscribers?
- Should a `TOKEN_REFRESHED` callback exception remain console-only, or should auth-js expose an optional observer-error hook?
- Should explicit stale-token reentry return the event session, a typed error, or retain current behavior?
- Should the notification-scoped result be available to cross-tab callbacks, where it can avoid a redundant refresh without a local in-flight operation?
- Does a custom `PromiseConstructor` change the internal Deferred rejection observation result?
- Does `dispose()` during notification need separate treatment? It remains outside this campaign's chosen owner.

## Stop conditions

Stop or narrow if:

- the focused real-code tests disprove the synthetic result;
- either patch requires global non-blocking subscribers;
- callback-error isolation hides transport failures;
- nested retrieval requires another service rotation;
- the result depends on a framework-specific scheduler;
- a current upstream patch already covers the same pinned behavior and acceptance cases;
- the work requires production credentials, hosted data, or upstream contact.

## Upstream boundary

No upstream issue, pull request, discussion, comment, review, reaction, or message was created or changed. Any upstream packet remains held for separate human authorization.
