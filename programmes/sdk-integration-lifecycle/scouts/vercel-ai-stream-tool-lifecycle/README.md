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

## Final conclusions

- Reader cancellation is consumer-scoped and is not an operation abort by itself.
- Explicit abort while a provider read remains pending is the active core candidate under campaign #76. Owned PR [`teamleaderleo/ai#1`](https://github.com/teamleaderleo/ai/pull/1) descends cleanly from the pin and includes broader regression coverage, but remains a draft with two expected-failure race tests and no executed Node/Edge evidence.
- Provider close after partial output needs a truthful truncated/incomplete classification under campaign #94. Existing external UI outcome work is useful compatibility precedent but does not remove the need to test missing terminal protocol state.
- Resumable Stop state must not leak across runs. Campaign #95 owns that work; owned PR [`teamleaderleo/ai#3`](https://github.com/teamleaderleo/ai/pull/3) has a normal narrow state-reset test and an expected-failure delayed-Stop test, so it remains a draft sequential mitigation rather than a run-scoped fix.
- Idle UI responses need optional transport liveness for self-hosted reverse-proxy deployments. Campaign #150 and owned draft [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4) add client-branch-only SSE comments, public-helper propagation, timer/cancellation guards, documentation, and focused tests. Real HTTP/proxy validation remains open.
- Ordinary provider stream errors already reject the root result promises at the pinned revision.
- Current streaming translation already uses an explicit single-owner live-stream contract and does not reproduce the older promise-only deadlock.
- Duplicate `ToolLoopAgent` callback, UI outcome, and large-output tee-retention implementation work stopped where active external candidates already provide stronger coverage.

Scout issue #17 is ready for synthesis. Promoted implementation and validation work belongs to campaigns #76, #94, #95, and #150. No upstream contact was performed.