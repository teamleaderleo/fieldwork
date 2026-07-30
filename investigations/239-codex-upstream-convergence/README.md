# Codex upstream convergence workspace

State: `active — evidence collection and canonicalization`

Parent issue: [Fieldwork #239](https://github.com/teamleaderleo/fieldwork/issues/239)  
Programme: [agent and CLI execution, #14](https://github.com/teamleaderleo/fieldwork/issues/14)  
Target hub: [Codex, #8](https://github.com/teamleaderleo/fieldwork/issues/8)  
General autonomous initiative: [#254](https://github.com/teamleaderleo/fieldwork/issues/254)  
Current read-only upstream pin: [`openai/codex@a01a2d91461a57809e944de7758477b92617ab01`](https://github.com/openai/codex/commit/a01a2d91461a57809e944de7758477b92617ab01)  
Upstream contact authorized: `false`

## In simple words

Codex lets a model discover tools, call them, receive results, keep a conversation, reconnect services, run subprocesses, and resume later. Those actions cross several components. A tool can be advertised by one snapshot, executed by another runtime, reported to the model, stored to history, and replayed after restart.

Fieldwork found several places where those facts can drift apart. Examples include a stale MCP refresh publishing after a newer one, a timeout describing the caller's deadline while a remote mutation may still finish, a tool result entering live conversation memory while durable append fails, or terminal bytes reaching a producer while a later subscriber misses them.

Issue #239 gathers those related investigations and asks one practical question: **which findings still survive current Codex, which were absorbed upstream, which conflict with new code, and which deserve separate proposal-ready outputs?**

The current answer is a set of bounded surviving invariants, each with its own source owner and evidence requirements. One giant patch would mix authority, persistence, execution, and transport semantics that require separate review.

## Why we care

Codex coordinates actions with side effects. The user and model need accurate answers to questions such as:

- Which tool definition authorized this call?
- Did the call reach the remote service?
- Did the remote effect finish, cancel, or remain unknown?
- Did Codex durably record the result it showed the model?
- Can resume, fork, compaction, or replay reconstruct the same logical history?
- Did a subprocess finish with all retained output?
- Can an older refresh replace a newer catalogue or runtime?

An incorrect answer can lead to duplicate retries, missing context, stale capability use, misleading success or timeout records, lost output, or recovery from the wrong source state. Each consequence requires its own evidence; this workspace keeps the facts separate while explaining how they meet.

## What we are doing here

The convergence pass has six jobs:

1. pin current public source and classify upstream drift;
2. map each Fieldwork candidate to the exact current ownership seam;
3. search current and historical prior art;
4. classify each candidate as absorbed, portable, mechanically conflicting, semantically conflicting, complementary, or obsolete;
5. execute surviving bounded candidates on exact source heads;
6. turn accepted findings into one or more canonical outputs with explicit alternatives and limits.

## Investigation map

| Area | Core question | Durable file | Main owned records |
| --- | --- | --- | --- |
| Whole-system model | How do discovery, authority, execution, persistence, history, and recovery relate? | [`findings/problem-map.md`](findings/problem-map.md) | #239, #83, #84, #85, #134 |
| Upstream drift and overlap | What changed after each inspected pin, and which source candidates still survive? | [`findings/upstream-drift-and-overlap.md`](findings/upstream-drift-and-overlap.md) | Codex #45, #46, #48, #49, #51–#53 |
| Prior art | Which upstream and Fieldwork changes already own parts of these problems? | [`precedent/fieldwork-and-upstream-prior-art.md`](precedent/fieldwork-and-upstream-prior-art.md) | campaign reports and current source history |
| Alternatives | Which packaging and implementation approaches were considered? | [`alternatives/approach-selection.md`](alternatives/approach-selection.md) | #239 decision surface |
| Canonical outputs | Which explanations or proposal packets currently represent the work? | [`canonical/README.md`](canonical/README.md) | coordinator decision |
| Current continuation | What exact heads, runs, blockers, and next actions remain? | [`handoff.md`](handoff.md) | #239 abandonment-safe handoff |

## Current upstream state

The previous convergence pin was `97576b1794872e342450ebd577123e052ab57626`.

The current read-only head is `a01a2d91461a57809e944de7758477b92617ab01`, three commits later:

1. `e6cfd40c3f444aadd6017c9eeab01db70f48961a` exposes connector candidates during external-agent detection;
2. `745603a5a1eb48b6f343633d622eeb72dd549d7b` ignores passthrough metadata when reconciling rollout items;
3. `a01a2d91461a57809e944de7758477b92617ab01` preserves executor paths in read-command actions and updates their app-server protocol representation.

The first commit enters capability-discovery context. The second enters rollout reconciliation and must be included in persistence/history review. The third adds adjacent execution-provenance context. Their combined delta leaves the active deferred-loader, MCP runtime, append-outcome, and terminal source fences unchanged. See [`evidence/upstream-snapshot-2026-07-31.md`](evidence/upstream-snapshot-2026-07-31.md).

## Current candidate picture

### Deferred discovery and Responses Lite

Owned source: `teamleaderleo/codex#45`.

The source idea retains semantic residue: deferred tool metadata still needs an executable authority boundary. Current Code Mode now runs through a standalone host, so the old source placement requires a fresh design and source application. Upstream's logical websocket trace repair addresses replay recording after prewarm; it leaves first-generated Responses Lite capability-manifest transmission as a separate question.

### MCP reconnect and publication

Owned sources: `teamleaderleo/codex#46` and `teamleaderleo/codex#48`.

Current upstream lifecycle refactors do not establish the Fieldwork invariants that explicit host refresh requests fresh connections and only the newest eligible generation publishes its own accepted catalogue. These candidates remain complementary in meaning. Their historical source heads need a current-source review before proposal status.

### Append acknowledgement and result persistence

Owned source prerequisite: `teamleaderleo/codex#51`.  
Execution carrier: `teamleaderleo/codex#52`.

Current `Session::persist_rollout_items` logs append errors and returns no outcome to the caller. The bounded append-acknowledgement prerequisite therefore retains semantic residue. Typed `Persisted` versus `Ambiguous`, retry authority, duplicate reconciliation, compaction gating, and remote-effect settlement remain later and separate layers.

Current carrier head: `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`.  
Authoritative run: `30582576317`, queued at this workspace snapshot.

### Terminal output retention

Historical source: `teamleaderleo/codex#49`.  
Execution carrier: `teamleaderleo/codex#53`.

Upstream adopted `VecDeque` buffering and improved invalid-UTF-8 progress. That work overlaps the same files and makes the historical patch mechanically conflicting. It does not transfer producer-owned retention before best-effort broadcast, so semantic residue remains.

Current carrier head: `d5028fc9771407aa7a9bafbceb7eba051b91de36`.  
Authoritative run: `30582012412`, queued at this workspace snapshot.

### Timeout and cancellation certainty

Fieldwork #134 and #162 separate caller deadline, cancellation delivery, transport state, and remote-effect certainty. Delivery of a cancellation request never proves absence of a committed mutation. This layer feeds result receipts but belongs to MCP operation lifecycle rather than generic append acknowledgement.

## Canonical output plan

Several outputs are expected because the audiences and decisions differ:

1. a plain-language Codex lifecycle model;
2. a current-upstream convergence ledger;
3. separate proposal packets for surviving bounded invariants;
4. a carrier retirement and successor ledger;
5. a negative-result or stopped record for absorbed or obsolete candidates.

The current canonical index is [`canonical/README.md`](canonical/README.md). Candidate status remains explicit until exact-head execution and independent review complete.

## Active decisions

- Keep append acknowledgement separate from remote execution settlement.
- Keep MCP generation publication separate from prepared or active call authority.
- Preserve upstream terminal decoding improvements while restacking producer-owned retention.
- Treat Code Mode host migration as a new authority boundary for deferred discovery.
- Permit several canonical outputs instead of forcing the entire portfolio into one patch or one upstream conversation.
- Retire execution carriers only after source, receipts, and successor links reach durable canonical records.

## Snapshot limits

This workspace is a coordinator synthesis surface. Campaign reports, owned source branches, exact workflow receipts, and review records remain the evidence authorities for their bounded claims.

Run status and upstream head can change after this snapshot. [`handoff.md`](handoff.md) records the exact checked state and continuation protocol.