# F83 rollout append acknowledgement: expose the durable-history result at the session boundary

Finding state: `delivery-gate-ready`

Workstream: `K/O/I — mutation persistence, synthesis, and exact-head review`  
Canonical Fieldwork issue: `#83`  
Parent convergence issue: `#239`  
Canonical implementation: `teamleaderleo/codex#84`  
Exact implementation head: `d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`  
Exact implementation base: `a01a2d91461a57809e944de7758477b92617ab01`  
Current read-only public source inspected: `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Authoritative execution carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`  
Authoritative workflow: `30583967538`  
Independent source review: `4823945751`  
Strongest evidence class: `target-executed`  
Current review disposition: `ACCEPT` the bounded prerequisite; `HOLD` direct-current-head delivery until the named restack gate  
Desk routing: `Delivery Desk #160 D2`  
Upstream contact authorized: `no`

## In simple words

Codex first adds conversation items to live memory and then asks the thread store to append them to durable rollout history. The session boundary previously discarded whether that append succeeded.

The selected three-file change returns the append result to the caller. Its tests distinguish three outcomes: the write succeeded, the write failed before durable history changed, or durable history changed and the acknowledgement was lost. The current return type is a boolean prerequisite. A later finding must turn the failed acknowledgement into typed `Absent` or `Ambiguous` state before retry, compaction, replay, or cleanup can rely on it.

The source diff and exact execution are complete. One bounded delivery gate remains: replay the byte-equivalent three-file source directly onto the current public Codex head, renew the exact tests, and receive fresh complete-diff review.

## Why we care

A model-visible result and a durable result record are separate facts. Codex can retain a result in live conversation memory while the durable append fails. It can also receive an append error after the write became authoritative.

Those cases require different later recovery:

- a confirmed pre-write failure may mean the item is absent from durable history;
- a commit-then-error outcome means durable presence is possible or already established;
- either error remains insufficient authority for automatic mutation retry;
- compaction and replay need conservative persistence state instead of assuming that a locally returned error means absence.

This finding establishes the acknowledgement boundary only. It leaves typed persistence certainty and every consumer of that certainty to later bounded work.

## Governing invariant

The session boundary must preserve the canonical result of the durable append attempt without treating live-memory insertion, raw-item publication, or an error return as equivalent proof of durable absence or presence.

## Change thesis

1. **Current behaviour** — `record_conversation_items` updates live history, attempts durable append, publishes raw items, and returns no append outcome.
2. **Consequence** — callers cannot distinguish acknowledged persistence from append failure, and a later layer can only infer persistence from weaker observations.
3. **Selected improvement** — return the durable append acknowledgement while preserving current live-history and raw-item order.
4. **Evidence** — four exact source controls and the complete `codex-thread-store` package passed before the clean source branch was published.
5. **Boundary** — boolean failure deliberately leaves pre-write absence and commit-then-error ambiguity unclassified for the next finding.

## Exact source fence

`teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2` changes exactly:

- `codex-rs/core/src/session/mod.rs`;
- `codex-rs/core/src/session/turn_tests.rs`;
- `codex-rs/thread-store/src/in_memory.rs`.

Production behaviour:

- `record_conversation_items` returns the result of the rollout append attempt;
- ephemeral sessions with no `LiveThread` return success because no durable store owns the session;
- an append error remains logged and now returns failure;
- existing live-history mutation and raw-item publication order remain intact.

Test-only support:

- one-shot pre-write append failure;
- one-shot commit-then-error acknowledgement loss;
- ordinary in-memory store behaviour remains unchanged when neither hook is armed.

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The session now exposes the durable append acknowledgement | `source-read` | complete three-file diff at `d8299b7f...` | return value is boolean |
| Pre-write failure leaves the tested durable history unchanged | `target-executed` | exact control `append_outcome_reports_prewrite_failure` in run `30583967538` | in-memory thread-store fixture |
| Commit-then-error can report failure after the item is durable | `target-executed` | exact control `append_outcome_reports_commit_then_error_as_failure` | does not classify all backend failure modes |
| Ephemeral sessions remain successful without a durable owner | `target-executed` | exact control `append_outcome_ephemeral_history_is_authoritative` | no persistent store involved |
| Ordinary acknowledged append remains successful | `target-executed` | exact control `append_outcome_reports_successful_live_append` | one exact target revision |
| Current public drift leaves the source fence unchanged | `source-read` | complete compare `a01a2d... → 413492...` | later relevant drift expires this conclusion |

## Exact execution

Carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`  
Workflow: `30583967538`

The carrier:

- applied the reviewed three-file append delta to the exact `a01a2d...` base;
- verified the exact source fence;
- formatted the source;
- resolved and ran four unique full test names with `--exact`;
- ran the complete `codex-thread-store` package;
- published the one-commit source branch only after success.

The retained marker is `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`.

## Current-source relation

The implementation is one commit directly above `a01a2d91461a57809e944de7758477b92617ab01`.

The complete public compare from that base through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa` changes account-plan, authentication, rate-limit, app-server schema, protocol permissions, sandbox, and TUI status files. It leaves all three implementation files unchanged.

The source conclusion therefore carries forward within its exact fence. Delivery still prefers a direct child of `413492...` so proposal text, ancestry, execution, and review all name one current base.

## Alternatives considered

### A — Return a bounded append acknowledgement now

Selected.

- establishes the missing session boundary with three production/test files;
- preserves current call ordering;
- lets later typed receipt work consume an explicit fact;
- keeps retry, replay, compaction, and remote-effect policy outside this prerequisite.

### B — Introduce the complete typed persistence and replay model in the same patch

Deferred.

- crosses session, receipt, rollout, compaction, resume, fork, rollback, and retry owners;
- widens the review and rollback surface before the prerequisite is current and accepted;
- receipt replay carrier `teamleaderleo/codex#78` still has independent evidence and bounded-scan repairs.

### C — Keep logging append failures and infer state later

Rejected.

- discards canonical acknowledgement at the owner boundary;
- forces later consumers to infer persistence from live memory, logs, or generic errors;
- cannot distinguish pre-write absence from commit-then-error ambiguity.

### D — Treat every append error as durable absence

Rejected.

The commit-then-error control demonstrates durable presence alongside a returned error.

## Selected direction and losing reasons

Selected direction: land the acknowledgement prerequisite as a direct-current-head source candidate, then build typed persistence certainty as a separate finding.

| Deferred or rejected direction | Losing reason | Reopening trigger |
| --- | --- | --- |
| Combined acknowledgement, receipt, replay, and compaction patch | mixed owners and rollback boundaries | independent findings converge after acceptance |
| Logging-only continuation | loses the canonical append fact | append API later supplies an equivalent typed result without this boundary |
| Error implies absence | contradicted by commit-then-error execution | target store contract proves atomic error-before-write semantics across all backends |
| Automatic retry after failure | effect and durable-result certainty remain incomplete | stable logical identity plus explicit retry authority and confirmed terminal evidence |

## Independent review

Review `4823945751` inspected the complete three-file diff at `d8299b7f...` against exact base `a01a2d...` and classified the bounded prerequisite `ACCEPT`.

The review also classified current drift through `413492...` as file-disjoint and semantically unchanged within the fence. It held promotion for one direct-current-head materialization or an explicit acceptance of the file-disjoint base relation.

This finding selects direct-current-head materialization because it gives the next reviewer one ancestry, one source head, one exact test receipt, and one proposal base.

## Edge cases covered

- session with no durable `LiveThread`;
- acknowledged append;
- deterministic failure before write;
- deterministic error after write;
- durable-history inspection after each failure mode;
- one-shot failure injection;
- complete current-public changed-file comparison.

## Edge cases outside this finding

- typed `Absent`, `Persisted`, or `Ambiguous` result state;
- duplicate and conflicting result reconciliation;
- receipt checkpoint format and bounded replay;
- resume, fork, rollback, and compaction consumers;
- retry authorization;
- remote tool-effect settlement;
- backend-specific transaction guarantees;
- process or terminal output persistence.

## Current transition

Finding state: `delivery-gate-ready`.

Exact next transition:

1. create a source-only branch directly from `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`;
2. apply the byte-equivalent three-file source diff with no workflow or carrier files;
3. renew the four unique exact controls and complete `codex-thread-store` package;
4. verify the exact three-file fence and direct parent;
5. obtain fresh independent complete-diff review;
6. transfer the receipt to the source PR and retire carriers `#80`, `#52`, and historical source `#51` after exact successor proof;
7. open the typed persistence-certainty successor only after this prerequisite is current and accepted.

Clearing condition: a direct-current-head source PR has exact target execution, clean three-file diff, independent acceptance, and no temporary workflow.

Non-delegable human decision: `none`.

## Reopening trigger

Reopen source comparison when public Codex changes one of the three source files, changes the `LiveThread` append contract, or supplies an equivalent typed append outcome that absorbs this candidate.

## References

- Fieldwork issues #83, #239, #254, #213, and #160.
- Owned Codex source PR `teamleaderleo/codex#84`.
- Owned Codex execution carrier `teamleaderleo/codex#80`.
- Historical source and carriers `teamleaderleo/codex#51` and `#52`.
- Independent review `4823945751`.
- Workflow `30583967538`.
- Current public source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
