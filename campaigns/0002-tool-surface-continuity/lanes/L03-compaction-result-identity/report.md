# Compaction and tool-result identity

## In simple words

Codex records a tool call before execution and records its result after the tool future finishes. Compaction then replaces the active history with user messages plus a summary or encrypted compaction item. The replacement deliberately removes raw tool calls and results.

A complete call/result pair therefore crosses compaction only through the summary or compaction checkpoint. A missing result receives a prompt-only synthetic `aborted` output. Duplicate results remain duplicated. A reordered result stays reordered. A result delivered after compaction becomes an orphan and disappears from the next model prompt. Current source has no pre-compaction fail-closed gate for mutation calls with incomplete identity.

The practical rule is simple: **compaction is safe for mutation history only after every mutation call has one durable result and one durable completion receipt, or after an explicit reconciliation marks the outcome.**

## Assignment and source boundary

- Fieldwork issue: #38
- Campaign: #31
- Related scout: #23
- Campaign synthesis: #51
- Lane: `campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/`
- Target revision: [openai/codex `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`](https://redirect.github.com/openai/codex/commit/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc)
- Retrieval date: 2026-07-29
- Target-source interaction: read-only
- Mutation tests: synthetic `set_marker(value=green)` only

Evidence labels follow the campaign vocabulary: **Documented**, **Observed**, **Inferred**, **Unknown**, and **Negative result**.

## Bottom line

**Documented:** Local compaction sends normalized history to a summary request, waits for `response.completed`, and installs a replacement made from selected user messages plus the generated summary. Raw function calls and outputs are absent from that replacement.

**Documented:** Remote compaction v1 sends normalized history with the current step's model-visible tool specifications. Its installed history filter drops function calls, custom calls, shell calls, tool-search calls, and every corresponding output.

**Documented:** Remote compaction v2 also sends the current step's model-visible tool specifications. It requires `response.completed` and exactly one compaction output, then installs retained user messages plus that compaction output. Its tests explicitly discard a function call from installed history.

**Documented:** Prompt normalization inserts a deterministic synthetic `aborted` output for a missing function result, removes orphan outputs, preserves duplicate matching outputs, and preserves existing order.

**Observed in the synthetic fixture:** All three compaction implementations produce the same identity result for the five fault classes. Complete pairs lose raw identity at installation; missing, duplicated, reordered, and late results have no fail-closed checkpoint.

**Inferred:** A mutation can complete in its handler while result delivery remains ambiguous. Once compaction commits a replacement, a later result keyed only by the old `call_id` has no surviving call to attach to and becomes prompt-invisible.

## Code and test map

| Boundary | Source | Relevant behavior |
|---|---|---|
| Local compaction request | [`compact.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact.rs#L264-L335) | Clones history, calls `for_prompt`, builds a default tool-less compaction prompt, retries the stream, and requires completion. |
| Local replacement | [`compact.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact.rs#L338-L401) | Collects user messages and the final summary, then replaces active history. |
| Local history builder | [`compact.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact.rs#L613-L670) | Emits initial context, retained user messages, and a summary message; it has no call/result retention branch. |
| Remote v1 request | [`compact_remote_request.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_request.rs#L25-L99) | Normalizes cloned history, attaches `tool_router.model_visible_specs()`, and calls the remote compact endpoint. |
| Remote v1 installation | [`compact_remote.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote.rs#L170-L337) | Processes endpoint history and installs a replacement. |
| Remote history filter | [`compact_remote.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote.rs#L338-L381) | Drops all call and result variants from installed compacted history. |
| Remote output trimming | [`compact_remote.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote.rs#L383-L468) | Shrinks payloads before compaction while preserving call IDs and item IDs. |
| Remote v2 attempt | [`compact_remote_v2_attempt.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_v2_attempt.rs#L32-L137) | Normalizes history, appends a compaction trigger, attaches current tool specs, and emits raw provider completion after validation. |
| Remote v2 stream validation | [`compact_remote_v2.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_v2.rs#L332-L439) | Retries retryable stream errors, requires `response.completed`, and requires exactly one compaction output item. |
| Remote v2 replacement | [`compact_remote_v2.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_v2.rs#L203-L324) | Builds and persists the replacement history, then completes the compaction lifecycle item. |
| Remote v2 retention test | [`compact_remote_v2.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/compact_remote_v2.rs#L610-L646) | Demonstrates that a function call disappears from installed history. |
| Prompt normalization | [`context_manager/normalize.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/context_manager/normalize.rs#L22-L147) | Inserts synthetic missing outputs with stable IDs. |
| Orphan removal | [`context_manager/normalize.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/context_manager/normalize.rs#L149-L221) | Removes outputs whose matching call is absent. |
| Prompt projection | [`context_manager/history.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/context_manager/history.rs#L125-L209) | Raw history stays unchanged; `for_prompt` normalizes a cloned snapshot. Replacement increments history version. |
| Normalization tests | [`context_manager/history_tests.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/context_manager/history_tests.rs#L1550-L1732) | Covers synthetic aborted outputs, orphan removal, and stable synthetic IDs. |
| Tool-call persistence | [`stream_events_utils.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/stream_events_utils.rs#L289-L392) | Persists the call immediately, then queues handler execution. |
| Tool-result persistence | [`session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L2120-L2145) | Records each resolved tool future as a response item. |
| Provider completion and drain | [`session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L2506-L2541), [`session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L2690-L2732) | Emits raw provider completion, then drains tool futures and records results. |
| Tool cancellation outcome | [`tools/parallel.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/tools/parallel.rs#L76-L214) | Uses terminal-outcome state during cancellation and returns an aborted result when execution has no terminal outcome. |
| Durable replacement checkpoint | [`session/mod.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L3208-L3254) | Persists `CompactedItem.replacement_history`; no parallel call/result receipt is stored. |
| Resume and fork hydration | [`session/mod.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/mod.rs#L1299-L1480) | Reconstructs history from rollout for resume and fork. |
| Rollout compaction replay | [`session/rollout_reconstruction.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/rollout_reconstruction.rs#L114-L323) | Uses the newest surviving replacement history as the complete base. |
| Rollout suffix replay | [`session/rollout_reconstruction.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/rollout_reconstruction.rs#L319-L443) | Appends newer response items after that base; future prompt projection removes an orphan late result. |
| Mid-turn compaction continuation | [`session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L424-L464) | Reuses the same step context and client session for inline compaction, then continues the loop before draining pending user steer input. |
| Sampling retry | [`session/turn.rs`](https://redirect.github.com/openai/codex/blob/3725f02cf38d856bc82bb46dd68ab61bb96ec6fc/codex-rs/core/src/session/turn.rs#L1313-L1410) | Reuses the turn-scoped client session and rebuilds retry input from current normalized history. |

## Lifecycle trace

### 1. Normal tool turn

1. A sampling response emits a tool call.
2. Codex assigns an item ID when needed.
3. Codex persists the tool-call response item immediately.
4. Codex dispatches the handler through the request-scoped `ToolCallRuntime`.
5. The provider stream reaches `response.completed`; Codex emits `RawResponseCompleted` with the provider response ID and usage.
6. Codex drains in-flight tool futures.
7. Each resolved tool future becomes a result response item and is appended to history and rollout.
8. The next sampling request calls `for_prompt`, which repairs missing outputs and removes orphans in a cloned projection.

This ordering creates distinct receipts:

- provider response completed;
- tool handler reached a terminal outcome;
- result item constructed;
- result item persisted;
- result item delivered to the client;
- result item included in the next model prompt.

Current compaction metadata preserves the provider completion of the compaction request. It does not preserve this six-stage identity ledger for prior mutation calls.

### 2. Local compaction

1. Clone raw history.
2. Project it through prompt normalization.
3. Send a summary request with default tool settings.
4. Retry retryable stream failures.
5. Require provider completion.
6. Generate replacement history from user messages and the summary.
7. Persist the replacement as the new history base.

A missing result is visible to the summary model as `aborted`; the raw history still lacked that real result. The replacement then removes both the call and synthetic output.

### 3. Remote compaction v1

1. Clone raw history.
2. Truncate oversized outputs while preserving item and call IDs.
3. Project through prompt normalization.
4. Attach the current step's model-visible tool specifications.
5. Call the remote compact endpoint.
6. Filter endpoint output.
7. Remove every call/result variant from installed history.
8. Persist the replacement as the new history base.

### 4. Remote compaction v2

1. Clone, trim, and normalize history.
2. Append `CompactionTrigger`.
3. Attach current step tool specifications.
4. Stream the request with at most two transport retries.
5. Require `response.completed` and exactly one compaction item.
6. Retain user messages and append the compaction item.
7. Persist that replacement as the new history base.

### 5. Continuation after inline compaction

Inline compaction reuses the same turn-scoped client session and the same captured step context. After installation, the turn loop continues. A later sampling request captures a fresh step only when the loop no longer holds the previous one. This protects within-step advertisement/execution consistency, while result identity still depends on the replaced history checkpoint.

### 6. Resume and fork

Resume and fork replay rollout records. The newest surviving `CompactedItem.replacement_history` becomes a complete base; older response items cease to affect rebuilt history. Newer response items are appended from the rollout suffix.

A late result recorded after the compacted checkpoint can therefore reappear in raw reconstructed history. Since its call was removed by the checkpoint, the next `for_prompt` projection classifies the result as orphaned and removes it.

## Identity invariants at each boundary

| Boundary | Call item ID | `call_id` | Result item ID | Provider completion | Client delivery | Current invariant |
|---|---:|---:|---:|---:|---:|---|
| Model output item done | assigned | present | — | pending | call may stream | call is persisted before handler execution |
| Tool future terminal outcome | present in history | reused | constructed later | provider response may already be complete | pending | handler result exists in process memory |
| Result persistence | present | matched | assigned | recorded separately | raw item emitted | pair exists in raw history |
| Prompt projection | preserved | matched | preserved or synthetic | unavailable as pair metadata | unavailable | missing gets synthetic `aborted`; orphan removed |
| Compaction request | preserved in prompt | preserved | preserved/synthetic | compaction completion pending | request events | pair content reaches compactor |
| Compaction installation | removed | removed | removed | compaction completion established | compact lifecycle emitted | summary/compaction item becomes sole semantic carrier |
| Resume/fork | only if in replacement or suffix | only if in surviving items | only if in surviving items | old provider receipt absent from identity pair | reconstructed initial messages | replacement is authoritative base |

## Synthetic fault fixture

Files:

- `artifacts/compaction_identity_fixture.py`
- `artifacts/fixture-output.json`

The fixture models the source-established function-call normalization and the installed replacement forms for local, remote v1, and remote v2 compaction. It executes no external tool and changes no external state.

Benign operation:

```text
set_marker(value="green") -> marker=green
```

Fault classes:

1. complete pair;
2. missing result;
3. duplicated result;
4. result before call;
5. result delivered after compaction.

### Fixture result matrix

| Scenario | Prompt immediately before compaction | Installed history immediately after compaction | Resume/fork effect | Current mutation outcome |
|---|---|---|---|---|
| Complete | one call + one result | zero calls + zero results | checkpoint survives | completed outcome represented only by summary/compaction item |
| Missing | one call + synthetic `aborted` result | zero calls + zero results | synthetic repair is absent; checkpoint survives | ambiguous outcome becomes an aborted narrative candidate |
| Duplicated | one call + two results | zero calls + zero results | checkpoint survives | both results reach compactor; conflict resolution delegated to compaction model/endpoint |
| Reordered | result remains before call | zero calls + zero results | checkpoint survives | causal order stays ambiguous |
| Late | synthetic `aborted` reaches compactor | late raw result appears after checkpoint, then prompt normalization removes it | same on resume/fork | completed result becomes silently model-invisible |

Fixture assertions cover 15 cases: five fault classes across three compaction implementations.

## Immediate before-and-after comparison

### Before compaction

The model prompt can contain a fully paired call/result, a synthetic aborted result, duplicate outputs, or a reordered output. Normalization enforces existence and orphan removal. It does not enforce uniqueness, causal order, mutation safety, provider receipt linkage, or result-delivery state.

### After compaction

Raw call/result items disappear from active history. `CompactedItem.replacement_history` persists that reduced state and becomes authoritative for resume and fork. Any safety property depending on old call IDs must live in the summary, encrypted compaction item, or a separate durable receipt.

### First deterministic divergence

For missing and late outcomes, the first deterministic divergence occurs in `ContextManager::for_prompt`:

- missing result: a synthetic `aborted` output appears;
- late result after installation: the output disappears as an orphan.

Compaction then makes either projection durable by replacing the raw pair history.

## Tool-surface loss versus result-delivery loss

These are separate failure classes.

### Effective tool-surface loss

- Remote compaction v1 and v2 receive `tool_router.model_visible_specs()` from the captured step.
- Inline continuation reuses the step context and client session across compaction.
- Normal sampling builds its tool payload from the request-scoped router.
- Compacted history intentionally lacks tool declarations and historical call/result items.

**Negative result:** Result normalization does not directly remove current tool specifications from remote compaction requests. A reduced post-compaction tool payload belongs to step capture, hydration, planning, or transport reuse lanes.

### Completed-result delivery or transcript loss

- A tool's authoritative side effect can finish before its result is persisted or delivered.
- Missing output normalization records `aborted` only in the prompt projection.
- A late result after compaction has no surviving call and becomes orphaned.
- Client-visible raw response events, rollout persistence, and model-visible prompt history remain separate checkpoints.

Scout #23 demonstrates a parallel local-exec delivery gap where authoritative subprocess output can exceed the bounded client transcript. This lane's fault is identity-based: the result item itself can lose its model-visible parent after compaction.

## Retry, duplication, silent loss, and stop behavior

### Sampling transport retry

A retryable sampling error returns through the request loop after in-flight tool futures are drained. The retry rebuilds input from current normalized history and reuses the same client session. Historical calls in the prompt are not automatically dispatched again; dispatch happens only for a newly emitted model output item.

**Negative result:** The traced continuation path contains no direct replay loop that re-executes every historical call lacking a result.

### Duplicate mutation risk

A duplicated result for one call ID remains visible to the compactor. A semantically repeated mutation with a fresh call emitted by a retried provider response enters the normal dispatch path again. The traced runtime has terminal-outcome handling for one invocation, while this lane found no cross-request idempotency ledger keyed by logical mutation.

### Silent loss

A late result appended after replacement is persisted in the rollout suffix and then removed from the next prompt as an orphan. This is silent model-visible loss; raw persistence may still contain the item.

### Stop behavior

Remote v2 stops on a stream ending before `response.completed` and on zero or multiple compaction output items. Local and remote compaction stop on request errors according to their retry/fallback policy. None of the three implementations stops solely because a prior mutation call has missing, duplicated, reordered, or late result identity.

## Fail-closed requirements

A safe mutation boundary should enforce the following before compaction, continuation, resume, and fork.

1. **Raw-history census.** Inspect raw history before prompt normalization. Every mutation call must have one non-empty call item ID, one non-empty `call_id`, exactly one result item, and one non-empty result item ID.
2. **Causal order.** The durable result must follow the durable call, or a typed provider receipt must prove a valid reordered delivery.
3. **Completion ledger.** Persist handler terminal outcome, result construction, result persistence, provider response completion, and client delivery as separate fields.
4. **Compaction gate.** Block compaction when a mutation call is pending, missing, duplicated, reordered without proof, or paired with conflicting results.
5. **Pending preservation.** Preserve an explicit `pending_mutation` or `ambiguous_mutation` checkpoint instead of synthesizing `aborted` into the only semantic record.
6. **Late-result reconciliation.** Match late results against a retained identity ledger. Surface a typed `late_result_after_compaction` event and update the checkpoint.
7. **Retry policy.** Permit automatic retry only for operations declared read-only or idempotent under a stable idempotency key. Require read-after-write reconciliation for ambiguous mutations.
8. **Duplicate policy.** Reject multiple results for one call ID unless byte-identical duplicate delivery is proven and deduplicated with an audit receipt.
9. **Resume/fork validation.** Validate the compacted checkpoint and suffix before the first resumed sampling request.
10. **User-visible stop.** When reconciliation cannot establish the outcome, stop further mutation and state the ambiguous operation, call ID, and required recovery action.

## Repair proposals

### P0 — pre-compaction mutation identity validator

Add a validator over raw `ContextManager` history before every local, remote v1, remote v2, token-budget, manual, and automatic compaction path. Return a typed error with the affected call IDs. Run it before payload trimming and before prompt normalization.

Suggested regression cases:

- complete pair accepted;
- missing mutation result rejected;
- two results for one call rejected;
- result before call rejected unless backed by a receipt;
- empty call or item ID rejected;
- read-only incomplete call can follow an explicit separate policy.

### P0 — durable compacted operation receipts

Extend the compaction checkpoint with privacy-safe operation receipts:

```text
logical_operation_id
call_item_id
call_id
result_item_id
operation_class: read_only | idempotent_mutation | mutation
handler_state: pending | completed | failed | aborted | ambiguous
provider_response_id
provider_completed
result_persisted
client_delivered
result_digest
reconciled_at
```

The summary can remain semantic context; the receipt carries identity and audit state.

### P1 — late-result reconciliation

During `record_conversation_items` and rollout reconstruction, resolve an orphan result against compacted receipts before prompt normalization. Update the receipt or append a typed reconciliation item. Preserve conflicting late results for explicit review.

### P1 — duplicate and ordering validator in prompt projection

Add uniqueness and causal-order checks alongside `ensure_call_outputs_present` and `remove_orphan_outputs`. Keep synthetic aborted outputs for legacy/read-only recovery only after mutation classification.

### P1 — retry idempotency contract

Add operation-class metadata to tool specifications and require stable idempotency keys for automatic mutation retries. A transport retry may continue the model request; it must never imply permission to repeat an ambiguous mutation.

### P2 — client-delivery checkpoint

Record privacy-safe delivery acknowledgements separately from provider completion and rollout persistence. This permits diagnostics to say “provider completed; result persisted; client delivery absent” instead of collapsing these into one status.

## Controls and negative findings

- **Control:** Same benign call/result input is evaluated for local, remote v1, and remote v2 installation.
- **Control:** Complete pair, missing, duplicate, reordered, and late cases use the same call ID and benign payload.
- **Control:** The fixture compares raw history, normalized prompt, installed replacement, resumed/forked history, raw late suffix, and next prompt.
- **Control:** Provider compaction completion is fixed true so identity behavior remains the tested variable.
- **Negative result:** Output payload trimming preserves item IDs and call IDs.
- **Negative result:** Remote v2 rejects incomplete provider completion and multiple compaction items.
- **Negative result:** Stable synthetic output IDs prevent prompt-cache churn when the source call item has an ID.
- **Negative result:** Historical prompt calls are not automatically re-executed; execution follows newly emitted model calls.
- **Negative result:** Current request-scoped router reuse protects advertisement/execution consistency within one step.
- **Negative result:** The owned fork comparison returned no compaction/result-identity source changes among the reported changed files; this lane therefore evaluates the public source pin directly.

## Unknowns

- Private host/client acknowledgement semantics after `send_raw_response_items`.
- Provider-side deduplication for repeated semantic mutations with new call IDs.
- Contents and guarantees of encrypted compaction items beyond the public client contract.
- Private transport behavior when a tool handler reaches a terminal outcome during connection loss.
- Whether any external service retains an operation ledger unavailable in public Codex source.

## Reproduction

From the repository root:

```bash
python3 campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/artifacts/compaction_identity_fixture.py \
  --output campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/artifacts/fixture-output.json
python3 -m py_compile \
  campaigns/0002-tool-surface-continuity/lanes/L03-compaction-result-identity/artifacts/compaction_identity_fixture.py
```

Observed result:

```text
15 cases passed
fixture-output.json sha256: 6cd32ee368bc94cc4525b06f2c46ed588baf5daea179db6e29419b835c8e94df
```

The fixture output is deterministic for fixture version 1.

## Evidence quality

- Source tracing: **Documented** at the pinned revision.
- Synthetic fault matrix: **Observed** in the lane fixture.
- Mutation completion before result persistence: **Documented** ordering plus **Inferred** ambiguity window.
- Late orphan result becoming prompt-invisible: **Observed** in the source-faithful fixture and supported by documented normalization/reconstruction behavior.
- Real provider mutation duplication: **Unknown**; no live mutation test was performed.

## Handoff summary

The first identity divergence occurs before compaction installation, in prompt normalization: missing results become synthetic `aborted` outputs, while late post-compaction results become orphans. Compaction then persists a replacement with no raw call/result identity, and resume/fork treats that replacement as authoritative. Current source protects compaction provider completion and request-scoped tool routing; it lacks a mutation-aware identity gate and durable operation receipt.
