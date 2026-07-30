# Canonical outputs for Codex convergence

Parent workspace: [`../README.md`](../README.md)  
Decision owner: Fieldwork #239 coordinator  
Current upstream pin: `745603a5a1eb48b6f343633d622eeb72dd549d7b`  
Last reviewed for this index: 2026-07-31

## In simple words

This directory declares which presentations currently represent the Codex convergence work. Several outputs are allowed because a new reader, a source reviewer, and a proposal reviewer need different levels of detail.

The findings remain the evidence trail. Canonical outputs select and explain that evidence for a named purpose.

## Output index

| Output | Audience and purpose | Status | Evidence inputs | Current limit |
| --- | --- | --- | --- | --- |
| [`convergence-model.md`](convergence-model.md) | Any reader who needs to understand what #239 is doing and why | `accepted` for internal orientation | problem map, drift ledger, alternatives, precedent | system explanation; no source proposal acceptance |
| [`../findings/upstream-drift-and-overlap.md`](../findings/upstream-drift-and-overlap.md) | Workers and reviewers deciding whether a historical Codex candidate survives current upstream | `candidate` | exact source pins, current file overlap, carrier state | refresh after relevant upstream drift or carrier publication |
| Append acknowledgement proposal packet | Codex source reviewer | `pending` | owned Codex #51/#52 and persistence prior art | waits for exact current-head source publication and review |
| Terminal producer-retention proposal packet | Codex source reviewer | `pending` | owned Codex #49/#53 and current unified-exec prior art | waits for exact carrier result and source-only diff review |
| MCP refresh generation proposal packet | Codex runtime reviewer | `pending` | owned Codex #46/#48 plus current upstream reconnect work | current overlap with upstream #34952/#35151 requires exact comparison |
| Deferred executable-authority proposal packet | Code Mode and request-construction reviewer | `disputed` | owned Codex #45, Responses Lite findings, standalone host migration | owning source boundary requires redesign |
| Responses Lite first-generated capability packet | transport and request reviewer | `held` | historical source intent and stack diagnostics | lower-level exact-prefix and retry evidence required |
| MCP timeout outcome model | MCP lifecycle and receipt reviewer | `candidate` in Fieldwork #134/#162 | executed six-control matrix and manager ownership analysis | modern high-level operation cancellation remains separate |
| Carrier retirement ledger | Fieldwork reviewer | `pending` | #239 classifications and exact receipt transfer | carriers #52/#53 remain active |

## Canonicalization rules applied here

- `accepted` names an audience and claim boundary.
- An orientation document can be accepted while every source candidate remains under review.
- A source proposal stays pending until its canonical branch, exact head, current base, complete diff, exact tests, and retained receipts are known.
- A disputed output preserves the viable question and the unresolved decision.
- A held output preserves useful evidence while preventing premature implementation claims.
- Absorbed or obsolete candidates will receive retained stopped records rather than disappearing from the history.

## Current accepted output

[`convergence-model.md`](convergence-model.md) is the accepted internal explanation of the portfolio. It states:

- the end-to-end tool lifecycle;
- why several ledgers can diverge;
- the independent invariants under review;
- why several proposal packets are preferable to one mega-patch;
- what completion means for issue #239.

Acceptance of this explanation carries no merge or upstream-contact authority.

## Decision log

### 2026-07-31 — accept one system model and several bounded proposal outputs

Decision:

- use one plain-language lifecycle model for orientation;
- retain independent technical findings;
- produce separate proposal packets by source owner and invariant;
- allow new Fieldwork issues when a canonical candidate becomes independently actionable;
- preserve disputed or stopped results beside accepted outputs.

Reason:

The Codex portfolio spans request construction, Code Mode host authority, MCP runtime publication, operation settlement, ThreadStore append, rollout reconciliation, and unified execution. These owners need separate tests, compatibility review, and rollback.

Inputs:

- [`../findings/problem-map.md`](../findings/problem-map.md);
- [`../findings/upstream-drift-and-overlap.md`](../findings/upstream-drift-and-overlap.md);
- [`../alternatives/approach-selection.md`](../alternatives/approach-selection.md);
- [`../precedent/fieldwork-and-upstream-prior-art.md`](../precedent/fieldwork-and-upstream-prior-art.md).

Limits:

Exact source proposal decisions remain pending. Current upstream interaction remains read-only.