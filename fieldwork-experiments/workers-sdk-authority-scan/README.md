# Workers SDK cross-operation authority scan

Current public source reviewed: `cloudflare/workers-sdk@20470fa8b09761c50b5c2c1d6a5f2652b61bd271`.

Fieldwork review surface: #473.

Public upstream contact authorized/performed: `false` / `false`.

## What this is

This is not one giant bug or one ready-to-send pull request.

It is a cluster of related findings about **mutable process-wide state surviving longer than the operation that owns it** inside long-lived or embedded Workers SDK processes.

The recurring pattern is:

1. operation A installs an account, credential profile, fetch function, prompt handler, Access credential, or log level;
2. A awaits or remains alive;
3. operation B replaces or removes that process-global state;
4. A resumes using B's authority, or B inherits A's stale authority.

Ordinary one-command CLI use may never overlap this way. The risk is most relevant to embedded Wrangler, tests, programmatic APIs, dev sessions, concurrent commands, and other long-lived Node processes.

All retained evidence uses public source and synthetic sentinel identities. No real credential, account, Access application, deployment, network target, or private data was used.

## Findings at a glance

| Issue | Plain-English problem | Current evidence | Likely repair size |
| --- | --- | --- | --- |
| #471 | Wrangler can reuse an account selected under earlier credentials without validating it under the current credentials. | Source-confirmed; model-executed; current-head native baseline exists. | Medium; exact error classification remains. |
| #472 | A pending deployment can switch to fetch/logger/prompt functions installed by a later operation. | Source-confirmed; model-executed; Linux/macOS native baseline passed, remaining checks need classification. | Medium-to-large migration to operation context. |
| #496 | Active auth profile and temporary-account state are one mutable process-wide auth object. | Source-confirmed; model-executed; native overlap carrier exists. | Large foundational repair. |
| #529 | Cloudflare Access headers are cached by domain and can outlive removed/rotated credentials; failed detection can become a permanent negative cache entry. | Source-confirmed; model-executed; baseline and a bounded stacked repair exist. | Small-to-medium; best near-term source candidate. |
| #530 | A Wrangler dev session's log level mutates the singleton logger and survives failure/stop or crosses sessions. | Source-confirmed; model-executed. | Small-to-medium; existing `runWithLogLevel()` is direct precedent. |

Adjacent but separately owned: #466 covers Vite project environment values copied into `process.env` and later consumed by asynchronous remote-binding authentication.

## What is actually proven

### Source behavior

The reviewed source contains the process-wide state and read-after-await paths described by the five issues. The public-source refresh from the earlier pin did not alter the relevant source fences.

### Executed models

The committed dependency-free models reproduce the ownership switches using sentinel values:

```sh
node fieldwork-experiments/workers-sdk-authority-scan/account-cache-and-deploy-context.mjs
node fieldwork-experiments/workers-sdk-authority-scan/auth-operation-scope.mjs
node fieldwork-experiments/workers-sdk-authority-scan/access-cache-credential-lifetime.mjs
node fieldwork-experiments/workers-sdk-authority-scan/dev-log-level-lifetime.mjs
node fieldwork-experiments/workers-sdk-authority-scan/repair-comparisons.mjs
```

Those models establish the mechanism and compare bounded repair directions. They are not a substitute for the repository's real package tests.

### Target-native carriers

- `teamleaderleo/workers-sdk#6` covers #471, #472, and #496 on the earlier exact base.
- `teamleaderleo/workers-sdk#7` reproduces #529 Access-cache lifetime.
- `teamleaderleo/workers-sdk#10` is a stacked bounded #529 repair.
- `teamleaderleo/workers-sdk#11` is the current-head #471 account-cache baseline.
- `teamleaderleo/workers-sdk#8` is the current-head #472 deploy-context baseline.

No public Cloudflare issue, pull request, comment, review, reaction, or message was created.

## What is not proven yet

