# F294: Classify connector-call payload exposure and stalled-turn recovery

Finding state: `target-characterized / comparative-evaluation-active`

Workstream: `I/N — cross-repository audit and Codex process, cancellation, and recovery`  
Canonical Fieldwork issue: `#294`  
Canonical finding path: `findings/F294-connector-call-stall/finding.md`  
Canonical implementation: `none`  
Exact implementation head: `none`  
Synthetic model source: `3a0cf7b1b6eb579277ed8749fd5dd6f0d514a709`  
Target-native Codex source: `teamleaderleo/codex#110@526bb798695e9103e6efbf0342ccf6adbbcdc23a` over `openai/codex@f0c30e528a54bdf0fa9a4d52ff74b34383434811`  
Strongest evidence class: `observed` incident + `model-executed` contract + `target-characterized` public-Codex liveness boundary  
Current review disposition: `COMPARE bounded liveness and uncertainty-preserving receipt designs`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

A private connector instruction appeared in chat as half-finished JSON. The turn then stayed in `Thinking` and ended as `Stopped thinking` instead of returning a result or a clear error.

The investigation now proves one real public-Codex lifecycle boundary: when a runtime opts into cancellation cleanup, observes cancellation, and then never finishes cleanup, the enclosing tool-call task can remain pending without a terminal receipt. A cooperative cleanup control still settles normally.

That result does not explain the separate mobile presentation leak. The proprietary connector and ChatGPT mobile renderer are outside public Codex, so the presentation owner remains unlocated.

## Why we care

The presentation symptom crosses an interface boundary: internal tool arguments should not become assistant prose. Even a privacy-safe payload is confusing; another call could contain sensitive or implementation-specific values.

The lifecycle result crosses a liveness boundary: one non-settling cleanup future can prevent the caller from receiving any typed final state. A user cannot tell whether work is active, failed, cancelled, or still producing effects.

A naive timeout can make the interface responsive while inventing certainty. Returning ordinary `cancelled` after abandoning cleanup would hide whether local cleanup finished or remote effects stopped. The durable result therefore needs both bounded settlement and explicit uncertainty.

## Current finding

The original observation contains two independent questions:

1. **presentation integrity** — incomplete or unknown tool events must never become assistant prose;
2. **terminal settlement** — a non-settling runtime must not hold the turn forever, and any early terminal receipt must preserve uncertainty about cleanup and remote effects.

The synthetic schema-v2 model executes both desired contracts. The public-Codex characterization proves the uncovered wait exists at one target-native boundary. Neither result attributes the mobile payload presentation to Codex.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| A truncated internal-looking JSON payload became visible in ChatGPT mobile. | observed | `evidence/20260731-observed-mobile-incident.md` | One incident; owner and frequency unknown. |
| The visible turn produced no normal result or typed error before `Stopped thinking`. | observed | Same evidence note | Backend events and elapsed time are unavailable. |
| The repaired event/settlement contract executes on Node 22 and 24. | model-executed | Fieldwork carrier #351, workflow `30626853243`, jobs `91144004050` and `91144003927`, exact `9/9` | Synthetic model only; no product-owner attribution. |
| Public Codex dispatches direct tool calls from completed response items rather than partial direct-call deltas. | source-read | `session/turn.rs`, `stream_events_utils.rs`, and `tools/router.rs` on the pinned public source | Proprietary host and mobile presentation layers remain outside the repository. |
| An opted-in cleanup future that never settles can keep the enclosing public-Codex tool-call task pending after cancellation. | target-characterized | `teamleaderleo/codex#110@526bb798...`; carrier #118; workflow `30632906276`; job `91163308818` | Bounded test observation; no production timeout policy selected. |
| Cooperative runtime cleanup still settles normally. | target-characterized | Same exact carrier and existing cooperative control | Does not prove every runtime cleans up correctly. |
| Public Codex caused the mobile payload presentation. | unknown | none | Must not be asserted without a host/client fixture or trace. |
| Cancellation request proves cleanup or remote-effect cancellation. | false as a general inference | synthetic model and target-native review | Runtime acknowledgement and remote-effect evidence remain separate facts. |

## Exact executed evidence

### Synthetic schema-v2 contract

Execution carrier #351 at `bb5e8a7ccaa51ae68181a2b8845d9ba1f63b96f4` passed:

- workflow `30626853243`;
- Fieldwork integrity `30626853359`;
- Node 22.23.1 job `91144004050`, exact `9/9`;
- Node 24.18.0 job `91144003927`, exact `9/9`.

Artifacts:

- Node 22 artifact `8792117981`, digest `sha256:db925d945281dbe8ed6dcebed9d357f6f2108156b1736fc047e0a8d74819d127`;
- Node 24 artifact `8792114882`, digest `sha256:0966d9ac21dac9e04ca1bba4f092ab8a46b50a981e75abc0dfe619d92c38ef28`.

The matrix proves:

- partial and unknown events stay quarantined;
- one completed call identity dispatches at most once;
- only explicit runtime acknowledgement produces `cancelled`;
- natural completion and independent failure after a cancellation request retain causality-neutral states;
- non-settlement becomes bounded `outcome_unknown`;
- late completion cannot rewrite an emitted terminal receipt;
- durable receipts omit arbitrary provider, secret-shaped, and failed-control text.

### Target-native public Codex characterization

Canonical source:

- public base: `f0c30e528a54bdf0fa9a4d52ff74b34383434811`;
- owned source PR: `teamleaderleo/codex#110`;
- exact source head: `526bb798695e9103e6efbf0342ccf6adbbcdc23a`;
- changed-file fence: `codex-rs/core/src/tools/mod.rs` and `codex-rs/core/src/tools/nonsettling_cancellation_tests.rs` only.

Execution:

- workflow-only carrier: `teamleaderleo/codex#118@0b2d5048fbb857e7e258cdfe64d83753e4e0bf33`;
- workflow `30632906276`;
- job `91163308818`;
- Rust 1.95.0 setup, repository formatting, exact source ancestry, and one-workflow-file fence passed;
- `cancellation_waiting_for_nonsettling_runtime_cleanup_has_no_terminal_receipt` passed;
- `tool_runtime_cancellation_cooperatively_cleans_up_before_returning_cancelled` passed.

Bounded conclusion:

```text
runtime opts into cancellation cleanup
→ runtime observes cancellation
→ cleanup future never settles
→ enclosing tool-call task has no terminal receipt during the bounded observation window
```

The cooperative control proves the test does not label every cancellation path as stuck.

## System and ownership map

### Response and presentation

The model response stream produces output-item and argument-delta events. Public Codex constructs direct function calls from completed response items and treats premature stream closure as an error. The proprietary connector name and mobile rendering path from the incident do not appear in public source.

Potential presentation owners remain:

- model-output serialization;
- a ChatGPT host event adapter;
- connector orchestration;
- shared app-server protocol handling;
- mobile rendering or fallback presentation.

### Tool execution and cleanup

`ToolCallRuntime` owns public-Codex tool dispatch. A runtime may declare that the caller should wait for runtime cancellation cleanup. That choice protects resources when cleanup cooperates, but creates an unbounded caller wait when cleanup never settles.

### Receipt authority

At least five facts need separate representation:

- cancellation requested;
- runtime acknowledged cancellation;
- local cleanup confirmed;
- runtime task settled;
- remote effect confirmed or unknown.

A single `cancelled` bit cannot truthfully stand for all five.

## Historical and technical precedent

### Existing cooperative cleanup behavior

Public Codex already tests a runtime that cooperatively cleans up before returning a cancelled result. The new characterization adds the missing opposite control rather than replacing the intended cooperative behavior.

### Synthetic causality repair

The first six-case model labelled any grace-window settlement after a cancellation request as `cancelled`. The schema-v2 repair split explicit acknowledgement, later natural completion, later independent failure, and non-settlement. This is the receipt vocabulary needed for reviewing a bounded-liveness candidate.

### Adjacent public reports

- response-header wait can hang indefinitely: https://redirect.github.com/openai/codex/issues/31376
- desktop can stay thinking while another runtime remains active: https://redirect.github.com/openai/codex/issues/23292
- Goal workflow can remain in Thinking after steering: https://redirect.github.com/openai/codex/issues/35641

These reports support the general liveness concern but do not match the exact connector-presentation incident.

## Design directions under review

### Option A — keep the unbounded wait

Advantage: never returns before opted-in cleanup finishes.

Failure: one broken or lost cleanup future can hold the user-visible turn forever. The target-native characterization proves this failure shape exists.

### Option B — generic watchdog, then return ordinary cancellation

Advantage: bounded caller latency and small control-flow change.

Failure: `cancelled` would overstate certainty. Cleanup may remain unfinished and remote effects may continue. This option loses unless the runtime explicitly acknowledges cancellation and the host can prove the required cleanup boundary.

### Option C — bounded wait, then detach and emit `outcome_unknown`

Advantage: the caller receives a terminal receipt without inventing cancellation certainty. Late cleanup can continue under separate ownership.

Required work:

- define who owns the detached task;
- prevent task/resource leaks;
- make late completion observable without rewriting the already emitted receipt;
- preserve mutation and retry safety;
- define shutdown behavior.

