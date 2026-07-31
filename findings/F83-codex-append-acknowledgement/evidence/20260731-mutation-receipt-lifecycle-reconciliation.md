# Codex mutation receipt lifecycle reconciliation — 2026-07-31

## In simple words

Codex can request a state-changing operation, observe a handler result, append that result to live conversation memory, attempt durable rollout persistence, compact the conversation, resume or fork later, and continue deferred work. Each boundary knows a different fact.

The campaign needs one durable receipt lineage that preserves those facts without turning a local error into a claim about the external side effect. The receipt must also prevent automatic redispatch whenever Codex cannot prove the earlier operation stayed harmless.

The immediate source work is narrower than the full lifecycle repair. The append-acknowledgement prerequisite is accepted. A current-public-pin source PR now carries the versioned receipt wire vocabulary. Replay, checkpoint authority, Code Mode delivery, compaction enforcement, resume, fork, rollback, ephemeral continuation, and retry remain separate implementation slices.

## Record purpose

This evidence record reconciles the campaign handoff, current Fieldwork records, current owned Codex branches, current read-only public Codex, and the next execution sequence.

It also records the architecture that later slices must preserve. That architecture separates:

1. logical operation identity;
2. selected runtime effect;
3. dispatch certainty;
4. external outcome certainty;
5. terminal observation;
6. durable result certainty;
7. lineage dispatch ownership;
8. receipt epoch and ordered updates.

The separation prevents one broad success or error value from silently answering questions owned by other lifecycle boundaries.

## Exact current identity

Retrieval date: `2026-07-31`.

### Read-only public Codex

