# Supabase auth callback-error execution — 2026-07-30

State: `target-executed`

Campaign: #78

Parent scout: #21

Successful-refresh candidate: #148

Failed-refresh teardown candidate: #188

Initial-session delivery candidate: #189

Owned experiment: `teamleaderleo/supabase-js#1`

Supabase source pin: `63318987365bbcea2c31a00b62cbb95b21083ad5`

Executed experiment head: `8a0c55a40a62f03d1856b287f5a5f4124d44ce1b`

Focused workflow: `30501713639`

SDK Compliance workflow: `30501713955`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

The expanded auth-js matrix confirms three separate callback ownership results.

1. A successful token refresh must stay successful after credentials are committed, even when a `TOKEN_REFRESHED` application listener throws an `AuthError`.
2. A rejected refresh can leave another concurrent caller waiting forever when a `SIGNED_OUT` listener throws during cleanup.
3. An `INITIAL_SESSION` listener that throws after receiving a real session is called again with `null`.

Only the first result belongs to central candidate #148. The other two now have separate candidate issues so one implementation decision does not absorb three different lifecycle contracts.

## Exact execution receipt

The corrected test setup was executed on Ubuntu 24.04 against the pull-request integration revision produced from owned experiment head `8a0c55a40a62f03d1856b287f5a5f4124d44ce1b`.

Both experiment jobs passed:

```text
token-aware-committed-result: success
early-shared-settlement: success
```

Each job executed:

```text
PASS fieldwork-settlement-boundaries.test.ts
PASS fieldwork-refresh-notification-settlement.test.ts
PASS fieldwork-init-refresh-subscriber-error.test.ts
PASS fieldwork-initial-session-callback-error.test.ts

Test Suites: 4 passed, 4 total
Tests:       15 passed, 15 total
```

SDK Compliance also passed on the corrected experiment head. The ordinary repository pull-request workflow remained queued at the time this record was created and is not included in the new evidence claim.

## Result A — strengthen #148

The matrix covers `TOKEN_REFRESHED` listeners that throw the publicly exported `AuthError` while the old access token is expired.

Under both `throwOnError: false` and `throwOnError: true`, both experimental variants isolate the listener error after successful commit and prove:

- `refreshSession()` returns the rotated session successfully;
- storage retains the rotated refresh token;
- `lastRefreshFailure` remains null;
- callback diagnostics remain logged;
- the initiating operation still waits for listener completion.

This closes an important classification gap in #148. Callback-error isolation prevents a committed refresh from entering the generic refresh-failure catch, where current source can otherwise remove the newly stored session and cache the application exception as a refresh failure.

The preferred design remains notification-scoped committed result plus `TOKEN_REFRESHED` callback-error isolation. The new execution does not make broad early shared settlement preferable.

## Result B — candidate #188

The failed-refresh characterization confirms:

```text
expired session
refresh service returns non-retryable AuthError
_removeSession clears storage
SIGNED_OUT listener throws
initiating caller rejects with listener error
joined caller remains pending at the bounded observation deadline
```

The result occurs before the successful-refresh settlement variants differ. It belongs to failure teardown and total singleflight completion.

Candidate #188 owns the rule that every created refresh Deferred settles exactly once even when cleanup or notification fails.

## Result C — candidate #189

The initial-session characterization confirms:

```text
listener receives INITIAL_SESSION with stored session
listener throws
same listener receives INITIAL_SESSION with null
original listener error is logged
```

This result comes from `_emitInitialSession()` placing session retrieval and application callback execution inside one catch boundary.

Candidate #189 owns one-delivery semantics and separation of session-loading failures from application callback failures.

## Evidence classification

| Claim | Evidence class | Receipt or limitation |
| --- | --- | --- |
| Successful refresh callback `AuthError` is safely isolated by both lab variants | `target-executed` | focused run `30501713639`, both jobs, 15-test matrix |
| Current failed-refresh teardown can orphan a joined caller | `target-executed` | bounded negative characterization in `fieldwork-settlement-boundaries.test.ts` |
| Current initial callback failure produces a second null delivery | `target-executed` | `fieldwork-initial-session-callback-error.test.ts` |
| SDK policy and repository compliance on corrected experiment head | gate-scoped `full-gate` | SDK Compliance `30501713955` only |
| Ordinary repository pull-request CI on corrected head | pending | no result claimed here |
| Browser, React Native, writable SSR cookie, hosted Auth, and live Realtime integration | unexecuted | remains outside this focused run |

## Self-review and harness history

The first prepared versions of the two expired-session tests planted an expired session before client initialization. Initialization could therefore enter recovery before the test installed its refresh stub.

That prepared head supplies no evidence for those cases.

The executed head repairs the harness by:

1. initializing with empty storage;
2. writing the expired session afterward;
3. installing the service stub;
4. invoking the exact refresh path.

The focused logs show all four intended suites ran on the corrected head.

## Updated candidate ordering

1. #148 — successful `TOKEN_REFRESHED` settlement and committed-result ownership.
2. #188 — failed-refresh teardown and total shared Deferred settlement.
3. #189 — initial-session callback error ownership and one-delivery semantics.
4. refresh response diagnostics — separate observability decision.
5. disposal isolation — feature or major-version contract, not current defect correction.

## Next gates

### #148

- record a new exact-head independent disposition using the 15-test receipt;
- isolate the preferred implementation from the two-variant lab;
- run writable and intentionally non-writing SSR cookie controls;
- run browser or React Native notification delivery;
- prove Realtime receives the rotated token before the initiating refresh returns;
- rebase over accepted refresh lifecycle work without importing unrelated features.

### #188

- decide original-error versus aggregate-error authority;
- guarantee total Deferred settlement across storage, verifier, and callback failures;
- test concurrent public, auto-refresh, and `getSession()` joiners;
- prevent unhandled internal rejection.

### #189

- separate session retrieval and callback catch boundaries;
- define one null-or-diagnostic rule for genuine load failure;
- cover multiple listeners, unsubscribe timing, and unobserved background-task rejection.

## Boundary

No public Supabase issue, pull request, review, comment, reaction, branch, or message was created or changed.
