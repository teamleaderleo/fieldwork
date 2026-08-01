# Upstream issue result — UI-message streams need first-byte and idle liveness

Draft status: `not applicable — equivalent public issue already exists`  
Public interaction authorized: `no`

## Current result

A new issue must not be filed. Public issue [`vercel/ai#17805`](https://github.com/vercel/ai/issues/17805), opened July 22, 2026, already records the same failure and desired API:

- an idle UI-message stream produces no body byte, so some servers and reverse proxies expose no response head before their timeout;
- after the first byte, prolonged body silence can trigger an intermediary idle cutoff;
- the reporter supplies a minimal `createUIMessageStreamResponse()` reproduction;
- the reporter describes an SSE-comment workaround and asks for `keepAliveMs` plus self-hosting guidance;
- a maintainer classified the report as a high-confidence bug.

The public issue also provides stronger operational context than Fieldwork's controlled carrier: Next.js standalone on Railway behind Cloudflare, Cloudflare 524 behavior, origin 499 logs, and HTTP/3 reconnect symptoms. Fieldwork did not access or independently verify that deployment.

## Fieldwork validation retained

The owned work independently supports the issue's mechanism:

- real Node response opening byte before UI data: run `30506032517`, job `90755875694`;
- controlled forwarding proxy remains open during 1,050 ms of source silence with a 450 ms cutoff;
- canonical completion and persistence bytes stay unchanged;
- complete candidate CI and changeset verification pass at `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`.

## Additional edge observations

Any accepted fix should preserve two lifecycle properties:

1. reject invalid `keepAliveMs` before locking or teeing the source and before invoking a persistence callback;
2. let client cancellation settle without waiting for an independent `consumeSseStream` tee branch.

These observations belong in the durable packet. They must not be posted to the public issue without exact authorization.

## Filing checklist

- [x] Current issue and pull-request search repeated on `2026-08-01`.
- [x] Equivalent issue found.
- [x] Duplicate filing retired.
- [x] Private and internal links remain outside any public draft.
- [x] Upstream contact authority remains absent.

## Reopening condition

Prepare a fresh issue draft only if the public issue closes without an accepted equivalent, current `main` still exhibits the behavior, and the user grants exact authority for a new upstream interaction. Repeat duplicate search immediately before drafting or filing.
