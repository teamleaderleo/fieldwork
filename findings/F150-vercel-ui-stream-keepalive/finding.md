# F150: Keep idle Vercel AI UI streams alive without polluting persisted protocol data

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#150`  
Canonical implementation: `teamleaderleo/ai#4`  
Exact implementation head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`  
Exact behavior-executed head: `7c8b95b12e7a47e0f614ff949b645e546488eea7`  
Exact base revision: `2b872b0db3769decf69945830c66a897c1e37347`  
Strongest evidence class: `integration-executed` for first-byte and controlled proxy liveness  
Review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

A healthy model or tool can remain silent for a long time. During that silence an HTTP response may not emit its first body byte, and a proxy may close the connection as idle.

The selected repair adds optional `keepAliveMs`. When enabled, only the client-facing Server-Sent Events branch sends an immediate comment and later idle comments. SSE clients ignore comments. Persistence and resumable storage continue receiving the original canonical stream.

## Why this matters

A healthy operation can appear dead before its first visible chunk. Injecting heartbeat data into the canonical stream would instead contaminate persistence, replay, and protocol state.

Leaving the current behavior unchanged preserves the bounded first-byte and idle-timeout failure. Frequency and an appropriate interval remain deployment-specific.

## Governing invariant

Optional transport liveness bytes may affect only the client response branch and must not change canonical UI data, persisted SSE bytes, resumable replay, or disabled-option behavior.

Required properties:

1. emit a first body byte before source data when enabled;
2. refresh liveness during silence;
3. use protocol-defined ignorable comments;
4. keep synthetic bytes out of persistence;
5. validate before source lock, tee, or callbacks;
6. retain one pending source read and demand-aware comments;
7. clear timers and ignore late reads on every terminal path;
8. keep interval guidance deployment-specific.

## Current finding

A client-only SSE-comment wrapper after the persistence tee is the narrowest compatible design. It emits `: stream-open\n\n` immediately and `: keep-alive\n\n` after idle intervals. Real data resets the interval. Client cancellation clears timers and requests downstream cancellation without waiting for an independent persistence branch.

Repository formatting is now resolved at exact head `b0bbcf29aec186014ddd05dc05194da0a5b8a114`: the temporary formatter workflow deleted itself and `ultracite fix` changed only the two intended helper tests. The automation-authored successor produced `action_required` runs with zero jobs; this is trigger evidence, not product failure. Exact head `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb` adds the required 100-iteration open/cancel soak and has ordinary CI `30592239115` plus Verify Changesets `30592239084` queued.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The pinned helper may emit no body until source data or close | `source-read` | response helper at `2b872b0d...` | Header behavior depends on adapter/runtime |
| Immediate comment flushes a real Node response | `integration-executed` | run `30506032517`, head `7c8b95b...` | Controlled Node runtime |
| Periodic comments preserve a connection past a controlled idle deadline | `integration-executed` | 450 ms deadline, 1050 ms source silence | Synthetic proxy |
| Client-only placement preserves persistence bytes | `target-executed` | PR #4 unit controls and source diff | Exact current-head CI pending |
| Repository formatter owns final spelling | `target-executed` | commit `b0bbcf29...` removed carrier and formatted two tests | Its zero-job runs are not a product gate |
| Repeated cancellation retires timer and source work | `target-test-prepared` | 100-iteration soak at `b4b57263...` | Hosted execution pending |

## Ownership map

- Canonical data: existing UI message stream transformed into SSE.
- Persistence: `consumeSseStream` receives the canonical tee before wrapping.
- Transport: the client branch emits comments only.
- Backpressure: one source read pending; comments emit only with demand.
- Cancellation: clear timer, mark closed, request branch cancellation, ignore late read.
- Completion: preserve canonical `[DONE]`, close, retire timer.

## Historical precedent

### Server-Sent Events comments

The WHATWG event-stream algorithm treats lines beginning with `:` as comments rather than dispatched data. The SDK must additionally preserve persistence topology, backpressure, and cancellation.

### Existing persistence tee

The pinned response helpers already separate client delivery and persistence. Placing liveness after that split preserves canonical storage.

## Decision criteria

1. no byte change when disabled;
2. no synthetic persistence or replay data;
3. standards-compatible client behavior;
4. real first-byte and idle-liveness effect;
5. bounded buffering;
6. observable cancellation and timer cleanup;
7. propagation through every public helper;
8. deployment-specific interval wording.

## Alternatives and results

| Option | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- |
| Heartbeat UI/data chunks | persistence comparison | changes canonical application data | rejected |
| Wrap before persistence tee | `consumeSseStream` byte control | comments enter storage | rejected |
| Client-only SSE comments after tee | unit controls plus Node/proxy probe | liveness with byte preservation | selected |
| Docs-only/no heartbeat | controlled idle proxy | connection closes during silence | rejected |
| Runtime-specific first flush only | continued idle deadline | does not maintain portable liveness | rejected |
| Manual formatter guessing | repeated `ultracite check` | same tests rejected | rejected |
| Repository formatter | exact bounded formatter carrier | authoritative two-file result | selected |

## Independent criticism

- Agent helpers initially accepted the shared option type while dropping its value. Explicit forwarding and propagation tests were added.
- Client cancellation initially risked waiting for an independent persistence tee. The selected branch cancel is requested without controlling client settlement.
- Two manual formatting guesses failed. Repository `ultracite fix` became the source of truth.
- A reversing result would show a supported client treating comments as data, persistence bytes changing, retained timers/readers under soak, or an exact-head candidate failure.

## Covered edge cases

- immediate opening comment;
- periodic idle comment and reset after real data;
- normal completion and `[DONE]` preservation;
- cancellation with and without persistence tee;
- late pending read after cancellation;
- invalid intervals before lock/tee/callback;
- Fetch, Node, streamText, and agent propagation;
- demand-aware buffering;
- 100 repeated open/cancel cycles with one source cancel and zero timers per cycle.

## Deferred boundaries

| Boundary | Next record or stop |
| --- | --- |
| Explicit supported-client parser matrix | #150 delivery gate |
| Named production proxy/runtime | integration successor or bounded documented stop |
| Deployment interval guidance | candidate documentation |
| Provider health and operation timeout | separate lifecycle finding |

## Exact receipts

| Head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `7c8b95b...` | transport `30506032517`, job `90755875694` | real Node first byte and controlled proxy liveness passed | `integration-executed` |
| `bf3942cd...` | Verify Changesets `30580829628` | passed | `target-executed` |
| `bf3942cd...` | CI `30580829614` | every visible job passed except two test-format files | partial gate |
| formatter carrier `28c31fb...` | CI `30587646844`, changesets `30587646845` | carrier published successor | execution carrier |
| `b0bbcf29...` | CI `30591830160`, changesets `30591830161` | `action_required`, zero jobs | trigger/authority result only |
| `b4b57263...` | CI `30592239115`, changesets `30592239084` | queued at last refresh | `target-test-prepared` |

## Complete-diff boundary

The candidate contains 13 product, documentation, changeset, and test files. Temporary formatter machinery is absent at the current head. The newest change is one test file adding the repeated cancellation control.

## Selected direction and reopening trigger

Selected direction: optional client-only SSE comments after the canonical persistence tee, with repository-authoritative formatting and repeated cancellation proof.

Reopen for a supported client that treats comments as data, evidence of persistence contamination, an unbounded timer/read/cancel leak, or a first-party portable liveness primitive with less surface and the same ownership boundaries.

Non-delegable human decision: none.

## Exact transition

Settle CI `30592239115` and Verify Changesets `30592239084`; repair any exact candidate failure; then run explicit supported-client parsing, finish deployment guidance, classify representative runtime/proxy evidence, and obtain independent complete-diff review.