- Current inspected public head: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`.
- Commit: `Refresh precomputed app-server protocol exports (#36239)`.
- Public Codex remains read-only.

The move from the campaign handoff pin `a01a2d91461a57809e944de7758477b92617ab01` to `4642370542739d5dd080b0c87a9de06a6435d3db` contains three commits. Their changed files cover account plans, authentication, permissions, sandbox policy, app-server protocol exports, and related tests. They leave the current two-file receipt wire fence untouched.

### Accepted append acknowledgement

- Canonical source: `teamleaderleo/codex#84`.
- Source head: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`.
- Exact base: `a01a2d91461a57809e944de7758477b92617ab01`.
- Execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`.
- Run: `30583967538`.
- Result: four exact controls and the complete `codex-thread-store` package passed.
- Independent review: `4823945751`.
- Disposition: accepted bounded prerequisite; direct-current-head packaging remains a separate delivery step.

### Current receipt wire source

- Source PR: `teamleaderleo/codex#95`.
- Exact public base: `4642370542739d5dd080b0c87a9de06a6435d3db`.
- Source head at opening: `15414d7e5da8109e03dca24111664b272e4a5717`.
- Source branch: `fieldwork/83-receipt-wire-v1-464237`.
- Source fence:
  - `codex-rs/protocol/src/lib.rs`;
  - `codex-rs/protocol/src/tool_operation.rs`.
- Current evidence class: `target-test-prepared`.

The source carries versioned protocol types for direct and Code Mode logical identity, operation effect, terminal state, durable-result state, epoch activation, ordered full-state updates, and bounded checkpoints.

### Current receipt wire execution carrier

- Carrier PR: `teamleaderleo/codex#96`.
- Carrier head at opening: `5873af57e20cfa70b471539520e7d8649257919c`.
- Carrier base: source head `15414d7e5da8109e03dca24111664b272e4a5717`.
- Carrier delta: one workflow file.
- Workflow run: `30598182882`.
- State at this record: queued.

The carrier requires:

- exact two-file source fence;
- exact one-file carrier fence;
- workspace formatting;
- unique resolution of five declared test names;
- five executions using full names and `--exact`;
- the complete `codex-protocol` package.

### Historical wire source and failed carrier

- Historical source PR: `teamleaderleo/codex#73@e205ffe911dcbd661b47c4107e7f26ae772f8182`.
- Historical base: `a01a2d91461a57809e944de7758477b92617ab01`.
- Independent source review found no source blocker.
- Historical carrier: `teamleaderleo/codex#74@ac562bc0cba7d9f81ecd97aac7191a8d09e8c52c`.
- Run: `30584078430`.
- Result: stopped during formatting before any test execution.
- Evidence class: carrier failure only; zero target-test evidence.

The failed carrier remains durable evidence. It supplies no reason to reject the protocol contract and no reason to describe the tests as executed.

## Reconciliation of campaign records

Several durable records describe different moments of the same campaign.

| Record | Recorded public pin | Recorded owned state | Current interpretation |
| --- | --- | --- | --- |
| `campaigns/0003-compaction-mutation-identity/question.md` | `3725f02...` | initial staged question | historical campaign definition |
| `campaigns/0003-compaction-mutation-identity/STATUS.md` | `3725f02...` | owned main through direct-result persistence | historical implementation checkpoint |
| operator handoff supplied in conversation | `a01a2d...` | broad lifecycle synthesis | current architecture input with an expired source pin |
| Fieldwork issue #83 | through `413492...` | append prerequisite accepted; typed receipt and replay active | current live routing record before this refresh |
| Fieldwork PR #292 | `464237...` | current Codex evidence synthesis | current parent authoring head |
| owned Codex PRs #95/#96 | `464237...` | source-only receipt wire plus exact execution carrier | current receipt wire transition |

The differences reflect source movement and staged work. A new worker should begin from this record, issue #83, Fieldwork PR #292, source PR #95, and carrier #96. Historical records remain evidence inputs.

## Established facts

### Observed in source or executed owned tests

1. Live conversation history can receive an item before durable rollout append reports its outcome.
2. A pre-write failure and a commit-then-error acknowledgement loss can both return failure while leaving different durable histories.
3. The session caller can receive append acknowledgement without replacing `LiveThread` or `ThreadStore` ownership.
4. Existing direct-result receipt work records `Persisted` only after authoritative append success and records `Ambiguous` after append failure.
5. The canonical live receipt owner belongs to session lifetime rather than one turn lifetime.
6. Direct and Code Mode operations require different logical identity forms.
7. Full-history forks and compaction snapshots can multiply persisted history, including large inline payloads, according to public Codex reports.
8. Ephemeral resume, unexpected fork lineage, pathless side conversations, and inherited active lifecycle markers have public reports demonstrating real recovery and observability pressure.

### Inferred architecture conclusions

1. Conversation history alone cannot answer whether an external side effect occurred.
2. One linear lifecycle enum loses important combinations.
3. A durable receipt checkpoint must carry enough state to reconstruct uncertainty after compaction.
4. Rollback can remove conversational causation while preserving terminal or ambiguous external-effect knowledge.
5. Forked children should inherit knowledge while dispatch ownership remains explicit.
6. Deferred continuation and mutation receipts need one lineage checkpoint.
7. Automatic retry must consume explicit identity, effect, outcome, and retry authority.

These conclusions remain `Inferred` until each owning source slice and test matrix executes.

## Logical operation identity

### Direct execution

```text
Direct(call_id)
```

The model-visible response call ID is the logical identity.

### Nested Code Mode execution

```text
CodeMode(cell_id, runtime_tool_call_id)
```

The cell and runtime tool call identify the logical operation inside the code execution surface.

### Synthetic host identity

A synthetic host call ID belongs to transport and orchestration. It can change during host restart, process reconstruction, resume, rebinding, or internal retry. Including it in logical identity would make one external operation appear new.

The current wire source encodes the direct and Code Mode forms and excludes the synthetic host ID from the Code Mode form.

## Receipt certainty dimensions

The historical compact receipt source uses effect, terminal state, and durable-result state. Later core work should preserve their independence and extend the internal owner where required.

### Effect

```text
read_only
potential_mutation
```

Effect should come from the exact selected runtime. Unsupported or late observations use the conservative potential-mutation classification.

### Dispatch certainty

```text
not_dispatched
dispatched
unknown
```

Examples:

- argument rejection before runtime selection can establish `not_dispatched`;
- entering the external request boundary establishes `dispatched`;
- process loss around dispatch can establish `unknown`.

### External outcome certainty

```text
succeeded
failed_before_effect
cancelled_before_effect
unknown
```

A local timeout, dropped wait, cancellation request, cancellation delivery, connection loss, or handler formatting error cannot establish that an external mutation stayed absent.

### Terminal observation

```text
pending
completed
failed
aborted
ambiguous
```

This field records what the selected runtime reported locally. It remains separate from external outcome certainty.

### Durable result certainty

A fuller persistence model should distinguish at least:

```text
absent
accepted
written
durable
ambiguous
```

The exact number of stages depends on the canonical writer contract. Queue acceptance, line write, flush, filesystem durability, thread-store transaction commit, and projection visibility represent different facts.

The current compact wire uses:

```text
pending
persisted
ambiguous
```

That form remains sufficient for the first protocol slice. The core owner and append API can later refine internal stages while preserving wire compatibility through a versioned transition.

### Lineage dispatch owner

```text
current_thread
parent_owned
inherited_terminal
inherited_ambiguous
```

A forked child can retain receipt knowledge without gaining permission to activate parent-owned work.

### Ordering

```text
receipt_epoch
update_sequence
```

Every durable update belongs to one epoch. Replay must reject updates before activation, gaps, regressions, and conflicting duplicates. Identical duplicate updates may be idempotent when the complete record agrees.

## Authoritative append outcomes

A useful writer contract should name the strongest completed stage instead of collapsing every outcome into one boolean.

Candidate result family:

```text
Accepted(sequence)
Written(sequence)
Flushed(sequence)
Rejected(reason)
TimedOut(last_known_sequence)
WriterClosed(last_durable_sequence)
Ambiguous(last_accepted_sequence, last_durable_sequence)
```

The accepted append prerequisite exposes success versus error to the session caller. It deliberately leaves this typed family to successor work.

A writer timeout should retire that writer generation, preserve the caller's last accepted sequence, preserve the store's last durable sequence, and force reconciliation during reconstruction. Continuing to trust an unhealthy writer can extend uncertainty across later items.

## Replay contract

Replay should operate as a validate-then-install transaction.

### Input selection

1. Find the newest supported receipt checkpoint within the effective rollout lineage.
2. Respect the active rollback boundary.
3. Read receipt updates after that checkpoint in ordinal order.
4. Bound record count, receipt count, and decoded byte size.

### Temporary validation state

Replay builds a temporary ledger and validates:

- supported version;
- activation before update;
- epoch agreement;
- monotonic sequence;
- identical duplicate sequence only;
- no conflicting duplicate sequence;
- no unexplained gap;
- bounded operation count;
- bounded checkpoint size;
- explicit `coverage_lost` propagation;
- valid rollback ownership;
- valid parent/child lineage ownership.

### Installation

The live session owner changes only after the complete selected segment validates. A partial replay failure must leave the previous live owner untouched or install one explicit invalid/coverage-lost state. Destructive drain-and-requeue approaches can lose evidence during failure and should be excluded.

### Unknown versions

Unknown versions remain visible and fail closed. Deserializing an unknown record into an empty ledger would authorize continuation from missing evidence.

### Capacity

The live owner can remain bounded. Reconciled entries may retire only after durable evidence proves their later reconstruction. Ambiguous or unresolved potential mutations cannot disappear through ordinary eviction.

When capacity is exhausted before safe retirement, set permanent `coverage_lost` for the epoch and block consequential continuation.

## Compaction contract

Compaction should use prepare, persist, validate, install.

### Pre-request gate

Before any local, remote v1, or remote v2 compaction request is constructed:

- validate raw call/result identity;
- reject unreconciled potential mutations;
- reject receipt coverage loss;
- reject unsupported receipt versions;
- reject conflicting, late, duplicate, or reordered observations that remain unresolved.

### Request interval

Summary generation can take long enough for operation state to change. The prepared compaction carries the expected history and receipt epoch.

### Pre-install gate

Immediately before `replace_compacted_history`:

- rerun the shared receipt preflight;
- confirm the expected prior history epoch;
- confirm the expected receipt epoch;
- confirm the compacted checkpoint covers every retained active or ambiguous operation;
- confirm the compacted rollout append reached the required persistence stage.

### Installation

Install replacement history only after the required acknowledgement. Then advance the history and receipt epochs together.

The shared preflight eventually belongs at six boundaries:

1. local request construction;
2. local replacement installation;
3. remote v1 request construction;
4. remote v1 replacement installation;
5. remote v2 request construction;
6. remote v2 replacement installation.

Compaction enforcement follows durable replay, checkpoint authority, nested result delivery, and safe retirement. Enabling it earlier can turn long healthy sessions into permanent coverage-loss failures.

## Resume contract

Every resume should emit one identity-resolution receipt containing privacy-safe fields:

```text
requested_selector
selector_value_digest
resolution_source
thread_was_running
resolved_thread_id
returned_thread_id
relationship
```

Relationship vocabulary:

```text
same_thread
materialized_thread
fork
copied_history
referenced_history
reconstructed_from_rollout
```

The test matrix should repeat each selector across:

- a running thread;
- an unloaded persisted thread;
- a clean process restart;
- post-compaction history;
- post-rollback history;
- a moved or unavailable rollout path;
- supplied history combined with an ID.

Returned identity and relationship should remain deterministic and recorded.

## Ephemeral continuation contract

Resume requires an explicit persistence policy before writer or thread materialization.

A decisive test:

1. create one durable thread;
2. resume it ephemerally;
3. execute several turns;
4. terminate the ephemeral process;
5. resume the durable thread normally;
6. verify ephemeral turns are absent;
7. verify ephemeral receipt state cannot silently contaminate durable state.

Consequential operations in a truly non-persistent child need either external idempotency or a parent-owned durable receipt publication before dispatch. A pathless child that can mutate and lose all receipt evidence creates a forensic blind spot.

## Fork contract

Fork modes have different persistence mechanics and one shared safety rule:

> The child inherits knowledge; dispatch ownership remains explicit.

At the fork boundary classify each operation:

```text
terminal_inherited
ambiguous_inherited
active_parent_owned
child_eligible
```

An operation already activated by the parent cannot become child-dispatchable merely because history was copied.

Copied-history forks also create scale and replay risks:

- repeated checkpoints;
- duplicated compaction snapshots;
- duplicated inline payloads;
- conflicting physical copies of one logical receipt segment;
- inherited lifecycle markers appearing current beneath the child identity.

Referenced ancestry avoids physical duplication while adding retention and reconstruction dependencies. Receipt epochs and branch ownership must remain explicit in either mode.

## Rollback contract

Rollback changes conversation history while external effects remain facts.

### Operation completed before the target

Retain terminal receipt knowledge. Conversation rollback cannot reverse an external effect.

### Operation after the target with certain pre-dispatch failure

The receipt may be removed or marked rolled back when proof establishes `not_dispatched`.

### Operation after the target with possible dispatch

Preserve an ambiguity tombstone after removing the triggering conversation segment.

A safe rollback transaction:

1. identify the target;
2. reconstruct history and receipts through the target;
3. scan the removed tail for consequential operations;
4. retain terminal external effects;
5. retain possible dispatch as ambiguity tombstones;
6. persist rollback marker and replacement receipt checkpoint;
7. require authoritative append outcome;
8. install replacement state.

## Deferred continuation contract

Goal continuation and mutation receipt state form one lineage.

A combined checkpoint should bind:

```text
checkpoint_version
thread_id
parent_thread_id
history_epoch
receipt_epoch
goal_revision
goal_deferred
goal_activation_turn
fork_boundary
rollback_boundary
active_operation_receipts
```

Otherwise a restart can restore a deferred goal while losing the receipt that says its mutation was already dispatched.

The decisive branch test should activate a potential mutation, fork mid-turn, defer the goal in one branch, interrupt before terminal receipt durability, restart, resume both branches, and trigger the next explicit turn. Continuation and dispatch must each happen at most once. Ambiguity should produce a reconciliation requirement.

## Retry authority

Receipt certainty and retry authority remain separate.

Automatic retry requires all of:

- stable logical identity;
- explicit read-only or provider-idempotent authority;
- confirmed terminal evidence compatible with replay;
- unchanged selected runtime authority;
- no ambiguous persistence range;
- no lineage ownership conflict;
- no receipt coverage loss.

Exactly-once external execution requires provider support such as an idempotency key, remote transaction, reconciliation read, or stable operation key. The local ledger can preserve at-most-once automatic dispatch under uncertainty. It cannot invent remote certainty.

## ChatGPT Web comparison boundary

Codex source supports implementation claims about the open repository and shared Codex runtime surfaces. ChatGPT Web private orchestration remains opaque.

A ChatGPT field trial can still observe the same lifecycle questions:

- capability visible;
- capability executable;
- mutation requested;
- external effect observed;
- result delivered;
- conversation retained the result after long continuation;
- fresh conversation or reconnect changed capability;
- ambiguous mutation reconciled through read-after-write.

Those observations can support a shared product invariant. They cannot establish literal code reuse, writer identity, compaction implementation, or receipt ownership inside the private host.

Fieldwork issue #46 remains the correct owned trial lane. It requires unique operation identities, benign reads, reversible writes, read-after-write reconciliation, redaction, and immediate pause after an ambiguous mutation.

## Required source sequence

### Stage 1 — receipt wire execution

Owner: Codex PRs #95/#96.

Gate:

- exact two-file source fence;
- formatting;
- five exact focused controls;
- full `codex-protocol` package;
- independent complete-diff review.

### Stage 2 — direct-current append acknowledgement

Carry the accepted three-file append prerequisite directly onto the current public pin, renew the four exact controls and complete thread-store package, receive independent review, and retire superseded carriers after receipt transfer.

### Stage 3 — replay owner

Implement schema-bound rollout records, bounded validate-then-install replay, rollback-aware reconstruction, unknown-version rejection, sequence validation, checkpoint authority, and coverage loss.

Controls must include:

- update before activation;
- identical duplicate sequence;
- conflicting duplicate sequence;
- regression;
- gap;
- unknown version;
- direct identity restore;
- Code Mode identity restore;
- checkpoint plus tail;
- capacity overflow;
- rollback removal;
- rollback ambiguity tombstone;
- parent-owned fork receipt;
- process restart.

### Stage 4 — nested Code Mode delivery

Add source-qualified nested result persistence. Direct and nested paths must never update each other's receipts.

### Stage 5 — safe retirement

Retire reconciled receipts only after durable reconstruction proof. Preserve unresolved and ambiguous potential mutations. Propagate permanent coverage loss when bounds fill before safe retirement.

### Stage 6 — compaction preflight

Install the shared gate at all six request and installation boundaries and bind replacement installation to expected history and receipt epochs.

### Stage 7 — lifecycle consumers

Apply the receipt lineage to resume identity, ephemeral policy, fork ownership, rollback, deferred continuation, fallback, and retry.

## Decisive lifecycle scenario

One end-to-end synthetic test should cross several boundaries:

1. activate a potentially mutating logical operation;
2. reach dispatched state;
3. commit a synthetic external effect;
4. lose result acknowledgement before durable receipt completion;
5. begin compaction;
6. fork during the compaction request;
7. roll back the initiating user turn in one branch;
8. restart the process;
9. resume both branches through different selectors;
10. activate deferred continuation;
11. prove zero automatic redispatch;
12. prove parent and child retain ambiguity with explicit ownership;
13. reconcile through a read operation;
14. mark the original operation terminal once;
15. permit later compaction;
16. restart and prove checkpoint replay yields the same ledger.

Smaller unit and integration controls should isolate each transition so a failure identifies its owner.

## Evidence classification

| Statement | Evidence class | Current support | Limit |
| --- | --- | --- | --- |
| Append acknowledgement can reach the session caller | `target-executed` | Codex #84/#80 and run `30583967538` | Boolean prerequisite only |
| Direct result receipt persistence waits for authoritative append success | `source-read` and owned focused execution from accepted foundation | owned receipt implementation through `1d9cc970...` | Historical owned main; current-source restack remains |
| Receipt wire contract is current-pin source | `source-read` | Codex #95 at `15414d7...` | Current carrier queued at record time |
| Five current-pin wire controls pass | `Unknown` | carrier #96 run `30598182882` queued | Update after conclusion |
| Replay must validate before live installation | `Inferred` | historical replay failure review and lifecycle analysis | Requires source and execution |
| Fork child inherits knowledge without dispatch ownership | `Inferred` | fork reports and lifecycle semantics | Requires implementation controls |
| ChatGPT and Codex share literal lifecycle code | `Unknown` | no private-host source | Observational comparison only |

## Immediate next actions

1. Classify carrier #96 at its exact head and transfer the receipt to source PR #95.
2. Obtain independent complete-diff review of #95 after executed evidence exists.
3. Record #95/#96 and the public `464237...` pin in issue #83 and the current F239 synthesis.
4. Build the replay owner directly against current source, using the validate-then-install and bounded failure rules in this record.
5. Keep nested Code Mode delivery separate from direct result persistence.
6. Enable compaction gates only after replay, checkpoint authority, and safe retirement execute.

## Stop and reopening rules

Stop promotion when any of these remain:

- zero-test or substring-only green;
- source-generation failure;
- unknown protocol version accepted silently;
- receipt gap or conflicting duplicate accepted;
- checkpoint omission treated as an empty healthy ledger;
- potential mutation evicted without durable reconstruction proof;
- parent-active operation becoming child-dispatchable;
- rollback removing possible-dispatch knowledge;
- ephemeral mutation with no durable parent or external idempotency receipt;
- compaction replacement installed before authoritative persistence;
- automatic retry from generic error or local timeout.

Reopen architecture selection when current source introduces an authoritative equivalent receipt ledger, changes rollout/checkpoint ownership, replaces copy/reference fork semantics, or supplies a provider-level idempotency contract that changes retry authority.

## Boundary

- Synthetic and reversible operations only.
- No credentials, live accounts, purchases, production resources, public messages, deployments, or consequential external writes.
- Public `openai/codex` remains read-only.
- Owned Codex branches and Fieldwork records may carry source, tests, execution machinery, and evidence.
- Public upstream contact remains unauthorized.
