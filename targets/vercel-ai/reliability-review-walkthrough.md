# Vercel AI SDK Reliability Review Walkthrough

This document is the human review entry point for the Vercel AI SDK reliability campaign. It deliberately groups findings by engineering boundary rather than by discovery order or issue number.

## What this portfolio is — and is not

The work is a reliability and lifecycle audit of the Vercel AI SDK monorepo and its first-party packages and examples. It is not a claim that every finding is a security vulnerability, nor that the SDK is generally unusable.

Most findings live at boundaries that are difficult to test exhaustively:

1. Web Streams reader ownership and cancellation;
2. overlapping asynchronous requests and stale generations;
3. callbacks that can throw or return rejected promises;
4. retry, polling, reconnect, and deadline authority;
5. state that spans more than one request, step, or process lifetime.

A large SDK can have many individually correct components while still accumulating lifecycle defects at the seams between them. The audit intentionally stresses those seams.

## Why several defects appeared together

### 1. The same primitive appears in many packages

Readable streams, abort signals, delayed promises, retry helpers, and callback hooks are reused across core generation, UI streams, MCP transport, workflow transport, provider polling, and framework adapters. A missing ownership rule can therefore appear in several distinct call paths without those call paths being duplicates.

### 2. Happy-path tests do not prove terminal ownership

A test that receives the expected chunks does not necessarily prove that:

- the reader lock was released;
- the losing asynchronous task was adopted;
- cancellation reached the true producer;
- no stale request can publish afterward;
- cleanup failure did not replace the primary result;
- no unhandled rejection was emitted after the assertion completed.

The campaign adds discriminators for those terminal properties.

### 3. Compatibility layers multiply race combinations

The repository combines browser Web Streams, Node runtimes, Edge runtimes, multiple UI frameworks, transport protocols, workflow durability, provider-specific asynchronous jobs, and user callbacks. The number of possible orderings grows much faster than the number of public APIs.

### 4. Some behavior became newly important

The SDK is actively evolving. For example, core-owned asynchronous video polling was merged into public main on 2026-08-03. A deadline weakness that was previously research against an open design is now relevant to released core behavior.

## Evidence levels

Use these labels consistently during review.

### Runtime-confirmed

A minimal standalone probe demonstrates the platform behavior or failure mechanism. This is strong evidence that the underlying primitive behaves as claimed, but it does not replace package-native regression tests.

### Target-native confirmed

A repository test fails on the unpatched target and passes on the exact candidate. This is the preferred discriminator.

### Exact-head CI passed

The recorded commit SHA passed the relevant repository matrix. A later commit invalidates the receipt, even when the later change looks cosmetic.

### Technically ready

The exact diff has target-native controls, exact-head CI, complete-diff review, and no known blocking overlap or compatibility issue. This does not authorize public submission or merge.

### Hold

The candidate contains a known defect, incomplete ownership rule, stale evidence, or unresolved compatibility question. Do not prepare it for public delivery.

### Research

The failure is established, but the production boundary or compatible repair is not yet selected.

## Already submitted publicly

### AsyncIterableStream rejected-read cleanup

Public PR: `vercel/ai#18371`

The public contribution releases the iterator's reader when `reader.read()` rejects, preserves the exact source rejection, avoids cancelling an already-errored stream, and leaves later iterator calls terminal.

Current state:

- the AI SDK automated bugfix review approved the change and classified risk as low;
- a bot-generated competing PR, `vercel/ai#18400`, implements the same production shape with a consolidated test file;
- no maintainer-requested source change is currently recorded;
- the visible Vercel status failure is an external deployment authorization status, not a product-test failure.

Do not prepare or send this campaign again. Any next action should respond only to concrete upstream maintainer direction about which duplicate PR to retain.

## Current review queue

### Ready: URL-support regular expressions

Owned-fork PR: `teamleaderleo/ai#22`

Problem: shared global or sticky `RegExp` objects mutate `lastIndex`, so identical URL checks can alternate or depend on caller-owned state.

Repair: save `lastIndex`, evaluate from zero, and restore the caller value in `finally`.

Review focus:

- confirm caller state is restored on match, mismatch, and exception;
- confirm ordinary non-stateful regex behavior is unchanged;
- confirm cloning the regex would not offer a necessary semantic advantage;
- confirm no URL or media-type matching rule changes.

Disposition: technically ready and the smallest current delivery candidate.

### Ready: response-size reader cleanup

Owned-fork PR: `teamleaderleo/ai#23`

Problem: `reader.cancel()` rejection can replace an already established size-limit error, upstream read error, or successful result.

Repair: contain cancellation failure and always release the reader lock.

Review focus:

- confirm cleanup failure cannot replace the primary outcome;
- confirm cancellation is still attempted;
- confirm lock release remains unconditional;
- confirm early `Content-Length` behavior and byte accounting are untouched.

Disposition: technically ready.

### Ready with overlap decision: UI error formatter containment

Owned-fork PR: `teamleaderleo/ai#15`

