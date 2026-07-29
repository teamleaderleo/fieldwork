# MCP Request Authority Test Matrix

Date: 2026-07-30  
Campaign: #84  
Latest inspected public Codex revision: `9cf6b3905c102cf38b4f93ec2533261a99764d4d`

## Purpose

This matrix decides which state owns an MCP operation when catalogue, policy, connection, timeout, and publication generations overlap.

The governing split is:

- future requests use the newest accepted publication;
- existing work keeps the identity and authority under which it was sampled or dispatched;
- uncertain post-dispatch work remains attached to its original lineage and cannot be replayed or reassigned.

## Required receipt fields

Every case records:

- sampling step and call identity;
- operation effect;
- advertised catalogue and schema digest A;
- captured prepared-call presence;
- captured runtime, client, and authority digest A;
- transport request identity;
- live runtime and catalogue generation B;
- live authority digest B;
- A/B fingerprint result;
- cancellation request and delivery result;
- remote terminal certainty;
- authoritative result-persistence result;
- execution client identity;
- typed outcome.

## Matrix

| ID | Starting state A | Later state B or event | Expected outcome |
|---|---|---|---|
| A01 | Prepared A requires prompt | B becomes permissive | A prompt remains required; B cannot relax the call |
| A02 | Prepared A is permissive | B requires prompt | B tightens the call; prompt is required |
| A03 | Prepared client A | A closes; B has same tool | Fail on A; do not reroute to B |
| A04 | Prepared A schema v1 | B has same name, schema v2 | Execute captured A or fail closed; never reinterpret A arguments under B |
| C01 | Cached A, no prepared call | B removes tool | Typed unavailable result |
| C02 | Cached A, no prepared call | B fingerprint equals A | Execute B and record verified late rebind |
| C03 | Cached A schema v1 | B same name, schema v2 | Typed revision mismatch before rewrite, approval, or execution |
| C04 | Cached A | B changes approval or safety annotations | Typed authority mismatch; require new sampling step |
| C05 | Cached A | B changes visibility or exposure metadata | Typed authority mismatch |
| C06 | Cached A | B changes file-input rewrite metadata | Fail before rewrite or upload |
| C07 | Cached A | B changes plugin, connector, hook, or environment provenance | Fail closed; do not run B under A's receipt |
| R01 | Refresh publication A in flight | Host reload requests generation B | A cannot consume B's reconnect requirement |
| R02 | Older relist R1 in flight | Newer R2 publishes first | R1 is superseded and cannot publish |
| R03 | Host refresh B in flight | Server notification C arrives | Apply declared ticket ordering and retain both typed outcomes |
| R04 | Newer refresh fails | Older success finishes late | Older result remains superseded unless explicit retain-old policy selects it |
| T01 | Potential mutation running on A | Codex local timeout fires without cancel | Mark `MayStillRun`; persisted timeout does not close execution |
| T02 | Potential mutation running on A | Cancellation is delivered and server cooperates | Record cancellation evidence; classify confirmed abort only when remote/transport semantics justify it |
| T03 | Potential mutation running on A | Cancellation send fails or stalls | Return bounded timeout plus unknown cancellation delivery; remain `MayStillRun` |
| T04 | Potential mutation running on A | Server ignores cancellation and commits late | Remain attached to A; reconcile late completion; no automatic retry |
| T05 | Potential mutation running on A | Session-expiry recovery becomes available | Do not replay without idempotency or proof first attempt did not execute |
| T06 | Stateless modern one-shot request | Local stream is closed on timeout | Confirm whether request cancellation token fires and mutation is suppressed |
| T07 | Stateful or resumable modern request | Local stream disconnects | Treat as `MayStillRun` until stronger terminal evidence exists |
| X01 | Timed-out A remains live | Refresh publishes B | B governs future requests; A operation and late result remain tied to A |
| X02 | Timed-out A remains live | Compaction or resume begins | Carry A's uncertainty; block mutation replay and unsafe compaction |

## Authority fingerprint

The minimum A/B fingerprint contains:

- configured connection identity;
- observed remote server identity;
- canonical server and tool name;
- input schema;
- output schema when part of the callable contract;
- visibility and exposure metadata;
- annotations affecting approval, safety, or scheduling;
- file-input declarations and rewrite metadata;
- plugin, connector, and hook provenance;
- approval modes and permission environment.

Description drift may be reported separately if excluded from execution authority, but it still belongs in the receipt because the model planned from A's description.

## Effective approval rule

For already-sampled work:

```text
effective permission = captured authority A intersect current restrictions B
```

Practical result:

- prompt when either side requires a prompt;
- deny when either side denies;
- use the tighter sandbox or permission restriction;
- never let B auto-approve a call A required the user to approve;
- apply B's relaxation only to a new sampling step.

## Execution-certainty rule

Result persistence and execution certainty are independent.

```text
persisted timeout output + unknown remote terminal state = MayStillRun
```

A potential mutation becomes safe for automatic continuation only after one of:

- confirmed remote terminal result;
- confirmed terminal cancellation with adequate protocol semantics;
- durable application receipt or idempotency reconciliation proving the effect;
- explicit human resolution.

## Stop condition

This slice is complete when compiled owned-Codex tests cover the matrix's prepared-call, cached-late-binding, generation, timeout, and cross-boundary cases, and the canonical Campaign #83 receipt records the accepted authority and execution-certainty result.
