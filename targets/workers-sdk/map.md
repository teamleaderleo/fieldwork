# Target Map: Cloudflare Workers SDK

Repository: https://github.com/cloudflare/workers-sdk

## Why it is here

Wrangler, Miniflare, Workers testing, local development, and deployment behaviour overlap with Stensibly and other hosted tools. Runtime and deployment failures can often be reproduced without speculative feature work.

## Areas worth understanding

- Wrangler configuration and deployment lifecycle;
- local-versus-hosted behavioural differences;
- OAuth and callback development flows;
- Durable Objects and persistence testing;
- Vite and framework integration;
- generated bindings and TypeScript declarations;
- error classification, cleanup, and recovery;
- reproducible deployment verification.

## Evidence we can produce

- minimal Worker projects;
- isolated configuration fixtures;
- local and hosted comparison runs;
- fault-injected lifecycle tests;
- deployment transcripts with secrets removed;
- generated-type snapshots;
- cross-platform CLI regressions.

## Entry standard

Separate platform behaviour from SDK behaviour. Confirm whether a defect belongs in Workers SDK, workerd, the dashboard, documentation, or the application.

## Stop conditions

- safe reproduction requires production credentials or customer data;
- the behaviour is controlled by an undocumented hosted rollout;
- a local workaround is more appropriate than changing shared tooling;
- upstream scope is unclear and maintainer direction is unavailable.
