# F294: Classify connector-call payload exposure and stalled-turn recovery

Finding state: `comparative-evaluation-active`

Workstream: `I/N — cross-repository audit and Codex process, cancellation, and recovery`  
Canonical Fieldwork issue: `#294`  
Canonical finding path: `findings/F294-connector-call-stall/finding.md`  
Canonical implementation: `none`  
Exact implementation head: `none`  
Exact base or source revision: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`; core paths inspected at `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, with the one-commit delta limited to precomputed protocol archives  
Strongest evidence class: `source-read` plus one `observed` user-interface incident  
Reviewed input generation: `issue #294 body generation created 2026-07-31T23:17:06Z`  
Current review disposition: `EXECUTE distinguishing fixtures`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

A private connector instruction appeared in the chat as half-finished JSON. The chat then stayed in `Thinking` and ended as `Stopped thinking` instead of returning a result or a clear error.

The evidence does not yet show one bug. It may be a presentation failure that exposed an internal event, a lifecycle failure that let a tool wait without a terminal receipt, or both. Public Codex source explains part of the lifecycle but does not contain the proprietary connector or the ChatGPT mobile renderer, so attribution remains open.

The next work is two separate controlled tests: prove incomplete tool-call data cannot become visible assistant text, and prove a tool future that never cooperates still reaches a bounded terminal turn state.

## Why we care

The observed presentation breaks an important interface boundary: internal tool arguments should not be shown as an assistant answer. Even a privacy-safe payload is confusing; a different call could contain sensitive or implementation-specific values.

The stalled recovery breaks a separate reliability boundary: a tool or client failure should end in a typed success, failure, timeout, cancellation, or outcome-unknown receipt. A turn that remains `Thinking` leaves the user unable to tell whether work is active, failed, cancelled, or still producing effects.

Frequency, backend duration, and broader exposure are unknown. This finding retains one incident and does not extrapolate prevalence.

## What happens if we leave it alone

Observed consequence:

- the user saw a truncated internal-looking connector payload;
- no normal tool result or assistant recovery appeared;
- the turn later ended as `Stopped thinking`.

Plausible but unproved consequences:

- other internal arguments could be exposed by the same presentation fallback;
- a non-settling runtime could hold a turn until manual cancellation or platform intervention;
- the backend and client could disagree about whether a turn is still active;
- retries after an ambiguous terminal state could duplicate a state-changing effect.

The last consequence belongs to the existing mutation-identity and timeout-outcome campaigns unless a fixture connects it to this incident.

## Current finding

One user-visible incident establishes a composed symptom, not a single owner.

Public Codex currently waits for a completed response item before constructing and dispatching a direct function call. It treats a stream that closes before `response.completed` as an error. It also awaits in-flight tool futures after response processing, with cancellation delegated into each runtime and no generic per-tool watchdog visible in that drain path.

The first two facts make public Codex's normal direct-function-call event path an unlikely sole explanation for raw partial arguments becoming assistant text. The final fact leaves a real terminal-settlement question for runtimes that ignore, lose, or fail to observe cancellation.

The working comparison therefore has two axes:

1. **presentation integrity** — incomplete or unknown tool events must never become assistant prose;
2. **terminal settlement** — every dispatched or partially dispatched call must produce a bounded terminal receipt for the turn, even when the runtime does not cooperate.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A truncated internal-looking JSON payload became visible in ChatGPT mobile. | observed | `evidence/20260731-observed-mobile-incident.md` | One incident; owner and frequency unknown. |
| The visible turn did not produce a normal result or typed error before `Stopped thinking`. | observed | Same evidence note | Backend events and elapsed time are unavailable. |
| Public Codex dispatches direct tool calls from completed `ResponseItem::FunctionCall` items. | source-read | `codex-rs/core/src/session/turn.rs`; `codex-rs/core/src/stream_events_utils.rs`; `codex-rs/core/src/tools/router.rs` at `413492cd...` | Proprietary ChatGPT host and connector layers are outside this repository. |
| A stream closing before `response.completed` becomes a Codex stream error. | source-read | `try_run_sampling_request` in `codex-rs/core/src/session/turn.rs` | Does not prove the mobile client displays that error correctly. |
| Direct function-call argument deltas are not emitted through the custom-tool argument-diff consumer in the inspected path. | source-read | `ResponseEvent::OutputItemAdded` and `ToolCallInputDelta` handling in `codex-rs/core/src/session/turn.rs` | Other host protocol events or client fallbacks remain unknown. |
| Codex awaits in-flight tool futures after stream processing. | source-read | `drain_in_flight` and post-loop drain in `codex-rs/core/src/session/turn.rs` | A runtime may implement its own timeout; no claim is made about the proprietary connector. |
| No close duplicate was found for the combined raw-payload-plus-stalled-turn sequence. | source-read/search | Fieldwork and read-only public issue searches on 2026-07-31 | Search terminology and inaccessible private trackers limit completeness. |
| Public Codex caused this incident. | unknown | none | Must not be asserted without a fixture or platform trace. |

