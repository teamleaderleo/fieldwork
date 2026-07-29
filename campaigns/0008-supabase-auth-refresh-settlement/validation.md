# Validation record

## Scope

- Campaign: `#78`
- Parent scout: `#21`
- Owned fork PR: [`teamleaderleo/supabase-js#1`](https://github.com/teamleaderleo/supabase-js/pull/1)
- Source pin: [`supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5)
- Experiment head: `teamleaderleo/supabase-js@f589f01234bf057c6d872ac44a1255fe31b433cf`
- Validation date: `2026-07-30`
- Upstream contact authorized: `false`

## Corrected focused workflow

Workflow run: `teamleaderleo/supabase-js` run `30485952998`

The workflow:

1. checks out the owned-fork draft pull request;
2. reads Node from the repository `.nvmrc` (`22`);
3. installs the pinned pnpm workspace;
4. syntax-checks the experiment runner;
5. regenerates and compares the dependency-free model result;
6. applies one candidate patch to the pinned real `GoTrueClient.ts`;
7. copies three focused Jest files into auth-js;
8. runs the tests through the repository's auth-js Jest configuration;
9. restores the checkout.

## Focused result

| Variant | Test suites | Tests | Result | Clean exit |
| --- | ---: | ---: | --- | --- |
| Early shared settlement | 3 | 11 | pass | yes |
| Notification-scoped committed result | 3 | 11 | pass | yes |

The earlier run passed its assertions but emitted a Jest open-handle warning because the experiment's timeout races left losing timers alive. The timeout helpers were changed to clear their timers in `finally`. The clean rerun produced no open-handle warning.

## Acceptance cases exercised

Both candidates passed tests for:

1. no-argument nested `refreshSession()` returns the committed rotated session;
2. one token-service stub call in the manual reproducer;
3. stored and returned refresh tokens agree;
4. a throwing `TOKEN_REFRESHED` listener is logged without overturning the committed refresh;
5. every listener still runs after one listener fails;
6. no unhandled rejection is observed;
7. the initiating refresh waits for SSR-like async cookie work;
8. queued initialization notification supplies the event session without a second rotation;
9. cross-tab notification supplies the event session without a second rotation;
10. non-refresh listener failures retain current rejection behavior;
11. notification transport failures remain visible.

## Deliberate distinguishing assertions

### Early shared settlement

- an old-token caller joined during subscriber work settles before subscriber completion;
- an explicit stale-token nested refresh during a manual refresh succeeds through the already-resolved shared Deferred;
- after a post-commit BroadcastChannel failure, a joined caller receives success while the initiating caller receives the transport exception.

### Notification-scoped committed result

- an old-token caller joined during subscriber work waits until subscriber completion;
- an explicit stale-token nested refresh during a manual refresh reaches the bounded timeout;
- after a post-commit BroadcastChannel failure, both the joined caller and the initiating caller receive rejection.

The final distinction strengthens the recommendation against early shared settlement: one committed refresh can produce two caller-visible outcomes when a later notification transport step fails.

## Repository-wide checks

Owned-fork experiment head: `f589f01234bf057c6d872ac44a1255fe31b433cf`

| Check | Result |
| --- | --- |
| Fieldwork auth refresh settlement workflow | pass |
| SDK Compliance | pass |
| Ordinary pull-request CI | pass |
| Draft-merge blocker | expected failure because the PR remains draft |

The ordinary pull-request workflow completed successfully across its repository matrix. Completed jobs included package builds, common checks, public API drift checks, package-export validation, ESM and CJS loading, Hermes compatibility, cross-platform unit and type checks, and package suites for auth-js, postgrest-js, storage-js, functions-js, realtime-js, and the Supabase client.

Fieldwork PR #91 also passes:

- Fieldwork integrity;
- external-reference policy.

## Evidence limits

The focused tests use the real pinned auth client and repository Jest setup, but mock the Auth HTTP response and storage contents. They do not run:

- a live Auth service;
- a hosted Supabase project;
- a full Next.js or other server framework request;
- real browser BroadcastChannel delivery;
- React Native, Deno, or worker-specific runtime behavior for the settlement cases;
- Docker-backed full Auth integration tests using the candidate source patch.

Repository CI establishes package compatibility for the experiment branch. It does not replace a bounded live SSR cookie trial or a real browser/React Native notification trial.

## Validation conclusion

Both implementation mechanisms work as designed in the real auth-js code at the pinned revision, and the experiment branch passes the complete repository pull-request and SDK compliance workflows.

The notification-scoped result remains preferred because it:

- fixes the normal no-argument nested refresh path across manual, initialization, and cross-tab notifications;
- preserves ordinary joined-caller timing;
- preserves one caller-visible outcome when notification transport fails;
- keeps the initiating operation waiting for required SSR work;
- limits temporary committed-result exposure to the active event and rotated token.

Its unresolved edge is explicit stale-token reentry. That should receive a deliberate typed-error or callback-context decision rather than broad early settlement of every refresh joiner.