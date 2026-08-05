# Vite, Rollup, and Rolldown lifecycle contract map

State: `ready`

## In simple words

Vite plugin behavior is not designed in isolation. Some lifecycle rules come from Rollup, and Rolldown aims to provide a compatible implementation that increasingly matters to Vite.

This batch first maps Rollup and Rolldown separately. Only after both maps return will a third worker compare them with Vite. The immediate work is research and contract recovery, not implementation.

## Coordination

- Parent batch issue: #639
- Programme hub: #15
- Vite target hub: #9
- Source lesson and current submitted work: #624
- Batch ID: `B20260805-001`
- Maximum active assignments: `2`
- Upstream contact authorized: `false`

## Assignment state

| Assignment | State | Owner | Output |
| --- | --- | --- | --- |
| `A001` Rollup lifecycle contract | `ready` | unclaimed | `results/A001.md` |
| `A002` Rolldown compatibility map | `ready` | unclaimed | `results/A002.md` |
| `A003` Vite reconciliation | `blocked` on accepted A001 and A002 handoffs | unclaimed | `results/A003.md` |

## Dispatch rule

A001 and A002 may be claimed in parallel by separate workers. A003 must not begin until the coordinator accepts both earlier handoffs as usable synthesis inputs.

Workers must pin exact source revisions at claim time, use separate result paths or dedicated Fieldwork branches, and report back to #639 with the Fieldwork handoff format.

## Shared boundary

The batch should classify behavior into:

1. shared Rollup contract;
2. Rolldown-compatible behavior or deliberate deviation;
3. intentional Vite adaptation;
4. plausible compatibility defect;
5. separate scheduling or error-policy proposal.

A locally coherent improvement is not automatically a compatibility fix. Existing external issues and pull requests are context and overlap checks, not a work queue.

## Completion gate

The batch is ready for coordinator synthesis when:

- A001 and A002 contain exact revisions, source and test maps, negative results, and handoffs;
- A003 contains the cross-target matrix and at least one bounded probe or explicit feasibility limit;
- contradictions and unknowns remain visible;
- any proposed follow-up names current behavior, consequence, likely owner, falsifiable evidence, and a bounded question;
- the coordinator records whether Rollup or Rolldown should remain reference repositories or become recurring Fieldwork targets;
- no public upstream interaction occurred.
