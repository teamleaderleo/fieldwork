# Deep dive — unit 24 Responses Lite first request after prewarm

## In simple words

Responses Lite places its compact tool catalogue in an `additional_tools` item at the front of the request input. Codex startup prewarm sends that prefix with `generate=false` so the WebSocket and server-side prefix are ready before the user turn.

The client records the warmup response as an untraced response. Generic incremental request preparation can then use its response id as `previous_response_id` for the first generated request. That is the wrong ownership boundary for Lite: the warmup was connection/prefix setup, while the first generated request needs the complete current logical request identity. The selected correction recognizes that transition, clears the warmup response receiver, and declines incremental construction for exactly that request.

## Governing invariant

> A Responses Lite prewarm may establish the connection and transmit the reusable prefix, but the first generated turn must carry the complete current logical request without a warmup `previous_response_id`; only a successfully generated response may become the predecessor of later incremental turns.

## Current behavior

Baseline at public revision `670f69416bf91c5dfd8b58669e78050b584ff053`:

- entrypoint: `ModelClientSession::stream`
- state owner: `ModelClientSession.websocket_session`, especially `last_response_rx` and `last_response_from_untraced_warmup`
- caller-visible result: a stream of response events
- side effects: opens/reuses a WebSocket, transmits request JSON, updates response-chain state
- cleanup owner: the WebSocket session and stream lifecycle
- persistence or publication boundary: request JSON crossing the provider WebSocket
- relevant ordering: prewarm response completes; first generated request is prepared; response id reuse is selected; retry can occur after stream failure

The baseline generic preparation path can derive an incremental first generated request from the untraced warmup response.

## Source map

