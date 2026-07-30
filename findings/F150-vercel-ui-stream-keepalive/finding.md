# F150: Keep idle Vercel AI UI streams alive without polluting persisted protocol data

Finding state: `delivery-gate-ready`

Workstream: `C — SDK, networking, protocol, and observability lifecycle`  
Canonical Fieldwork issue: `#150`  
Canonical finding path: `findings/F150-vercel-ui-stream-keepalive/finding.md`  
Canonical implementation: `teamleaderleo/ai#4`  
Exact implementation carrier head: `28c31fb9eba05915222ef0b5ac5b9bc64b619c08`  
Exact behavior-executed head: `7c8b95b12e7a47e0f614ff949b645e546488eea7`  
Exact base revision: `2b872b0db3769decf69945830c66a897c1e37347`  
Strongest evidence class: `integration-executed` for first-byte and controlled proxy liveness  
Reviewed input generation: `teamleaderleo/ai#4 at 28c31fb9eba05915222ef0b5ac5b9bc64b619c08`  
Current review disposition: `EXECUTE`  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

A model or tool can remain healthy while producing no UI message for a long time. During that silence, an HTTP response may not have emitted its first body byte, and an intermediary may close the connection as idle.

The selected repair adds an optional `keepAliveMs`. When enabled, the client-facing Server-Sent Events branch sends an immediate comment and later comments after idle intervals. SSE clients ignore comments. Persistence and resumable storage continue receiving only the original canonical stream.

The transport mechanism has executed against a real Node response and a controlled idle-closing proxy. The repository formatter still owns the exact spelling of two helper tests. Carrier `28c31fb...` runs `ultracite fix`, verifies the bounded diff, removes itself, and publishes a formatting-only successor before the next repository gate.

## Why we care

A healthy operation can appear dead before the first user-visible chunk. Sending heartbeat data into the canonical persistence stream would trade one reliability defect for replay and protocol contamination. The useful repair must keep transport liveness separate from application data.

## What happens if we leave it alone

A silent response can leave status and headers buffered and can cross a proxy idle deadline. Frequency depends on runtime, proxy configuration, model latency, and tool latency. The evidence supports the mechanism and bounded consequence, not one universal interval.

## Governing project goals and invariant

Governing invariant: optional transport liveness bytes may affect only the client response branch and must not change canonical UI data, persisted SSE bytes, resumable replay, or behavior when the option is unset.

Required properties:

1. first body byte can be emitted before source data;
2. idle liveness can continue through silence;
3. comments remain ignorable under SSE semantics;
4. persistence receives no synthetic bytes;
5. source locking and side effects occur only after option validation;
6. buffering remains bounded by downstream demand and one pending source read;
7. timers and late reads cannot leak across close, error, or cancellation;
8. interval choice remains deployment-specific.

## Current finding

A client-branch SSE-comment wrapper after the persistence tee is the narrowest compatible design. It emits `: stream-open\n\n` immediately and `: keep-alive\n\n` after idle intervals. Real source data resets the interval. Client cancellation clears timers immediately and requests downstream cancellation without waiting for an independent persistence branch.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The pinned helper may emit no body until source data or close | source-read | response helper at `2b872b0d...`; #150 | Header behavior depends on HTTP adapter |
| Immediate comment flushes a real Node response | integration-executed | carrier #6, run `30506032517`, head `7c8b95b...` | Controlled Node runtime |
| Periodic comments preserve a connection past a controlled idle deadline | integration-executed | same run; 450 ms deadline, 1050 ms silence | Synthetic proxy, not every production proxy |
| Client-only placement preserves persistence bytes | target-executed | PR #4 unit tests and complete source review | Current exact-head complete-diff review remains |
| Repository behavior and tests are otherwise green at `bf3942cd...` | target-executed partial gate | CI `30580829614`: build, docs, types, code consistency, and visible tests passed | `Lint & Format` rejected two helper tests |
| Repository formatter, not manual line guessing, owns the final spelling | source-read and target-test-prepared | root `package.json`: `ultracite fix`; carrier `28c31fb...` | Successor head and fresh CI pending |

