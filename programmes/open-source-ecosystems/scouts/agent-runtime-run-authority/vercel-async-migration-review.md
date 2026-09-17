# Vercel AI async-operation migration review

## In simple words

Vercel AI is moving video generation polling out of individual providers and into SDK core. That is the correct architectural direction, but the proposed core loop still treats `timeoutMs` as a clock checked between operations rather than as the authority that owns final settlement.

A status request can begin before the timeout, finish afterward, and still publish success. A status request or retry chain that never settles can outlive the timeout indefinitely. The same gap exists after a webhook notification: the notification wait is bounded, but the final status request is not.

The immediate research goal is to pin this invariant with target-native tests before provider-local behavior is centralized.

## Review boundary

- Upstream design: `vercel/ai#12515`, `feat(video): externalize polling control and webhook support for generateVideo`
- Reviewed head: `dd11a4bf2eebc609292740262951dc00445dbf6a`
- Base shown by the pull request: `1d36c72f32a2135e103631cd07e3182210f84911`
- Primary source: `packages/ai/src/generate-video/generate-video.ts`
- Primary tests: `packages/ai/src/generate-video/generate-video.test.ts`
- Provider contract: `packages/provider/src/video-model/v4/video-model-v4.ts`
- Retrieval date: 2026-08-04
- Upstream contact authorized: `false`

The reviewed upstream head has successful upstream CI. This review concerns an uncovered behavioral invariant, not a currently red upstream check.

## Architecture established

The migration adds optional `doStart` and `doStatus` methods to the video model contract. SDK core decides between legacy `doGenerate`, polling, and webhook-assisted completion.

For the new polling path, `executeStartStatusFlow` currently:

1. optionally creates a webhook endpoint;
2. calls `doStart` through the normal retry wrapper;
3. records `startTime` after submission;
4. bounds the polling sleep to the remaining timeout;
5. checks elapsed time after the sleep;
6. calls `doStatus` through the retry wrapper;
7. accepts `completed`, `pending`, or `error` after that awaited status chain.

This fixes the easiest legacy overshoot, where a full polling interval is slept after little time remains. It does not make the deadline authoritative across the status operation itself.

## Finding 1 — completed status can publish after the deadline

### Current behavior

The loop checks elapsed time immediately before `doStatus`, but performs no elapsed-time or deadline-signal check after `retry(() => model.doStatus(...))` returns.

A status call may therefore begin at `timeoutMs - 1`, finish later, and return `completed`. Core accepts and returns the videos even though the documented maximum wait has elapsed.

The same is true when the elapsed time is consumed by retry attempts or retry backoff rather than by one network request.

### Consequence

The central API would preserve the same semantic defect currently found across several provider-local implementations. Moving ownership into core would amplify the behavior across every migrated provider and make later correction a compatibility question.

### Evidence prepared

`target-tests/vercel-core-poll-deadline-authority.test.ts` contains a deterministic target-native regression that starts `doStatus` before the deadline, advances the clock beyond it, and then releases a completed result. The required outcome is timeout; the reviewed code returns success.

Evidence class: `target-test-prepared` until the branch workflow executes.

## Finding 2 — a status transport can outlive timeout indefinitely

### Current behavior

`doStatus` receives only the original caller abort signal. It does not receive a signal that aborts when `timeoutMs` expires, and the await is not raced against a deadline promise.

An injected fetch implementation, provider adapter, retry attempt, or other status transport that never settles can therefore keep `experimental_generateVideo` pending forever despite a finite `timeoutMs`.

Cooperative cancellation alone would also be insufficient because the SDK intentionally supports injected transports, which may ignore `AbortSignal`.

### Consequence

`timeoutMs` cannot currently serve as a request budget, fallback boundary, workflow deadline, or resource-ownership boundary. A caller may remain pending and remote polling may remain active after the configured timeout.

### Evidence prepared

The target-native regression races a never-settling `doStatus` against a short watchdog. The required result is the configured timeout error before the watchdog. The reviewed code remains pending.

