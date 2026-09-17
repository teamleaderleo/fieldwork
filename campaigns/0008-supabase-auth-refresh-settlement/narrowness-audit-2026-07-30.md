# Supabase candidate narrowness audit — 2026-07-30

State: `ready-for-review`

Campaign: #78

Central candidate: #148

Parent scout: #21

Fieldwork PR: #91

Owned experiment: `teamleaderleo/supabase-js#1`

Review date: `2026-07-30`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

Candidate #148 is a correctness repair, not a feature request.

The existing public operations already allow an auth listener to call `refreshSession()`. Current auth-js can turn that supported composition into a permanent wait during `TOKEN_REFRESHED`, and it can report failure after the rotated session has already been stored.

The proposed correction does not add a new public option, auth event, network retry policy, timer, reconnect listener, storage format, or service endpoint. It changes who may consume an already-committed refresh result during one notification window and how application-listener exceptions affect that committed result.

The candidate is narrow in ownership and change surface. It still has one compatibility-sensitive behavior change: a `TOKEN_REFRESHED` listener exception would be logged and isolated instead of rejecting the initiating refresh after commit. That exact boundary deserves independent review and integration controls.

## Why this is a defect correction

The candidate repairs existing behavior rather than introducing a new capability:

1. `refreshSession()` and async `onAuthStateChange` listeners already exist.
2. The current source and lockless-refactor history explicitly identify refresh from `TOKEN_REFRESHED` as the residual reentry hazard.
3. A normal no-argument nested refresh can wait forever even though the rotated session is already in storage.
4. A listener exception can make the public result disagree with committed storage.
5. Applications do not opt into a new lifecycle mode to receive the correction.
6. The desired result is preservation of the already-established one-refresh, awaited-listener, committed-session contract.

This is closer to correcting promise and result ownership than adding a user-facing auth feature.

## Expected production change surface

No clean production branch exists yet. The preferred candidate would likely require only these auth-js changes:

- one private notification-scoped committed-result slot;
- one early `_callRefreshToken` check for the rotated event token;
- set and clear that slot around actual `TOKEN_REFRESHED` delivery;
- retain the existing shared Deferred timing for old-token joiners;
- isolate application callback exceptions only for committed `TOKEN_REFRESHED` success;
- preserve rejection for notification transport failure and non-refresh event callback failure;
- place focused controls in normal auth-js test locations.

The first production candidate should not change:

- Auth service token rotation or reuse behavior;
- refresh request or response wire format;
- persisted session schema;
- public auth options;
- public auth event names;
- retry count, backoff, cooldown, online detection, or reconnect policy;
- automatic refresh ticker policy;
- SupabaseClient production behavior outside regression coverage;
- SSR adapter APIs;
- Realtime protocol behavior;
- application authorization or RLS policy.

## Compatibility-sensitive boundary

### Listener exception ownership

Current behavior allows an application callback exception to reject the initiating refresh after the new session has been stored.

The preferred candidate changes that result for `TOKEN_REFRESHED` only:

- all listeners still run;
- listener exceptions are still recorded;
- the initiating operation still waits for listener completion;
- the committed refresh returns success;
- transport errors remain failures;
- callback errors for other events retain current rejection behavior.

This is the largest user-visible compatibility decision in the candidate. Review should confirm that committed auth success is the correct owner and that applications still have a sufficient diagnostic path for callback failures.

### Token-and-time scope

The proposed slot identifies calls by the rotated refresh token during the active event window. It does not prove JavaScript callback ancestry.

An unrelated caller using that same rotated token during the window may receive the committed event result. The result is still the same current session and does not trigger a second rotation, but the concurrency boundary must be described accurately.

### Explicit stale-token reentry

A callback that explicitly supplies the old token remains outside the preferred first correction:

```ts
refreshSession({ refresh_token: oldToken })
```

Handling that case may require a typed error or a larger callback-context contract. Broad early settlement is rejected because it changes every joined caller and can split caller-visible outcomes after a transport failure.

## Comparison with nearby Supabase work