## System and ownership map

- Public entrypoints: response and pipe helpers for UI streams, `streamText`, and agent helpers.
- Canonical data owner: the original UI message stream transformed into canonical SSE.
- Persistence owner: `consumeSseStream` receives the canonical tee before keep-alive wrapping.
- Transport owner: the client branch emits SSE comments only.
- Backpressure: one source read may remain pending; comments emit only under client demand.
- Cancellation: clear timer, mark cancellation, request branch cancellation, ignore late source resolution.
- Completion: canonical `[DONE]` stays unchanged and timer state is retired.

## Historical precedent

### Server-Sent Events comments

- Source: WHATWG Server-Sent Events event-stream interpretation.
- Principle supported: lines beginning with `:` are comments and are ignored by event dispatch.
- Important difference: the SDK must also preserve tee ownership, persistence bytes, backpressure, and cancellation.

### Existing canonical persistence tee

- Source: Vercel AI response helpers at `2b872b0d...`.
- Principle supported: client delivery and persistence already have distinct branches.
- Important difference: the keep-alive wrapper must be placed after the split to preserve canonical storage.

## Decision criteria

1. no byte change when disabled;
2. no synthetic data in persistence or replay;
3. standards-compatible client behavior;
4. real first-byte and idle-liveness effect;
5. bounded buffering and one pending read;
6. cancellation and timer cleanup remain observable and testable;
7. option propagates through every public helper;
8. interval wording avoids a universal deployment promise.

## Alternatives and comparative results

| Option | Implementation or analysis | Distinguishing control | Result | Disposition |
| --- | --- | --- | --- | --- |
| A — emit heartbeat UI/data chunks | paper/source design | persistence and client protocol comparison | changes canonical application data | rejected |
| B — wrap before persistence tee | early candidate topology | `consumeSseStream` byte control | synthetic comments enter storage | rejected |
| C — client-only SSE comments after tee | PR #4 | persistence exclusion plus real Node/proxy probe | satisfies liveness and byte-preservation invariants | selected |
| D — docs-only/no heartbeat | baseline | 450 ms idle proxy during 1050 ms silence | connection closes without transport bytes | rejected |
| E — runtime-specific first-flush call only | paper design | continued silence past idle deadline | may open headers but does not maintain liveness portably | rejected |
| F — manually guess formatter output | commits through `bf3942cd...` | repository `ultracite check` | same two files still rejected | rejected |
| G — execute repository formatter | carrier `28c31fb...` | `ultracite fix`, whole check, exact path fence | authoritative bounded repair | selected |

## Independent criticism

- Review found agent helpers could accept the shared option type while silently dropping the value. Explicit propagation tests and forwarding were added.
- Review challenged cancellation that awaited a tee branch while persistence remained active. The selected client cancellation resolves independently and treats branch cancellation as eventual.
- Repository CI rejected two hand-formatted tests twice. The correction now delegates spelling to the project's own formatter rather than another manual edit.
- A reversing test would show a supported client treating comments as data, persistence bytes changing, timer/reader growth under repetition, or ordinary exact-head CI exposing a candidate-related failure.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Immediate opening comment | unit and real Node response | emitted before source chunk |
| Periodic idle comments | fake timers and controlled proxy | maintained connection through silence |
| Reset after real data | unit test | next heartbeat waits a full interval |
| Normal completion | unit and transport probe | `[DONE]` preserved; timer cleared |
| Client cancellation | unit tests | immediate client settlement; downstream cancel requested |
| Independent persistence tee | unit test | client does not wait for persistence branch |
| Pending read after cancel | unit test | late resolution ignored |
| Invalid interval | unit tests | rejected before lock, tee, or callback effects |
| Fetch, Node, streamText, agent propagation | helper tests | option reaches canonical response helper |
| Slow-client buffering | demand-aware source review | one pending read plus race-local data |
| Repository package/build/type/docs gates | CI `30580829614` | passed except formatting job |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning record or reopening trigger |
| --- | --- | --- |
| Repeated open/cancel soak | individual races do not measure retained timers/readers over repetition | #150 delivery gate |
| Explicit supported-client parser matrix | protocol precedent is broader than exact client implementations | #150 delivery gate |
| Named production proxy/runtime | controlled proxy proves mechanism | integration successor or bounded stop |
| Deployment interval guidance | needs wording tied to configured idle deadlines | candidate documentation |
| Provider health or operation timeout | different state owner | separate lifecycle finding |