| Area | Exact path and symbol | Responsibility | Relevant tests |
| --- | --- | --- | --- |
| request transition | [`client.rs` at `2c3f21d...`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/src/client.rs#L1609-L1631), `ModelClientSession::stream` | choose full or incremental WebSocket request and manage response-chain state | client and agent tests below |
| full-agent request identity | [`agent_websocket.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/agent_websocket.rs) | assert exact warmup prefix and complete first generated request through the agent harness | `websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm` |
| client continuation and retry | [`client_websockets.rs`](https://github.com/teamleaderleo/codex/blob/2c3f21d38056d2d77215cd9dce820a680d11cfe8/codex-rs/core/tests/suite/client_websockets.rs) | isolate response-chain reuse after success and reset after first-generation failure | `responses_lite_reuses_generated_response_after_full_first_turn`; `responses_lite_retries_full_first_turn_after_failed_generation` |

## Reproduction or characterization

### Setup

- exact historical source revision: `e520da008366cd720ef58fa0b489efc0a2867e97`
- exact historical base: `e6cfd40c3f444aadd6017c9eeab01db70f48961a`
- exact execution carrier: `40a56eefce26ea647a65779faeb783d65a84a49a`
- environment: GitHub Actions Linux runner, Rust workspace under `codex-rs`
- fixture: local WebSocket test server emitting warmup, generated, continuation, and failure events
- workflow: run `30584165709`, job `91011486628`

### Baseline result

Source inspection confirms the baseline has `last_response_from_untraced_warmup` state and generic incremental request preparation. The focused candidate tests are designed around observable outbound JSON: warmup contains `generate=false` and a nonempty Lite manifest; the first generated request must omit `previous_response_id` and preserve the complete warmup prefix plus user input.

### Candidate result

Historical exact execution recorded:

- `FIELDWORK_LITE_SOURCE_FENCE=3/3`
- `FIELDWORK_LITE_CLIENT_EXACT=2/2`
- `FIELDWORK_LITE_AGENT=default:101;large:0`

The two client tests passed under the ordinary runner configuration. The full-agent assertion passed at a 16 MiB Tokio worker stack; the default stack aborted with a stack overflow after entering the broader agent path.

## Failure model

1. Confirmed: startup prewarm sends a Lite prefix with `generate=false` and receives a response id.
2. Confirmed: the session marks that response as coming from an untraced warmup.
3. Confirmed from source: generic `prepare_websocket_request` may use available response-chain state for incremental request construction.
4. Inferred from the state transition and guarded candidate: the first generated Lite request can become chained to warmup state instead of sending the complete current request independently.
5. Confirmed by candidate tests: forcing a full first request produces the intended JSON, then later continuation uses the first generated response id; a failed first generation retries a complete request.

## Consequence and claim boundary

### Established

- The candidate changes one request-selection boundary in `ModelClientSession::stream`.
- The first non-warmup Lite request after untraced warmup clears `last_response_rx` and returns no incremental request.
- Subsequent successful generated responses remain eligible for ordinary incremental reuse.
- A failed first generated request leaves the retry independent from warmup state.
- The current source diff contains exactly one production file and two target-native test files.

### Inferred

- Sending the complete current request prevents stale or incomplete logical request identity from being represented only through a warmup response chain.
- The fix is provider-compatible because it uses the existing full-request path and does not change the wire schema.

### Unknown or unmeasured

- Production frequency and user-visible prevalence.
- Behavior through every proxy/provider deployment.
- Long-running WebSocket soak behavior.
- Current-head focused execution at `2c3f21d...`.

## Selected implementation

`ModelClientSession::stream` owns the transition because it has all required facts at request-selection time: `warmup`, `use_responses_lite`, and `last_response_from_untraced_warmup`.

For the first generated Lite request after untraced prewarm, it:

1. clears `last_response_rx`;
2. returns `(None, false)` instead of calling generic incremental preparation;
3. lets the existing full-request path serialize the current prompt and request settings.

The change leaves non-Lite requests, warmup requests, and ordinary post-generation continuation untouched. It adds no new public state and changes no provider schema.

## Compatibility analysis

- public API: unchanged
- source compatibility: internal implementation only
- binary or wire compatibility: existing full WebSocket request form; no schema change
- persistence or format compatibility: not applicable
- platform behavior: pure request-state logic; test runner stack behavior is separately classified
- performance and allocation: first generated Lite request retransmits the full current request once; later turns retain incremental behavior
- cancellation, retry, and recovery: failed first generation retries full; later failure behavior remains existing behavior
- generated output: not applicable
- migration or rollback: one-commit revert restores prior response-chain selection

## Adversarial and edge controls

- re-entry: continuation test proves later request reuses `resp-1`
- concurrency: session-local state; no new shared mutable state
- cancellation or interruption: direct cancellation control absent
- failure before ownership transfer: failed first-generation test returns an error and retries full
- failure after partial effect: retry opens a new connection and omits warmup predecessor
- cleanup failure: outside current claim
- same-key or same-resource collision: not applicable
- unrelated-resource isolation: changed-file fence excludes planner/tool-exposure work
- platform or runtime boundary: default-stack overflow versus 16 MiB pass is recorded as harness/runtime evidence

## Review risks

- **Risk: clearing `last_response_rx` discards useful server cache state.** The discard happens once, only at the Lite warmup-to-generation transition. Later continuation still uses the first generated response id.
- **Risk: the full request duplicates the warmup prefix.** That one-time duplication is intentional to establish complete request identity. Later turns remain incremental.
- **Risk: a broader equality check would be more precise.** The transition predicate directly expresses the lifecycle invariant and avoids comparing serialized request bodies.
- **Risk: the full-agent default-stack abort hides a product defect.** Both focused client controls pass under the ordinary runner; the same full-agent assertion passes with a larger worker stack. The packet keeps that limitation explicit and requires current-head renewal.

## Reversing evidence

Reopen the conclusion if:

- current Codex source defines warmup response ids as valid generated-turn predecessors for Lite;
- a current-head focused test shows the first generated request already carries complete identity through another mechanism;
- provider compatibility requires warmup chaining for the first generation;
- equivalent upstream work lands on public main;
- current-head execution shows the candidate breaks non-Lite or post-generation incremental requests.

## Adjacent work excluded

- deferred tool exposure and Code Mode catalogue planning
- planner priority or tool-registration changes
- broader Tokio worker-stack diagnosis
- WebSocket reconnect policy outside failed first-generation retry
- UI startup timing and prewarm scheduling
- provider deployment and proxy behavior beyond target-native fixtures