## System and ownership map

### Entry and model event

A model response stream produces output-item and argument-delta events. In the inspected public Codex path, `try_run_sampling_request` owns stream consumption, active item state, completion handling, and the transition to tool execution.

### Tool construction and dispatch

`ToolRouter::build_tool_call` converts a completed response item into a `ToolCall`. Direct function-call arguments remain a string in `ToolPayload::Function`; concrete handlers parse or validate their own payloads. `handle_output_item_done` records the completed call and queues a tool future.

### Turn settlement

After stream completion or failure, Codex drains queued tool futures. Cancellation tokens are passed to tool runtime execution. The turn returns only after the drain completes, then emits remaining token/diff state or returns `TurnAborted` if cancelled.

### Presentation boundary

The observed surface is ChatGPT mobile, not the public Codex TUI or desktop renderer. The proprietary `api_tool.find_in_resource` name and its response-resource URI do not appear in public Codex source. Ownership may lie in model-output serialization, a ChatGPT host event adapter, connector orchestration, a shared app-server protocol layer, or mobile rendering.

### Recovery boundary

At minimum, four identities need separation:

- response stream item;
- tool call and call ID;
- runtime execution future;
- client-visible turn state.

A terminal state for one does not prove settlement of the others.

## Historical precedent

### Codex response-header wait can hang indefinitely

- Source: https://redirect.github.com/openai/codex/issues/31376
- Revision or date: read 2026-07-31
- Principle supported: every wait boundary needs its own effective timeout and retry/terminal policy; an idle timeout elsewhere may not cover a pre-stream wait.
- Important difference: that report concerns transport establishment and `CLOSE_WAIT`, not connector argument presentation or an in-flight tool future.

### Codex desktop can stay thinking while a subagent remains active

- Source: https://redirect.github.com/openai/codex/issues/23292
- Revision or date: read 2026-07-31
- Principle supported: the visible main-turn terminal state can remain coupled to another runtime's lifecycle.
- Important difference: the retained incident involved one connector read and a raw JSON presentation leak, not a known subagent.

### Goal workflow can remain in Thinking after steering

- Source: https://redirect.github.com/openai/codex/issues/35641
- Revision or date: read 2026-07-31
- Principle supported: client-visible progress and backend continuation can diverge after an event-ordering transition.
- Important difference: no Goal workflow or steering event is known here.

### Fieldwork timeout-outcome and mutation-identity campaigns

- Sources: Fieldwork #83, #134, #162, and #239
- Revision or date: current records on 2026-07-31
- Principle supported: caller deadline, cancellation request, cancellation delivery, transport state, runtime completion, remote effect, result persistence, and client display are distinct facts.
- Important difference: this finding begins with a read-only connector and a presentation leak. It should not inherit state-changing replay claims without evidence.

### Duplicate search without a close presentation match

Fieldwork was searched for `stalled turn`, `partial function call`, `tool arguments`, `response.completed`, and `raw JSON`. Public Codex issues were searched for visible/rendered tool-call JSON, hangs, and stuck `Thinking`. Adjacent lifecycle reports were found, but no close match combined an unterminated internal connector payload displayed as chat text with missing bounded recovery.

## Approaches considered

### Retained Option A: split presentation and settlement fixtures

Build one fixture that supplies incomplete or unknown tool-call events and asserts no assistant-text exposure, and a separate fixture with a non-resolving tool future that asserts bounded cancellation/timeout settlement.

This is retained because either half can fail independently. A combined end-to-end test would be useful later but would not identify the first broken owner.

Option A loses if current source and protocol tests prove both properties and the incident cannot be reproduced at any owned boundary.

### Retained Option B: inspect host protocol fallback before proposing public Codex source

Map raw response-item notifications, unknown event handling, and client presentation fallbacks. The proprietary connector absence from public source is evidence to avoid patching the wrong repository.

Option B loses if a public Codex fixture reproduces the exact raw argument presentation without any host-specific layer.

### Deferred Option C: add a generic per-tool watchdog immediately

A watchdog may be justified, but timeout duration, cancellation authority, state-changing effects, and outcome-unknown semantics are separate design questions. Adding one before reproducing a non-settling runtime could convert an observability defect into unsafe replay or premature abandonment.

This option belongs to a focused successor if the non-resolving tool fixture establishes an uncovered wait.

### Declined: classify the screenshot as sufficient proof of a public Codex bug

The visible tool name and response URI are proprietary to this environment, and the public direct-function-call path does not expose partial direct arguments through the inspected diff consumer. Attribution would exceed the evidence.

### Declined: treat `Stopped thinking` as an adequate terminal receipt

That label does not state whether a tool began, finished, failed, was cancelled, timed out, or could still have effects. It is presentation state, not an execution outcome.

### Deferred: public issue or pull request

