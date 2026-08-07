# Vercel AI durable-workflow deadline boundary

## In simple words

The async-video migration lets callers replace ordinary timers with a durable workflow sleep function. Its own webhook example deliberately supplies a delay function that never resolves so an unused competing sleep is not committed when the webhook wins.

That makes the configured webhook `timeoutMs` ineffective: the timeout branch is implemented by calling the supplied delay function, so neither webhook receipt nor timeout settles when the webhook is lost.

The example pins Workflow `4.2.4`. Workflow `4.2.6` later hardened exactly the hook-versus-sleep `Promise.race` pattern, and current Vercel guidance recommends that pattern for webhook timeouts. The example therefore appears to combine an older runtime pin with a workaround that silently removes the advertised deadline.

This is related to, but distinct from, the late-status deadline bug. It suggests that one `delay` callback cannot safely represent polling intervals, cleanup-cancellable timers, and an authoritative operation deadline across every supported runtime version.

## Exact source boundary

- Reviewed migration head: `dd11a4bf2eebc609292740262951dc00445dbf6a`
- Example: `examples/next-workflow/workflow/async-apis.ts`
- Example dependency: `examples/next-workflow/package.json`, `workflow: 4.2.4`
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

The example comment explains the motivation: a competing durable sleep would be left uncommitted when the webhook wins. That avoids one older replay/commit concern, but it makes the public timeout contract false for the example.

## Current Workflow evidence

Primary current sources point toward durable racing rather than disabling the timeout:

- Workflow `4.2.6` release notes say the runtime fixed replay corruption when a workflow races a hook read against `sleep()`, making the committed branch win deterministically. See the Workflow releases and `vercel/workflow#2171`.
- Vercel's current human-in-the-loop guide explicitly bounds an indefinitely suspended webhook with `Promise.race([webhook, sleep('24h')])`.
- Vercel's June 2026 Workflow cancellation announcement says Workflow 5 beta supports standard `AbortController` and `AbortSignal` across workflow and step boundaries, including timeout races that cancel in-flight work.

Sources:

- https://github.com/vercel/workflow/releases
- https://github.com/vercel/workflow/pull/2171
- https://vercel.com/kb/guide/human-in-the-loop-with-chat-sdk-and-workflow-sdk
- https://vercel.com/changelog/workflow-sdk-now-supports-inflight-cancellation

These sources do not prove that simply upgrading the example is sufficient for every version and deployment. They do establish that an infinite delay is not the current intended general timeout pattern.

## Why an ordinary AbortController is not enough

A local timer or `AbortSignal.timeout()` can enforce wall-clock settlement in an ordinary Node process. A durable workflow may suspend and replay, and its status calls can themselves be workflow steps. A process-local timer does not necessarily represent the workflow's logical time or survive suspension.

Conversely, a user-provided durable sleep has version-specific replay and cancellation semantics. The active example avoids those semantics entirely by returning a never-settling promise, but that also removes the deadline.

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

For the current example, the smallest discriminating comparison is:

1. retain Workflow `4.2.4` plus the infinite delay and confirm lost-webhook non-settlement;
2. upgrade to a version containing the hook-versus-sleep race repair and pass durable `sleep` as the delay;
3. verify webhook-first, timeout-first, replay, and cancellation behavior;
4. confirm that no losing wait corrupts replay or remains operationally active.

This note does not select the final public API. It records that a core fix based only on a process-local timer will not cover durable execution, while the current example's custom delay does not enforce its own advertised timeout.

## Evidence status

Evidence class: `source-read` plus documented current Workflow behavior.

The lost-webhook outcome follows directly from the supplied never-settling promise. A full integration claim still requires execution under the exact Workflow versions because replay and cancellation behavior changed after `4.2.4`.

## Current disposition

Retain as an architectural constraint and a bounded integration-test candidate under scout #528. Keep it separate from the four ordinary core regressions until exact-version durable execution settles whether the repair is dependency/example-only or requires an AI SDK API change.
