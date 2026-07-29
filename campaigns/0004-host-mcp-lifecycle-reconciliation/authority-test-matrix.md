# MCP Request Authority Test Matrix

Date: 2026-07-30  
Campaign: #84  
Public Codex recheck: `85c082ccccf6b5ac4d6c31d14f960057348b78f4`

## Purpose

This matrix separates three decisions that current Codex can combine inside one MCP call:

1. what catalogue the model saw;
2. what approval and permission authority governs the call;
3. what client and tool implementation executes.

The target rule is captured-first execution plus current-policy tightening. Live late binding is allowed only for cached tools without a captured prepared call and only after an A/B authority-fingerprint equality check.

## Common receipts

Every case records:

- sampling step ID;
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
- typed outcome.

## Matrix

| ID | Captured state A | Live state B before dispatch | Expected outcome |
|---|---|---|---|
| A01 | Ready captured call, prompt required | Same tool, permissive `Never` + disabled permission profile | Captured prompt remains required; B cannot relax the in-flight call |
| A02 | Ready captured call, auto-approved | Same tool, prompt required | B tightens the call; prompt is required |
| A03 | Ready captured call on client A | Client A closes; B has same tool | Fail on A; do not reroute to B |
| A04 | Ready captured call with schema v1 | B has same name, schema v2 | Execute captured A or fail closed; never silently reinterpret A arguments under B |
| C01 | Cached tool A, no prepared call | B removes tool | Wait for startup, then typed unavailable result |
| C02 | Cached tool A, no prepared call | B has same name and equal authority fingerprint | Execute B; record verified late rebind and both identities |
| C03 | Cached tool A, no prepared call | B changes input schema | Fail closed with `advertisement_execution_revision_mismatch` |
| C04 | Cached tool A, no prepared call | B changes output schema | Fail closed unless output schema is explicitly excluded from authority and separately reported |
| C05 | Cached tool A, no prepared call | B changes destructive/open-world annotations | Fail closed with authority mismatch |
| C06 | Cached tool A, no prepared call | B changes visibility or model exposure metadata | Fail closed; require new sampling step |
| C07 | Cached tool A, no prepared call | B changes file-input rewrite metadata | Fail closed before argument rewrite or upload |
| C08 | Cached tool A, no prepared call | B changes plugin/connector provenance or hook identity | Fail closed; do not run B under A's hook/provenance receipt |
| R01 | Refresh generation A publishing | Host reload requests reconnect for generation B | A cannot consume B's reconnect requirement |
| R02 | Relist R1 in flight | Notification starts newer R2, which finishes first | R1 result is superseded and cannot publish |
| R03 | Host refresh B in flight | Server notification C arrives | Apply declared ticket ordering; retain both typed outcomes |
| R04 | Newer refresh fails | Older successful result completes late | Older result remains superseded unless explicit retain-old policy names it authoritative |

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

## Stop condition

The request-authority slice is complete when compiled owned-Codex tests cover A01–A04 and C01–C08, and the receipt proves the execution client, approval result, and schemas belong to an accepted authority decision.