Problem: a throwing custom `onError` formatter can escape while another failure is being handled, leave the UI stream open, and produce an unhandled rejection.

Repair: make the synchronous formatter boundary nonthrowing, replace the async Promise-constructor drain, and close on every terminal drain path.

Review focus:

- confirm successful custom formatter output remains unchanged;
- confirm exactly one generic error chunk is emitted on formatter failure;
- confirm synchronous execute, asynchronous execute, and merged-stream failures all close;
- decide how to present the patch relative to the older, broader upstream PR `vercel/ai#7855`, which proposes asynchronous formatter support.

Disposition: technically ready, but public delivery needs an explicit overlap strategy.

### Hold: MCP inbound SSE lifecycle

Owned-fork PR: `teamleaderleo/ai#20`

What is already fixed:

- locally single-flight connection startup;
- coalesced restart while an owner promise settles;
- clean-EOF reconnectability;
- `Last-Event-ID` resumption;
- server-provided SSE retry delay;
- bounded consecutive reopen failures;
- close-time timer cleanup;
- existing `405 -> 202 -> GET` compatibility.

Blocking finding: each inbound SSE connection acquires a reader, but the current terminal paths can retire the connection record without calling `reader.releaseLock()`.

Required repair:

- request cancellation through `connection.close()`;
- release the lock in the `processEvents()` terminal `finally`, after the pending read has settled;
- suppress release cleanup errors so they cannot replace the primary outcome;
- test clean EOF, explicit close during a pending read, and read error plus cancellation failure.

Disposition: hold until a new exact head passes the full matrix and complete-diff review.

### Hold: explicit abort terminal ownership

Owned-fork PR: `teamleaderleo/ai#7`

What is already fixed:

- abort can reject public result roots without waiting for another provider chunk;
- outward abort publication and closure do not wait for observability callbacks;
- provider cancellation is requested promptly;
- a later provider error cannot replace the selected abort outcome;
- the pre-registration provider-stream gap is handled.

Blocking finding: Node 26 reported unhandled rejections even while the assertions passed. The pattern matches lazy delayed promises being rejected before an internal observer is attached.

Selected repair direction:

```ts
const promise = delayedPromise.promise;
void promise.catch(() => {});
delayedPromise.reject(error);
```

Apply the same ordering to the initial-response-message root, remove the extra async observer wrapper, and add explicit unhandled-rejection controls on Node 22 and Node 26.

Disposition: hold. Old carriers `teamleaderleo/ai#1` and `#13` are closed as superseded.

### Research: core video polling deadline authority

Owned-fork PR: `teamleaderleo/ai#24`

The test-only characterization establishes that the merged core loop can:

- accept a completed status after `timeoutMs`;
- wait indefinitely for a status request that never settles;
- allow a retry chain to cross the deadline and later publish success;
- accept a late final status after a webhook arrived within the budget.

A production repair needs one authoritative operation deadline covering sleeps, webhook wait, every status request, retry delay and execution, and terminal-result acceptance.

The implementation must combine cooperative cancellation with a deadline race because an injected transport may ignore abort. The losing task must be safely adopted. Local timeout must not imply that the already-created remote provider job was cancelled.

Disposition: confirmed research, not yet a delivery patch.

## WorkflowAgent currency

Public main `94e6a99cd9f599b8d400e856d64edb2098d6e349` includes a useful adjacent fix for streaming executed sibling results when another tool pauses, but three campaign gaps remain:

- normal and approved local tools still receive no effective workflow abort signal;
- approval IDs are still `approval-${toolCallId}`;
- approved tools still receive `messages: []` even though telemetry receives the initiating prompt messages.

See [`workflow-agent-current-main-check.md`](./workflow-agent-current-main-check.md) for the exact current source boundary.

## Suggested human review order

1. PR #22 — smallest and lowest-risk behavioral patch;
2. PR #23 — compact cleanup policy patch;
3. PR #15 — technically ready, then decide overlap strategy;
4. PR #20 — review only after reader-release repair and new CI;
5. PR #7 — review only after zero-unhandled-rejection evidence;
6. PR #24 — review the contract and repair design, not the current test-only diff as a release candidate.

## Review checklist for every candidate

1. Is the failure reproduced by a discriminator that would fail on the unpatched source?
2. Does the repair have one clear owner for settlement, cancellation, and resource release?
3. Can cleanup failure mask the primary outcome?
4. Can a losing asynchronous task reject without an observer?
5. Can an older request or generation publish after a newer one starts?
6. Are callback failures contained according to the documented contract?
7. Does exact-head CI include every runtime relevant to the changed boundary?
8. Has current public main changed the owning file or made the patch obsolete?
9. Is there active upstream overlap that changes the delivery route?
10. Does the changeset match the changed public package and behavior?

## Delivery boundary

A `READY` label means the internal technical work is suitable for human delivery review. It does not authorize a public issue, pull request, comment, review, reaction, merge, release, or deployment.
