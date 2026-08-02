# Workers SDK authority repair comparisons

Issues: #471, #472, #496.

Current public source: `cloudflare/workers-sdk@20470fa8b09761c50b5c2c1d6a5f2652b61bd271`.

Native reproduction carrier: `teamleaderleo/workers-sdk#6@4c8d79f2a2abfe2dce0b501cb6de2874aedbfc89`, based on `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.

## Executed comparison

```sh
node fieldwork-experiments/workers-sdk-authority-scan/repair-comparisons.mjs
```

Output:

```text
PASS: cached account is reused only after current-credential validation
PASS: explicit config and environment account IDs retain precedence
PASS: async auth operation context preserves profile and temporary account
PASS: forwarding adapters preserve deploy-helper operation ownership
```

No real credentials, accounts, network calls, deployments, or prompts were used.

## #471 — cached account authority

### Selected next prototype

Treat the cached account as a hint. Before reusing it, validate that the current credentials can access that exact account ID. Explicit configuration and `CLOUDFLARE_ACCOUNT_ID` retain their documented precedence and remain the user's way to skip automatic selection.

A direct account validation request is preferred over fetching every account merely to check one cache entry. The target prototype must classify authentication failure, inaccessible account, transient API failure, and malformed response separately:

- inaccessible under current credentials: discard the hint and run normal account selection;
- transient or indeterminate request failure: preserve the error and do not silently choose another account;
- accessible: reuse the cache;
- explicit config/env ID: return without cache validation, preserving current contract.

### Rejected directions

- Persist raw or hashed credentials with the cache: unnecessary secret-derived state and rotation ambiguity.
- Purge only on login/logout: environment credentials can change without either operation.
- Trust profile name alone: environment credentials and API/compliance environment can change inside a profile.
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
