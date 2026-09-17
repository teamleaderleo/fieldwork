# Supabase token refresh, explained with keys and a doorbell

## The tiny story

Imagine an app has a key that opens a clubhouse door.

The key expires sometimes, so the app asks Supabase for a new key.

Supabase gives the app a new key. The app puts the new key safely in its pocket. Then the app rings a doorbell to tell everyone inside:

> We have a new key.

The people listening to that doorbell are application callbacks registered with `onAuthStateChange`.

## What happens today

The client currently does this:

1. Ask the Auth service for a new key.
2. Save the new key.
3. Ring the `TOKEN_REFRESHED` doorbell.
4. Wait for every listener to finish.
5. Mark the refresh operation complete.

Waiting for listeners is useful. A server-side listener may need to copy the new key into an HTTP cookie before the server sends its response.

The trouble comes from treating the saved key and every listener's work as one indivisible result.

## The circular-wait problem

One listener hears, “We have a new key,” and asks:

> Great. Can you refresh the key for me?

The inner refresh sees that a refresh is already running and waits for it.

The outer refresh is waiting for the listener.

So:

- the listener waits for the refresh;
- the refresh waits for the listener.

They can wait forever even though the new key is already saved.

## The callback-error problem

A listener can also throw an application error after the new key was saved.

Today that error can travel backward into the refresh operation. The caller hears, “Refresh failed,” while storage already contains the new key.

That gives the application two conflicting stories:

- stored state says success;
- the returned promise says failure.

The internal shared refresh promise can also reject without anybody waiting on that rejection.

## Why the server version is harder

A browser listener may update a menu or cache.

A server listener may write cookies into the response being prepared for the browser. `@supabase/ssr` uses an async auth listener for exactly this job.

Supabase previously tried moving auth listener work into a later timer. That avoided one deadlock, but a serverless request could finish before the timer ran. OAuth succeeded, yet the browser received no login cookie and still looked signed out.

So the library cannot simply ring the bell and walk away.

The initiating auth operation must keep waiting for required listener work, especially cookie persistence.

## Experiment A: finish the shared refresh early

After saving the new key:

1. mark the shared refresh result successful;
2. ring the bell;
3. continue waiting for every listener;
4. let the initiating caller return after the listeners finish.

This breaks the circular wait, including the unusual case where the listener explicitly supplies the old key.

Its cost is wider. Other callers already waiting on the shared refresh can receive success before the listeners finish.

A deeper audit found another cost: if the doorbell transport itself fails after the shared result was marked successful, joined callers can receive success while the initiating caller receives an exception. One refresh then has two answers.

## Experiment B: lend listeners the key already carried by the event

Keep the shared refresh completion timing unchanged.

While the `TOKEN_REFRESHED` bell is actively ringing, temporarily expose the event's saved key. A normal nested `refreshSession()` reads that key and receives the existing successful result instead of asking the Auth service to rotate again.

This works for:

- a manual refresh;
- a refresh event delayed until client initialization finishes;
- a refresh event received from another browser tab.

Ordinary callers using the old key keep their current waiting behavior.

The remaining gap is narrow: a listener that explicitly passes the stale, pre-refresh key can still enter the circular wait during a manual refresh.

## Current preference

Experiment B is the safer starting point.

It fixes the normal public usage while changing less timing for unrelated callers. It also avoids the “joined caller says success, initiating caller says failure” split found in Experiment A.

The stale-key edge still needs a deliberate answer. Possible choices include a dedicated typed error or an explicit callback context in a future API. A client-wide boolean cannot reliably tell a listener call from unrelated code that happens to run at the same time.

## What this finding means

This is a client reliability and state-consistency problem.

It can cause:

- auth calls that never settle;
- screens or workers waiting indefinitely;
- stored credentials disagreeing with returned results;
- duplicate retries or application actions;
- confusing unhandled promise errors.

The evidence does not indicate credential theft, an authorization bypass, or broken token rotation in the Auth service.

## Source trail

- Current auth callback contract and the documented residual refresh cycle: [pinned `GoTrueClient.ts`](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/src/GoTrueClient.ts)
- Current lockless migration notes: [lockless coordination migration](https://redirect.github.com/supabase/supabase-js/blob/63318987365bbcea2c31a00b62cbb95b21083ad5/packages/core/auth-js/migrations/lockless-coordination.md)
- Timer-based notification change: [PR #2014](https://redirect.github.com/supabase/supabase-js/pull/2014)
- SSR cookie regression report: [issue #2037](https://redirect.github.com/supabase/supabase-js/issues/2037)
- Revert restoring awaited SSR behavior: [PR #2039](https://redirect.github.com/supabase/supabase-js/pull/2039)
- Global non-blocking callback proposal and maintainer reasoning: [PR #2016](https://redirect.github.com/supabase/supabase-js/pull/2016)
- Lockless refactor retaining awaited callbacks: [PR #2392](https://redirect.github.com/supabase/supabase-js/pull/2392)
- Initialization-cycle fix: [PR #2498](https://redirect.github.com/supabase/supabase-js/pull/2498)
- Broad async-warning proposal and exact-reentry guidance: [PR #2477](https://redirect.github.com/supabase/supabase-js/pull/2477)
- Current SSR cookie callback: [pinned `createServerClient.ts`](https://redirect.github.com/supabase/ssr/blob/69a6209482ddde7b1bd769f7c8ca9a604cb65960/src/createServerClient.ts)
- Auth service refresh-token convergence: [pinned token service](https://redirect.github.com/supabase/auth/blob/163ab6faf15b3a4e578ce2f7f2e3f2725768dd05/internal/tokens/service.go)