| Work | Classification | Public surface | Breadth | Relationship to #148 |
| --- | --- | --- | --- | --- |
| Candidate #148 | correctness repair | none proposed | one auth settlement and callback-error boundary | current campaign |
| [Offline refresh and reconnect proposal](https://redirect.github.com/supabase/supabase-js/pull/2568) | broad lifecycle bug fix | no new option, but new online/offline behavior | retry, cooldown, reconnect, initialization, disposal, ticker | rebase and compatibility input |
| [Automatic refresh failure-limit proposal](https://redirect.github.com/supabase/supabase-js/pull/2573) | opt-in feature request | new option and new auth event | ticker, failure accounting, subscriber API, wrapper types | separate feature and subscriber-matrix input |
| [Realtime callback-mode initialization correction](https://redirect.github.com/supabase/supabase-js/pull/2464) | narrow wrapper correctness repair | no new API | SupabaseClient initialization and tests | useful comparison and regression input |
| [JWT expiration cross-check proposal](https://redirect.github.com/supabase/supabase-js/pull/2542) | proposed read-path correctness repair | no new API | stored-session read and tests | separate candidate with unresolved review defects |

The comparison supports calling #148 narrow. PR #2464 is the closest scale comparison: it corrects existing callback-mode ownership in two files without adding a public feature. PR #2568 is also a bug fix, but it intentionally changes several lifecycle owners. PR #2573 is explicitly an opt-in feature with a public option and event.

## Adjacent review: Realtime callback-mode initialization

The [Realtime callback-mode initialization correction](https://redirect.github.com/supabase/supabase-js/pull/2464) replaces an explicit token fetch plus `setAuth(token)` with `realtime.setAuth()` so Realtime remains in callback-managed mode.

Current Realtime source supports that intent:

- `setAuth()` without a token invokes the configured callback;
- the auth promise is registered before awaiting the callback;
- connection setup can wait for that in-flight auth promise;
- callback failure falls back to the cached token and is logged inside Realtime.

This is a similarly narrow correctness repair. It also strengthens the production gate for #148: the SupabaseClient regression should cover both ordinary auth-session forwarding and custom callback-managed Realtime auth, rather than assuming every client uses the same token owner.

## Adjacent review: JWT expiration cross-check

The [JWT expiration cross-check proposal](https://redirect.github.com/supabase/supabase-js/pull/2542) is small by changed-file count, but it is not currently review-ready.

### Source and claim concerns

1. The production patch decodes the access token once for syntax and again for `exp` reconciliation.
2. Local JWT decoding reads claims but does not verify the token signature.
3. Local `exp` inspection cannot detect server-side revocation, admin sign-out, or password-change invalidation.
4. A syntactically valid tampered token can carry an arbitrary `exp`; decoding alone does not establish authenticity.
5. The patch mutates `currentSession.expires_at` in memory but does not visibly persist the corrected value back to storage in the shown change.
6. An expired JWT with a future session-level expiry enters the existing refresh path; whether the caller receives null, a preserved session, or an error depends on refresh behavior rather than expiration decoding alone.

The PR rationale should therefore be narrowed to syntactic decoding and local expiration-metadata consistency. Revocation and authenticity claims require server verification.

### Test and execution concern

The current test patch begins the next test before closing the first new test block. The retained diff is syntactically incomplete.

The exact PR head has no successful ordinary target execution receipt. Its pull-request workflows are recorded as `action_required`, and the automated review reported parser failures in the test file.

Assessment:

**Source-read review finding; do not promote the patch as executed or ready.**

This is a useful contrast for Fieldwork: a two-file diff can still contain a broken test carrier and an overbroad security explanation. Narrowness requires a bounded owner, accurate claims, and an executable final diff.

## Self-review of candidate #148

### Strongest supported conclusion

Candidate #148 is a narrow correctness contract for an existing permanent-wait and committed-result disagreement.

### What remains unproved

- clean production implementation;
- real SSR cookie behavior;
- browser BroadcastChannel exchange;
- React Native persisted-session behavior;
- live Auth or hosted-project behavior;
- custom Promise compatibility;
- exact application diagnostics for isolated listener errors;
- explicit stale-token handling.

### Disposition

**ACCEPT classification as a narrow correctness candidate. HOLD production promotion for independent exact-head review, a clean one-candidate branch, and the named integration gates.**

## Recent Fieldwork process review

Draft PR #143 applied the requested gate-scoped `full-gate` and reviewed-input-generation repairs. The repair is coherent and candidate #148 is a direct dogfood case.

Draft PR #156 adds useful operational advice but currently creates a second project-wide review vocabulary. Its evidence classes and dispositions conflict with PR #143, and it treats contact authorization as a possible review disposition.

Review disposition recorded on #156:

- retain the execution and synchronization guidance;
- keep `REVIEWING.md` from #143 as the sole canonical promotion vocabulary;
- restack the newer material as a subordinate runbook;
- import rather than redefine evidence classes and dispositions;
- keep upstream authorization as a separate explicit authority input.

## Next useful work

1. obtain an independent exact-head disposition on #148;
2. keep the two-variant fork PR as research rather than production code;
3. create one clean production branch only after candidate acceptance;
4. add normal auth-js tests and SupabaseClient/Realt​ime token-owner controls;
5. run writable and intentionally non-writing SSR cookie controls;
6. run browser or React Native notification controls;
7. rebase over accepted auth lifecycle work without importing unrelated features;
8. keep all public Supabase interaction unauthorized until a separate decision.

## Boundary

No public Supabase issue, pull request, comment, review, reaction, branch, or message was created or changed during this audit.