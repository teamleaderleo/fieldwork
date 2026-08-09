# Tauri filtered pending-emit ordering model receipt — 2026-08-09

## In simple words

The first no-bound architectural alternative looked good on simple reentrant listen/unlisten cases but failed a deeper nested-emission ordering control. It must not replace the current queue semantics as-is.

Evidence class: `model-executed`  
Environment: Python `3.13.5`  
Campaign: #754  
Command: `python3 ordering_model.py`  
Upstream contact authorized: `false`

## Candidate B

Model:

- snapshot the current callbacks for an emission;
- release the handler registry before invoking callbacks;
- apply listen/unlisten immediately to the live registry;
- when a callback emits recursively, snapshot the then-current handlers and queue that selected child emission until the current callback pass ends.

This preserves the public filter lifetime because the filter can be evaluated synchronously against a snapshot instead of being stored in shared pending state.

## Results

```text
PASS unlisten-before-emit: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A')]
PASS listen-before-emit: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A'), ('nested-A1', 'B'), ('nested-A1', 'C')]
PASS emit-before-unlisten: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A'), ('nested-A1', 'B')]
PASS emit-before-listen: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A'), ('nested-A1', 'B')]
PASS later-callback-remove: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A'), ('nested-A1', 'B'), ('nested-A1', 'C')]
CURRENT deep: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A'), ('nested-A1', 'B'), ('nested-A1', 'C'), ('nested-C', 'A'), ('nested-C', 'B'), ('nested-C', 'C'), ('nested-A2', 'A'), ('nested-A2', 'C'), ('nested-B', 'A')]
CANDIDATE_B deep: [('outer', 'A'), ('outer', 'B'), ('nested-A1', 'A'), ('nested-A1', 'B'), ('nested-A1', 'C'), ('nested-C', 'A'), ('nested-A2', 'A'), ('nested-A2', 'C'), ('nested-B', 'A')]
NEGATIVE candidate B changes nested child-emission ordering/selection
```

## Why it loses

The current pending implementation detaches the parent's pending list before executing a queued child emit. New actions produced inside that child go into a fresh pending list and are flushed before control returns to later siblings in the detached parent list.

Candidate B applies later parent-callback mutations to the live registry immediately. When an earlier queued child eventually runs, a grandchild emission observes those later mutations too early. In the discriminator, `nested-C` therefore loses listeners that current semantics still includes.

## Disposition

**REJECT candidate B as currently shaped.**

A viable no-bound design would need scoped or virtual event state that preserves the registry view at each pending-action position and lets descendants inherit that view. That is materially more complex than the original snapshot idea. Keep #749's already target-validated narrow panic repair independent while this interface problem remains under comparative evaluation.