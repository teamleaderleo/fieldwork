# F150: Keep idle Vercel AI UI streams alive without polluting persisted protocol data

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#150`  
Canonical finding path: `findings/F150-vercel-ui-stream-keepalive/finding.md`  
Canonical implementation: `teamleaderleo/ai#4`  
Exact implementation head: `bf3942cd1b615baa43fadcb27388a6911c0c5390`  
Exact base revision: `2b872b0db3769decf69945830c66a897c1e37347`  
Strongest evidence class: `integration-executed` on behavior-identical predecessor `7c8b95b12e7a47e0f614ff949b645e546488eea7`; current-head changeset gate passed and repository CI is queued  
Reviewed input generation: `teamleaderleo/ai#4 at bf3942cd1b615baa43fadcb27388a6911c0c5390`  
Current review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

A model or tool can work for a long time before producing the next UI message. During that silence, an HTTP response may have sent no body byte. Some servers delay flushing headers until the first body byte, and some proxies close an idle stream.

The candidate adds an optional `keepAliveMs` setting. When enabled, the client-facing Server-Sent Events stream immediately sends a comment and later sends another comment after each idle interval. SSE parsers ignore comments. The persistence branch continues to receive only the original canonical UI stream.

The product behavior and transport probe have executed. The current head contains only a formatting repair in two tests after the prior exact transport head. Current-head changeset verification passed; the full repository CI run remains queued.

## Why we care

A healthy generation can be cut off before any user-visible chunk arrives. The browser or client sees a dead connection even though the model or tool is still working. A synthetic byte sent to persistence would create a second problem by changing replay or resumable-stream data.

The useful implementation must therefore keep the network connection alive while preserving canonical protocol and persistence bytes.

## What happens if we leave it alone

A silent response can leave status and headers buffered and can cross a proxy idle deadline. The observed external report and controlled transport probe support this failure mode. Frequency depends on deployment runtime, proxy configuration, model latency, and tool latency; one universal interval cannot be inferred.

## Current finding

An opt-in SSE-comment wrapper on the client response branch can provide first-byte and idle liveness while leaving persistence, resumable storage, and UI protocol chunks unchanged.

The option must validate before locking or teeing the source, keep one source read pending, emit only under downstream demand, clear timers on every terminal path, and resolve client cancellation without waiting for an independent persistence tee.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The pinned helper can emit no response body until source data or close | source-read | `packages/ai/src/ui-message-stream/create-ui-message-stream-response.ts` at `2b872b0d...`; #150 | Runtime header-flush behavior still depends on the HTTP adapter |
| Immediate SSE comment flushes a real Node response before source data | integration-executed | carrier `teamleaderleo/ai#6`, run `30506032517`, candidate `7c8b95b...` | Controlled Node server, not every hosted runtime |
| Periodic comments preserve a controlled proxy connection past its idle limit | integration-executed | run `30506032517`, 450 ms proxy deadline, 1050 ms source silence | Synthetic proxy, not a named production proxy |
| Synthetic comments stay out of persistence | target-executed | candidate unit tests and complete source diff in `teamleaderleo/ai#4` | Requires complete-diff review at current head before landing |
| Current head repairs repository formatting only | source-reviewed | commits `1c807d26...` and `bf3942cd...`; two helper tests | Current-head full CI remains queued |

## System and ownership map

- Entry points:
  - `createUIMessageStreamResponse`;
  - `pipeUIMessageStreamToResponse`;
  - `streamText().toUIMessageStreamResponse()`;
  - `streamText().pipeUIMessageStreamToResponse()`;
  - `createAgentUIStreamResponse`;
  - `pipeAgentUIStreamToResponse`.
- Canonical data owner: the existing UI message stream transformed into canonical SSE.
- Persistence owner: `consumeSseStream` receives the canonical tee before the client-only keep-alive wrapper.
- Transport owner: the wrapper emits `: stream-open\n\n` and `: keep-alive\n\n` only to the client response branch.
- Backpressure: at most one source read stays pending; comments are emitted only when the client branch has demand.
- Cancellation: the timer is cleared immediately; source-branch cancellation is requested and may settle later when another tee branch remains active.
- Completion: canonical `[DONE]` remains unchanged and timers are cleared.

## Historical precedent

### Server-Sent Events comment lines

- Source: https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
- Principle supported: lines beginning with `:` are comments and are ignored by the event dispatch algorithm.
- Important difference: the standard defines parser behavior, while this finding must also preserve persistence bytes, cancellation, and backpressure in the SDK's tee topology.

### External Vercel AI idle-stream report

- Source: https://github.com/vercel/ai/issues/17805
- Principle supported: users can encounter silent UI streams that fail behind deployment transport boundaries.
- Important difference: one report does not define a universal heartbeat interval or prove every proxy has the same behavior.

## Approaches considered

### Retained approach: client-branch SSE comments

This uses protocol-defined ignorable bytes, opens the response immediately, refreshes liveness after idle intervals, and leaves persistence unchanged.