## Finding 3 — webhook mode only bounds notification receipt

### Current behavior

`waitForWebhook` races the notification promise against a timeout delay. Once the notification wins, the timeout controller is cancelled and core invokes `doStatus` outside that race.

A notification can arrive just before the deadline, after which the final status request may run indefinitely or publish a late success.

This conflicts with the public option description that calls `timeoutMs` the maximum time to wait for completion, including webhook mode.

### Evidence prepared

The target-native webhook regression resolves the notification within the budget, holds the final `doStatus`, advances beyond the deadline, and then returns completed. The required outcome is timeout; the reviewed code accepts success.

## Finding 4 — retries are outside one explicit operation budget

`doStart` and every `doStatus` call use the SDK retry wrapper, but the polling deadline is not passed into that wrapper as a remaining budget. A retriable status failure can therefore consume retry delay and later return success after the polling deadline.

This is distinct from ordinary per-request retry policy. The operation deadline must bound the whole status-and-retry sequence even if individual attempts remain retryable.

A follow-up control should use a retriable `APICallError`, force retry delay across the deadline, and verify that timeout—not the second attempt's terminal response—owns settlement.

## Secondary operational concern — parallel call cancellation

When `n` requires several provider calls, core starts independent flows under `Promise.all`. If one flow rejects, `Promise.all` returns that rejection but does not cancel sibling flows.

The siblings may continue polling, waiting for webhooks, or publishing provider work after the user-visible aggregate call has failed. This is not yet promoted as a separate defect because the existing API also parallelizes provider calls, but central async orchestration makes explicit sibling cancellation and remote-operation ownership worth testing.

## Existing test gap

The migration's timeout test repeatedly returns `pending` from promptly settling status calls. It proves that the loop eventually checks elapsed time between polls.

It does not cover:

- a completed status response crossing the deadline;
- an error response crossing the deadline;
- a never-settling status operation;
- retry delay or retry attempts crossing the deadline;
- webhook notification followed by a slow final status request;
- a custom transport ignoring abort;
- aggregate sibling cancellation after one flow fails.

Upstream review discussion already notes that polling timeout behavior differs from the SDK's retry/backoff conventions and could be confusing. No inspected thread states or tests the stronger terminal-authority invariant above.

## Required invariant

After the operation deadline expires:

1. no late `completed` response may become the call result;
2. no late provider error may replace the already-authoritative timeout unless the API explicitly chooses different arbitration;
3. no retry attempt may begin or continue solely because an earlier attempt started within the budget;
4. a never-settling transport must not keep the returned promise pending;
5. caller abort and timeout must remain distinguishable;
6. local timeout must not falsely claim that the remote provider job was cancelled;
7. polling and webhook paths must use the same settlement rule.

The exact equality boundary must also be specified. A conservative rule is that a result observed at or after the deadline cannot publish.

## Likely repair boundary

Create one operation-deadline owner immediately after successful submission. It should:

- calculate one absolute deadline;
- combine caller abort with an internal deadline signal for cooperative cancellation;
- race every sleep, status call, webhook wait, and retry chain against that deadline;
- pass remaining budget into retry behavior or disable retries once no budget remains;
- re-check deadline authority before merging late warnings or metadata and before returning any terminal result;
- preserve provider-specific error translation while keeping timeout settlement authoritative after expiry;
- cancel local sibling flows when an aggregate multi-call operation fails, if that behavior is selected.

The mechanism can live in SDK core without becoming a public provider-utils API. The important deliverable is the invariant and its conformance tests, not a particular helper name.

## Current disposition

**Retain as highest-priority candidate in scout #528.**

Next evidence steps:

1. execute the three exact-head core regressions against `dd11a4bf2eebc609292740262951dc00445dbf6a`;
2. add retry-crosses-deadline and late-error arbitration controls;
3. compare one minimal core repair with the separate provider-utils wrapper alternative;
4. keep the provider-local Google and xAI tests as backward-compatibility evidence;
5. do not contact or modify upstream without separate authorization.
