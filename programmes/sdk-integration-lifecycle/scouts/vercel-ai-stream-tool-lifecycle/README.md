# Vercel AI stream and tool lifecycle scout

## Current disposition

The original `report.md` preserves the broad reconnaissance and synthetic probe as conducted. Its initial recommendation to pursue reader cancellation during local tool execution was superseded after reviewing the pinned source, tests, history, and surrounding proposals.

Pinned target: [`vercel/ai@2b872b0db3769decf69945830c66a897c1e37347`](https://redirect.github.com/vercel/ai/commit/2b872b0db3769decf69945830c66a897c1e37347).

Use these documents for synthesis in this order:

1. `plain-language-explainer.md` — restaurant-order, partial-delivery, phone-call, and package analogies for cancellation, truncation, transport liveness, and resumable Stop ownership;
2. `verification-notes.md` — branch-history audit, ordinary tests, expected-failure tests, runnable commands, and remaining implementation gates;
3. `adjacent-sdk-review.md` — historical precedent, reviewed subsystems, stopped duplicates, and the promoted idle UI stream campaign;
4. `follow-up-terminal-outcomes.md` — corrected cancellation contract, result-settlement model, and validation gates;
5. `surrounding-lifecycle-candidates.md` — separated original findings, stopped branches, promoted campaigns, and source links;
6. `report.md` — architecture map, lifecycle traces, focused test map, and original probe record;
7. `artifacts/synthetic-cancellation-probe.output.json` — recorded primitive-level probe output.

## Four-campaign synthesis packet

1. **#76 — explicit-abort terminal settlement.** Owned draft [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) descends cleanly from the pin and includes pending-read, pre-abort, active-tool, root/derived-result, and multi-consumer coverage. Callback-stall and abort/error races remain expected failures, and no Node/Edge run has executed here.
2. **#94 — truncated-stream classification.** Preserve useful partial output while distinguishing a provider close without a terminal protocol event from ordinary completion. Existing external UI outcome work is compatibility precedent, not a substitute for the incomplete-close matrix.
3. **#95 — resumable Stop ownership.** Owned draft [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3) proves the ordered stale-state reset and records delayed Stop as an expected failure. A complete design still needs run identity and conditional state ownership.
4. **#150 — idle UI response liveness.** Owned draft [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4) adds opt-in client-branch SSE comments, propagation through Fetch/Node/`streamText`/agent helpers, bounded buffering, timer and cancellation guards, documentation, and focused tests. Real HTTP/proxy execution remains open.

## Additional conclusions

- Reader cancellation is consumer-scoped and is not an operation abort by itself.
- Ordinary provider stream errors already reject the root result promises at the pinned revision.
- Current streaming translation already uses an explicit single-owner live-stream contract and does not reproduce the older promise-only deadlock.
- Duplicate `ToolLoopAgent` callback, UI outcome, and large-output tee-retention implementation work stopped where active external candidates already provide stronger coverage.

Scout issue #17 is ready for synthesis. Promoted implementation and validation work belongs to campaigns #76, #94, #95, and #150. No upstream contact was performed.