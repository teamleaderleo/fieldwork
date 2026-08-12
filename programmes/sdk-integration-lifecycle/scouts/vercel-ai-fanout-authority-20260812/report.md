# Vercel AI SDK aggregate fanout authority scout

Issue: #868  
Programme: #13  
Target hub: #2  
Exact public Vercel AI revision: [`59d6defd09f1855ccd95687dcccb1dd0122815d8`](https://redirect.github.com/vercel/ai/commit/59d6defd09f1855ccd95687dcccb1dd0122815d8)  
Worker: `chatgpt:gpt-5.6-sol`  
Retrieval date: 2026-08-12  
Claim scope: mechanism and interface  
Upstream contact authorized: `false`

## Question

When one public AI SDK operation fans out into several side-effecting provider calls, what owns sibling lifetime after one child makes aggregate success impossible?

This scout begins as a contract question, not a defect claim.

## Current source map

### Image generation

[`packages/ai/src/generate-image/generate-image.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/ai/src/generate-image/generate-image.ts) computes the number of child calls from `n` and `maxImagesPerCall`, launches those calls through `Promise.all`, and forwards the caller's `abortSignal` into each child model call.

The aggregate function has no additional abort controller or generation object for sibling failure. Therefore one child rejection can reject the public operation while a sibling remains pending under an unaborted caller signal.

Current tests strongly cover happy-path fanout: requested counts, split call sizes, warnings, usage, response metadata, and provider metadata are aggregated. The sampled abort test verifies caller signal forwarding. No sampled test assigns an aggregate failure policy when one parallel child rejects.

### Video generation

[`packages/ai/src/generate-video/generate-video.ts`](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/packages/ai/src/generate-video/generate-video.ts) uses the same aggregate `Promise.all` fanout from `n` and `maxVideosPerCall`.

A child video call can be much longer-lived than an image call. On the start/status path it may own:

- a remote operation created by `doStart()`;
- polling delays;
- `doStatus()` requests and retries;
- webhook wait/finalization;
- final asset download.

Current core also now mints one stable idempotency key per logical `doStart()` before retrying that start. That reduces duplicate remote starts within one child. It does not define what sibling children should do after a different child fails.

The accepted owned-fork deadline candidate `teamleaderleo/ai#30` explicitly listed sibling provider calls as outside its local operation-deadline contract. That limit remains useful here but is not evidence that sibling continuation is wrong.

## Public API framing

The current [`experimental_generateVideo` reference](https://redirect.github.com/vercel/ai/blob/59d6defd09f1855ccd95687dcccb1dd0122815d8/content/docs/07-reference/01-ai-sdk-core/13-generate-video.mdx) presents `n` as one requested number of outputs and `maxVideosPerCall` as the threshold that causes the SDK to make multiple provider calls.

Historical image batching introduction [`218d001890e930e02c5cbdc2d3bc5ffbf2e3523a`](https://redirect.github.com/vercel/ai/commit/218d001890e930e02c5cbdc2d3bc5ffbf2e3523a) similarly introduced automatic multi-call batching around provider limits. Its retained review discussion concerns the setting and documentation. No sampled review text defines partial failure, sibling cancellation, or partial-result recovery.

This leaves the important normative boundary open rather than proving a defect.

## Why the question generalizes

The provider/media details can be removed without changing the engineering question:

> One API invocation creates several child operations. One child selects aggregate failure. Which children still have authority to consume resources, make side effects, or publish callbacks afterward?

Useful dimensions are:

- fail-fast settlement versus all-settled settlement;
- local cancellation versus remote cancellation;
- child work already accepted before sibling failure;
- whether partial success is intentionally discarded;
- whether late child rejection is fully adopted and contained;
- whether caller abort and sibling-failure abort need distinct reasons;
- whether all child work shares one logical billing/retry/recovery identity or only one return value.

## First target-native discriminators

### Image fanout

Use `MockImageModelV4` with `n = 2` and `maxImagesPerCall = 1`.

1. Prove both child calls start.
2. Child A rejects with a sentinel error.
3. Child B remains pending and records its received signal.
4. Require the aggregate promise to reject with A.
5. Observe whether B's signal is still live after aggregate rejection.
6. Allow B to resolve after aggregate failure and record any callback/state consequence.
7. Repeat with B rejecting late and install an unhandled-rejection observer.
8. Caller-abort control: abort the caller and prove both children see the caller-owned signal.

The discriminator should describe current behavior before asserting a desired policy.

### Video fanout

Use `MockVideoModelV4` with `n = 2` and `maxVideosPerCall = 1` on the start/status path.

1. Acknowledge two distinct remote operation IDs.
2. Child A reaches terminal error.
3. Child B remains pending in status work.
4. Observe whether B's polling/status signal is changed by A's failure.
5. Allow B to complete late and confirm no aggregate result is published after the public promise already failed.
6. Repeat with B's status operation rejecting late.
7. Caller-abort control separates caller cancellation from any proposed aggregate sibling-retirement policy.

No live provider or paid operation is required for the first proof.

## Policy candidates

### A. Fail-fast plus best-effort sibling retirement

The first child failure selects aggregate failure. The SDK aborts locally owned sibling work. This can stop cooperative transports, retries, polling, downloads, and future callbacks. It cannot honestly claim a remote provider job was cancelled unless that provider exposes and executes a cancellation operation.

This policy is attractive if the public call represents one indivisible logical request and successful sibling outputs are unusable once aggregate success is impossible.

### B. All-settled aggregate failure

All started children are awaited. The public operation rejects only after every child settles.

This preserves complete local accounting and avoids leaving adopted child promises behind, but one fast failure can remain pending behind slow or hung siblings. It also gives the caller no partial result through the current API.

### C. Explicit independent-child behavior

Retain current fail-fast `Promise.all` behavior and define child operations as independent once started. Caller abort remains the only cross-child cancellation authority.

This may be a valid contract, especially when remote work cannot be reliably cancelled, but the lifetime/cost implication should be explicit enough for callers requesting large `n`.

### D. Partial-result return surface

Return successful outputs plus child failures.

This changes the public result model substantially and should not be selected merely to solve lifetime bookkeeping. Keep it as a comparison boundary, not the default repair direction.

## Negative results / things not to overclaim

- `Promise.all` itself adopts the child promises it is given; a later sibling rejection is not automatically an unhandled rejection merely because the aggregate already rejected. A discriminator must observe actual runtime behavior rather than assume an unhandled-rejection consequence.
- Best-effort abort of an in-flight provider call does not imply reversal of an already accepted/billable remote operation.
- The new stable idempotency key for video `doStart()` addresses duplicate submission retries inside one child and does not establish sibling failure policy.
- The existing post-submission video deadline finding governs one child's local waiting authority, not sibling aggregation.

## Overlap

Fieldwork searches for aggregate sibling cancellation, partial fanout failure, `maxImagesPerCall`, `maxVideosPerCall`, and `Promise.all` found no existing Vercel issue owning this exact question.

Adjacent owners:

- #454 — asynchronous provider task identity and retry/deadline boundaries;
- owned AI PR #30 — post-submission video operation deadline;
- #545 — overlapping chat request authority;
- #461 — automatic chat resubmission coalescing.

Keep #868 separate unless execution shows the same primitive should govern both aggregate media fanout and another existing owner.

## Evidence state

- source-confirmed: fanout and caller-signal propagation;
- documented: one public `n` can require multiple provider calls;
- history-read: introducing image batching review did not expose a sampled failure policy;
- target-test-prepared: image and video discriminators specified above;
- target-executed: not yet;
- integration-executed: not yet.

## Stop condition

Stop after the image and video target-native discriminators execute and one conclusion wins:

1. a provider-independent ownership defect exists with a bounded core repair;
2. independent child continuation is deliberate/documentable behavior and the lane becomes a contract note;
3. meaningful improvement requires a broad partial-result/cancellation API redesign unsupported by current product contracts.

## Current recommendation

Execute the provider-independent discriminators before writing production source. Do not contact upstream and do not characterize continued sibling work as incorrect until the contract comparison has reversing evidence.

No third-party upstream mutation occurred.
