# Vercel AI stream and tool lifecycle scout

## Current disposition

The original `report.md` preserves the broad reconnaissance and synthetic probe as conducted. Its initial recommendation to pursue reader cancellation during local tool execution was superseded by the pinned source and test interpretation developed afterward.

Use these documents for synthesis in this order:

1. `follow-up-terminal-outcomes.md` — corrected cancellation contract and final branch dispositions;
2. `surrounding-lifecycle-candidates.md` — separated findings, stopped branches, and promoted campaigns;
3. `report.md` — architecture map, lifecycle traces, focused test map, and original probe record;
4. `artifacts/synthetic-cancellation-probe.output.json` — recorded primitive-level probe output.

## Final conclusions

- Reader cancellation is consumer-scoped and is not an operation abort by itself.
- Explicit abort while a provider read remains pending is the active core candidate under campaign #76 and owned PR `teamleaderleo/ai#1`.
- Provider close after partial output needs a truthful truncated/incomplete classification under campaign #94.
- Resumable Stop state must not leak across runs; campaign #95 owns that work and owned PR `teamleaderleo/ai#3` contains the minimal stale-state repair.
- Ordinary provider stream errors already settle aggregate results at the pinned revision.
- Duplicate ToolLoopAgent callback implementation work stopped because an existing upstream candidate covers that surface.

Scout issue #17 is ready for synthesis. No upstream contact was performed.