This is the leading generic direction.

### Option D — runtime-specific cancellation deadline

Advantage: runtimes with known cleanup contracts can choose appropriate bounds.

Failure: inconsistent defaults can reintroduce indefinite waits, and the caller still needs one generic terminal vocabulary. Runtime-specific policy is useful as an override on top of a safe host default, not as the only protection.

### Option E — abort or drop the dispatch task at the deadline

Advantage: simple ownership termination.

Failure: dropping a Rust future does not prove external cleanup or remote cancellation. Some resources may rely on cooperative teardown. The receipt still needs `cleanup_unconfirmed` or `outcome_unknown`.

### Option F — process-specific escalation

For subprocess runtimes, a staged signal/kill policy may provide stronger local cleanup evidence. It does not generalize to network connectors, in-process libraries, or remote services.

## Required next discriminators

1. deadline-edge race: cleanup settles immediately before and immediately after the bound;
2. task-drop behavior: verify which local resources are released when the dispatch future is dropped;
3. repeated cancellation: first request, duplicate request, and already-terminal behavior;
4. parallel calls: one non-settling runtime must not block unrelated completed calls from receiving receipts;
5. runtime opt-out: runtimes that do not request cleanup waiting retain current cancellation behavior;
6. late completion: detached cleanup settles after `outcome_unknown` without rewriting the first receipt;
7. mutation safety: unknown remote effect blocks automatic retry unless durable identity/reconciliation proves safety;
8. host shutdown: detached cleanup has an explicit join, abandonment, or escalation policy;
9. presentation independence: no lifecycle candidate may claim to fix the mobile raw-payload exposure without a host/client fixture.

## Edge and compatibility ledger

| Boundary | Current state |
| --- | --- |
| incomplete/unknown event quarantine | proved in synthetic model |
| once-only dispatch | proved in synthetic model |
| explicit cancellation acknowledgement | proved in synthetic model |
| bounded `outcome_unknown` vocabulary | proved in synthetic model |
| public-Codex non-settling wait | target-characterized |
| cooperative cleanup | target-characterized control |
| proprietary connector behavior | unknown |
| mobile rendering owner | unknown |
| deadline duration | design judgment, unselected |
| task-drop cleanup | unproved |
| detached task ownership | unproved |
| remote-effect settlement | unproved |
| automatic retry safety | out of scope without mutation receipts |
| parallel-call isolation | unproved |
| host shutdown semantics | unproved |

## Current disposition and desk routing

- Finding state: `target-characterized / comparative-evaluation-active`.
- Review disposition: `COMPARE bounded-liveness designs; no production patch yet`.
- Review Queue entry: none.
- Delivery lane: `not-entered`.
- Exact next transition: add the nine discriminators above to a source-level design carrier, beginning with deadline-edge, task-drop, parallel-call, and late-completion controls.
- Clearing condition: one candidate returns a bounded uncertainty-preserving receipt, contains or owns remaining cleanup, and preserves cooperative-runtime behavior.
- Presentation clearing condition: a separate host-visible fixture locates or excludes the event-to-assistant-text owner.
- Non-delegable human decision: choose the generic receipt and detached-cleanup ownership contract after the discriminator matrix executes.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | Initial F294 materialization | Split one observed composed symptom into presentation-integrity and terminal-settlement hypotheses; held public Codex attribution pending execution. |
| 2026-07-31 | Schema-v2 execution | Executed nine synthetic controls and replaced causally overbroad cancellation labels with acknowledgement-aware receipt states. |
| 2026-07-31 | Public-Codex target characterization | Proved an opted-in non-settling cleanup future can hold the enclosing tool-call task without a terminal receipt while cooperative cleanup still settles. |

## References

- `findings/F294-connector-call-stall/evidence/20260731-observed-mobile-incident.md`
- `findings/F294-connector-call-stall/evidence/20260731-boundary-model.md`
- `findings/F294-connector-call-stall/evidence/run_boundary_matrix.mjs`
- Fieldwork #23, #83, #134, #162, #239, #254, and #294
- `teamleaderleo/codex#110@526bb798695e9103e6efbf0342ccf6adbbcdc23a`
- `openai/codex@f0c30e528a54bdf0fa9a4d52ff74b34383434811`
- `codex-rs/core/src/tools/parallel.rs`
- `codex-rs/core/src/tools/nonsettling_cancellation_tests.rs`
- https://redirect.github.com/openai/codex/issues/31376
- https://redirect.github.com/openai/codex/issues/23292
- https://redirect.github.com/openai/codex/issues/35641
