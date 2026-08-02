# Workers SDK authority repair comparisons

Issues: #471, #472, #496.

Current public source: `cloudflare/workers-sdk@20470fa8b09761c50b5c2c1d6a5f2652b61bd271`.

Native reproduction carrier: `teamleaderleo/workers-sdk#6@4c8d79f2a2abfe2dce0b501cb6de2874aedbfc89`, based on `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.

Dedicated #471 regression: `teamleaderleo/workers-sdk#12@f1db75c385792f0d95119d68ece242fdd5333bf4`.

## Executed comparison

```sh
node fieldwork-experiments/workers-sdk-authority-scan/repair-comparisons.mjs
```

Output:

```text
PASS: cached account is reused only after current-credential validation
PASS: inaccessible cached account falls back to ordinary account selection
PASS: transient or inconsistent validation fails closed without replacing cache
PASS: explicit config and environment account IDs retain precedence
PASS: async auth operation context preserves profile and temporary account
PASS: forwarding adapters preserve deploy-helper operation ownership
```

No real credentials, accounts, network calls, deployments, or prompts were used.

## #471 — cached account authority

### Selected next prototype

Treat the cached account as a hint. Before reusing it, validate that the current credentials can access that exact account ID. Explicit configuration and `CLOUDFLARE_ACCOUNT_ID` retain their documented precedence and remain the user's way to skip automatic selection.

A direct account validation request is preferred over fetching every account merely to check one cache entry. Cloudflare's existing account-details operation is `GET /accounts/{account_id}` and returns information about a specific account available to the current authentication context. Current Workers SDK fetch plumbing already preserves HTTP status and API error code through `APIError`.

The intended ordering is:

1. temporary account, explicit config `account_id`, and `CLOUDFLARE_ACCOUNT_ID` keep current precedence and return without cache validation;
2. a cached account triggers one exact-account request under the current credentials, compliance region, API environment, and API base;
3. a successful response must contain the exact requested account ID; refresh the cached display name and reuse the ID;
4. only a response conclusively meaning “this authentication context cannot use this account” may discard the hint and enter ordinary account selection;
5. authentication failure, rate limiting, server failure, network failure, malformed response, or a mismatched returned account ID must propagate and leave the cache unchanged.

This preserves the distinction between stale authority and unavailable evidence. A transient validation failure must not silently select a different account, because that could route a command under an unintended account after an infrastructure error.

### Exact current-source fit

At public head `20470fa8...`:

- `getActiveAccountId()` still resolves temporary account, config, account-ID environment, then the profile-only cache;
- `getOrSelectAccountId()` still returns that cached ID before any current-credential account request;
- the five commits after the original reproduction base do not touch the auth factory, Wrangler adapter, account cache, or focused test owner;
- `fetchResultBase()` exposes a typed result or throws `APIError` with HTTP `status`, API `code`, structured metadata, and retry information;
- the account cache payload contains only `{ account }`, so credential, compliance, and API-environment identity are absent.

### Open target discriminator

The API documentation establishes the exact-account operation but does not define one universal “not accessible to this authentication context” error envelope for every token class. Before source repair, target-native MSW controls must pin the intended classification:

- confirmed absent/inaccessible account response enters ordinary selection;
- invalid or expired credentials propagate rather than clearing the cache;
- 429 and retryable 5xx responses propagate with retry metadata;
- malformed success and mismatched account identity fail closed;
- global key/email, user token, account token, OAuth, public/FedRAMP, staging/production, and custom API-base paths use the same authority rule.

If no narrow status/code classification is reliable, fall back to the existing `fetchAllAccounts()` result and check membership in that authoritative list. That is more expensive but safer than treating a broad 403 class as stale cache.

### Required target controls

- credential A validates cached account A;
- credential B cannot access cached A and selects B;
- credential C receives a transient validation error and neither selects nor rewrites the cache;
- exact-account response with a different ID is rejected;
- validation refreshes a changed account display name without changing ID;
- explicit config and account-ID environment skip validation;
- profile and compliance/API-environment changes cannot reuse unvalidated cache state;
- no raw credential, credential hash, API response body, or secret-derived identifier is persisted or logged.

### Rejected directions

- Persist raw or hashed credentials with the cache: unnecessary secret-derived state and rotation ambiguity.
- Purge only on login/logout: environment credentials can change without either operation.
- Trust profile name alone: environment credentials and API/compliance environment can change inside a profile.
- Treat every validation failure as inaccessible: transient failure could silently reroute the command.
- Fetch all memberships on every call without first testing an exact-account endpoint: safe but more expensive and can add avoidable permission requirements.

## #496 — auth operation ownership

### Selected compatibility prototype

Use `AsyncLocalStorage` to bind one mutable operation record containing:

- active profile;
- temporary-account permission;
- active temporary account.

Command dispatch should enter the operation context with its resolved profile and temporary policy before any asynchronous command work. Credential, storage, account, login, refresh, logout, and scope helpers should resolve the operation record first and retain the existing singleton only as a sequential compatibility fallback.

The record is mutable only by the owning async operation so temporary-account activation can occur after command entry without becoming process-global.

### Required negative controls

- operations finish out of order;
- operation B starts while A awaits and B finishes first;
- nested operation B does not mutate A after returning;
- detached callbacks and long-lived dev/tail sessions retain or explicitly capture A;
- sequential callers that do not use the operation runner retain current behavior;
- no operation record contains raw credentials beyond references already held by the auth flow.

### Rejected direction

Saving and restoring singleton fields in `finally` is not concurrency-safe.

## #472 — deploy-helper request and interaction ownership

### Selected compatibility prototype

Add an async operation context carrying the complete `DeployHelpersContext`. Keep compatibility exports as forwarding adapters:

- fetch functions forward to the current operation context;
- logger methods forward to the current operation logger;
- confirm, prompt, and select forward to the current operation interaction owner.

The Wrangler command path should run the command handler inside that context. The existing initializer may remain only as a sequential fallback for old internal consumers while call sites migrate to an explicit operation runner.

### Long-term direction

Pass an immutable context through deploy, versions, trigger, and helper entry points. The forwarding layer is a migration device, not the final public contract.

### Required negative controls

- overlapping deploys and triggers;
- B starts while A is in validation, asset upload, version upload, or confirmation;
- out-of-order completion;
- nested calls;
- detached callbacks;
- uninitialized context fails clearly;
- fallback context cannot override an active operation context;
- request bodies and diagnostics never cross owners.

## Promotion rule

The executed models select target prototypes but do not promote source. Promotion requires the native reproduction tests to fail for the intended reason, source repair on an exact base, focused before/after receipts, ordinary package gates, and independent complete-diff review.

Public upstream interaction remains unauthorized and was not performed.