- No complete source repair has passed all target-native gates for #471, #472, #496, or #530.
- #471 still needs a reliable distinction between “cached account is inaccessible under valid current credentials” and authentication, rate-limit, transport, server, or malformed-response failures.
- #472 still needs broad phase coverage and compatibility characterization for old internal consumers.
- #496 still needs detached-callback and long-lived-session coverage before an async-local bridge can be trusted.
- #529's stacked repair still needs terminal before/after native receipts; interactive Access-cookie owner and expiry remain a separate slice.
- #530 still needs to prove that long-lived event emitters, controllers, tunnels, and teardown callbacks retain the intended async log-level context.
- No eligible independent complete-diff review has been submitted on #473 or the checked owned-fork carriers.

## Recommended triage

### 1. Continue #529 first

This is the smallest consequential repair family:

- construct service-token headers from the current environment on each call;
- do not cache secret service-token headers by domain;
- do not cache probe errors as permanent `false` results;
- leave interactive cookie owner/expiry as an explicit follow-up.

A bounded repair already exists on `teamleaderleo/workers-sdk#10`. Classify its exact CI and diff before creating anything else.

### 2. Continue #530 second

The codebase already has an async-local `runWithLogLevel()` mechanism. The main work is proving whether all long-lived dev callbacks remain inside that ownership context and adding explicit captures where they do not.

### 3. Keep #471 active, but do not guess the API error rule

The selected design treats the cached account as a hint and validates `GET /accounts/{account_id}` under current authority. Only a conclusively inaccessible account should enter normal account selection. Broad failures must propagate and leave the cache unchanged.

If the API cannot provide a narrow reliable discriminator across credential types and environments, use authoritative membership from `fetchAllAccounts()` instead of treating every 403 as stale cache.

### 4. Treat #472 and #496 as architecture work

Both point toward operation-scoped context. They should not be “fixed” with save-and-restore globals because overlapping operations can finish out of order.

- #472 needs one immutable `DeployHelpersContext` per operation, with forwarding adapters only as a migration bridge.
- #496 needs one auth-operation record for profile and temporary-account authority, likely using `AsyncLocalStorage` as a compatibility bridge.

These may eventually share command-dispatch infrastructure, but they own different state and should retain separate tests and decisions.

## Review status — 2026-08-03

Checked review submissions and inline threads on:

- `teamleaderleo/fieldwork#473`;
- `teamleaderleo/fieldwork#467`;
- `teamleaderleo/workers-sdk#6`;
- `teamleaderleo/workers-sdk#7`;
- `teamleaderleo/workers-sdk#8`;
- `teamleaderleo/workers-sdk#10`;
- `teamleaderleo/workers-sdk#11`.

No submitted pull-request reviews or inline review threads were present. Existing comments are author checkpoints and CI receipts, not independent technical acceptance.

## Detailed write-ups

- #471 repair comparison: [`repair-comparisons.md`](repair-comparisons.md)
- #472 and #496 operation-context comparison: [`repair-comparisons.md`](repair-comparisons.md)
- #496 auth ownership: [`auth-operation-scope.md`](auth-operation-scope.md)
- #529 Access-cache lifetime: [`access-cache-credential-lifetime.md`](access-cache-credential-lifetime.md)
- #530 dev log-level lifetime: [`dev-log-level-lifetime.md`](dev-log-level-lifetime.md)
- Additional source pass: [`research-pass-2.md`](research-pass-2.md)

## Decision boundary

This branch is a research and routing record. It should not remain an undifferentiated queue indefinitely.

The next useful decision is:

1. classify and either accept, repair, or retire the existing #529 stacked repair;
2. then decide whether #530 merits its own native source candidate;
3. keep #471 in characterization until its exact error rule is settled;
4. hold #472/#496 as broader context architecture unless target-native evidence justifies the migration cost.

Public upstream interaction remains separately unauthorized.