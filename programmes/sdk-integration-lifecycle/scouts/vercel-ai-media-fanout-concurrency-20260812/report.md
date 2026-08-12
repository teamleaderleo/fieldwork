# Vercel AI SDK media fanout concurrency scout

Issue: #873  
Programme: #13  
Target hub: #2  
Exact public Vercel AI revision: [`59d6defd09f1855ccd95687dcccb1dd0122815d8`](https://redirect.github.com/vercel/ai/commit/59d6defd09f1855ccd95687dcccb1dd0122815d8)  
Worker: `chatgpt:gpt-5.6-sol`  
Retrieval date: 2026-08-12  
Claim scope: interface and mechanism  
Upstream contact authorized: `false`

## Question

When AI SDK automatically turns one media-generation request into several provider calls, who owns the maximum concurrency created by that fanout?

This starts as an ownership/API question. It does not assume the answer is a fixed core limit, provider-local queue, or new public option.

## Core image fanout

[`packages/ai/src/generate-image/generate-image.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/ai/src/generate-image/generate-image.ts):

- accepts `n?: number`, default one;
- accepts `maxImagesPerCall?: number`, but no concurrency option;
- resolves the provider/model per-call count;
- computes `callCount = ceil(n / maxImagesPerCall)`;
- materializes every child call count;
- starts the complete child list through `Promise.all`.

There is no core semaphore, chunk-of-chunks pass, or media-model `supportsParallelCalls` capability below this call site.

The image guide intentionally describes the automatically created provider calls as running in parallel. Therefore unlimited parallel fanout is current product behavior, not a hidden implementation accident.

## Embedding precedent

[`packages/ai/src/embed/embed-many.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/ai/src/embed/embed-many.ts) solves a similar batching problem differently:

- it exposes public `maxParallelCalls?: number`;
- the default is `Infinity`, so unbounded concurrency remains the compatibility default;
- it also reads model `supportsParallelCalls`;
- it groups provider-call chunks into bounded parallel groups;
- each active group still uses `Promise.all`.

This precedent is important but should not be overstated. It proves AI SDK already has a public concurrency-control concept for SDK-created batching; it does **not** prove media APIs must copy it.

## Concrete provider pressure: Black Forest Labs

Current Vercel [`BlackForestLabsImageModel`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/black-forest-labs/src/black-forest-labs-image-model.ts) declares:

```text
maxImagesPerCall = 1
```

Black Forest Labs primary API documentation retrieved on 2026-08-12 states:

- maximum 24 concurrent requests for most endpoints;
- maximum 6 concurrent requests for `flux-kontext-max`;
- requests over those active-task limits receive HTTP 429;
- queueing is recommended for high-volume use.

That produces a direct composition:

```text
ordinary BFL one-image model
n = 25
maxImagesPerCall = 1
core child count = 25
core starts all 25 through Promise.all
provider documented active-task ceiling = 24
```

For `flux-kontext-max`, the pressure point is only `n = 7` against a six-active-task ceiling.

This does not prove a live 429 because no paid request was made. It establishes that one SDK call can construct a provider-call burst larger than the documented provider concurrency allowance.

## Other-provider negative evidence

Replicate's primary API documentation publishes request-rate limits rather than the same fixed active-task ceiling:

- prediction creation has a request-rate allowance;
- bursts above the normal rate can be accepted before throttling;
- higher account limits can be granted.

That difference argues **against** a universal core concurrency number such as 6, 10, or 24.

Provider/account limits can vary by endpoint, account, deployment, model, and commercial tier. A static numeric model capability may therefore also be too crude.

## Prepared target-native characterization

Owned target PR: `teamleaderleo/ai#121`  
Exact base: `59d6defd09f1855ccd95687dcccb1dd0122815d8`  
Characterization head: `def36f33770006371d98aacada7646db640aa877`  
Changed production files: none  
Changed test files: one

The test uses `MockImageModelV4` with `maxImagesPerCall = 1` and requests `n = 25`.

Each child increments an active count and waits on one shared release latch. No child is allowed to settle until every expected child has had a chance to start.

The control records:

- total started child calls;
- current active child calls before release;
- maximum observed simultaneous children;
- final aggregation after releasing all children.

Current-source prediction:

```text
started = 25
active before release = 25
peak = 25
final generated images = 25
```

This is `target-test-prepared` until execution reaches the assertion.

## Candidate ownership directions

### A. Public media `maxParallelCalls`

Give `generateImage` and possibly `experimental_generateVideo` an explicit concurrency option analogous to `embedMany`.

Likely semantics:

- default `Infinity` to preserve current behavior;
- positive finite values bound only SDK-created child calls inside one public invocation;
- caller abort cancels queued/not-yet-started children and propagates to active children;
- ordering of returned media remains the logical child/output order rather than completion order;
- retries remain inside each child and therefore consume the child concurrency slot until that child's retry lifecycle settles.

Advantages:

- caller can align concurrency with provider/account quotas;
- no stale quota catalog inside AI SDK;
- one invocation still returns one aggregate result;
- direct precedent exists in `embedMany`.

Costs/questions:

- public API growth;
- needs validation for zero/negative/non-integer/Infinity;
- queued child ownership must compose with abort and sibling failure (#868);
- video remote jobs can outlive local slot release depending on when a child is considered settled.

### B. Provider/model concurrency capability

Let media models expose whether or how much automatic parallelism they support.

Advantages:

- provider adapter can prevent obviously unsupported parallel execution.

Problems:

- BFL's limits differ by endpoint/model;
- customer-specific higher limits make a baked-in number wrong for some users;
- quotas can change without package updates;
- account credentials and deployment identity can affect the applicable limit.

A boolean `supportsParallelCalls` is safer than a numeric quota but still cannot express useful limits such as six versus twenty-four.

### C. Provider-local queue or semaphore

The BFL adapter could serialize/bound all requests it starts.

Advantages:

- provider knows its documented defaults;
- protects direct adapter calls as well as `generateImage` fanout.

Problems:

- queue ownership becomes process-global or client-instance scoped;
- different API keys/projects may have independent quotas;
- higher negotiated limits cannot be used unless configurable;
- cross-request fairness and cancellation become provider-adapter responsibilities;
- a per-provider queue can unexpectedly couple unrelated callers.

This is a much larger lifetime contract than adding an aggregate-call option.

### D. Current unlimited fanout + documentation

Retain current implementation and tell callers to keep `n` within provider concurrency allowances or manually split calls.

This is defensible because:

- current image docs explicitly say automatic calls run in parallel;
- retry handling can recover some throttling responses;
- no portable media concurrency number exists.

The weak point is ergonomics: callers cannot keep one aggregate `generateImage` call while bounding only the concurrency that the SDK itself creates.

### E. Conservative built-in default

Set a finite concurrency default in media core.

This currently loses. Any single number is ungrounded across provider/account/model limits and changes existing timing/performance behavior.

## Interaction with retries

A provider 429 is not automatically proof that fanout concurrency is wrong. AI SDK retries retryable failures per child.

However, relying on retries as the only concurrency mechanism can create a thundering batch:

1. core starts more children than the active-task allowance;
2. several receive throttling responses;
3. their independent retry loops schedule later attempts;
4. successful siblings and retries compete as provider capacity becomes available.

A bounded caller-level executor could avoid creating avoidable throttling in the first place, while the existing retry policy remains the fallback for external/shared quota pressure.

This is a hypothesis about efficiency and request pressure, not yet target-executed or live-provider evidence.

## Interaction with #868

#868 is now target-executed and shows that after one fanout child makes the aggregate operation fail, already-started siblings continue independently.

A future bounded executor would create a shared implementation boundary but must not silently decide #868's policy:

- queued children not yet started after aggregate failure;
- active children already running after aggregate failure;
- caller abort;
- provider retry delays;
- output ordering.

Concurrency and sibling-failure authority remain separate contracts even if implemented by one helper.

## Interaction with #870

#870 owns the meaning of one fixed seed across automatic image fanout. Serializing children does not change the repeated-seed request content, so concurrency cannot be treated as a repair for deterministic duplicates.

## Negative results

- `embedMany` does not use a conservative finite default; its `maxParallelCalls` defaults to `Infinity`. Do not claim AI SDK generally promises bounded concurrency.
- BFL's documented 24/6 limits do not justify hard-coding those numbers in core.
- A provider-side 429 can be a normal shared-quota event even when one call's concurrency is reasonable. No live 429 is claimed here.
- Replicate's documented rate model differs from BFL's active-task model, weakening any universal provider capability number.
- This is not a security claim and does not imply a provider charge occurs for every throttled request.

## Overlap

Fieldwork searches found no existing Vercel lane for media `maxParallelCalls` or automatic image/video fanout concurrency.

Read-only public Vercel issue searches under image/video concurrency, rate-limit batching, and `maxParallelCalls` wording found no matching owner at retrieval time.

Adjacent internal owners:

- #868 — sibling lifetime after fanout failure;
- #870 — deterministic seed semantics across successful image fanout;
- #454 — asynchronous provider task identity and retry/deadline authority.

## Evidence state

- source-confirmed: image fanout launches complete child list through `Promise.all`;
- source-confirmed: BFL adapter is one image per call;
- provider-documented: BFL active-task ceilings and queueing guidance;
- documented: image automatic calls run in parallel;
- source-confirmed: `embedMany` exposes `maxParallelCalls`, default `Infinity`;
- target-test-prepared: peak-25 mock image control;
- target-executed: pending;
- integration-executed: no live provider request.

## Current recommendation

Execute the provider-independent peak-concurrency control first.

If it confirms the expected all-at-once burst, prefer comparing **caller-level bounded aggregate concurrency** against **documentation-only/current behavior**. Do not hard-code provider quotas in core and do not add a provider-global semaphore without a separate owner/credential/fairness design.

No production candidate is selected yet.

No third-party upstream mutation occurred.
