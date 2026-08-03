# Vercel AI durable-workflow deadline boundary

## In simple words

The async-video migration lets callers replace ordinary timers with a durable workflow sleep function. Its own webhook example deliberately supplies a delay function that never resolves so an unused competing sleep is not committed when the webhook wins.

That makes the configured webhook `timeoutMs` ineffective: the timeout branch is implemented by calling the supplied delay function, so neither webhook receipt nor timeout settles when the webhook is lost.

This is related to, but distinct from, the late-status deadline bug. It suggests that one `delay` callback cannot safely represent polling intervals, cleanup-cancellable timers, and an authoritative operation deadline in every runtime.

## Exact source boundary

- Reviewed migration head: `dd11a4bf2eebc609292740262951dc00445dbf6a`
- Example: `examples/next-workflow/workflow/async-apis.ts`
- Core timeout owner: `packages/ai/src/generate-video/generate-video.ts`
- Retrieval date: 2026-08-04
- Upstream contact authorized: `false`

## Observed example behavior

The workflow example defines `waitWithoutSchedulingTimeout()` as a promise that never settles. In webhook mode it passes that function as `poll.delay` while also passing `timeoutMs`.

Core `waitForWebhook` implements timeout by racing the webhook receipt against:

```text
delay(timeoutMs).then(throw timeout)
```

With the example's delay function, that timeout promise never resolves or rejects. If the webhook is never delivered, the generation remains pending indefinitely despite the named timeout constant.

The example comment explains the motivation: a competing durable sleep would be left uncommitted when the webhook wins. That is a legitimate workflow concern, but it means the public timeout contract is no longer true for this integration.

## Why an ordinary AbortController is not enough

A local timer or `AbortSignal.timeout()` can enforce wall-clock settlement in an ordinary Node process. A durable workflow may suspend and replay, and its status calls can themselves be workflow steps. A process-local timer does not necessarily represent the workflow's logical time or survive suspension.

Conversely, a user-provided durable sleep may not be safely cancellable after another event wins a race. The example avoids scheduling it entirely by returning a never-settling promise.

The design therefore needs to decide which layer owns the authoritative deadline:

1. SDK wall-clock time inside one process;
2. a durable workflow scheduler or cancellation scope;
3. an outer caller-owned workflow timeout;
4. a provider-native operation expiry;
5. some explicit combination with documented arbitration.

## API pressure

The current `poll.delay` callback is asked to support several different jobs:

- interval sleeping;
- remaining-budget sleeping;
- webhook timeout;
- cancellation cleanup after another branch wins;
- durable workflow suspension.

Those jobs have different commit and cancellation semantics. A stronger design may need separate capabilities, for example:

- `sleep(interval, signal)` for polling cadence;
- `withDeadline(operation, remaining)` or an operation-scoped deadline signal;
- explicit outer-workflow ownership where core timeout is disabled;
- a documented `timeoutMs: undefined` state instead of silently accepting an unenforceable timeout.

This note does not select the final API. It records that a core fix based only on calling the custom delay or only on a process-local timer will not cover every advertised integration.

## Evidence status

Evidence class: `source-read`.

A target-native test could reproduce the never-settling custom webhook delay, but the expected result depends on whether a custom delay is contractually required to settle. Before promoting this into a separate defect, the API contract and durable workflow ownership need an explicit decision.

## Current disposition

Retain as an architectural constraint under scout #528 and the Vercel deadline candidate. Do not combine it with the four ordinary core regressions until the intended durable timeout contract is settled.