### Declined: inject heartbeat UI chunks

That would alter application protocol data, persistence, replay, and potentially client state.

### Declined: wrap before the persistence tee

Synthetic comments would enter `consumeSseStream` and resumable storage, violating canonical byte preservation.

### Declined: fixed global interval

Deployment idle limits vary. The API should expose an opt-in deployment-specific interval and avoid a universal guarantee.

### Deferred: provider timeout or abort policy

Provider execution deadlines and operation cancellation are different owners. A network heartbeat does not prove the model or tool remains healthy.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Immediate opening comment | unit and real Node response probe | emitted before source chunk |
| Periodic idle comments | fake-timer unit tests and controlled proxy | emitted after idle intervals |
| Reset after real data | unit test | next heartbeat waits a full interval |
| Normal completion | unit and transport probe | `[DONE]` preserved; timer cleared |
| Client cancellation | unit tests | client cancel resolves immediately; downstream cancel requested |
| Independent persistence tee | unit test | client cancellation does not wait for persistence branch |
| Pending read resolves after cancel | unit test | late result ignored |
| Invalid interval | unit tests | rejected before source lock, tee, or callback effects |
| Fetch, Node, streamText, and agent propagation | helper tests | option reaches response helper |
| Slow-client buffering | source review and demand control | bounded to one pending read and race-local data |
| Real first-byte flush | run `30506032517` | passed |
| Controlled proxy idle deadline | run `30506032517` | passed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Repeated open/cancel leak soak | Current tests cover individual races, not a long repetition count | #150 current-head execution carrier |
| Supported UI clients beyond protocol parser assumptions | Needs explicit client matrix | #150 acceptance gate |
| Named production proxy/runtime | Synthetic proxy proves mechanism only | #150 integration follow-up |
| Deployment interval guidance | Needs documentation wording tied to configurable proxy deadlines | #150 candidate docs change |
| No-byte-change option-off control across every helper | Source and unit evidence exist; full repository CI still pending | current-head CI `30580829614` |
| Provider health semantics | Heartbeat is transport liveness only | separate operation-lifecycle finding |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/ai@7c8b95b...` | transport carrier run `30506032517`, job `90755875694` | Ubuntu 24.04, Node `v22.23.1`, pnpm `10.33.4` | opening byte and controlled proxy idle liveness passed | integration-executed |
| `teamleaderleo/ai@7c8b95b...` | Verify Changesets `30501900875` | hosted runner | passed | target-executed |
| `teamleaderleo/ai@7c8b95b...` | CI `30501900893` | Node matrix | product, docs, TypeScript, and test jobs passed; formatting rejected two helper tests | target-executed partial gate |
| `teamleaderleo/ai@bf3942cd...` | Verify Changesets `30580829628` | hosted runner | passed | target-executed |
| `teamleaderleo/ai@bf3942cd...` | CI `30580829614` | hosted runner | queued | target-test-prepared |

## Complete-diff and compatibility review

- Changed-file fence: 13 files in `teamleaderleo/ai#4`.
- Current base relationship: pinned base `2b872b0d...`; branch is intentionally research-pinned and requires current-base review before land-ready status.
- Temporary carrier: transport PR `teamleaderleo/ai#6` was execution-only; canonical implementation remains PR #4.
- Compatibility surfaces examined:
  - SSE parser semantics;
  - persistence byte identity;
  - Fetch and Node response helpers;
  - streamText and agent forwarding;
  - cancellation with and without persistence tee;
  - timer cleanup;
  - downstream demand and bounded buffering.
- Known routine work:
  - current-head CI completion;
  - repetition leak control;
  - explicit supported-client control;
  - deployment interval guidance;
  - representative named proxy/runtime validation or a documented bounded stop.
- Reviewer eligibility: current implementation is coherent but remains D2 until the named gates clear.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `D2`
- Exact next transition: finish current-head CI, then run repeated cancellation and supported-client controls on the same exact head.
- Clearing condition: all current-head repository jobs pass and the remaining transport/client/documentation controls have exact receipts or a bounded documented stop.
- Required subgates: CI `30580829614`, leak soak, client comment parsing, deployment guidance, representative runtime/proxy evidence.
- User decision requested: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-29 | initial candidate | Selected client-only SSE comments with persistence exclusion |
| 2026-07-30 | run `30506032517` | Upgraded first-byte and controlled proxy claims to integration-executed |
| 2026-07-30 | CI `30501900893` | Isolated repository failure to formatting in two new helper tests |
| 2026-07-30 | `bf3942cd...` | Repaired exact formatter output without product behavior changes |

## References

- https://github.com/teamleaderleo/fieldwork/issues/150
- https://github.com/teamleaderleo/ai/pull/4
- https://github.com/teamleaderleo/ai/pull/6
- https://github.com/vercel/ai/issues/17805
- https://html.spec.whatwg.org/multipage/server-sent-events.html
- GitHub Actions runs `30506032517`, `30501900875`, `30501900893`, `30580829628`, and `30580829614`
