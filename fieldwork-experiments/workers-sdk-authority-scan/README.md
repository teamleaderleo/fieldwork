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

### Current-head target-native baseline carrier

Owned fork PR: `teamleaderleo/workers-sdk#11`

- branch: `fieldwork/471-account-cache-current-baseline`;
- exact base: `20470fa8b09761c50b5c2c1d6a5f2652b61bd271`;
- exact head: `d8b5b58841791144f43cd3051615fad1b70a43e5`;
- changed path: `packages/wrangler/src/__tests__/account-cache-authority.test.ts`;
- current state: current-head characterization committed; repository workflows require classification.

The baseline writes cached account A, changes the active environment credential to sentinel credential B, installs account-authority handlers, and records that `getOrSelectAccountId({})` returns A without making a validation request.

Older-base PR `teamleaderleo/workers-sdk#12` is closed as superseded and is not an admissible current-head receipt.

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

### Current-head target-native baseline carrier

Owned fork PR: `teamleaderleo/workers-sdk#8`

- branch: `fieldwork/472-deploy-context-current-baseline`;
- exact base: `20470fa8b09761c50b5c2c1d6a5f2652b61bd271`;
- exact head: `cdda73d799ed41fbf89af6309b99c7507f65150d`;
- changed path: `packages/deploy-helpers/tests/index.test.ts`;
- current state: Linux and macOS package matrices succeeded; Windows and repository checks require classification.

The baseline begins operation A, suspends it before reading the package's live context bindings, installs context B, then proves A resumes through B's fetch, logger, and confirmation handlers.

Older-base PR `teamleaderleo/workers-sdk#13` is closed as superseded and is not an admissible current-head receipt.

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

- classify exact workflows and run the focused package command for `teamleaderleo/workers-sdk#11`;
- shared auth tests for token, global key/email, OAuth-to-env, profile, and compliance/API-environment changes;
- Wrangler command and embedded API sequences in one process;
- explicit account-ID precedence controls;
- no-secret-retention assertions.

### Deploy context

- classify exact Windows/check failures and run the focused package command for `teamleaderleo/workers-sdk#8`;
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
