# Vercel AI stream and tool lifecycle scout

## Current disposition

The original `report.md` preserves the broad reconnaissance and synthetic probe as conducted. Its initial recommendation to pursue reader cancellation during local tool execution was superseded after reviewing the pinned source, tests, and surrounding proposals.

Pinned target: [`vercel/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://redirect.github.com/vercel/ai/commit/2b872b0db3769decf69945830c66a897c1e37347).

Use these documents for synthesis in this order:

1. `follow-up-terminal-outcomes.md` — corrected cancellation contract, result-settlement model, and validation gates;
2. `surrounding-lifecycle-candidates.md` — separated findings, stopped branches, promoted campaigns, and source links;
3. `report.md` — architecture map, lifecycle traces, focused test map, and original probe record;
4. `artifacts/synthetic-cancellation-probe.output.json` — recorded primitive-level probe output.

## Final conclusions

- Reader cancellation is consumer-scoped and is not an operation abort by itself.
- Explicit abort while a provider read remains pending is the active core candidate under campaign #76. Owned PR [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) is a draft pending Node/Edge execution and callback-ordering review.
- Provider close after partial output needs a truthful truncated/incomplete classification under campaign #94.
- Resumable Stop state must not leak across runs. Campaign #95 owns that work; owned PR [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3) is only a draft sequential-state mitigation, not a run-scoped fix.
- Ordinary provider stream errors already reject the root result promises at the pinned revision.
- Duplicate `ToolLoopAgent` callback implementation work stopped because the [existing upstream candidate](https://redirect.github.com/vercel/ai/pull/15867) covers that surface.

Scout issue #17 is ready for synthesis. No upstream contact was performed.