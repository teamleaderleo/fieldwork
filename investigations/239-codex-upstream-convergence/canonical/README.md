# Canonical outputs for Codex convergence

Parent workspace: [`../README.md`](../README.md)  
Canonical technical finding: [`F239`](../../../findings/F239-codex-upstream-convergence/finding.md)  
Decision owner: Fieldwork #239 coordinator  
Current upstream pin: `3016671bb077c43448b8fa88f3edfa9772e17058`  
Last reviewed for this index: 2026-07-31  
Upstream contact authorized: `no`

## In simple words

This directory declares which presentations currently represent the Codex convergence work. Several outputs are allowed because a new reader, a source reviewer, and a proposal reviewer need different levels of detail.

The canonical F239 finding owns the technical conclusion and transition state. Workspace evidence remains the research trail. Files in this directory select and explain that evidence for a named audience; their presentation status does not grant source acceptance or delivery authority.

## Output index

| Output | Audience and purpose | Status | Evidence inputs | Current limit |
| --- | --- | --- | --- | --- |
| [`convergence-model.md`](convergence-model.md) | Anyone who needs to understand what #239 is doing and why | `accepted` for internal orientation | F239, problem map, drift ledger, alternatives, precedent | system explanation; no source proposal acceptance |
| [`../findings/upstream-drift-and-overlap.md`](../findings/upstream-drift-and-overlap.md) and dated evidence snapshots | Workers and reviewers deciding whether a historical candidate survives current source | `candidate` | source pins through `3016671...`, current carrier heads | refresh after relevant upstream drift or carrier publication |
| Append acknowledgement proposal packet | Codex session/ThreadStore reviewer | `held` | owned #51/#52 and current-pin carrier #80 | run `30583967538` and source-only review remain |
| Terminal producer-retention proposal packet | Codex unified-exec reviewer | `held` | owned #49/#53 and current unified-exec prior art | run `30585540688` and source-only review remain |
| MCP refresh generation packet | Codex runtime reviewer | `candidate` | owned #46/#48 plus current reconnect work | exact comparison with upstream #34952/#35151 remains |
| Deferred executable-authority packet | Code Mode/request-construction reviewer | `disputed` | owned #45, Responses Lite findings, standalone-host migration | owning source boundary requires redesign |
| Responses Lite first-generated capability packet | Transport/request reviewer | `held` | historical intent and stack diagnostics | lower-level exact-prefix and retry evidence required |
| MCP timeout outcome model | MCP lifecycle reviewer | `candidate` in Fieldwork #134/#162 | executed matrix and manager ownership analysis | current high-level operation cancellation remains separate |
| Carrier retirement ledger | Fieldwork reviewer | `candidate` | F239 classifications and exact receipt transfer | #52/#53/#80 successor mapping remains active |

## Status rules applied here

- `accepted` names an audience and claim boundary.
- An orientation document can be accepted while source candidates remain under execution or comparison.
- `candidate` means ready for comparison, not source acceptance.
- `disputed` preserves a viable output with a technical or human choice still open.
- `held` preserves evidence while preventing premature implementation claims.
- `superseded` and `retired` preserve history and name the successor.
- Output status never replaces F239's `comparative-evaluation-active` state.

## Current accepted output

[`convergence-model.md`](convergence-model.md) is the accepted internal explanation of the portfolio. It explains:

- the end-to-end tool lifecycle;
- why several ledgers can diverge;
- the independent invariants under review;
- why several proposal packets are preferable to one mega-patch;
- what completion means for issue #239.

Acceptance carries no merge, delivery, or public-upstream authority.

## Decision log

### 2026-07-31 — one system model and several bounded technical outputs

Decision:

- use one plain-language lifecycle model for orientation;
- retain independent technical findings and evidence notes;
- produce separate proposal packets by source owner and invariant;
- open successor findings when a candidate becomes independently actionable;
- preserve disputed, held, stopped, and superseded results beside accepted outputs;
- keep F239 `comparative-evaluation-active` while technical execution and comparison can still distinguish directions.

Reason:

The portfolio spans request construction, Code Mode host authority, MCP runtime publication, operation settlement, ThreadStore append, rollout reconciliation, and unified execution. These owners need separate tests, compatibility review, and rollback.

Inputs:

- [`../../../findings/F239-codex-upstream-convergence/finding.md`](../../../findings/F239-codex-upstream-convergence/finding.md);
- [`../findings/problem-map.md`](../findings/problem-map.md);
- [`../findings/upstream-drift-and-overlap.md`](../findings/upstream-drift-and-overlap.md);
- [`../alternatives/approach-selection.md`](../alternatives/approach-selection.md);
- [`../precedent/fieldwork-and-upstream-prior-art.md`](../precedent/fieldwork-and-upstream-prior-art.md);
- [`../handoff.md`](../handoff.md).

Limits:

Exact source proposal decisions remain pending. Public upstream remains read-only.
