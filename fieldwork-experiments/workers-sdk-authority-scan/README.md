# Workers SDK authority scan — 2026-08-01

## Scope

Bounded current-head review of authority that survives or crosses operation boundaries in Cloudflare Workers SDK.

Original exact upstream revision:

`95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`

Current public-head refresh:

`20470fa8b09761c50b5c2c1d6a5f2652b61bd271`

The five-commit drift between those revisions does not touch the auth factory, Wrangler user adapter, account-cache implementation, deploy-helpers context, or their source paths listed below. Both source findings remain current at the refreshed head.

This pass stopped after confirming and recording two findings. It did not continue into broader scouting.

## In simple words

Two places can keep using information that belongs to a different operation:

1. Wrangler can keep an account selected under earlier credentials after the credentials change.
2. Deploy helpers can switch a pending deployment to the fetch, logger, or prompt functions installed by a later operation.

Both were reproduced using sentinel identities only. No real credentials, accounts, API requests, deployments, or upstream interactions were used.

## Finding 1 — Cached account outlives credential identity

Canonical issue: #471

### Source path

- `packages/workers-auth/src/core/factory.ts`
- `packages/workers-auth/src/wrangler/index.ts`
- `packages/wrangler/src/user/user.ts`
- `packages/workers-utils/src/config-cache.ts`

### Source conclusion

The account cache filename is derived from the CLI and active profile. `getActiveAccountId()` checks config, account-ID environment, then cache. `getOrSelectAccountId()` returns that result without fetching the accounts available to the current credentials.

A credential or compliance/API-environment change is not represented in the cache identity.

### Executed model

```text
PASS: credential change reuses prior cached account without account lookup
PASS: profile-only cache does not encode compliance or API environment
```

### Target-native reproduction carrier

Owned fork PR: `teamleaderleo/workers-sdk#12`

- branch: `fieldwork/471-account-cache-authority-repro`;
- exact base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- exact reproducer head: `f1db75c385792f0d95119d68ece242fdd5333bf4`;
- changed path: `packages/wrangler/src/__tests__/account-cache-authority.test.ts`;
- current state: target-native regression committed; exact CI conclusion pending.

The regression uses only sentinel tokens and accounts. It expects account B after credentials switch from A to B in one process. Current source is expected to return cached account A before consulting B's mocked account list.

### Current disposition

**ACCEPT SOURCE FINDING / EXECUTE TARGET REPRODUCTION.**

Treat cached account selection as a hint that must be validated under current authority. Do not persist raw or hashed credentials merely to key the cache.

## Finding 2 — Deploy-helper context is process-global

Canonical issue: #472

### Source path

- `packages/deploy-helpers/src/shared/context.ts`
- `packages/deploy-helpers/src/index.ts`
- `packages/deploy-helpers/src/deploy/deploy.ts`
- `packages/wrangler/src/core/register-yargs-command.ts`
- `packages/wrangler/src/api/deploy-helpers-context.ts`
- `packages/wrangler/src/api/index.ts`

### Source conclusion

Deploy helpers export mutable live bindings for logger, four fetch helpers, and three interaction functions. Initialization replaces all of them globally.

Deploy and trigger helpers are asynchronous and read those live bindings after awaited work. Another initializer can therefore replace the context observed by an already-running operation.

### Executed model

```text
PASS: pending operation switches to later global fetch and logger context
PASS: explicit operation context keeps fetch and logger ownership stable
```

### Current disposition

**ACCEPT SOURCE FINDING / EXECUTE TARGET REPRODUCTION.**

The preferred direction is one immutable context per operation. Save-and-restore global state is not concurrency-safe.

## Exact model command

The committed model is identical to the executed content.

```sh
node fieldwork-experiments/workers-sdk-authority-scan/account-cache-and-deploy-context.mjs
```

## Required next execution

### Account cache

- conclude the exact focused result on `teamleaderleo/workers-sdk#12`;
- shared auth tests for token, global key/email, OAuth-to-env, profile, and compliance/API-environment changes;
- Wrangler command and embedded API sequences in one process;
- explicit account-ID precedence controls;
- no-secret-retention assertions.

### Deploy context

- two concurrent mocked deploys with distinct fetch, API-base, logger, confirmation, prompt, and selection owners;
- interruption during validation, assets, version upload, and trigger phases;
- CLI/API/custom-consumer overlap;
- failure, cancellation, nested calls, and detached-callback characterization.

## Sensitive-handling boundary

The Linux Fieldwork `SECURITY_RECONVENE.md` rule was consulted because these findings involve credentials and request ownership. They remain in the ordinary workflow: all evidence is public-source, synthetic, disposable or owned, and contains no real secret, live target, unauthorized access, destructive action, persistence, or production-changing behavior.

Switch to a public-safe `RECONVENE` checkpoint and stop deepening the path if that boundary changes.

## Boundary

- #466 owns Vite project environment leakage.
- #471 owns cached account authority.
- #472 owns deploy helper fetch/logger/prompt ownership.
- #190 owns the host-global Undici dispatcher.
- #187 owns container registry client credentials.
- #186 owns remote proxy-session identity.

Public upstream contact remains unauthorized and was not performed.