No public upstream interaction is authorized. A public packet would also be premature until ownership is located and a privacy-safe deterministic reproducer exists.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Incomplete visible JSON | Observed screenshot sequence | Payload prefix was unterminated and visible. |
| Normal result/error absent | Observed screenshot sequence | No normal connector result or typed error appeared before stop. |
| Stream closes before completion | Public source read | Codex constructs an explicit stream error. |
| Direct function-call partial argument deltas | Public source read | Inspected direct path does not attach the custom-tool argument diff consumer. |
| Completed direct call construction | Public source read | Dispatch begins from completed response item and preserves arguments for handler parsing. |
| In-flight tool settlement | Public source read | Turn drains queued tool futures; no generic watchdog is visible in that function. |
| Current-source drift | Compare `413492cd...` to `46423705...` | One commit changes only precomputed app-server protocol archive files; inspected core source remains current. |
| Duplicate search | Fieldwork and public issue search | Adjacent hang reports found; no close combined match. |
| Privacy retention | Evidence note | Only a short non-secret payload prefix is retained; screenshot binary omitted. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| State-changing connector effects after timeout | Current call was read-only and execution is unproved | #83/#134/#162 unless a fixture connects this path. |
| Mobile renderer implementation | Not present in accessible public source | Reopen when an owned client source or event trace is available. |
| Proprietary connector runtime internals | Not present in public Codex | Reopen with connector logs, a controlled runtime, or repeated incident. |
| Network pre-stream hang | Existing public precedent is separate | #294 only if the fixture shows the same terminal-state presentation. |
| Subagent lifecycle | No subagent involved in observed intent | #239 lane N or a successor if reproduction requires one. |
| Frequency and affected versions | One incident and no platform build metadata | Another privacy-safe incident or telemetry summary. |
| Sensitive argument exposure | No sensitive data observed and unsafe to manufacture casually | Use synthetic secrets in an owned presentation fixture only. |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| ChatGPT mobile incident, 2026-07-31 ~07:06 +08:00 | User-observed conversation sequence | Mobile client; exact build unknown | Partial internal payload visible; turn later `Stopped thinking` | observed |
| `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa` | Read `session/turn.rs`, `stream_events_utils.rs`, `tools/router.rs`, and function-call error/runtime contracts | GitHub source | Located completed-item dispatch, stream-close error, argument-delta behavior, and in-flight drain | source-read |
| `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db` | Commit search and compare from `413492cd...` | GitHub source | Current head one commit ahead; only precomputed protocol archives changed | source-read |
| Fieldwork | Exact-term issue searches | GitHub tracker | No close duplicate; adjacent lifecycle campaigns retained | source-read |
| Public Codex tracker | Read-only issue searches | GitHub tracker | Adjacent #31376, #23292, and #35641; no close combined match | source-read |

No target-executed reproducer exists yet.

## Complete-diff and compatibility review

- Finding branch base: Fieldwork composed protocol head `c2946c71b7330b74d326deb7af18a5ae55afce99` from draft PR #283.
- Changed-file fence: this canonical finding and one privacy-safe evidence note only.
- Product source changed: none.
- Current public Codex source fence: `4642370542739d5dd080b0c87a9de06a6435d3db`.
- Compatibility surfaces examined: response stream completion, direct function-call construction, custom-tool argument diff presentation, tool-future drain, turn cancellation/error return.
- Compatibility surfaces not examined: proprietary ChatGPT host adapter, mobile renderer, connector runtime, platform telemetry.
- Temporary carrier status: none.
- Known routine work: build two discriminating fixtures and inspect protocol fallback handling.
- Reviewer eligibility: independent exact-head review required after fixtures or before stopping the finding.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE distinguishing fixtures`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: create a bounded owned Codex/app-server test carrier for incomplete-event presentation and non-settling-tool cancellation.
- Clearing condition: one exact-head fixture locates or excludes each owner independently and records a typed terminal-state expectation.
- Required subgates: no-dispatch control for incomplete calls; no-assistant-text control; cancellation/timeout terminal receipt; post-cancellation runtime-state check.
- Autonomous work remaining: source map test harnesses, run fixtures, classify first divergent boundary, and cross-review.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | Initial F294 materialization | Split one observed composed symptom into presentation-integrity and terminal-settlement hypotheses; held public Codex attribution pending execution. |
| 2026-07-31 | Safe-reference self-audit | Routed public Codex issue citations through `redirect.github.com`; technical conclusion unchanged. |

## References

- `findings/F294-connector-call-stall/evidence/20260731-observed-mobile-incident.md`
- Fieldwork #23, #83, #134, #162, #239, #254, and #294
- `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`
- `codex-rs/core/src/session/turn.rs`
- `codex-rs/core/src/stream_events_utils.rs`
- `codex-rs/core/src/tools/router.rs`
- `codex-rs/tools/src/function_call_error.rs`
- `codex-rs/tools/src/tool_executor.rs`
- https://redirect.github.com/openai/codex/issues/31376
- https://redirect.github.com/openai/codex/issues/23292
- https://redirect.github.com/openai/codex/issues/35641