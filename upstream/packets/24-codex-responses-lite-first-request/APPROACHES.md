# Approaches — unit 24 Responses Lite first request after prewarm

## In simple words

The selected direction ends the warmup response chain at the exact transition into the first generated Lite turn. It preserves prewarm, preserves later incremental reuse, and keeps the patch inside one client decision plus focused tests.

Broader answers—disabling prewarm, reconnecting every time, increasing worker stacks, or changing tool planning—either widen behavior or address separate evidence.

## Decision criteria

1. The first generated Lite request carries the complete current logical request without a warmup predecessor.
2. Later generated turns retain incremental reuse.
3. Failure of the first generated request retries the complete request.
4. The patch stays inside the owning client boundary and target-native tests.
5. Wire format and public APIs remain unchanged.

## Selected approach

### Terminate the warmup chain before first generation

- Design: when `!warmup && use_responses_lite && last_response_from_untraced_warmup`, clear `last_response_rx` and skip incremental request preparation.
- Owning boundary: `ModelClientSession::stream` immediately before request construction.
- Evidence: current three-file diff at `2c3f21d38056d2d77215cd9dce820a680d11cfe8`; historical run `30584165709` / job `91011486628`.
- Advantages: exact lifecycle predicate; one production hunk; existing full-request serialization; ordinary continuation unchanged; retry behavior directly testable.
- Costs and risks: one complete first generated request after prewarm; current-head focused renewal pending.
- Remaining controls: run all three exact tests and ordinary `codex-core` gates on the clean current head.

## Viable alternatives

### Compare the warmup prefix and generated request identity

- Design: build both forms and choose incremental only when a serialized equivalence rule proves it safe.
- Why it remains plausible: could generalize across future warmup forms.
- What it would improve: finer-grained reuse decisions if multiple warmup contracts emerge.
- What it would widen or complicate: request normalization, ordering, omitted/default fields, and future schema evolution.
- Exact discriminator: a supported Lite case where warmup chaining is valid for first generation and the selected lifecycle predicate retransmits materially expensive data.
- Reopening trigger: target maintainers define such a contract.

### Represent warmup and generated predecessors with distinct typed state

- Design: replace the boolean/session combination with an explicit response-chain state enum.
- Why it remains plausible: stronger state-machine readability.
- What it would improve: impossible-state prevention and future extension.
- What it would widen or complicate: larger refactor across WebSocket session transitions and tests.
- Exact discriminator: repeated bugs caused by ambiguous response provenance.
- Reopening trigger: adjacent response-chain work already requires that refactor.

## Executed losing approaches

### Treat a larger worker stack as the repair

- Exact branch, patch, or commit: historical execution carriers culminating in `teamleaderleo/codex#58@40a56eefce26ea647a65779faeb783d65a84a49a`.
- What ran: full-agent assertion under default and 16 MiB Tokio worker stacks.
- Result: default exit `101`; large-stack exit `0`.
- Why it lost: stack size changes the test harness/runtime condition and does not define first-request identity.
- Useful evidence retained: separates the full-agent runner abort from the two focused client controls.

### Preserve the broad early carrier

- Exact branch, patch, or commit: `teamleaderleo/codex#23@ccd4ce3...`.
- What ran: early paired source and large-stack workflows.
- Result: useful characterization, but 114 changed files and unrelated work.
- Why it lost: unsuitable source fence and stale base.
- Useful evidence retained: original reproduction and stack discriminator.

## Rejected easy answers

### Reuse the warmup response id

- Temptation: maximize incremental reuse from the first generated request.
- Why it is incomplete or unsafe: warmup uses `generate=false`; it has no generated-turn ownership and can leave current request identity implicit in a setup response chain.
- Negative control or source fact: the selected tests require no first-generation `previous_response_id`, complete prefix identity, later reuse of `resp-1`, and a full retry after failure.

### Disable Lite prewarm

- Temptation: remove the transition entirely.
- Why it is incomplete or unsafe: discards startup latency work and changes feature behavior beyond the defect.
- Negative control or source fact: the candidate preserves one handshake for warmup plus first generation in the success path.

### Reconnect before every generated request

- Temptation: guarantee full request independence.
- Why it is incomplete or unsafe: sacrifices ordinary incremental continuation and WebSocket reuse.
- Negative control or source fact: continuation test proves `previous_response_id = resp-1` after the first generated response.

### Fold in planner or deferred-tool changes

- Temptation: both areas concern Lite tool manifests.
- Why it is incomplete or unsafe: planner exposure owns which tools enter the catalogue; this unit owns response-chain identity after prewarm.
- Negative control or source fact: current source fence contains only `client.rs` and two WebSocket test files.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`teamleaderleo/codex#23`](https://github.com/teamleaderleo/codex/pull/23) | broad Lite diagnostic and source carrier | closed | historical characterization only |
| [`teamleaderleo/codex#58`](https://github.com/teamleaderleo/codex/pull/58) | execution-only carrier and workflow | open historical | exact receipt; exclude from source |
| [`teamleaderleo/codex#87`](https://github.com/teamleaderleo/codex/pull/87) | exact three-file source on `e6cfd...` | open historical | direct predecessor |
| [`teamleaderleo/codex#129`](https://github.com/teamleaderleo/codex/pull/129) | internal transplant onto current public base | merged | materialization only |
| [`teamleaderleo/codex#130`](https://github.com/teamleaderleo/codex/pull/130) | clean current-base source | open draft | canonical current carrier |
| Public issue/PR searches on `2026-08-01` | Responses Lite/prewarm/`previous_response_id` overlap | no equivalent result | no public duplicate found |

## Deferred adjacent work

- worker-stack root cause — separate runtime/test-harness investigation
- deferred tool loader and Code Mode exposure — separate planner unit
- production prevalence — needs telemetry or a user reproduction
- generalized response provenance state — future refactor if repeated defects justify it

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-30 | broad carrier `#23` plus early exact controls | isolate the client transport invariant | broad source mixed unrelated changes | source isolation fails |
| 2026-07-30 | source `e520da...`, carrier `40a56e...`, run `30584165709` | accept historical bounded behavior | 3/3 fence, 2/2 client controls, large-stack full-agent pass | exact test contradicts claim |
| 2026-08-01 | public base `670f694...`; clean head `2c3f21d...` | retain selected patch on current base with `REPAIR` disposition | three files unchanged across public drift; current focused execution pending | current source or contract changed |
