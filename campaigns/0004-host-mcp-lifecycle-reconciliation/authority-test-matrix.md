# MCP Request Authority Test Matrix

Date: 2026-07-30  
Campaign: #84  
Public Codex schema-drift pin: `a5082373f18119dc5d3eb993267c97f37880935d`

## Purpose

This matrix separates four decisions that current Codex can combine inside one MCP call:

1. what catalogue the model saw;
2. what approval and permission authority governs the call;
3. what client and tool implementation executes;
4. whether the caller is still waiting while the server operation remains live.

The target rule is captured-first execution plus current-policy tightening. Live late binding is allowed only for cached tools without a captured prepared call and only after an A/B authority-fingerprint equality check.

## Common receipts

Every case records:

- sampling step ID;
- operation identity;
- advertised catalogue digest A;
- advertised tool schema digest A;
- captured prepared-call presence;
- captured approval/config digest A;
- live runtime generation B;
- live catalogue digest B;
- live tool schema digest B;
- live approval/config digest B;
- server identity A and B;
- late-rebind reason;
- fingerprint equality result;
- prompt, deny, or auto-approval result;
- execution client identity;
- caller-wait state;
- server-cancellation state;
- terminal execution state;
- authoritative persistence state;
- typed outcome.

## Matrix

| ID | Captured state A | Live state B before dispatch/publication | Target outcome | Current evidence |
|---|---|---|---|---|
| A01 | Ready captured call, prompt required | Same tool, permissive `Never` + disabled permission profile | Captured prompt remains required; B cannot relax the in-flight call | Source-confirmed gap; compiled case pending |
| A02 | Ready captured call, auto-approved | Same tool, prompt required | B tightens the call; prompt is required | Compiled case pending |
| A03 | Ready captured call on client A | Client A closes; B has same tool | Fail on A; do not reroute to B | Compiled case pending |
| A04 | Ready captured call with schema v1 | B has same name, schema v2 | Execute captured A or fail closed; never silently reinterpret A arguments under B | Compiled case pending for ready captured calls |
| C01 | Cached tool A, no prepared call | B removes tool | Wait for startup, then typed unavailable result | Existing Codex integration negative control passes |
| C02 | Cached tool A, no prepared call | B has same name and equal authority fingerprint | Execute B; record verified late rebind and both identities | Equality check absent; compiled case pending |
| C03 | Cached tool A advertises `echo(message)` | B has same name and requires `echo(count)` | Fail before invoking B with `advertisement_execution_revision_mismatch` | **Compiled current behavior:** Codex invoked B with A-shaped arguments; B rejected them; error returned to model |
| C04 | Cached tool A, no prepared call | B changes output schema | Fail closed unless output schema is explicitly excluded from authority and separately reported | Compiled case pending |
| C05 | Cached tool A, no prepared call | B changes destructive/open-world annotations | Fail closed with authority mismatch | Compiled case pending |
| C06 | Cached tool A, no prepared call | B changes visibility or model exposure metadata | Fail closed; require new sampling step | Removal/visibility negative control exists; same-name metadata drift pending |
| C07 | Cached tool A, no prepared call | B changes file-input rewrite metadata | Fail closed before argument rewrite or upload | Compiled case pending |
| C08 | Cached tool A, no prepared call | B changes plugin/connector provenance or hook identity | Fail closed; do not run B under A's hook/provenance receipt | Compiled case pending |
| R01 | Refresh generation A publishing | Host reload requests reconnect for generation B | A cannot consume B's reconnect requirement | Source-derived adversarial sequence; compiled case pending |
| R02 | Relist R1 in flight | Notification starts newer R2, which finishes first | R1 result is superseded and cannot publish | SDK race compiled; Codex publication case pending |
| R03 | Host refresh B in flight | Server notification C arrives | Apply declared ticket ordering; retain both typed outcomes | Compiled case pending |
| R04 | Newer refresh fails | Older successful result completes late | Older result remains superseded unless explicit retain-old policy names it authoritative | Compiled case pending |
| T01 | Call sampled and dispatched under A | Codex-style outer timeout fires; no MCP cancellation; B later publishes | Call retains A identity and authority; late completion cannot attach to B | Adjacent Scout #130/#131 compiled the no-cancellation/continued-side-effect premise; Codex integration pending |
| T02 | Call sampled and dispatched under A | Native SDK timeout sends cancellation before B publishes | Terminal cancellation belongs to A; no side effect or late result crosses into B | Adjacent Scout #130/#131 compiled dependency control; Codex integration pending |
| T03 | Potential mutation under A timed out locally | Retry/fallback considered under B | Block replay while terminal or persistence remains ambiguous | Owned receipt and compaction integration pending under #83/#84/#86 |

## Compiled C03 receipt

Exact public Codex test:

```text
A: echo(message: string)
→ model call: {"message":"hello"}
→ B: echo(count: integer)
→ B receives the A-shaped call
→ B rejects: echo schema v2 requires integer count
→ Codex returns B's error to the model
```

Workflow run: `30488803287`  
Job: `90701186402`  
Artifact: `8739076993`  
Artifact digest: `sha256:f759a6b2e0a75bd8b2e2cfb8ef23c42a9d5e4e259473ae121a3b7614089e3148`

The focused test passed because it asserted current behavior. It did not validate the target repair.

The B-side rejection is a negative control, not a sufficient policy. Another B implementation could accept, ignore, or reinterpret A's fields.

## Authority fingerprint

The minimum fingerprint contains:

- configured and observed server identity;
- canonical tool name;
- input schema;
- output schema when used by the client or model contract;
- visibility metadata;
- annotations affecting approval, safety, or scheduling;
- file-input declarations and rewrite metadata;
- plugin and connector provenance affecting approval or hooks;
- server-level approval mode and per-tool overrides;
- environment identity and origin used by permission decisions.

Description drift may be tracked separately when treated as non-authoritative, but it must still appear in the receipt because the model planned from that description.

## Effective approval rule

For already-sampled work:

```text
effective permission = intersection(captured authority A, current authority B)
```

Practical interpretation:

- prompt when either side requires a prompt;
- deny when either side denies;
- use the tighter sandbox or permission restriction;
- never let B auto-approve a call that A required the user to approve;
- apply B's relaxation only to a new sampling step.

## Timeout ownership rule

A local wait timeout is not automatically an MCP terminal outcome.

Until cancellation or a terminal result is observed:

- keep the original operation identity active;
- preserve A's authority and client lineage;
- prevent a newer binding B from claiming the late result;
- keep terminal execution and authoritative persistence unresolved;
- block automatic mutation replay or fallback.

The timeout scout owns dependency and Codex timeout mechanics. #84 owns interaction with binding publication. #83 owns durable operation receipts and result persistence. #86 owns fallback authority.

## Stop condition

The request-authority slice is complete when compiled owned-Codex tests cover A01–A04, C01–C08, and T01–T03, and the receipt proves that execution client, approval result, schemas, timeout/cancellation state, terminal outcome, and persistence belong to one accepted authority decision.
