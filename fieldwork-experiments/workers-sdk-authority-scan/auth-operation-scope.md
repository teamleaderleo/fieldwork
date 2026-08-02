# Wrangler auth operation ownership

Canonical issue: #496.

## Reviewed source

Current public head: `20470fa8b09761c50b5c2c1d6a5f2652b61bd271`.

The five-commit delta from the earlier review pin `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d` does not touch the relevant auth, command-dispatch, or request paths.

Relevant files:

- `packages/workers-auth/src/flow.ts`
- `packages/workers-auth/src/core/factory.ts`
- `packages/wrangler/src/user/user.ts`
- `packages/wrangler/src/core/register-yargs-command.ts`
- `packages/wrangler/src/cfetch/internal.ts`

## Source finding

Wrangler creates one process-wide auth object. Its OAuth flow stores these mutable values in closure state:

- `activeProfile`;
- `temporaryAllowed`;
- `activeTemporaryAccount`.

Command dispatch calls `setProfile(profile)` and `setTemporaryAllowed(...)` before awaiting the command handler. A later overlapping dispatch therefore replaces the profile and clears the temporary-account latch observed by an earlier pending command.

Cloudflare API requests do not capture credentials when the client is created. The custom fetcher calls `requireLoggedIn()` and `requireApiToken()` for each request. A command can therefore begin under profile A and issue a later request with profile B after another command dispatch.

Likewise, a temporary command can begin with a temporary account, then a later dispatch calls `setTemporaryAllowed(...)`, clears the singleton temporary account, and causes the first command's later credential lookup to fall back to stored or environment credentials.

## Executed model

Command:

```sh
node fieldwork-experiments/workers-sdk-authority-scan/auth-operation-scope.mjs
```

Output:

```text
PASS: pending operation switches to later active auth profile
PASS: later command dispatch clears a pending operation's temporary account
PASS: explicit auth context preserves operation credential ownership
```

The model uses sentinel tokens only. No account, credential, network call, deployment, or public upstream interaction was used.

## Native reproduction carrier

Owned fork PR: `teamleaderleo/workers-sdk#6`.

Exact execution base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.

Exact carrier head at materialization: `4c8d79f2a2abfe2dce0b501cb6de2874aedbfc89`.

The carrier adds target-native tests for #471, #472, and #496 without a product repair. The tests state the owner-correct behavior and are expected to expose the current source behavior.

## Consequences to verify natively

- request A can authenticate with profile B after an await;
- account selection and account-cache filenames can switch with the active profile;
- temporary-account authority can disappear mid-command;
- later command dispatch can replace an earlier command's stored credential backend;
- login, refresh, logout, scope reads, and credential writes can resolve the later profile;
- concurrent embedded command/API consumers can interfere even when their configuration paths differ.

## Preferred repair direction

Create one immutable auth operation context after profile and temporary-account resolution, then pass or bind that context to every command handler and request created by that operation.

A bounded `AsyncLocalStorage` operation context is a possible compatibility bridge because credential lookups occur inside asynchronous request paths. Detached callbacks and long-lived development sessions still require explicit tests.

Saving and restoring singleton values in `finally` is rejected because overlapping commands can finish out of order.

## Required target controls

1. Two overlapping commands using profiles A and B retain their own credentials before and after awaits.
2. Cloudflare SDK client requests resolve the creating operation's profile, not the latest global profile.
3. A temporary command retains its temporary account after another dispatch starts.
4. A non-temporary command never inherits a temporary account.
5. Account selection and account caches remain tied to the intended operation profile.
6. Login, refresh, logout, scopes, and credential writes stay profile-correct.
7. Failure, cancellation, and nested command execution do not leak profile or temporary state.
8. Sequential CLI behavior remains compatible.
9. No raw or derived credential material enters durable evidence.

## Boundary

- The account cache's validity under changed credentials remains #471.
- Deploy-helper fetch/logger/prompt ownership remains #472.
- Vite project environment leakage remains #466.
- Remote binding session identity remains #186.

This finding owns the active auth profile and temporary-account lifecycle for one Wrangler operation.
