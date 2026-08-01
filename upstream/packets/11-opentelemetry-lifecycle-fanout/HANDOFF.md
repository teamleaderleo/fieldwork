# Handoff — Unit 11: snapshot lifecycle targets before concurrent fanout

## Current disposition

`HOLD`

The bounded technical direction is accepted from predecessor execution and review. The clean current-public-base source exists with a six-file diff. Promotion remains held until its exact-head workflow matrix completes, an independent reviewer accepts that exact clean diff, and target changelog/submission requirements are resolved.

## Exact identities

- Public upstream base: [`2c931bf4eec18a234a28706567c6977f08139abd`](https://github.com/open-telemetry/opentelemetry-js/commit/2c931bf4eec18a234a28706567c6977f08139abd)
- Owned source branch: [`upstream/unit-11-lifecycle-fanout`](https://github.com/teamleaderleo/opentelemetry-js/tree/upstream/unit-11-lifecycle-fanout)
- Exact source head: [`641528c9786f7d027fef4f4a76ae685f7107d394`](https://github.com/teamleaderleo/opentelemetry-js/commit/641528c9786f7d027fef4f4a76ae685f7107d394)
- Owned validation PR: [`teamleaderleo/opentelemetry-js#18`](https://github.com/teamleaderleo/opentelemetry-js/pull/18)
- Packet branch: [`p0/435-unit-11-opentelemetry-lifecycle-fanout`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-11-opentelemetry-lifecycle-fanout/upstream/packets/11-opentelemetry-lifecycle-fanout)
- Exact packet head: recorded by the final issue #435 handoff after this file is committed
- Accepted predecessor source: [`db7a0b3a2179f43bf1e0145c8352ff0367bdce79`](https://github.com/teamleaderleo/opentelemetry-js/commit/db7a0b3a2179f43bf1e0145c8352ff0367bdce79)
- Accepted predecessor review: [`4824609621`](https://github.com/teamleaderleo/opentelemetry-js/pull/6#pullrequestreview-4824609621)

## Work completed

- Read the Fieldwork operating instructions, upstream workflow, index, templates, target contribution guide, canonical finding, owning issue and comments, scout archive, source PR, adjacent lifecycle compositions, target tests, exact workflow receipts, and relevant public prior art.
- Verified the current public base commit exists in `open-telemetry/opentelemetry-js`.
- Confirmed the only public-base change after the accepted predecessor base was unrelated sampler-jaeger-remote work.
- Created the clean owned source branch directly from the inspected public base.
- Restacked exactly three production files and three target-native test files.
- Removed research-specific wording from test error messages.
- Created owned validation PR #18 against a pinned base mirror branch.
- Materialized the complete packet: `README.md`, `DEEP_DIVE.md`, `APPROACHES.md`, `TESTS.md`, `UPSTREAM_ISSUE.md`, `UPSTREAM_PR.md`, `REVIEW.md`, and this handoff.
- Preserved the safe-call-only negative result, the live-array mutation review, the test-only TypeScript inference failure, exact passing predecessor receipts, duplicate search, alternatives, excluded adjacent work, and public-ready drafts.

## Changed-file fence

1. `packages/sdk-trace/src/MultiSpanProcessor.ts`
2. `packages/sdk-trace/test/common/MultiSpanProcessor.attempt-all.test.ts`
3. `experimental/packages/sdk-logs/src/MultiLogRecordProcessor.ts`
4. `experimental/packages/sdk-logs/test/common/MultiLogRecordProcessor.attempt-all.test.ts`
5. `packages/sdk-metrics/src/MeterProvider.ts`
6. `packages/sdk-metrics/test/MeterProvider.attempt-all.test.ts`

The exact compare is [`2c931bf4...641528c`](https://github.com/teamleaderleo/opentelemetry-js/compare/2c931bf4eec18a234a28706567c6977f08139abd...641528c9786f7d027fef4f4a76ae685f7107d394). No workflows, publishers, receipts, generated output, dependency files, or unrelated formatting appear in the target diff.

## Tests executed

### Accepted predecessor exact head

Head `db7a0b3a2179f43bf1e0145c8352ff0367bdce79` completed successfully:

- Unit Tests `30592187966`;
- Lint `30592187969`;
- E2E Tests `30592187917`;
- Bundler tests `30592187954`;
- W3C Trace Context Integration `30592187936`;
- Ensure API Peer Dependency `30592187910`;
- CodeQL Analysis `30592187920`;
- Zizmor GitHub Actions Security Analysis `30592187924`.

Changelog run `30592187934` was the expected owned-fork skipped policy result. Review `4824609621` accepted the complete six-file diff and classified the branch `land-ready` subject to authority.

### Current clean exact head

Final snapshot at `2026-08-01 08:06 +08:00` for head `641528c9786f7d027fef4f4a76ae685f7107d394`:

- Unit Tests `30674494793`: queued; ten jobs queued;
- E2E Tests `30674494785`: queued; seven jobs queued;
- Lint `30674494830`: queued; one job queued;
- Bundler tests `30674494832`: queued; one job queued;
- W3C Trace Context Integration `30674494799`: queued; one job queued;
- Ensure API Peer Dependency `30674494801`: queued; one job queued;
- CodeQL Analysis `30674494779`: queued; one job queued;
- Zizmor GitHub Actions Security Analysis `30674494823`: queued; one job queued.

No clean-head product conclusion is claimed yet.

## Strongest supported finding

A lifecycle aggregate must define its current membership before invoking user-controlled children. A shallow opening snapshot combined with per-child synchronous safe-call reaches every opening child while preserving eager `Promise.all` concurrency, current trace/logs/metrics error behavior, and future collection mutation.

The claim is attempt-all invocation. It does not establish settle-all completion, aggregate diagnostics, idempotent child shutdown, safe retry, timeout cleanup cessation, or delayed same-owner recursion handling.

## Negative results and rejected approaches

- Safe-call over live arrays passed the first product matrix but still allowed a first child to delete a later indexed child.
- Catching only around `Promise.all` cannot catch a throw that occurs while promise inputs are still being constructed.
- Permanent freezing or copying changes future membership behavior.
- Sequential awaiting changes concurrency and latency.
- Settle-all aggregation changes caller-visible error timing and error types.
- First snapshot-generation metrics callbacks inferred as `() => never`; explicit `() => void` typing repaired only the test fixture.

## Remaining blockers

1. All eight clean-head workflows remain queued.
2. Exact clean-head independent complete-diff review remains pending.
3. The target contribution guide requires changelog entries for behavior changes; final formatting depends on a real public PR number or an explicit skip decision.
4. The clean diff is direct from current base, while its six file-level commits should be squashed before public submission unless maintainers prefer the series.
5. Public upstream `main`, duplicate search, contribution policy, and AI-disclosure expectations must be refreshed immediately before any authorized submission.
6. Public upstream contact remains unauthorized.

## Continuation steps

1. Refresh PR #18 workflow conclusions for the exact source head.
2. Classify and repair any clean-head failure; update every packet identity after a source change.
3. Obtain independent review of the exact six-file compare.
4. When the matrix and review pass, change disposition from `HOLD` to `READY` only after changelog packaging and current-main refresh are complete.
5. Request explicit user authority for the exact public issue or PR interaction.
6. After authorized submission, update the packet with the real upstream link, intentional-reference marker where required, exact submitted head, review feedback, and outcome.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.  
No public issue, pull request, comment, review, reaction, branch, email, or message was created or changed.
