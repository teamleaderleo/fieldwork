# Exact-head review audit — 2026-07-30

## In simple words

The OpenTelemetry proposal packet was checked against newer Fieldwork review rules and against current repository state. That audit found one stale coordination branch, one real production regression in the first `startNodeSDK()` repair, and three useful process-review findings in other active Fieldwork pull requests.

No upstream contact occurred.

## Scope

- Fieldwork repository current main: `8194842618d55f5065fb27228d0593cb364822d9`
- Fieldwork packet branch reviewed head before this audit: `387f033c8ed55886b17a86be027f9234cb2549a9`
- OpenTelemetry fork base: `7b06368b7362a30ca69c178f43bd94dfbb36f85d`
- `NodeSDK` start-guard head: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`
- repaired `startNodeSDK()` cleanup head: `482cb975f78572bc65a9b263fb677b7a274e2fff`

## Other Fieldwork work reviewed

### PR #143 — exact-head review and promotion hygiene

Reviewed head: `ec0b43245392d4e8faa29bc1624c75c6dd97c173`

Disposition recorded: `REPAIR`.

Finding:

The proposed receipt permits GitHub issue `updated_at` as an issue-body generation. That timestamp is not body-specific and can advance for unrelated conversation or metadata activity. Using it as a body revision would invalidate otherwise valid reviews noisily.

Recommended repair:

- prefer a body digest or explicit body revision marker;
- track live labels, state, assignees, and other metadata as separate reviewed inputs only when they affect the disposition;
- describe `updated_at` only as an intentionally coarse snapshot marker, not a body generation.

The connected GitHub identity is also the PR author, so GitHub rejected a formal `REQUEST_CHANGES` review. A review comment records the repair disposition.

### PR #105 — human review queue

Reviewed head: `b4c2ca07a344ed3c1714ccb9d3fe4ea1cb62809a`

Disposition recorded: `REVISE`.

Finding:

The queue claimed to represent the live decision front but omitted the active OpenTelemetry JS lifecycle packet even though target hub #4, scout #19, and synthesis PR #32 exposed five promoted units and two retained execution-gated leads.

Recommended repair:

Add a bounded queue card or monitored-work entry preserving these evidence classes:

- owned-fork implementation plus prepared tests for the two narrow helper fixes;
- issue-first contract candidates for trace shutdown, metric construction, and global ownership;
- source-derived/prepared-test status for interleaving and fanout until execution exists.

The omission also demonstrates why a same-day dated snapshot needs exact source generations or a generated-at input fence.

### PR #154 — continuous coordination compiler research

Reviewed head: `83f91359f628e567a06726246929481043cf2e3c`

Disposition recorded: `REVISE`.

Finding:

The proposed authority example reduced authority to fields such as `grants_upstream_contact: false` and `effects_authorized`. That is not enough for a future mutation controller to prove that a particular actor may perform a particular effect on a particular current object.

Recommended repair:

Use capability-shaped authority records binding:

- grant and issuer identity;
- principal or actor;
- exact action or capability;
- repository/resource/subject;
- bound source and subject generations or digests;
- issue time, expiry, and revocation generation;
- delegation limits.

Evaluator receipts should reference the exact authority record. Revocation or actor changes must invalidate derived eligibility even when the evidence graph is unchanged.

## Own Fieldwork packet review

### PR #32 staleness

Reviewed packet head: `387f033c8ed55886b17a86be027f9234cb2549a9`

Compared with current main `8194842618d55f5065fb27228d0593cb364822d9`:

- status: diverged;
- ahead: 34 commits;
- behind: 85 commits;
- merge base: `09fe47ac92ec9c0c333b4979011f6321795deff2`.

Disposition: `HOLD` for repository promotion.

Action taken:

- converted PR #32 back to draft;
- posted an exact-head self-review receipt;
- kept target hub #4, programme hub #13, and scout #19 current so the packet remains discoverable without pretending the stale branch is promotion-ready.

Required clearing condition:

Reconcile the report and proposal files with current main, especially root README and target-map edits, then perform a fresh complete-diff review.

## Own fork review

### PR #2 — `NodeSDK` one-start-attempt guard

Current head: `14b524ff0c0d8e39321c31be218b0c9ee0ca0b78`

Base relation:

- ahead of pinned base by 2 commits;
- behind by 0;
- production diff remains seven additions in `sdk.ts` plus one focused test file.

Disposition: `EXECUTE`.

No new source defect was found in this audit. The patch remains intentionally narrow and does not claim a complete start/shutdown state machine.

### PR #3 — failed `startNodeSDK()` setup cleanup

First reviewed head: `3f79d0d93155edd82174d161caafd650aefdcfd7`

Self-review finding:

The first implementation created and globally published providers before invoking user-controlled instrumentation registration. If a provider setter or instrumentation `enable()` threw, the function returned no shutdown handle while the newly published globals remained installed.

Repair:

- register instrumentation against newly created providers before process-global publication;
- clean up helper-created components if registration throws;
- preserve the thrown registration error;
- add a regression test asserting that no context or tracer global is published and the created tracer provider receives shutdown.

Repaired head: `482cb975f78572bc65a9b263fb677b7a274e2fff`

Disposition: `EXECUTE`.

Remaining limitation:

The cleanup starts provider shutdown synchronously but cannot await it because `startNodeSDK()` is synchronous. Cleanup-error preservation and asynchronous shutdown rejection handling remain a follow-up boundary.

## Evidence classes

- Fieldwork and fork source review: `source-read`.
- Retained async/retry probe: `model-executed`.
- Fork tests: `target-test-prepared`.
- Target package execution for new lifecycle tests: not retained.
- Full repository gate: not claimed.

## Contact boundary

No OpenTelemetry upstream issue, pull request, comment, review, reaction, or direct backlink was created. Fieldwork and user-owned fork activity remained within authorized repositories.
