# Supabase continuation harness correction — 2026-07-30

State: `active-validation`

Campaign: #78

Central candidate: #148 generation 2

Owned experiment: `teamleaderleo/supabase-js#1`

Supabase source pin: `63318987365bbcea2c31a00b62cbb95b21083ad5`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## Correction

Self-review found that the first prepared versions of two new tests installed an expired session before calling `GoTrueClient.initialize()`.

That setup was invalid for the intended characterization. Initialization can detect an expired stored session and enter recovery before the test installs its `_refreshAccessToken` stub. The test could therefore make a network attempt, remove the session, or otherwise fail before reaching the `_callRefreshToken` path under examination.

Affected prepared cases:

- `TOKEN_REFRESHED` listener throwing `AuthError` under both `throwOnError` modes;
- failed-refresh `SIGNED_OUT` listener leaving a concurrent joiner pending.

## Repair

Owned lab head `8a0c55a40a62f03d1856b287f5a5f4124d44ce1b` now:

1. creates and initializes the client with empty storage;
2. writes the expired session after initialization completes;
3. installs the refresh service stub;
4. invokes the exact refresh path being characterized.

The successful transport and cross-tab controls that use an unexpired session retain their earlier setup.

## Evidence effect

The prior prepared head `e7fdfbbe4818d764f1ec85186388b901477e9b6b` supplies no execution evidence for the new expired-session cases. Its workflows had not started when the setup defect was found.

Current exact-head runs:

- focused settlement workflow `30501713639`;
- SDK Compliance `30501713955`;
- ordinary pull-request CI `30501713862`;
- expected draft blocker `30501714093`.

All were queued or pending when this correction was recorded.

Evidence remains `source-read + target-test-prepared` until the focused workflow completes on `8a0c55a40a62f03d1856b287f5a5f4124d44ce1b` and the logs show that the intended assertions ran.

## Boundary

This correction changes only the test harness. It does not alter the source findings, candidate #148 invariant, production recommendation, or external-contact boundary.