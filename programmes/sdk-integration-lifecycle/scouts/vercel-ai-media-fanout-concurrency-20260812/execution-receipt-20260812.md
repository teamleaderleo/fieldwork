# Execution receipt — image fanout peak concurrency

Issue: #873  
Durable report: `report.md`  
Exact public Vercel AI base: [`59d6defd09f1855ccd95687dcccb1dd0122815d8`](https://redirect.github.com/vercel/ai/commit/59d6defd09f1855ccd95687dcccb1dd0122815d8)  
Target characterization: `teamleaderleo/ai#121`  
Characterization head: `def36f33770006371d98aacada7646db640aa877`  
Execution carrier: `teamleaderleo/ai#122`  
Carrier head: `e661a9a3cb80e00292f46593d8f207cff908d182`  
Run: `31558628164`  
Job: `93996131656`  
Runner: Ubuntu 24.04 / Node 22  
Evidence class: `target-executed`

## Gates

The dedicated target-native workflow completed successfully and reached every requested gate:

1. frozen-lockfile workspace install — passed;
2. focused characterization formatting — passed;
3. `ai` package type-check — passed;
4. `ai` package build — passed;
5. focused peak-concurrency control — passed;
6. existing `generate-image` Node suite — passed.

## Executed result

The focused control calls `generateImage()` with:

```text
n = 25
model.maxImagesPerCall = 1
maxRetries = 0
```

Every child increments an active counter and then blocks on one shared release latch. No child is permitted to settle until the test has observed all expected child entries.

Before release, the target-native control observed and required:

```text
started children = 25
active children = 25
peak simultaneous children = 25
```

After the latch was released, all children completed and the public aggregate result contained 25 images.

Executed conclusion:

> Current `generateImage()` can enter all SDK-created one-image child calls concurrently before any child settles.

## Provider composition boundary

Black Forest Labs' current Vercel adapter reports one image per call. Primary BFL API documentation retrieved for the scout states active-task ceilings of 24 concurrent requests for most endpoints and 6 for `flux-kontext-max`, with HTTP 429 above the allowance and queueing recommended for high-volume use.

The target-native control proves the SDK side of that composition. No live BFL request or 429 is claimed.

## What this does not prove

- It does not prove a universal finite media concurrency limit should be added.
- It does not prove a caller using BFL will always receive a 429 at those exact counts; account/provider conditions can vary.
- It does not establish that retries are broken.
- It does not establish whether concurrency ownership belongs in core, the provider model, or documentation.

## Current comparison

The strongest implementation comparison remains:

1. add caller-owned media `maxParallelCalls`, likely defaulting to `Infinity` for compatibility, mirroring the existing `embedMany` concept;
2. retain current unlimited fanout and document the provider-limit interaction.

Provider-global queues and fixed core numeric caps remain weaker because provider/account limits vary and could couple unrelated callers.

No third-party upstream interaction occurred.