## Exact execution and receipts

| Repository/head | Workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/ai@7c8b95b...` | transport `30506032517` / job `90755875694` | real Node first byte and controlled proxy liveness passed | integration-executed |
| same behavior head | CI `30501900893` | product/docs/types/tests passed; two formatting failures | target-executed partial gate |
| `teamleaderleo/ai@bf3942cd...` | Verify Changesets `30580829628` | passed | target-executed |
| same head | CI `30580829614` | every visible job passed except `Lint & Format`; same two files rejected | target-executed partial gate |
| carrier `28c31fb...` | repository formatter plus fresh PR runs `30587646844` / `30587646845` | queued or pending successor | target-test-prepared |

## Complete-diff and compatibility review

The product candidate spans 13 product/test files. Carrier `28c31fb...` adds one temporary workflow that must delete itself; the final source head should differ from `bf3942cd...` only in the two formatter-owned tests.

Compatibility surfaces reviewed: SSE parser semantics, persistence identity, Fetch and Node response helpers, streamText and agent forwarding, cancellation with an active persistence tee, timer cleanup, downstream demand, and disabled-option behavior.

## Selected direction, losing reasons, and reopening trigger

Selected direction: optional client-only SSE comments after the persistence tee, with repository-authoritative formatting for the two helper tests.

Losing reasons:

- heartbeat UI/data chunks alter application protocol;
- pre-tee wrapping contaminates persistence;
- docs-only leaves the transport failure unchanged;
- first-flush-only approaches do not maintain idle liveness;
- manual formatter guesses failed the exact project check.

Reopening trigger: a supported client that does not ignore SSE comments, evidence that comments enter persistence, an unbounded cancellation/timer leak, or a first-party portable liveness primitive that preserves the same boundaries with less surface.

Non-delegable human decision: none.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `D2`
- Exact next transition: let carrier `28c31fb...` publish the formatter-owned successor, run current-head CI and changeset verification, then execute leak/client/documentation controls.
- Clearing condition: ordinary exact-head repository gate passes and the remaining transport/client/documentation controls have receipts or a bounded documented stop.
- Required subgates: formatting successor, full CI, leak soak, supported-client parsing, deployment guidance, representative runtime/proxy evidence.
- Non-delegable decision: none.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-29 | initial candidate | selected client-only SSE comments with persistence exclusion |
| 2026-07-30 | run `30506032517` | first-byte and controlled proxy claims became integration-executed |
| 2026-07-30 | CI `30501900893` | repository failure isolated to two helper test formats |
| 2026-07-31 | CI `30580829614` | second manual formatting guess rejected; all other visible jobs passed |
| 2026-07-31 | carrier `28c31fb...` | repository formatter selected as authority for exact spelling |

## References

- Fieldwork #150
- `teamleaderleo/ai#4` and `#6`
- Vercel AI source at `2b872b0db3769decf69945830c66a897c1e37347`
- WHATWG Server-Sent Events specification
- GitHub Actions runs `30506032517`, `30501900875`, `30501900893`, `30580829628`, `30580829614`, `30587646844`, and `30587646845`
